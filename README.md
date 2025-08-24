# Liora AI Assistant 🤖

A sophisticated AI assistant with multiple personalities, real-time search capabilities, and **adaptive learning** that makes it smarter over time!

## ✨ Features

### 🧠 **Adaptive Learning System**
- **Learns from every conversation** - Liora analyzes your communication style, preferred topics, and engagement patterns
- **Personalized responses** - Adapts humor level, formality, response length, and topics based on your preferences
- **Learning insights** - View your interaction statistics, success rates, and learning progress in the sidebar
- **Feedback system** - Rate responses (👍 Good, 😐 Okay, 👎 Bad) to help Liora improve
- **Topic tracking** - Remembers your favorite subjects and focuses conversations on them
- **Communication style detection** - Automatically adapts to your preferred way of communicating

### 🎭 **Multiple Personalities**
- **Sarcastic & Funny** 😏 - Witty, dramatic, and entertaining with human-like gestures
- **Neutral Researcher** 🔬 - Analytical and knowledge-focused
- **Creative Storyteller** ✨ - Imaginative and artistic
- **Wise Mentor** 🧘 - Thoughtful and philosophical

### 🔍 **Real-time Information**
- **Live search** - Get current news, weather, stock prices, and real-time information
- **Wikipedia integration** - Access to vast knowledge base with natural conversation flow
- **Time/date queries** - Instant responses for time-related questions

### 💬 **Advanced Conversation Features**
- **Streaming responses** - Real-time text generation for natural conversation flow
- **Conversation memory** - Persistent chat history across sessions
- **Multiple AI models** - Choose from Gemini, Mistral, Llama, or GPT-3.5
- **Smart conversation starters** - Dynamic openings based on current events and Wikipedia topics

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- API keys for:
  - Google Gemini AI
  - Tavily Search
  - OpenRouter (for additional models)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd aii
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   Create a `.env` file with your API keys:
   ```
   GEMINI_API_KEY=your_gemini_api_key
   TAVILY_API_KEY=your_tavily_api_key
   OPENROUTER_API_KEY=your_openrouter_api_key
   ```

4. **Run the application**
   ```bash
   streamlit run app.py
   ```

## 🧠 How Learning Works

### **Automatic Learning**
- **Topic Analysis** - Liora identifies and tracks your preferred conversation topics
- **Communication Style Detection** - Learns whether you prefer formal, casual, or technical communication
- **Engagement Patterns** - Monitors your engagement level and adjusts response strategies
- **Response Effectiveness** - Analyzes how well responses match your questions and preferences

### **Learning Metrics**
- **Interaction Count** - Total number of conversations
- **Success Rate** - Percentage of effective responses
- **Average Satisfaction** - User feedback scores
- **Learning Progress** - Beginner → Intermediate → Advanced levels

### **Adaptive Features**
- **Dynamic Response Length** - Adjusts based on your message patterns
- **Personality Adjustments** - Modifies humor, formality, and enthusiasm levels
- **Topic Focus** - Prioritizes your favorite subjects in conversations
- **Engagement Strategies** - Uses different approaches based on your engagement level

## 🎯 Usage Examples

### **Learning in Action**
```
User: "Tell me about AI"
Liora: *adjusts imaginary glasses* Oh, you're asking about AI! I've noticed you're really into technology topics. Let me share some fascinating insights about artificial intelligence that I think you'll find interesting...

[After a few conversations about tech]
User: "What's the weather like?"
Liora: *leans in conspiratorially* Well well well, look who's asking about weather! I've learned you usually prefer detailed explanations, so let me give you the full meteorological breakdown...
```

### **Feedback System**
After each response, you can provide feedback:
- **👍 Good** - Liora learns this response style works well
- **😐 Okay** - Liora adjusts for improvement
- **👎 Bad** - Liora learns to avoid similar responses

## 📊 Learning Insights

The sidebar shows real-time learning data:
- **Your favorite topics** (based on conversation analysis)
- **Communication style preference** (formal/casual/technical)
- **Success rate** and **satisfaction scores**
- **Learning progress level**

## 🔧 Configuration

### **Model Selection**
Choose from multiple AI models:
- **Gemini 1.5 Flash** (default) - Fast and efficient
- **Mistral 7B** - Lightweight and quick
- **Llama 3.1 8B** - Meta's efficient model
- **GPT-3.5 Turbo** - OpenAI's reliable model

### **Personality Modes**
Switch between personalities to match your mood:
- **Sarcastic & Funny** - For entertainment and casual chats
- **Neutral Researcher** - For learning and analysis
- **Creative Storyteller** - For imagination and creativity
- **Wise Mentor** - For guidance and reflection

## 🛠️ Technical Details

### **Learning Data Storage**
- `liora_learning_data.pkl` - Core learning metrics and patterns
- `conversation_patterns.json` - Effective response patterns
- `user_preferences.json` - User communication preferences

### **Learning Algorithms**
- **Topic Frequency Analysis** - Tracks preferred subjects
- **Sentiment Analysis** - Monitors conversation mood
- **Engagement Assessment** - Measures user interest levels
- **Response Effectiveness Scoring** - Evaluates response quality

## 🤝 Contributing

Contributions are welcome! Areas for improvement:
- Enhanced learning algorithms
- Additional personality modes
- More sophisticated feedback systems
- Advanced conversation analysis

## 📝 License

This project is licensed under the MIT License.

---

**Liora gets smarter with every conversation!** 🧠✨
