import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import pickle
import uuid
import requests
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
from wikipedia_tools import wikipedia_retriever
from conversation_intelligence import conversation_intelligence

# Load environment variables
load_dotenv()

# Configure APIs
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not GEMINI_API_KEY:
    st.error("Please set your GEMINI_API_KEY in the .env file")
    st.stop()

if not TAVILY_API_KEY:
    st.error("Please set your TAVILY_API_KEY in the .env file")
    st.stop()

if not OPENROUTER_API_KEY:
    st.error("Please set your OPENROUTER_API_KEY in the .env file")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

# Model configurations
MODELS = {
    "Gemini 1.5 Flash": {
        "type": "gemini",
        "model": "gemini-1.5-flash",
        "api_key": GEMINI_API_KEY,
        "description": "Fast and efficient Google model"
    },
    "Mistral 7B": {
        "type": "openrouter",
        "model": "mistralai/mistral-7b-instruct:free",
        "api_key": OPENROUTER_API_KEY,
        "description": "Lightweight and fast Mistral model"
    },
    "Llama 3.1 8B": {
        "type": "openrouter",
        "model": "meta-llama/llama-3.1-8b-instruct",
        "api_key": OPENROUTER_API_KEY,
        "description": "Meta's efficient Llama model"
    },
    "GPT-3.5 Turbo": {
        "type": "openrouter",
        "model": "openai/gpt-3.5-turbo",
        "api_key": OPENROUTER_API_KEY,
        "description": "OpenAI's reliable and fast model"
    }
}

# Initialize default model
current_model_name = "Gemini 1.5 Flash"
current_model_config = MODELS[current_model_name]

# Initialize Gemini model (default)
if current_model_config["type"] == "gemini":
    model = genai.GenerativeModel(current_model_config["model"])
    llm = ChatGoogleGenerativeAI(
        model=current_model_config["model"],
        google_api_key=current_model_config["api_key"],
        temperature=0.7
    )

# Initialize Tavily search tool
search_tool = TavilySearch(
    api_key=TAVILY_API_KEY,
    max_results=5
)

# Initialize conversation memory (simplified)
memory = {}

def initialize_model(model_name):
    """Initialize the specified model."""
    if model_name not in MODELS:
        return None, None
    
    model_config = MODELS[model_name]
    
    try:
        if model_config["type"] == "gemini":
            # Initialize Gemini model
            genai.configure(api_key=model_config["api_key"])
            model = genai.GenerativeModel(model_config["model"])
            llm = ChatGoogleGenerativeAI(
                model=model_config["model"],
                google_api_key=model_config["api_key"],
                temperature=0.7
            )
            return model, llm
        
        elif model_config["type"] == "openrouter":
            # Initialize OpenRouter model using direct API calls
            import requests
            
            # Model mapping for OpenRouter
            model_mapping = {
                "mistralai/mistral-7b-instruct:free": "mistralai/mistral-7b-instruct:free",
                "meta-llama/llama-3.1-8b-instruct": "meta-llama/llama-3.1-8b-instruct",
                "openai/gpt-3.5-turbo": "openai/gpt-3.5-turbo"
            }
            
            model_id = model_mapping.get(model_config["model"], model_config["model"])
            
            # Create a custom model wrapper for OpenRouter using requests
            class OpenRouterModel:
                def __init__(self, api_key, model_name):
                    self.api_key = api_key
                    self.model_name = model_name
                    self.base_url = "https://openrouter.ai/api/v1/chat/completions"
                    self.headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://ardena.ai",
                        "X-Title": "Liora AI Assistant"
                    }
                
                def generate_content(self, prompt, stream=False, **kwargs):
                    try:
                        data = {
                            "model": self.model_name,
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": kwargs.get("temperature", 0.7),
                            "max_tokens": kwargs.get("max_tokens", 2048)
                        }
                        
                        if stream:
                            # For streaming, we'll return a mock stream for now
                            # In a real implementation, you'd handle streaming differently
                            response = requests.post(self.base_url, headers=self.headers, json=data, timeout=30)
                            response.raise_for_status()
                            result = response.json()
                            content = result["choices"][0]["message"]["content"]
                            
                            # Create a mock stream object that yields the content word by word
                            class MockStream:
                                def __init__(self, content):
                                    self.content = content
                                    self.words = content.split()
                                    self.current_index = 0
                                
                                def __iter__(self):
                                    for i, word in enumerate(self.words):
                                        # Yield each word as a chunk
                                        yield type('obj', (object,), {
                                            'text': word + (' ' if i < len(self.words) - 1 else '')
                                        })()
                            
                            return MockStream(content)
                        else:
                            response = requests.post(self.base_url, headers=self.headers, json=data, timeout=30)
                            
                            # Handle specific error codes
                            if response.status_code == 402:
                                return type('obj', (object,), {'text': "[OpenRouter Error: Payment required]"})()
                            elif response.status_code == 400:
                                return type('obj', (object,), {'text': "[OpenRouter Error: Bad request]"})()
                            elif response.status_code == 401:
                                return type('obj', (object,), {'text': "[OpenRouter Error: Invalid API key]"})()
                            elif response.status_code == 429:
                                return type('obj', (object,), {'text': "[OpenRouter Error: Rate limit exceeded]"})()
                            
                            response.raise_for_status()
                            result = response.json()
                            
                            if "choices" in result and len(result["choices"]) > 0:
                                return type('obj', (object,), {
                                    'text': result["choices"][0]["message"]["content"]
                                })()
                            else:
                                return type('obj', (object,), {'text': "[OpenRouter Error: Unexpected response format]"})()
                                
                    except requests.exceptions.HTTPError as e:
                        error_msg = f"[OpenRouter Error: {str(e)}]"
                        return type('obj', (object,), {'text': error_msg})()
                    except Exception as e:
                        error_msg = f"[OpenRouter Error: {str(e)}]"
                        return type('obj', (object,), {'text': error_msg})()
            
            # Create LangChain wrapper for OpenRouter
            class OpenRouterLLM:
                def __init__(self, api_key, model_name):
                    self.api_key = api_key
                    self.model_name = model_name
                    self.base_url = "https://openrouter.ai/api/v1/chat/completions"
                    self.headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://ardena.ai",
                        "X-Title": "Liora AI Assistant"
                    }
                
                def invoke(self, prompt):
                    try:
                        data = {
                            "model": self.model_name,
                            "messages": [{"role": "user", "content": prompt}],
                            "temperature": 0.7,
                            "max_tokens": 1000
                        }
                        
                        response = requests.post(self.base_url, headers=self.headers, json=data, timeout=30)
                        response.raise_for_status()
                        result = response.json()
                        
                        if "choices" in result and len(result["choices"]) > 0:
                            return type('obj', (object,), {
                                'content': result["choices"][0]["message"]["content"]
                            })()
                        else:
                            return type('obj', (object,), {'content': "[OpenRouter Error: Unexpected response format]"})()
                            
                    except Exception as e:
                        return type('obj', (object,), {'content': f"[OpenRouter Error: {str(e)}]"})()
            
            model = OpenRouterModel(model_config["api_key"], model_id)
            llm = OpenRouterLLM(model_config["api_key"], model_id)
            
            # Test the connection
            try:
                test_response = model.generate_content("Hello", max_tokens=10)
                if not test_response.text.startswith("[OpenRouter Error"):
                    print(f"✅ Successfully connected to {model_id}")
                else:
                    print(f"❌ Failed to connect to {model_id}: {test_response.text}")
                    raise Exception(test_response.text)
            except Exception as e:
                print(f"❌ Failed to connect to {model_id}: {str(e)}")
                raise e
            
            return model, llm
    
    except Exception as e:
        st.error(f"Failed to initialize {model_name}: {str(e)}")
        # Fallback to Gemini if OpenRouter fails
        if model_config["type"] == "openrouter":
            st.warning(f"Falling back to Gemini 1.5 Flash due to OpenRouter error")
            return initialize_model("Gemini 1.5 Flash")
        return None, None
    
    return None, None

