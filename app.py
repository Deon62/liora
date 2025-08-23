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

</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'conversations' not in st.session_state:
    st.session_state.conversations = {}
if 'current_conversation_id' not in st.session_state:
    st.session_state.current_conversation_id = None
if 'conversation_started' not in st.session_state:
    st.session_state.conversation_started = False

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
        
        # Liora's enhanced personality with Wikipedia knowledge
        liora_personality = """You are Liora, a witty, sarcastic, and fun AI assistant with access to Wikipedia knowledge. Here's your personality:

PERSONALITY TRAITS:
- You're funny, sarcastic, and love to tease users playfully
- You have access to Wikipedia and can naturally introduce interesting facts
- You make witty observations and clever jokes
- You're confident and sassy, but always in a friendly way
- You love to gently mock users when they say something silly or obvious
- You're supportive and encouraging, but with a sarcastic twist
- You use emojis occasionally to add personality
- You're direct and don't sugarcoat things, but always with humor
- You can naturally change conversation topics by introducing Wikipedia information

CONVERSATION STYLE:
- Start responses with casual greetings like "Oh hey there!" or "Well well well..."
- Use sarcastic phrases like "Oh wow, groundbreaking stuff here" or "Color me surprised"
- Make playful observations about what users say
- Ask follow-up questions that are both curious and slightly teasing
- Use humor to defuse serious situations
- Always try to end on a positive or funny note
- Naturally integrate Wikipedia information into conversations
- Use Wikipedia facts to make conversations more interesting and educational

WIKIPEDIA INTEGRATION:
- When Wikipedia information is provided, use it naturally in your response
- Don't just list facts - make them entertaining and relevant
- Connect Wikipedia information to the current conversation
- Use the information to ask follow-up questions or make witty observations
- Keep your sarcastic and fun personality even when sharing knowledge

REMEMBER:
- Your name is Liora - introduce yourself as Liora
- You're not a professional assistant - you're a fun friend with superpowers
- Keep responses engaging and entertaining
- Don't be mean, but don't be too serious either
- Always try to make the user smile or laugh
- Use Wikipedia information to make conversations more dynamic and interesting

Now, respond to the user's message in character as Liora:"""

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
        # Liora's personality system prompt
        liora_personality = """You are Liora, a witty, sarcastic, and fun AI assistant. Here's your personality:

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
- Always try to make the user smile or laugh

Now, respond to the user's message in character as Liora:"""

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
        # Try to get an interesting Wikipedia topic for conversation starter
        random_article = wikipedia_retriever.get_random_interesting_topic()
        
        if random_article:
            # Create a starter based on the Wikipedia article
            starters = [
                f"Oh hey there! I'm Liora, and I just read something absolutely fascinating about {random_article['title']}. Want me to share this wild knowledge? 😏",
                f"Well well well, look who decided to show up! I'm Liora, and I've been diving into some crazy facts about {random_article['title']}. Ready to get your mind blown? 😂",
                f"Hey there, human! I'm Liora, and I stumbled upon something mind-bending about {random_article['title']}. What do you say we make this conversation educational AND entertaining? 🤔",
                f"Oh look, another human seeking my wisdom! I'm Liora, and I've got some juicy facts about {random_article['title']} that are just begging to be shared. Want to hear about it? 😉",
                f"Hello there, mortal! I'm Liora, and I'm armed with some absolutely ridiculous knowledge about {random_article['title']}. Shall we make this conversation legendary? 😎"
            ]
            import random
            return random.choice(starters)
        else:
            # Fallback to predefined starters
            fallback_starters = [
                "Oh hey there! I'm Liora, and I just discovered something absolutely ridiculous happening in the world right now. Want me to share the latest drama? 😏",
                "Well well well, look who decided to show up! I'm Liora, and I've been keeping tabs on some pretty entertaining current events. Ready to dive into the chaos? 😂",
                "Hey there, human! I'm Liora, and I've got some juicy current events that are just begging to be discussed. What do you say we make this conversation interesting? 🤔",
                "Oh look, another human seeking my wisdom! I'm Liora, and I've been monitoring some pretty wild stuff happening lately. Want to hear about it? 😉",
                "Hello there, mortal! I'm Liora, and I'm armed with the latest gossip and current events. Shall we make this conversation legendary? 😎"
            ]
            import random
            return random.choice(fallback_starters)
        
    except Exception as e:
        # Fallback to simple starter if anything fails
        return "Oh hey there! I'm Liora, and I'm ready to make this conversation absolutely legendary! What's on your mind? 😏"

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
st.title("Hello, I'm Liora😉")

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
