import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
import json
from datetime import datetime
import pickle
import uuid

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("Please set your GEMINI_API_KEY in the .env file")
    st.stop()

genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-1.5-flash')

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
        padding: 8px 0;
        margin: 4px 0;
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
        padding: 6px 12px;
        font-weight: 400;
        transition: background-color 0.2s;
        text-align: left;
    }
    .stButton > button:hover {
        background-color: #374151;
    }
    
    /* Title styling */
    h1 {
        color: white;
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 2rem;
        text-align: center;
    }
    

    
    /* Sidebar styling */
    .css-1d391kg {
        background-color: #262730;
    }
    
    /* Remove default margins and padding */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 6rem;
    }
    
    /* Chat container styling */
    .stContainer {
        margin-bottom: 80px;
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


# Function to generate AI response with streaming
def generate_response_stream(prompt, conversation_history=None):
    try:
        if conversation_history:
            # Include conversation history for context
            full_prompt = f"Conversation history:\n{conversation_history}\n\nCurrent message: {prompt}"
        else:
            full_prompt = prompt
        
        response = model.generate_content(full_prompt, stream=True)
        return response
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}"

# Function to generate AI response (non-streaming fallback)
def generate_response(prompt, conversation_history=None):
    try:
        if conversation_history:
            # Include conversation history for context
            full_prompt = f"Conversation history:\n{conversation_history}\n\nCurrent message: {prompt}"
        else:
            full_prompt = prompt
        
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

# Function to start conversation
def start_conversation():
    if not st.session_state.current_conversation_id:
        create_new_conversation()
    
    initial_questions = [
        "Hi! I'm your AI assistant. What's on your mind today?",
        "Hello! I'd love to get to know you better. What interests you most?",
        "Hey there! I'm here to chat. What would you like to talk about?",
        "Welcome! I'm curious - what's something you're passionate about?",
        "Hi! I'm excited to chat with you. What's been on your mind lately?"
    ]
    
    import random
    initial_question = random.choice(initial_questions)
    
    # Add the initial message to the current conversation
    conversation = st.session_state.conversations[st.session_state.current_conversation_id]
    conversation["messages"].append({
        "role": "assistant",
        "content": initial_question,
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
        st.markdown("<p style='color: white; margin: 0; padding-top: 8px;'>New chat</p>", unsafe_allow_html=True)
    
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
        
        # Start conversation if not started
        if not st.session_state.conversation_started:
            if st.button("🎤 Start Conversation", key="start_conv"):
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
            
            # Stream the response
            if hasattr(response_stream, '__iter__'):
                for chunk in response_stream:
                    if hasattr(chunk, 'text'):
                        full_response += chunk.text
                        # Update the placeholder with the current response
                        with message_placeholder.chat_message("assistant"):
                            st.write(full_response)
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