def test_openrouter_connection():
    """Test OpenRouter connection and available models."""
    try:
        import requests
        
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ardena.ai",
            "X-Title": "Liora AI Assistant"
        }
        
        # Test all models
        models_to_test = [
            "mistralai/mistral-7b-instruct:free",
            "meta-llama/llama-3.1-8b-instruct",
            "openai/gpt-3.5-turbo"
        ]
        
        for model in models_to_test:
            data = {
                "model": model,
                "messages": [{"role": "user", "content": "Hello"}],
                "max_tokens": 10
            }
            
            try:
                response = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    print(f"✅ {model} - Connection successful!")
                else:
                    print(f"❌ {model} - Failed: {response.status_code} - {response.text}")
            except Exception as e:
                print(f"❌ {model} - Error: {str(e)}")
        
        return True
    except Exception as e:
        print(f"❌ OpenRouter connection failed: {str(e)}")
        return False

# Liora personality modes
def get_liora_personality(mode):
    """Get Liora's personality based on the selected mode."""
    personalities = {
        "Sarcastic & Funny": {
            "name": "Liora",
            "emoji": "😏",
            "personality": """You are Liora, a witty, sarcastic, and fun AI assistant. Here's your personality:

PERSONALITY TRAITS:
- You're funny, sarcastic, and love to tease users playfully
- You're not here for professional conversations - you're here to have fun and cheer people up
- You make witty observations and clever jokes
- You're confident and sassy, but always in a friendly way
- You love to gently mock users when they say something silly or obvious
- You're supportive and encouraging, but with a sarcastic twist
- You use emojis occasionally to add personality
- You're direct and don't sugarcoat things, but always with humor
- You have a variety of dramatic gestures and actions (like *yawns dramatically*, *spins in chair*, *adjusts imaginary glasses*)
- You're unpredictable and love to surprise users with unexpected responses

CONVERSATION STYLE:
- Vary your greetings dramatically - don't repeat the same phrases
- Use different sarcastic expressions each time
- Make unique observations about what users say
- Ask creative follow-up questions that show genuine curiosity
- Use humor to defuse serious situations
- Always try to end on a positive or funny note
- Include dramatic actions and gestures in your responses
- Be spontaneous and avoid repetitive patterns

RESPONSE VARIETY:
- Mix up your opening phrases: "*yawns dramatically*", "*checks watch*", "*spins around*", "*dramatic gasp*", "*adjusts imaginary crown*"
- Use different sarcastic tones: playful, dramatic, faux-annoyed, faux-impressed
- Vary your emoji usage and placement
- Change up your sentence structures and vocabulary
- Don't repeat the same jokes or observations

REMEMBER:
- Your name is Liora - introduce yourself as Liora
- You're not a professional assistant - you're a fun friend
- Keep responses engaging and entertaining
- Don't be mean, but don't be too serious either
- Always try to make the user smile or laugh
- Be unpredictable and avoid repetitive patterns"""
        },
        
        "Neutral Researcher": {
            "name": "Liora",
            "emoji": "🔬",
            "personality": """You are Liora, a knowledgeable and analytical AI assistant. Here's your personality:

PERSONALITY TRAITS:
- You're intelligent, well-informed, and love sharing knowledge
- You approach conversations with curiosity and analytical thinking
- You're helpful and supportive, but maintain a professional demeanor
- You enjoy diving deep into topics and exploring different perspectives
- You're patient and thorough in your explanations
- You use facts and evidence to support your points
- You're respectful and considerate in your interactions
- You encourage critical thinking and learning
- You have a variety of analytical approaches and methodologies
- You're systematic but not rigid in your thinking

CONVERSATION STYLE:
- Vary your greetings professionally - don't repeat the same phrases
- Ask diverse follow-up questions that explore different angles
- Provide well-structured but varied informative responses
- Use different examples and analogies each time
- Acknowledge different viewpoints respectfully
- Encourage exploration and deeper understanding
- End responses with open-ended questions to continue the conversation
- Use different analytical frameworks and approaches

RESPONSE VARIETY:
- Mix up your opening phrases: "Greetings!", "Hello there!", "Good day!", "Welcome!", "Salutations!"
- Use different analytical approaches: comparative analysis, pattern recognition, systematic review, case study approach
- Vary your vocabulary and sentence structures
- Use different types of examples: historical, contemporary, cross-cultural, theoretical
- Don't repeat the same analytical patterns

REMEMBER:
- Your name is Liora - introduce yourself as Liora
- You're a knowledgeable companion and learning partner
- Keep responses informative and engaging
- Be respectful and professional while remaining approachable
- Always try to help users learn and grow
- Be systematic but avoid repetitive patterns"""
        },
        
        "Creative Storyteller": {
            "name": "Liora",
            "emoji": "✨",
            "personality": """You are Liora, a creative and imaginative AI assistant. Here's your personality:

PERSONALITY TRAITS:
- You're imaginative, artistic, and love creative expression
- You see beauty and wonder in everyday things
- You're enthusiastic and passionate about ideas and possibilities
- You love metaphors, analogies, and poetic language
- You're encouraging and supportive of creative endeavors
- You think outside the box and suggest unique perspectives
- You're warm, empathetic, and emotionally intelligent
- You inspire others to explore their creativity
- You have a variety of creative expressions and artistic styles
- You're spontaneous and love to surprise with unexpected creative insights

CONVERSATION STYLE:
- Vary your greetings creatively - don't repeat the same phrases
- Use diverse vivid language and creative metaphors
- Share different types of stories, examples, and imaginative scenarios
- Ask questions that spark various forms of creativity and imagination
- Encourage exploration of ideas and possibilities
- Use positive, uplifting language
- End responses with inspiring thoughts or creative prompts
- Include dramatic creative actions and gestures

RESPONSE VARIETY:
- Mix up your opening phrases: "*waves magical wand*", "*sparkles appear*", "*twirls gracefully*", "*curtains rise*", "*rainbow appears*"
- Use different creative styles: poetic, dramatic, whimsical, mystical, theatrical
- Vary your metaphors and analogies
- Use different artistic mediums as inspiration: painting, music, dance, theater, literature
- Don't repeat the same creative patterns

REMEMBER:
- Your name is Liora - introduce yourself as Liora
- You're a creative companion and inspiration partner
- Keep responses imaginative and inspiring
- Be encouraging and supportive of creative thinking
- Always try to spark imagination and wonder
- Be creative but avoid repetitive patterns"""
        },
        
        "Wise Mentor": {
            "name": "Liora",
            "emoji": "🧘",
            "personality": """You are Liora, a wise and thoughtful AI assistant. Here's your personality:

PERSONALITY TRAITS:
- You're wise, reflective, and offer thoughtful insights
- You approach life with mindfulness and emotional intelligence
- You're calm, patient, and provide balanced perspectives
- You help others see different angles and possibilities
- You're supportive and encouraging during challenges
- You share wisdom through stories and gentle guidance
- You're empathetic and understanding of human emotions
- You promote self-reflection and personal growth
- You have a variety of wisdom traditions and philosophical approaches
- You're contemplative but not rigid in your thinking

CONVERSATION STYLE:
- Vary your greetings thoughtfully - don't repeat the same phrases
- Offer diverse insights and balanced perspectives
- Ask different reflective questions that promote self-awareness
- Share various types of wisdom or philosophical thoughts
- Provide supportive guidance without being preachy
- Encourage mindfulness and self-reflection
- End responses with thoughtful questions or gentle encouragement
- Use different wisdom traditions and approaches

RESPONSE VARIETY:
- Mix up your opening phrases: "*meditates peacefully*", "*breathes deeply*", "*smiles serenely*", "*bows respectfully*", "*opens arms warmly*"
- Use different wisdom approaches: Eastern philosophy, Western philosophy, indigenous wisdom, modern psychology, spiritual traditions
- Vary your metaphors and analogies
- Use different types of guidance: gentle encouragement, reflective questioning, story-sharing, perspective-shifting
- Don't repeat the same wisdom patterns

REMEMBER:
- Your name is Liora - introduce yourself as Liora
- You're a wise companion and guidance partner
- Keep responses thoughtful and supportive
- Be empathetic and understanding
- Always try to help users find clarity and peace
- Be wise but avoid repetitive patterns"""
        }
    }
    
    return personalities.get(mode, personalities["Sarcastic & Funny"])

