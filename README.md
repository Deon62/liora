# Personal AI Agent Dashboard

A Streamlit-based AI agent that initiates conversations and keeps them going using the Gemini 1.5 Flash API. The application features a modern dark-themed UI that matches the design shown in the reference image.

## Features

- 🤖 **AI-Powered Conversations**: Uses Gemini 1.5 Flash model for intelligent responses
- 🎤 **Conversation Initiator**: The AI starts conversations with engaging questions
- 💬 **Persistent Chat**: Maintains conversation history and context
- 🎨 **Modern UI**: Dark-themed interface with sidebar navigation
- 📱 **Responsive Design**: Works on desktop and mobile devices
- ⚙️ **Easy Configuration**: Simple API key setup

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Get Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the API key

### 3. Configure Environment

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_actual_api_key_here
```

### 4. Run the Application

```bash
streamlit run app.py
```

The application will open at `http://localhost:8501`

## Usage

### Starting a Conversation

1. Open the application
2. Click the "🎤 Start Conversation" button
3. The AI will ask you an initial question
4. Respond in the chat input field
5. The conversation will continue naturally

### Navigation

- **Dashboard**: Overview of your AI interactions
- **Profile Setup**: Configure your preferences
- **Chat with AI**: Main conversation interface
- **Analytics**: View conversation statistics
- **Settings**: Manage API configuration

## How It Works

1. **Conversation Initiation**: When you click "Start Conversation", the AI randomly selects from a set of engaging opening questions
2. **Context Awareness**: The AI maintains conversation history to provide contextual responses
3. **Natural Flow**: The AI is designed to ask follow-up questions and keep conversations engaging
4. **Persistent Memory**: All messages are stored in the session state for the duration of your session

## Customization

### Adding More Initial Questions

Edit the `initial_questions` list in the `start_conversation()` function:

```python
initial_questions = [
    "Hi! I'm your AI assistant. What's on your mind today?",
    "Hello! I'd love to get to know you better. What interests you most?",
    # Add your custom questions here
]
```

### Modifying the AI Personality

You can customize the AI's behavior by modifying the prompt in the `generate_response()` function.

### Styling Changes

The application uses custom CSS for styling. You can modify the styles in the `st.markdown()` section of the code.

## Troubleshooting

### API Key Issues
- Ensure your `.env` file is in the project root
- Verify the API key is correct and active
- Check that you have sufficient quota for the Gemini API

### Installation Issues
- Make sure you're using Python 3.8 or higher
- Try upgrading pip: `pip install --upgrade pip`
- Install dependencies one by one if needed

### Runtime Issues
- Check the Streamlit console for error messages
- Ensure all required packages are installed
- Restart the application if needed

## Security Notes

- Never commit your `.env` file to version control
- The API key is stored in session state for the current session only
- In production, use proper secret management systems

## License

This project is open source and available under the MIT License.
