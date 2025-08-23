# Liora AI Assistant

A conversational AI assistant built with Streamlit, featuring multiple personality modes and model switching capabilities.

## Features

- 🤖 Multiple AI models (Gemini 1.5 Flash, Mistral 7B, Llama 3.1 8B, GPT-3.5 Turbo)
- 🎭 Four personality modes (Sarcastic & Funny, Neutral Researcher, Creative Storyteller, Wise Mentor)
- 🔍 Real-time search capabilities with Tavily
- 📚 Wikipedia integration for dynamic conversations
- 💬 Persistent conversation history
- 🎨 Clean, dark-themed UI

## Deployment on Streamlit Cloud

### Prerequisites
- GitHub repository with the code
- API keys for the following services:
  - Google Gemini API
  - Tavily Search API
  - OpenRouter API

### Setup Steps

1. **Fork/Clone this repository** to your GitHub account

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Set the main file path to `app.py`

3. **Configure Environment Variables:**
   In Streamlit Cloud's app settings, add these secrets:
   ```
   GEMINI_API_KEY = your_gemini_api_key
   TAVILY_API_KEY = your_tavily_api_key
   OPENROUTER_API_KEY = your_openrouter_api_key
   ```

4. **Deploy!** The app should now be live and accessible.

## Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up environment variables:**
   Create a `.env` file with your API keys:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   TAVILY_API_KEY=your_tavily_api_key
   OPENROUTER_API_KEY=your_openrouter_api_key
   ```

3. **Run the app:**
   ```bash
   streamlit run app.py
   ```

## API Keys Required

- **Google Gemini API**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Tavily Search API**: Get from [Tavily](https://tavily.com/)
- **OpenRouter API**: Get from [OpenRouter](https://openrouter.ai/)

## Features in Detail

### Personality Modes
- **Sarcastic & Funny**: Witty, playful, and entertaining responses
- **Neutral Researcher**: Analytical and informative approach
- **Creative Storyteller**: Imaginative and artistic responses
- **Wise Mentor**: Thoughtful and philosophical guidance

### AI Models
- **Gemini 1.5 Flash**: Fast and efficient Google model
- **Mistral 7B**: Lightweight and fast Mistral model
- **Llama 3.1 8B**: Meta's efficient Llama model
- **GPT-3.5 Turbo**: OpenAI's reliable and fast model

## Troubleshooting

If you encounter deployment issues:
1. Check that all API keys are properly set in Streamlit Cloud secrets
2. Ensure your GitHub repository is public or you have proper access
3. Verify that the main file path is set to `app.py`
4. Check the deployment logs for any dependency conflicts

## License

This project is open source and available under the MIT License.