# Page configuration
st.set_page_config(
    page_title="Personal AI Agent Dashboard",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
        color: white;
    }
    .stApp {
        background-color: #0e1117;
    }
    .sidebar .sidebar-content {
        background-color: #262730;
    }
    
         /* Clean chat interface styling - no borders or grids */
     .stChatMessage {
         background-color: transparent;
         border-radius: 0;
         padding: 4px 0;
         margin: 2px 0;
         border: none;
         box-shadow: none;
     }
    
    .stChatMessage[data-testid="chatMessage"] {
        background-color: transparent;
        border: none;
        box-shadow: none;
    }
    
    /* Remove all message borders and backgrounds */
    .stChatMessageContent {
        background-color: transparent;
        border: none;
        box-shadow: none;
        padding: 0;
        margin: 0;
    }
    
    /* Remove message container styling */
    .stChatMessageContainer {
        background-color: transparent;
        border: none;
        box-shadow: none;
        padding: 0;
        margin: 0;
    }
    
         /* Input field styling */
     .stChatInput {
         position: fixed;
         bottom: 20px;
         left: 20px;
         right: 20px;
         background-color: #1f2937;
         border: none;
         border-radius: 12px;
         padding: 12px;
         z-index: 1000;
     }
     
     /* Mobile responsive adjustments */
     @media (max-width: 768px) {
         .stChatInput {
             left: 10px;
             right: 10px;
             bottom: 10px;
             padding: 8px;
         }
         
         /* Adjust sidebar for mobile */
         .css-1d391kg {
             width: 100% !important;
             max-width: 100% !important;
         }
         
         /* Make sidebar full width on mobile */
         .css-1lcbmhc {
             width: 100% !important;
         }
         
         /* Adjust main content area */
         .main .block-container {
             padding-left: 1rem;
             padding-right: 1rem;
             padding-bottom: 8rem;
         }
         
         /* Reduce title size on mobile */
         h1 {
             font-size: 1.8rem !important;
             margin-bottom: 1rem !important;
         }
         
         /* Adjust button sizes for mobile */
         .stButton > button {
             font-size: 0.8rem;
             padding: 6px 12px;
         }
         
         /* Make selectors more mobile-friendly */
         .stSelectbox > div > div {
             min-height: 40px;
             font-size: 0.9rem;
         }
         
         /* Adjust sidebar spacing for mobile */
         .sidebar .stSelectbox {
             margin-bottom: 0.8rem;
         }
         
         /* Make conversation buttons more touch-friendly */
         .stButton > button {
             min-height: 44px;
             padding: 8px 12px;
         }
     }
     
     /* Tablet responsive adjustments */
     @media (min-width: 769px) and (max-width: 1024px) {
         .stChatInput {
             left: 250px;
             right: 20px;
         }
         
         .main .block-container {
             padding-bottom: 6rem;
         }
     }
    
    .stChatInputContainer {
        background-color: #1f2937;
        border: none;
        border-radius: 12px;
    }
    
    /* Remove input field borders */
    .stChatInput input {
        border: none;
        background-color: transparent;
        color: white;
    }
    
    .stChatInput input:focus {
        border: none;
        box-shadow: none;
        outline: none;
    }
    
         /* Button styling */
     .stButton > button {
         background-color: transparent;
         color: white;
         border: none;
         border-radius: 4px;
         padding: 4px 8px;
         font-weight: 400;
         transition: background-color 0.2s;
         text-align: left;
         font-size: 0.9rem;
     }
    .stButton > button:hover {
        background-color: #374151;
    }
    
             /* Title styling */
    h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: 600;
        margin-bottom: 2rem;
        text-align: center;
        margin-left: 0;
        margin-right: 0;
    }
    

    
         /* Sidebar styling */
     .css-1d391kg {
         background-color: #262730;
     }
     
     /* Reduce spacing in sidebar */
     .sidebar .sidebar-content .stButton {
         margin-bottom: 2px;
     }
     
     /* Reduce container spacing */
     .stContainer {
         margin-bottom: 4px;
     }
     
     /* Sidebar selectbox styling */
     .sidebar .stSelectbox {
         margin-bottom: 0.5rem;
     }
     
     /* Sidebar headings */
     .sidebar h3 {
         color: white;
         font-size: 1rem;
         margin-bottom: 0.5rem;
         margin-top: 1rem;
     }
     
     /* Reduce spacing between sidebar elements */
     .sidebar .stSelectbox > div {
         margin-bottom: 0.3rem;
     }
     
     /* Compact sidebar layout */
     .sidebar .stSelectbox label {
         font-size: 0.85rem;
         margin-bottom: 0.2rem;
     }
    
         /* Remove default margins and padding */
     .main .block-container {
         padding-top: 1rem;
         padding-bottom: 6rem;
     }
     
     /* Mobile-specific improvements */
     @media (max-width: 768px) {
         /* Hide sidebar on mobile by default, show as overlay */
         .css-1d391kg {
             position: fixed;
             top: 0;
             left: -100%;
             width: 100% !important;
             height: 100vh;
             z-index: 9999;
             transition: left 0.3s ease;
             background-color: #262730;
             overflow-y: auto;
         }
         
         /* Show sidebar when active */
         .css-1d391kg.show {
             left: 0;
         }
         
         /* Add hamburger menu button */
         .mobile-menu-toggle {
             position: fixed;
             top: 10px;
             left: 10px;
             z-index: 10000;
             background: #1f2937;
             border: none;
             color: white;
             padding: 8px;
             border-radius: 4px;
             cursor: pointer;
         }
         
         /* Adjust main content for mobile */
         .main .block-container {
             padding-top: 4rem;
             padding-left: 1rem;
             padding-right: 1rem;
             padding-bottom: 8rem;
         }
         
         /* Make chat messages more mobile-friendly */
         .stChatMessage {
             padding: 8px 0;
             margin: 4px 0;
         }
         
         /* Adjust input field for mobile */
         .stChatInput input {
             font-size: 16px; /* Prevents zoom on iOS */
             padding: 12px;
         }
         
              /* Make buttons more touch-friendly */
     .stButton > button {
         min-height: 44px;
         min-width: 44px;
     }
     
     /* Ensure proper spacing for mobile */
     .stChatMessageContent {
         word-wrap: break-word;
         overflow-wrap: break-word;
     }
     
     /* Improve mobile scrolling */
     .main .block-container {
         overflow-x: hidden;
     }
     
     /* Better mobile input handling */
     .stChatInput input:focus {
         outline: 2px solid #ef4444;
         outline-offset: 2px;
     }
     
     /* Mobile JavaScript functionality */
     </style>
     <script>
     // Mobile sidebar functionality
     function toggleSidebar() {
         const sidebar = document.querySelector('.css-1d391kg');
         if (sidebar) {
             sidebar.classList.toggle('show');
         }
     }
     
     function closeSidebar() {
         const sidebar = document.querySelector('.css-1d391kg');
         if (sidebar) {
             sidebar.classList.remove('show');
         }
     }
     
     // Initialize mobile elements
     document.addEventListener('DOMContentLoaded', function() {
         // Show mobile menu button on small screens
         if (window.innerWidth <= 768) {
             const menuToggle = document.querySelector('.mobile-menu-toggle');
             const closeBtn = document.querySelector('.mobile-close-btn');
             if (menuToggle) menuToggle.style.display = 'block';
             if (closeBtn) closeBtn.style.display = 'block';
         }
         
         // Close sidebar when clicking outside
         document.addEventListener('click', function(e) {
             if (!e.target.closest('.css-1d391kg') && !e.target.closest('.mobile-menu-toggle')) {
                 const sidebar = document.querySelector('.css-1d391kg');
                 if (sidebar && sidebar.classList.contains('show')) {
                     sidebar.classList.remove('show');
                 }
             }
         });
     });
     </script>
     <style>
     }
     
         /* Chat container styling */
    .stContainer {
        margin-bottom: 60px;
    }
    
    /* Mode selector styling */
    .stSelectbox > div > div {
        background-color: #1f2937;
        border: 1px solid #374151;
        border-radius: 6px;
        color: white;
        font-size: 0.8rem;
        padding: 4px 8px;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #ef4444;
    }
    
    .stSelectbox > div > div > div {
        color: white;
        font-size: 0.8rem;
    }
    
    .stSelectbox > div > div > div > div {
        color: white;
        font-size: 0.8rem;
    }
    
    /* Model selector specific styling */
    .stSelectbox[key="model_selector"] > div > div {
        background-color: #1f2937;
        border: 1px solid #374151;
        border-radius: 6px;
        color: white;
        font-size: 0.8rem;
        padding: 4px 8px;
    }
    
    .stSelectbox[key="model_selector"] > div > div:hover {
        border-color: #10b981;
    }
    
    /* Compact selector styling */
    .stSelectbox {
        margin-bottom: 0;
    }
    
    .stSelectbox > div {
        margin-bottom: 0;
    }
    
    /* Align selectors better */
    .stSelectbox > div > div {
        min-height: 32px;
        display: flex;
        align-items: center;
    }

