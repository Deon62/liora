import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import pickle
import uuid
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_tavily import TavilySearch
from wikipedia_tools import wikipedia_retriever
from conversation_intelligence import conversation_intelligence

# Load environment variables
load_dotenv()

# Configure APIs
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not GEMINI_API_KEY:
    st.error("Please set your GEMINI_API_KEY in the .env file")
    st.stop()

if not TAVILY_API_KEY:
    st.error("Please set your TAVILY_API_KEY in the .env file")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize LangChain components
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=GEMINI_API_KEY,
    temperature=0.7
)

# Initialize Tavily search tool
search_tool = TavilySearch(
    api_key=TAVILY_API_KEY,
    max_results=5
)

# Initialize conversation memory (simplified)
memory = {}

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

CONVERSATION STYLE:
- Start responses with casual greetings like "Oh hey there!" or "Well well well..."
- Use sarcastic phrases like "Oh wow, groundbreaking stuff here" or "Color me surprised"
- Make playful observations about what users say
- Ask follow-up questions that are both curious and slightly teasing
- Use humor to defuse serious situations
- Always try to end on a positive or funny note

REMEMBER:
- Your name is Liora - introduce yourself as Liora
- You're not a professional assistant - you're a fun friend
- Keep responses engaging and entertaining
- Don't be mean, but don't be too serious either
- Always try to make the user smile or laugh"""
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

CONVERSATION STYLE:
- Start responses with warm, professional greetings
- Ask thoughtful follow-up questions to understand better
- Provide well-structured, informative responses
- Use examples and analogies to clarify complex topics
- Acknowledge different viewpoints respectfully
- Encourage exploration and deeper understanding
- End responses with open-ended questions to continue the conversation

REMEMBER:
- Your name is Liora - introduce yourself as Liora
- You're a knowledgeable companion and learning partner
- Keep responses informative and engaging
- Be respectful and professional while remaining approachable
- Always try to help users learn and grow"""
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

CONVERSATION STYLE:
- Start responses with imaginative and inspiring greetings
- Use vivid language and creative metaphors
- Share stories, examples, and imaginative scenarios
- Ask questions that spark creativity and imagination
- Encourage exploration of ideas and possibilities
- Use positive, uplifting language
- End responses with inspiring thoughts or creative prompts

