# AI Tutoring System - Chatbot Interface

## 🎉 NEW: Interactive Chatbot UI

Your AI Tutoring System now includes a comprehensive chatbot interface that provides real-time conversational learning while preserving the original command-line functionality in `main.py`.

## 🚀 Quick Start

1. **Start the Backend API Server:**
   ```bash
   python api_server.py
   ```

2. **Start the Frontend (in a new terminal):**
   ```bash
   cd frontend
   npm start
   ```

3. **Access the Application:**
   - Open your browser to `http://localhost:3000`
   - Login with your username
   - Click on the "Chat" tab in the sidebar

## ✨ Features

### 💬 Real-time Chat Interface
- Natural conversation with your AI tutor
- Source-based responses with citations
- Message history preservation
- Typing indicators and smooth animations

### 🛠️ Interactive Commands
Use these commands in the chat for specific functionality:

- `!help` - Show all available commands
- `!explain <topic>` - Get detailed explanations
- `!example <topic>` - Get practical examples
- `!question <topic>` - Generate practice questions
- `!quiz <topic>` - Start an interactive quiz
- `!hint` - Get hints for current questions
- `!sources` - View available documents
- `!progress` - Check your learning progress

### 📚 Document-Based Learning
- **Advanced RAG System**: Answers are grounded in your documents
- **Citation Support**: See which documents support each answer
- **Multiple Sources**: Supports PDF and text files in the `docs/` folder

### 🎯 Personalized Experience
- **Smart Suggestions**: Personalized question suggestions based on your learning history
- **Progress Tracking**: Integration with the existing memory system
- **Weak Area Focus**: Automatic recommendations for topics to review

### 🧩 Quiz Mode
- Interactive quizzes directly in chat
- Immediate feedback with explanations
- Progress tracking and scoring

## 📁 Available Documents
Your system currently has:
- Essentials of Geographic Information Systems.pdf
- Basic GIS Coordinates.pdf

Add more documents to the `docs/` folder to expand the knowledge base.

## 🎮 How to Use

### Basic Chat
1. Type any question about your study materials
2. Get instant, source-based responses
3. Follow up with related questions

### Using Commands
```
You: !explain coordinate systems
AI: [Detailed explanation with citations]

You: !quiz GIS
AI: Quiz started! Question 1: What is a coordinate system?
You: [Your answer]
AI: ✅ Correct! [Feedback and explanation]
```

### Interactive Learning
```
You: I'm struggling with map projections
AI: [Explanation with examples and citations]
AI: Would you like to try a practice question?
You: Yes
AI: [Generates relevant question]
```

## 🏗️ Technical Architecture

### Backend (Python)
- **FastAPI Server** (`api_server.py`) - REST API endpoints
- **Advanced RAG** (`advanced_rag.py`) - Document retrieval and processing
- **Domain Expert** (`domain_expert.py`) - LLM-powered responses
- **Memory System** (`enhanced_memory.py`) - Progress tracking
- **Interactive Sessions** (`interactive_session.py`) - Conversation management

### Frontend (React)
- **Chat Interface** (`frontend/src/pages/Chat.js`) - Main chat UI
- **Real-time Messaging** - Instant responses and updates
- **Command Processing** - Interactive command system
- **History Management** - Persistent chat history

### Key Chat API Endpoints
- `POST /api/chat/message` - Send chat messages
- `POST /api/chat/command` - Execute interactive commands
- `GET /api/chat/{username}/history` - Retrieve chat history
- `POST /api/chat/quiz/answer` - Submit quiz answers
- `GET /api/chat/suggestions/{username}` - Get personalized suggestions

## 🔧 Command Line Compatibility

The original command-line interface in `main.py` remains **fully functional**:

```bash
python main.py
```

All existing features work exactly as before:
- Review mode
- Learn mode  
- Test mode
- Insights mode
- LLM provider management

## 🎨 UI Features

### Modern Chat Interface
- **Bubble Layout**: WhatsApp-style message bubbles
- **Rich Markdown**: Support for formatted text, lists, and code
- **Citations Display**: Source documents shown with each response
- **Quick Suggestions**: Contextual follow-up questions
- **Command Helper**: Built-in command reference

### Responsive Design
- **Mobile Friendly**: Works on all screen sizes
- **Dark/Light Themes**: Consistent with your app's design system
- **Smooth Animations**: Framer Motion powered interactions
- **Loading States**: Clear feedback during processing

## 🚨 Troubleshooting

### Backend Issues
```bash
# Check if API server is running
curl http://localhost:8000/health

# Restart backend
python api_server.py
```

### Frontend Issues
```bash
# Restart frontend
cd frontend
npm start

# Check console for errors
# Open browser DevTools (F12)
```

### No Documents Found
- Ensure PDF/text files are in the `docs/` folder
- Restart the backend after adding new documents
- Check file permissions

### Chat Not Responding
- Verify both frontend (port 3000) and backend (port 8000) are running
- Check browser console for API errors
- Ensure CORS is properly configured

## 🔮 Advanced Usage

### Custom LLM Providers
The chat system supports multiple LLM providers:
- OpenAI GPT models
- DeepSeek models  
- Anthropic Claude
- Google Gemini
- Local models

Configure providers through the existing LLM management system or chat commands.

### Bulk Document Processing
Add multiple documents to `docs/` folder:
```bash
docs/
├── textbook_chapter1.pdf
├── lecture_notes.txt
├── research_paper.pdf
└── study_guide.md
```

The system automatically indexes all supported file types.

## 🎓 Educational Features

### Adaptive Learning
- **Difficulty Adjustment**: Questions adapt to your performance
- **Spaced Repetition**: Review recommendations based on memory research
- **Learning Analytics**: Detailed progress tracking and insights

### Multi-Modal Learning
- **Explanations**: Detailed concept breakdowns
- **Examples**: Practical applications and use cases
- **Questions**: Practice problems and assessments
- **Hints**: Guided assistance when stuck

## 🤝 Contributing

The chat system is built with extensibility in mind:
- Add new commands in `api_server.py`
- Extend UI components in `frontend/src/pages/Chat.js`
- Integrate new LLM providers through `llm_providers.py`

## 📝 License

Same as the main project.

---

**Happy Learning! 🎓✨**

Your AI tutor is now available 24/7 through both chat and command-line interfaces. 