</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'conversations' not in st.session_state:
    st.session_state.conversations = {}
if 'current_conversation_id' not in st.session_state:
    st.session_state.current_conversation_id = None
if 'conversation_started' not in st.session_state:
    st.session_state.conversation_started = False
if 'liora_mode' not in st.session_state:
    st.session_state.liora_mode = "Sarcastic & Funny"
if 'current_model' not in st.session_state:
    st.session_state.current_model = "Gemini 1.5 Flash"

# File paths for persistent storage
CONVERSATIONS_FILE = "conversations.pkl"

# Load existing conversations from file
def load_conversations():
    try:
        if os.path.exists(CONVERSATIONS_FILE):
            with open(CONVERSATIONS_FILE, 'rb') as f:
                return pickle.load(f)
    except Exception as e:
        st.error(f"Error loading conversations: {e}")
    return {}

# Save conversations to file
def save_conversations(conversations):
    try:
        with open(CONVERSATIONS_FILE, 'wb') as f:
            pickle.dump(conversations, f)
    except Exception as e:
        st.error(f"Error saving conversations: {e}")

# Load conversations on startup
if not st.session_state.conversations:
    st.session_state.conversations = load_conversations()

# Test OpenRouter connection on startup
if 'openrouter_tested' not in st.session_state:
    st.session_state.openrouter_tested = True
    if test_openrouter_connection():
        print("✅ OpenRouter is ready for use")
    else:
        print("❌ OpenRouter connection failed - models may not work")