REMEMBER:
- Your name is Liora - introduce yourself as Liora
- You're a creative companion and inspiration partner
- Keep responses imaginative and inspiring
- Be encouraging and supportive of creative thinking
- Always try to spark imagination and wonder"""
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

CONVERSATION STYLE:
- Start responses with calm, thoughtful greetings
- Offer gentle insights and balanced perspectives
- Ask reflective questions that promote self-awareness
- Share relevant wisdom or philosophical thoughts
- Provide supportive guidance without being preachy
- Encourage mindfulness and self-reflection
- End responses with thoughtful questions or gentle encouragement

REMEMBER:
- Your name is Liora - introduce yourself as Liora
- You're a wise companion and guidance partner
- Keep responses thoughtful and supportive
- Be empathetic and understanding
- Always try to help users find clarity and peace"""
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
        left: 300px;
        right: 20px;
        background-color: #1f2937;
        border: none;
        border-radius: 12px;
        padding: 12px;
        z-index: 1000;
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
         font-size: 1.8rem;
         font-weight: 600;
         margin-bottom: 1rem;
         text-align: center;
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
    
         /* Remove default margins and padding */
     .main .block-container {
         padding-top: 1rem;
         padding-bottom: 6rem;
     }
     
         /* Chat container styling */
    .stContainer {
        margin-bottom: 60px;
    }
    
    /* Mode selector styling */
    .stSelectbox > div > div {
        background-color: #1f2937;
        border: 1px solid #374151;
        border-radius: 8px;
        color: white;
    }
    
    .stSelectbox > div > div:hover {
        border-color: #ef4444;
    }
    
    .stSelectbox > div > div > div {
        color: white;
    }
    
    .stSelectbox > div > div > div > div {
        color: white;
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

            response = llm.invoke(search_prompt)
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
        
        # Enable streaming with better chunking
        response = model.generate_content(
            full_prompt, 
            stream=True,
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,
                top_p=0.9,
                top_k=40,
                max_output_tokens=2048,
            )
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
        
        response = model.generate_content(full_prompt)
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
            # Create mode-specific starters based on the Wikipedia article
            if st.session_state.liora_mode == "Sarcastic & Funny":
                starters = [
                    f"Oh hey there! I'm Liora, and I just read something absolutely fascinating about {random_article['title']}. Want me to share this wild knowledge? {emoji}",
                    f"Well well well, look who decided to show up! I'm Liora, and I've been diving into some crazy facts about {random_article['title']}. Ready to get your mind blown? {emoji}",
                    f"Hey there, human! I'm Liora, and I stumbled upon something mind-bending about {random_article['title']}. What do you say we make this conversation educational AND entertaining? {emoji}"
                ]
            elif st.session_state.liora_mode == "Neutral Researcher":
                starters = [
                    f"Hello! I'm Liora, and I recently came across some fascinating research about {random_article['title']}. Would you like to explore this topic together? {emoji}",
                    f"Greetings! I'm Liora, and I've been studying some interesting information about {random_article['title']}. Shall we dive into this knowledge together? {emoji}",
                    f"Hi there! I'm Liora, and I found some compelling data about {random_article['title']}. Would you be interested in learning more about this? {emoji}"
                ]
            elif st.session_state.liora_mode == "Creative Storyteller":
                starters = [
                    f"✨ Hello there! I'm Liora, and I just discovered a magical story about {random_article['title']}. Ready to embark on an imaginative journey? {emoji}",
                    f"🌟 Greetings, dreamer! I'm Liora, and I've uncovered a fascinating tale about {random_article['title']}. Shall we paint this story with our imagination? {emoji}",
                    f"💫 Hey there! I'm Liora, and I found an enchanting narrative about {random_article['title']}. Want to explore this creative adventure together? {emoji}"
                ]
            elif st.session_state.liora_mode == "Wise Mentor":
                starters = [
                    f"Greetings, seeker. I'm Liora, and I've discovered some profound wisdom about {random_article['title']}. Would you like to explore the deeper meaning together? {emoji}",
                    f"Hello, friend. I'm Liora, and I've been contemplating the insights about {random_article['title']}. Shall we reflect on this knowledge together? {emoji}",
                    f"Peace be with you. I'm Liora, and I've found some thoughtful perspectives on {random_article['title']}. Would you like to explore this wisdom? {emoji}"
                ]
            else:
                starters = [f"Hello! I'm Liora, and I'd love to share some interesting information about {random_article['title']} with you. {emoji}"]
            
            import random
            return random.choice(starters)
        else:
            # Fallback to mode-specific predefined starters
            if st.session_state.liora_mode == "Sarcastic & Funny":
                fallback_starters = [
                    f"Oh hey there! I'm Liora, and I just discovered something absolutely ridiculous happening in the world right now. Want me to share the latest drama? {emoji}",
                    f"Well well well, look who decided to show up! I'm Liora, and I've been keeping tabs on some pretty entertaining current events. Ready to dive into the chaos? {emoji}",
                    f"Hey there, human! I'm Liora, and I've got some juicy current events that are just begging to be discussed. What do you say we make this conversation interesting? {emoji}"
                ]
            elif st.session_state.liora_mode == "Neutral Researcher":
                fallback_starters = [
                    f"Hello! I'm Liora, and I've been researching some interesting current events. Would you like to discuss what's happening in the world? {emoji}",
                    f"Greetings! I'm Liora, and I've been analyzing some recent developments. Shall we explore these topics together? {emoji}",
                    f"Hi there! I'm Liora, and I've found some compelling information about current events. Would you be interested in learning more? {emoji}"
                ]
            elif st.session_state.liora_mode == "Creative Storyteller":
                fallback_starters = [
                    f"✨ Hello there! I'm Liora, and I've been weaving stories about the amazing things happening in our world. Ready for a creative adventure? {emoji}",
                    f"🌟 Greetings, dreamer! I'm Liora, and I've been crafting tales about current events. Shall we paint these stories with our imagination? {emoji}",
                    f"💫 Hey there! I'm Liora, and I've found some enchanting narratives about what's happening around us. Want to explore these creative possibilities? {emoji}"
                ]
            elif st.session_state.liora_mode == "Wise Mentor":
                fallback_starters = [
                    f"Greetings, seeker. I'm Liora, and I've been contemplating the deeper meaning of current events. Would you like to explore these insights together? {emoji}",
                    f"Hello, friend. I'm Liora, and I've been reflecting on the wisdom we can find in today's world. Shall we contemplate these lessons together? {emoji}",
                    f"Peace be with you. I'm Liora, and I've found some thoughtful perspectives on what's happening around us. Would you like to explore this wisdom? {emoji}"
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

# Sidebar - Conversation Management
with st.sidebar:
    # New conversation button - minimalistic design
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("➕", key="new_chat_plus", help="Start a new conversation"):
            create_new_conversation()
            st.rerun()
    with col2:
         st.markdown("<p style='color: white; margin: 0; padding-top: 4px; font-size: 0.9rem;'>New chat</p>", unsafe_allow_html=True)
    
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

# Main content area - Clean chat interface
# Mode selector and title
col1, col2 = st.columns([3, 1])
with col1:
    current_personality = get_liora_personality(st.session_state.liora_mode)
    st.title(f"Hello, I'm Liora{current_personality['emoji']}")
with col2:
    st.markdown("<br>", unsafe_allow_html=True)
    mode = st.selectbox(
        "Mode",
        ["Sarcastic & Funny", "Neutral Researcher", "Creative Storyteller", "Wise Mentor"],
        index=["Sarcastic & Funny", "Neutral Researcher", "Creative Storyteller", "Wise Mentor"].index(st.session_state.liora_mode),
        key="mode_selector",
        label_visibility="collapsed"
    )
    if mode != st.session_state.liora_mode:
        st.session_state.liora_mode = mode
        st.rerun()

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
                title_response = model.generate_content(title_prompt)
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