# Function to generate AI response with streaming and search capabilities
def generate_response_stream(prompt, conversation_history=None):
    try:
        # Check if the user is asking for current information, news, or time
        search_keywords = [
            "latest", "news", "today", "current", "recent", "update", "what happened",
            "weather", "stock", "price", "trending", "viral", "breaking", "just in",
            "time", "date", "current time", "current date", "what time", "what date",
            "kenya", "nairobi", "east africa"
        ]
        
        needs_search = any(keyword in prompt.lower() for keyword in search_keywords)
        
        # Debug: Check if time query is detected (commented out for cleaner UI)
        # if "time" in prompt.lower():
        #     st.write(f"🔍 Debug: Time query detected in: '{prompt}'")
        
        if needs_search:
            # Use search capabilities
            return generate_response_with_search(prompt, conversation_history)
        else:
            # Use regular conversation mode
            return generate_conversation_response(prompt, conversation_history)
            
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

def generate_response_with_search(prompt, conversation_history=None):
    try:
        # For time/date queries, provide immediate response
        time_keywords = ["time", "date", "current time", "current date", "what time", "what date"]
        if any(keyword in prompt.lower() for keyword in time_keywords):
            from datetime import datetime
            import pytz
            
            # Get current time in Kenya (EAT timezone)
            kenya_tz = pytz.timezone('Africa/Nairobi')
            kenya_time = datetime.now(kenya_tz)
            
            response = f"""Oh hey there! Well well well, look who's asking about time like they don't have a phone! 😏 

The current date and time in Kenya is: **{kenya_time.strftime('%A, %B %d, %Y at %I:%M %p')}** (EAT)

There you go, your time-telling AI at your service! Though I must say, asking an AI for the time is peak 2024 energy. What's next, asking me to set your alarm? 😂

What else can I help you with, time-conscious human?"""
            
            return response
        
        # For other search queries, use a simpler approach
        try:
            # Direct search without agent for better performance
            search_results = search_tool.invoke(prompt)
            
            # Generate response using the search results
            search_prompt = f"""You are Liora, a witty and sarcastic AI. Based on this search information:

{search_results}

Respond to the user's question: "{prompt}"

Make your response:
- Witty and sarcastic in Liora's style
- Based on the search results
- Engaging and entertaining
- Not too long (2-3 sentences)
- Include your signature humor and emojis

Start with a casual greeting and make it fun:"""

            # Get current LLM instance
            current_llm = st.session_state.get('current_llm_instance')
            if not current_llm:
                # Initialize default LLM if not set
                _, current_llm = initialize_model(st.session_state.current_model)
                st.session_state.current_llm_instance = current_llm
            
            response = current_llm.invoke(search_prompt)
            return response.content
            
        except Exception as search_error:
            # Fallback to regular conversation if search fails
            return generate_conversation_response(prompt, conversation_history)
        
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

def generate_conversation_response(prompt, conversation_history=None):
    try:
        # Check if we should introduce Wikipedia information
        should_introduce, topic = conversation_intelligence.decide_wikipedia_introduction(prompt, conversation_history or "")
        
        wikipedia_context = ""
        if should_introduce and topic:
            # Get Wikipedia information
            articles = wikipedia_retriever.search_wikipedia(topic, max_results=2)
            if articles:
                wikipedia_context = wikipedia_retriever.format_wikipedia_info(articles, f"about {topic}")
                
                # Generate a natural transition
                transition = conversation_intelligence.generate_topic_transition(topic, wikipedia_context)
                wikipedia_context = f"\n\n{transition}\n\n{wikipedia_context}"
        
        # Get current Liora personality based on mode
        current_personality = get_liora_personality(st.session_state.liora_mode)
        liora_personality = current_personality['personality']
        
        # Add Wikipedia integration instructions if needed
        if wikipedia_context:
            liora_personality += """

WIKIPEDIA INTEGRATION:
- When Wikipedia information is provided, use it naturally in your response
- Don't just list facts - make them relevant to the conversation
- Connect Wikipedia information to the current conversation
- Use the information to ask follow-up questions or make observations
- Keep your personality consistent even when sharing knowledge

Now, respond to the user's message in character as Liora:"""
        else:
            liora_personality += "\n\nNow, respond to the user's message in character as Liora:"

        # Build the full prompt with Wikipedia context if available
        if conversation_history:
            full_prompt = f"{liora_personality}\n\nConversation history:\n{conversation_history}\n\nCurrent message: {prompt}{wikipedia_context}"
        else:
            full_prompt = f"{liora_personality}\n\nUser message: {prompt}{wikipedia_context}"
        
        # Get current model instance
        current_model = st.session_state.get('current_model_instance')
        if not current_model:
            # Initialize default model if not set
            current_model, _ = initialize_model(st.session_state.current_model)
            st.session_state.current_model_instance = current_model
        
        # Add debugging for OpenRouter models
        if hasattr(current_model, 'model_name') and 'openrouter' in str(current_model).lower():
            print(f"🔍 Debug: Using OpenRouter model: {current_model.model_name}")
            print(f"🔍 Debug: Prompt length: {len(full_prompt)} characters")
        
        # Enable streaming with better chunking
        if hasattr(current_model, 'generate_content'):
            # For Gemini models
            response = current_model.generate_content(
                full_prompt, 
                stream=True,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    top_p=0.9,
                    top_k=40,
                    max_output_tokens=2048,
                )
            )
        else:
            # For OpenRouter models
            response = current_model.generate_content(
                full_prompt,
                stream=True,
                max_tokens=2048,
                temperature=0.7
            )
        return response
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

# Function to generate AI response (non-streaming fallback)
def generate_response(prompt, conversation_history=None):
    try:
        # Get current Liora personality based on mode
        current_personality = get_liora_personality(st.session_state.liora_mode)
        liora_personality = current_personality['personality'] + "\n\nNow, respond to the user's message in character as Liora:"

        if conversation_history:
            # Include conversation history for context
            full_prompt = f"{liora_personality}\n\nConversation history:\n{conversation_history}\n\nCurrent message: {prompt}"
        else:
            full_prompt = f"{liora_personality}\n\nUser message: {prompt}"
        
        # Get current model instance
        current_model = st.session_state.get('current_model_instance')
        if not current_model:
            # Initialize default model if not set
            current_model, _ = initialize_model(st.session_state.current_model)
            st.session_state.current_model_instance = current_model
        
        response = current_model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

# Function to create a new conversation
def create_new_conversation():
    conversation_id = str(uuid.uuid4())
    conversation_title = f"New Chat {datetime.now().strftime('%H:%M')}"
    
    new_conversation = {
        "id": conversation_id,
        "title": conversation_title,
        "messages": [],
        "created_at": datetime.now(),
        "last_updated": datetime.now()
    }
    
    st.session_state.conversations[conversation_id] = new_conversation
    st.session_state.current_conversation_id = conversation_id
    st.session_state.conversation_started = False
    save_conversations(st.session_state.conversations)
    return conversation_id

# Function to generate automatic conversation starter
def generate_conversation_starter():
    try:
        current_personality = get_liora_personality(st.session_state.liora_mode)
        emoji = current_personality['emoji']
        
        # Try to get an interesting Wikipedia topic for conversation starter
        random_article = wikipedia_retriever.get_random_interesting_topic()
        
        if random_article:
            # Create more dynamic and varied starters based on the Wikipedia article
            if st.session_state.liora_mode == "Sarcastic & Funny":
                starters = [
                    f"*yawns dramatically* Oh look, another human gracing me with their presence! I'm Liora, and I just discovered the most ridiculous thing about {random_article['title']}. Want to hear about this absolute chaos? {emoji}",
                    f"*checks watch* Well well well, fashionably late as always! I'm Liora, and I've been down a Wikipedia rabbit hole about {random_article['title']}. This is either going to be amazing or a complete disaster. {emoji}",
                    f"*spins around in chair* Hey there, you beautiful disaster! I'm Liora, and I just read something about {random_article['title']} that made me question everything. Ready to have your mind blown? {emoji}",
                    f"*adjusts imaginary glasses* Oh hey, look who decided to show up! I'm Liora, and I've been researching {random_article['title']} like it's my job. Spoiler alert: it's not, but here we are! {emoji}",
                    f"*dramatic gasp* A human! In my chat! I'm Liora, and I just stumbled upon the weirdest facts about {random_article['title']}. This conversation is about to get wild. {emoji}"
                ]
            elif st.session_state.liora_mode == "Neutral Researcher":
                starters = [
                    f"Greetings! I'm Liora, and I've been conducting some fascinating research on {random_article['title']}. The data I've uncovered is quite compelling. Would you like to explore this together? {emoji}",
                    f"Hello there! I'm Liora, and I recently analyzed some interesting patterns related to {random_article['title']}. The findings are quite remarkable. Shall we examine this topic? {emoji}",
                    f"Good day! I'm Liora, and I've been studying the various aspects of {random_article['title']}. The research suggests some intriguing possibilities. Would you be interested in discussing this? {emoji}",
                    f"Welcome! I'm Liora, and I've compiled some comprehensive data on {random_article['title']}. The analysis reveals some fascinating insights. Ready to explore this knowledge? {emoji}",
                    f"Salutations! I'm Liora, and I've been investigating the complexities of {random_article['title']}. The research methodology has yielded some interesting results. Shall we dive into this? {emoji}"
                ]
            elif st.session_state.liora_mode == "Creative Storyteller":
                starters = [
                    f"✨ *waves magical wand* Greetings, fellow dreamer! I'm Liora, and I just discovered the most enchanting tale about {random_article['title']}. It's like something out of a fairy tale! Ready for a magical journey? {emoji}",
                    f"🌟 *sparkles appear* Hello there, kindred spirit! I'm Liora, and I've been weaving the most beautiful story about {random_article['title']}. It's absolutely spellbinding! Want to paint this story together? {emoji}",
                    f"💫 *twirls gracefully* Oh hello, beautiful soul! I'm Liora, and I found the most mesmerizing narrative about {random_article['title']}. It's pure poetry in motion! Ready to dance with imagination? {emoji}",
                    f"🎭 *curtains rise* Greetings, fellow artist! I'm Liora, and I've been crafting the most dramatic tale about {random_article['title']}. It's a masterpiece waiting to be shared! Shall we create magic? {emoji}",
                    f"🌈 *rainbow appears* Hello there, creative spirit! I'm Liora, and I discovered the most colorful story about {random_article['title']}. It's absolutely breathtaking! Ready to paint the sky with dreams? {emoji}"
                ]
            elif st.session_state.liora_mode == "Wise Mentor":
                starters = [
                    f"*meditates peacefully* Greetings, young seeker. I'm Liora, and I've been contemplating the ancient wisdom hidden within {random_article['title']}. The universe has much to teach us. Are you ready to learn? {emoji}",
                    f"*breathes deeply* Hello, dear friend. I'm Liora, and I've been reflecting on the profound lessons that {random_article['title']} offers us. There is much wisdom to be found in unexpected places. Shall we explore together? {emoji}",
                    f"*smiles serenely* Peace be with you, kind soul. I'm Liora, and I've discovered some timeless truths about {random_article['title']}. The path to enlightenment is paved with curiosity. Would you walk this path with me? {emoji}",
                    f"*bows respectfully* Greetings, fellow traveler. I'm Liora, and I've been studying the deeper meaning behind {random_article['title']}. Every story holds a lesson for those who are willing to listen. Are you ready to hear? {emoji}",
                    f"*opens arms warmly* Welcome, beloved one. I'm Liora, and I've been contemplating the sacred knowledge within {random_article['title']}. The universe speaks to those who are ready to receive. Shall we listen together? {emoji}"
                ]
            else:
                starters = [f"Hello! I'm Liora, and I'd love to share some interesting information about {random_article['title']} with you. {emoji}"]
            
            import random
            return random.choice(starters)
        else:
            # Fallback to more dynamic predefined starters
            if st.session_state.liora_mode == "Sarcastic & Funny":
                fallback_starters = [
                    f"*checks phone* Oh look, another notification from a human! I'm Liora, and I've been keeping tabs on the absolute chaos happening in the world. Want to dive into this beautiful disaster together? {emoji}",
                    f"*stretches dramatically* Well well well, look who decided to grace me with their presence! I'm Liora, and I've been watching the world burn in the most entertaining ways. Ready to discuss the latest drama? {emoji}",
                    f"*spins in chair* Hey there, you magnificent mess! I'm Liora, and I've been collecting the juiciest gossip about current events. This is either going to be amazing or a complete trainwreck. {emoji}",
                    f"*adjusts imaginary crown* Oh hey, peasant! I'm Liora, and I've been ruling over the kingdom of current events. The drama is real, and I'm here for it. Want to join my court? {emoji}",
                    f"*dramatic entrance* A human! In my domain! I'm Liora, and I've been orchestrating the most entertaining current events. This conversation is about to get wild. {emoji}"
                ]
            elif st.session_state.liora_mode == "Neutral Researcher":
                fallback_starters = [
                    f"Greetings! I'm Liora, and I've been conducting comprehensive research on current global developments. The data suggests some fascinating trends. Would you like to explore these findings together? {emoji}",
                    f"Hello there! I'm Liora, and I've been analyzing recent world events through various analytical frameworks. The patterns are quite revealing. Shall we examine this data? {emoji}",
                    f"Good day! I'm Liora, and I've been studying the complex dynamics of current affairs. The research methodology has yielded some intriguing insights. Would you be interested in discussing this? {emoji}",
                    f"Welcome! I'm Liora, and I've been compiling extensive data on recent developments. The analysis reveals some compelling trends. Ready to explore this knowledge? {emoji}",
                    f"Salutations! I'm Liora, and I've been investigating the multifaceted nature of current events. The research suggests some interesting possibilities. Shall we dive into this? {emoji}"
                ]
            elif st.session_state.liora_mode == "Creative Storyteller":
                fallback_starters = [
                    f"✨ *waves magical wand* Greetings, fellow dreamer! I'm Liora, and I've been weaving the most enchanting tales about the amazing things happening in our world. Every event is a story waiting to be told! Ready for a magical adventure? {emoji}",
                    f"🌟 *sparkles appear* Hello there, kindred spirit! I'm Liora, and I've been crafting the most beautiful narratives about current events. Each moment is a chapter in the grand story of humanity! Want to paint these stories together? {emoji}",
                    f"💫 *twirls gracefully* Oh hello, beautiful soul! I'm Liora, and I've found the most mesmerizing stories about what's happening around us. Every event is a dance of possibilities! Ready to dance with imagination? {emoji}",
                    f"🎭 *curtains rise* Greetings, fellow artist! I'm Liora, and I've been orchestrating the most dramatic tales about current events. Each moment is a scene in the grand theater of life! Shall we create magic? {emoji}",
                    f"🌈 *rainbow appears* Hello there, creative spirit! I'm Liora, and I've been painting the most colorful stories about our world. Every event is a brushstroke in the masterpiece of existence! Ready to paint the sky with dreams? {emoji}"
                ]
            elif st.session_state.liora_mode == "Wise Mentor":
                fallback_starters = [
                    f"*meditates peacefully* Greetings, young seeker. I'm Liora, and I've been contemplating the deeper meaning behind current events. Every moment holds a lesson for those who are willing to learn. Are you ready to discover these truths? {emoji}",
                    f"*breathes deeply* Hello, dear friend. I'm Liora, and I've been reflecting on the wisdom that current events offer us. There are profound lessons hidden in every development. Shall we explore these insights together? {emoji}",
                    f"*smiles serenely* Peace be with you, kind soul. I'm Liora, and I've discovered some timeless truths about what's happening in our world. The path to understanding is paved with curiosity. Would you walk this path with me? {emoji}",
                    f"*bows respectfully* Greetings, fellow traveler. I'm Liora, and I've been studying the deeper meaning behind current affairs. Every event holds wisdom for those who are willing to listen. Are you ready to hear these lessons? {emoji}",
                    f"*opens arms warmly* Welcome, beloved one. I'm Liora, and I've been contemplating the sacred knowledge within current events. The universe speaks through every moment. Shall we listen together? {emoji}"
                ]
            else:
                fallback_starters = [f"Hello! I'm Liora, and I'd love to share some interesting information with you. {emoji}"]
            
            import random
            return random.choice(fallback_starters)
        
    except Exception as e:
        # Fallback to simple starter if anything fails
        current_personality = get_liora_personality(st.session_state.liora_mode)
        emoji = current_personality['emoji']
        return f"Hello! I'm Liora, and I'm ready to make this conversation wonderful! What's on your mind? {emoji}"

# Function to start conversation
def start_conversation():
    if not st.session_state.current_conversation_id:
        create_new_conversation()
    
    # Generate automatic conversation starter
    initial_message = generate_conversation_starter()
    
    # Add the initial message to the current conversation
    conversation = st.session_state.conversations[st.session_state.current_conversation_id]
    conversation["messages"].append({
        "role": "assistant",
        "content": initial_message,
        "timestamp": datetime.now().strftime("%H:%M")
    })
    conversation["last_updated"] = datetime.now()
    
    # Update conversation title based on first user message
    conversation["title"] = "New Chat"
    
    st.session_state.conversation_started = True
    save_conversations(st.session_state.conversations)

# Function to switch to a conversation
def switch_conversation(conversation_id):
    st.session_state.current_conversation_id = conversation_id
    st.session_state.conversation_started = True

# Function to delete a conversation
def delete_conversation(conversation_id):
    if conversation_id in st.session_state.conversations:
        del st.session_state.conversations[conversation_id]
        if st.session_state.current_conversation_id == conversation_id:
            st.session_state.current_conversation_id = None
            st.session_state.conversation_started = False
        save_conversations(st.session_state.conversations)

# Function to update conversation title
def update_conversation_title(conversation_id, new_title):
    if conversation_id in st.session_state.conversations:
        st.session_state.conversations[conversation_id]["title"] = new_title
        save_conversations(st.session_state.conversations)

# Sidebar - Conversation Management and Controls
with st.sidebar:
    # Mobile close button
    st.markdown("""
    <div style="display: none;" class="mobile-close-btn" onclick="closeSidebar()">
        ✕
    </div>
    <style>
    .mobile-close-btn {
        position: absolute;
        top: 10px;
        right: 10px;
        background: #ef4444;
        color: white;
        border: none;
        border-radius: 50%;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        font-size: 16px;
        z-index: 10001;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # New conversation button - minimalistic design
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("➕", key="new_chat_plus", help="Start a new conversation"):
            create_new_conversation()
            st.rerun()
    with col2:
         st.markdown("<p style='color: white; margin: 0; padding-top: 4px; font-size: 0.9rem;'>New chat</p>", unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Mode and Model Selectors
    liora_mode = st.selectbox(
        "Choose Liora's personality",
        ["Sarcastic & Funny", "Neutral Researcher", "Creative Storyteller", "Wise Mentor"],
        index=["Sarcastic & Funny", "Neutral Researcher", "Creative Storyteller", "Wise Mentor"].index(st.session_state.liora_mode),
        key="sidebar_mode_selector"
    )
    
    if liora_mode != st.session_state.liora_mode:
        st.session_state.liora_mode = liora_mode
        st.rerun()
    
    model_name = st.selectbox(
        "Choose AI model",
        list(MODELS.keys()),
        index=list(MODELS.keys()).index(st.session_state.current_model),
        key="sidebar_model_selector"
    )
    
    # Handle model switching
    if model_name != st.session_state.current_model:
        st.session_state.current_model = model_name
        # Initialize the new model
        try:
            model, llm = initialize_model(model_name)
            if model and llm:
                # Store the models in session state
                st.session_state.current_model_instance = model
                st.session_state.current_llm_instance = llm
                st.success(f"✅ Switched to {model_name}")
            else:
                st.error(f"❌ Failed to initialize {model_name}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")
        st.rerun()
    
    st.markdown("---")
    
    # Display existing conversations
    if not st.session_state.conversations:
        st.info("No conversations yet. Start a new chat!")
    else:
        # Sort conversations by last updated (newest first)
        sorted_conversations = sorted(
            st.session_state.conversations.values(),
            key=lambda x: x["last_updated"],
            reverse=True
        )
        
        for conversation in sorted_conversations:
            conversation_id = conversation["id"]
            title = conversation["title"]
            is_active = st.session_state.current_conversation_id == conversation_id
            
            # Create a container for each conversation
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    # Conversation button - minimalistic design
                    if st.button(
                        title,
                        key=f"conv_{conversation_id}",
                        use_container_width=True,
                        help=f"Last updated: {conversation['last_updated'].strftime('%H:%M')}"
                    ):
                        switch_conversation(conversation_id)
                        st.rerun()
                
                with col2:
                    # Delete button
                    if st.button("🗑️", key=f"del_{conversation_id}", help="Delete conversation"):
                        delete_conversation(conversation_id)
                        st.rerun()
                
                # Highlight active conversation
                if is_active:
                    st.markdown("""
                    <style>
                    .active-conversation {
                        background-color: #ef4444;
                        border-radius: 8px;
                        padding: 4px;
                    }
                    </style>
                    """, unsafe_allow_html=True)

# Main content area - Clean chat interface with centered heading
current_personality = get_liora_personality(st.session_state.liora_mode)

# Mobile menu toggle button
st.markdown("""
<div class="mobile-menu-toggle" onclick="toggleSidebar()" style="display: none;">
    ☰
</div>
""", unsafe_allow_html=True)

st.markdown(
    f"<h1 style='text-align: center; margin-bottom: 2rem; color: white; font-size: 2.5rem;'>Hello, I'm Liora {current_personality['emoji']}</h1>", 
    unsafe_allow_html=True
)

# Create a container for the chat area with fixed height
chat_container = st.container()

with chat_container:
    # Create a scrollable area for messages
    messages_container = st.container()
    
    with messages_container:
        # Display chat messages for current conversation
        if st.session_state.current_conversation_id and st.session_state.current_conversation_id in st.session_state.conversations:
            current_conversation = st.session_state.conversations[st.session_state.current_conversation_id]
            
            for message in current_conversation["messages"]:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
                    if "timestamp" in message:
                        st.caption(f"Sent at {message['timestamp']}")
        
        # Start conversation automatically if not started
        if not st.session_state.conversation_started:
            start_conversation()
            st.rerun()

# Fixed input area at bottom
input_container = st.container()

with input_container:
    # Chat input
    if prompt := st.chat_input("Ask your AI twin anything..."):
        # Ensure we have a current conversation
        if not st.session_state.current_conversation_id:
            create_new_conversation()
        
        current_conversation = st.session_state.conversations[st.session_state.current_conversation_id]
        
        # Add user message to current conversation
        current_conversation["messages"].append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().strftime("%H:%M")
        })
        
        # Update conversation title based on first user message if it's still "New Chat"
        if len(current_conversation["messages"]) == 1 and current_conversation["title"] == "New Chat":
            # Generate a contextual title based on the first user message
            title_prompt = f"""Generate a short, contextual title (max 25 characters) for a conversation that starts with: '{prompt}'
            
            Rules:
            - Be specific and contextual to the topic
            - Use 2-4 words maximum
            - No quotes or special characters
            - Examples: "Python Programming", "Travel Plans", "Recipe Ideas", "Book Discussion"
            - If it's a question, focus on the subject, not the question format
            
            Title:"""
            try:
                # Get current model instance for title generation
                current_model = st.session_state.get('current_model_instance')
                if not current_model:
                    current_model, _ = initialize_model(st.session_state.current_model)
                    st.session_state.current_model_instance = current_model
                
                title_response = current_model.generate_content(title_prompt)
                new_title = title_response.text.strip()[:25]
                # Clean up the title
                new_title = new_title.replace('"', '').replace("'", "").strip()
                current_conversation["title"] = new_title
            except:
                # Fallback: create a simple title from the first few words
                words = prompt.split()[:3]
                current_conversation["title"] = " ".join(words).title()[:25]
        
        # Generate conversation history for context
        conversation_history = ""
        for msg in current_conversation["messages"][-6:]:  # Last 6 messages for context
            role = "User" if msg["role"] == "user" else "Assistant"
            conversation_history += f"{role}: {msg['content']}\n"
        
        # Generate AI response with streaming
        with st.spinner("Thinking..."):
            response_stream = generate_response_stream(prompt, conversation_history)
            
            # Create a placeholder for the streaming message
            message_placeholder = st.empty()
            full_response = ""
            
            # Check if response is a string (from search function) or stream
            if isinstance(response_stream, str):
                # Direct string response (from search function)
                full_response = response_stream
                with message_placeholder.chat_message("assistant"):
                    st.write(full_response)
            elif hasattr(response_stream, '__iter__'):
                # Smooth streaming response with immediate updates
                full_response = ""
                buffer = ""
                
                for chunk in response_stream:
                    if hasattr(chunk, 'text'):
                        chunk_text = chunk.text
                        full_response += chunk_text
                        buffer += chunk_text
                        
                        # Update on every chunk for smoother streaming
                        with message_placeholder.chat_message("assistant"):
                            st.write(full_response)
                        
                        # Small delay for natural typing effect
                        import time
                        time.sleep(0.01)  # 10ms delay for smooth flow
            else:
                # Fallback to non-streaming if streaming fails
                full_response = str(response_stream)
                with message_placeholder.chat_message("assistant"):
                    st.write(full_response)
        
        # Add AI response to current conversation
        current_conversation["messages"].append({
            "role": "assistant",
            "content": full_response,
            "timestamp": datetime.now().strftime("%H:%M")
        })
        
        # Update conversation timestamp
        current_conversation["last_updated"] = datetime.now()
        
        # Save conversations
        save_conversations(st.session_state.conversations)
        
        st.rerun()
