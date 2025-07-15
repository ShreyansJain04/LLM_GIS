# AI Tutoring System - API Documentation

## Table of Contents

1. [System Overview](#system-overview)
2. [Backend API Documentation](#backend-api-documentation)
3. [Python Module Documentation](#python-module-documentation)
4. [Frontend Components Documentation](#frontend-components-documentation)
5. [Usage Examples](#usage-examples)
6. [Setup and Configuration](#setup-and-configuration)

---

## System Overview

The AI Tutoring System is a comprehensive educational platform that combines advanced AI capabilities with user-friendly interfaces to provide personalized learning experiences. It features:

- **Advanced RAG (Retrieval-Augmented Generation)** with document processing
- **Multi-LLM Provider Support** (OpenAI, Anthropic, Ollama, DeepSeek)
- **Spaced Repetition Learning** with flashcards
- **Interactive Sessions** with dynamic difficulty adjustment
- **Enhanced Memory System** with learning pattern analytics
- **Document Processing** with PDF support and citation tracking
- **Web-based Frontend** with React components

---

## Backend API Documentation

### Base URL
```
http://localhost:8000
```

### Authentication
The system uses username-based authentication. All API endpoints require a valid username parameter.

### User Management Endpoints

#### Create User
```http
POST /api/users/create
```

**Request Body:**
```json
{
  "username": "string"
}
```

**Response:**
```json
{
  "message": "User created successfully",
  "username": "string",
  "profile": {
    "weak_areas": [],
    "topic_mastery": {},
    "history": [],
    "learning_plan": {},
    "performance_data": {},
    "last_active": "2024-01-01T00:00:00.000Z"
  }
}
```

#### Get User Profile
```http
GET /api/users/{username}/profile
```

**Response:**
```json
{
  "username": "string",
  "weak_areas": ["topic1", "topic2"],
  "topic_mastery": {
    "topic1": 0.75,
    "topic2": 0.60
  },
  "history": [],
  "learning_plan": {},
  "performance_data": {},
  "last_active": "2024-01-01T00:00:00.000Z"
}
```

#### Get User Insights
```http
GET /api/users/{username}/insights
```

**Response:**
```json
{
  "learning_patterns": {
    "time_of_day_performance": {},
    "session_duration_patterns": [],
    "mistake_patterns": {},
    "improvement_velocity": {},
    "concept_relationships": {}
  },
  "personalization": {
    "preferred_learning_style": "visual",
    "optimal_session_length": 20,
    "best_time_of_day": "morning",
    "difficulty_preference": "medium"
  },
  "personalized_recommendations": {}
}
```

### Learning Content Endpoints

#### Explain Concept
```http
POST /api/content/explain
```

**Request Body:**
```json
{
  "topic": "string",
  "detail_level": "basic|standard|advanced"
}
```

**Response:**
```json
{
  "explanation": "string",
  "citations": ["source1", "source2"],
  "related_topics": ["topic1", "topic2"]
}
```

#### Generate Question
```http
POST /api/content/question
```

**Request Body:**
```json
{
  "topic": "string",
  "difficulty": "easy|medium|hard",
  "question_type": "conceptual|practical|analytical",
  "previous_questions": ["question1", "question2"]
}
```

**Response:**
```json
{
  "question": "string",
  "question_type": "conceptual",
  "difficulty": "medium",
  "expected_answer": "string",
  "hints": ["hint1", "hint2"],
  "related_topics": ["topic1", "topic2"]
}
```

#### Check Answer
```http
POST /api/content/check-answer
```

**Request Body:**
```json
{
  "question": "string",
  "answer": "string",
  "username": "string"
}
```

**Response:**
```json
{
  "is_correct": true,
  "score": 0.85,
  "feedback": "string",
  "suggestions": ["suggestion1", "suggestion2"],
  "concepts_to_review": ["concept1", "concept2"]
}
```

### Session Management Endpoints

#### Start Interactive Session
```http
POST /api/sessions/start
```

**Request Body:**
```json
{
  "username": "string",
  "topic": "string",
  "mode": "learning|review|test"
}
```

**Response:**
```json
{
  "session_id": "string",
  "topic": "string",
  "mode": "learning",
  "commands_available": ["!help", "!explain", "!example"],
  "initial_content": "string"
}
```

#### Send Session Command
```http
POST /api/sessions/{session_id}/command
```

**Request Body:**
```json
{
  "command": "string",
  "input": "string"
}
```

**Response:**
```json
{
  "response": "string",
  "mode": "learning",
  "suggestions": ["suggestion1", "suggestion2"],
  "progress": 0.65
}
```

### Document Management Endpoints

#### Get Available Sources
```http
GET /api/sources
```

**Response:**
```json
{
  "sources": [
    {
      "filename": "document.pdf",
      "pages": 150,
      "processed": true,
      "indexed": true,
      "content_preview": "string"
    }
  ]
}
```

#### Query Documents
```http
POST /api/sources/query
```

**Request Body:**
```json
{
  "query": "string",
  "max_results": 10,
  "min_score": 0.7
}
```

**Response:**
```json
{
  "results": [
    {
      "content": "string",
      "source": "document.pdf",
      "page": 42,
      "score": 0.85,
      "citation": "[document.pdf, p. 42]"
    }
  ],
  "total_results": 5
}
```

### Flashcard Endpoints

#### Get Flashcards
```http
GET /api/flashcards/{username}/{topic}
```

**Response:**
```json
{
  "cards": [
    {
      "front": "string",
      "back": "string",
      "subtopic": "string",
      "difficulty": 1.5,
      "next_review": "2024-01-01T00:00:00.000Z",
      "mastery_level": 0.75
    }
  ],
  "stats": {
    "cards_studied": 50,
    "correct_answers": 42,
    "study_sessions": 10
  }
}
```

#### Study Flashcard
```http
POST /api/flashcards/{username}/{topic}/study
```

**Request Body:**
```json
{
  "card_id": "string",
  "performance": "again|hard|good|easy"
}
```

**Response:**
```json
{
  "next_review": "2024-01-01T00:00:00.000Z",
  "difficulty": 1.6,
  "mastery_level": 0.80,
  "stats_updated": true
}
```

---

## Python Module Documentation

### Memory Management (`memory.py`)

The memory module handles user data persistence, learning history, and performance tracking.

#### Functions

##### `load_user(username: str) -> dict`
Loads user data with file locking for concurrency safety.

**Parameters:**
- `username` (str): The user's username

**Returns:**
- `dict`: User profile data including weak areas, topic mastery, history, learning plan, performance data, and last active timestamp

**Example:**
```python
from memory import load_user

profile = load_user("john_doe")
print(f"User's weak areas: {profile['weak_areas']}")
```

##### `save_user(username: str, profile: dict) -> None`
Saves user profile data with file locking.

**Parameters:**
- `username` (str): The user's username
- `profile` (dict): Complete user profile data

**Example:**
```python
from memory import save_user, load_user

profile = load_user("john_doe")
profile['weak_areas'].append("calculus")
save_user("john_doe", profile)
```

##### `get_weak_areas(username: str) -> List[str]`
Returns topics where the user needs improvement.

**Parameters:**
- `username` (str): The user's username

**Returns:**
- `List[str]`: List of topics needing improvement

##### `get_performance_summary(username: str) -> Dict`
Generates a comprehensive performance summary.

**Parameters:**
- `username` (str): The user's username

**Returns:**
- `Dict`: Performance statistics including topics studied, mastered, and weak areas count

##### `record_learning_session(username: str, topic: str, performance: float, duration: int) -> None`
Records a completed learning session.

**Parameters:**
- `username` (str): The user's username
- `topic` (str): The topic studied
- `performance` (float): Performance score (0.0-1.0)
- `duration` (int): Session duration in minutes

### LLM Providers (`llm_providers.py`)

The LLM providers module implements a multi-provider system for various language models.

#### Classes

##### `LLMProvider` (Abstract Base Class)
Abstract base class for all LLM providers.

**Abstract Methods:**
- `generate(prompt: str, **kwargs) -> str`: Generate response from the LLM
- `is_available() -> bool`: Check if provider is available
- `get_info() -> Dict[str, Any]`: Get provider information

##### `OpenAIProvider`
Provider for OpenAI models (GPT-4, GPT-3.5-turbo).

**Constructor:**
```python
def __init__(self, model: str = None, api_key: str = None)
```

**Parameters:**
- `model` (str): Model name (default: "gpt-4")
- `api_key` (str): OpenAI API key

**Methods:**
- `generate(prompt: str, temperature: float = 0.7, max_tokens: int = 2000, **kwargs) -> str`

**Example:**
```python
from llm_providers import OpenAIProvider

provider = OpenAIProvider(model="gpt-4")
response = provider.generate("Explain quantum computing", temperature=0.5)
```

##### `AnthropicProvider`
Provider for Anthropic models (Claude).

**Constructor:**
```python
def __init__(self, model: str = None, api_key: str = None)
```

**Methods:**
- `generate(prompt: str, temperature: float = 0.7, max_tokens: int = 2000, **kwargs) -> str`

##### `LLMManager`
Manages multiple LLM providers and handles fallback logic.

**Methods:**
- `get_available_providers() -> List[str]`: Get list of available providers
- `set_provider(provider_name: str) -> bool`: Set active provider
- `generate(prompt: str, **kwargs) -> str`: Generate using active provider with fallback

**Example:**
```python
from llm_providers import llm_manager

llm_manager.set_provider("openai")
response = llm_manager.generate("What is machine learning?")
```

### Domain Expert (`domain_expert.py`)

The domain expert module provides advanced AI tutoring capabilities with RAG integration.

#### Functions

##### `query_domain_expert(prompt: str, context: str = "", citations: List[str] = None, provider: str = None, temperature: float = 0.7) -> str`
Query the domain expert with advanced RAG context.

**Parameters:**
- `prompt` (str): The question or request
- `context` (str): Optional pre-retrieved context
- `citations` (List[str]): Optional citations for context
- `provider` (str): Specific LLM provider to use
- `temperature` (float): LLM temperature setting

**Returns:**
- `str`: Generated response from domain expert

**Example:**
```python
from domain_expert import query_domain_expert

response = query_domain_expert(
    "What are the principles of machine learning?",
    provider="openai",
    temperature=0.5
)
```

##### `generate_question(topic: str, difficulty: str = "medium", question_type: str = "conceptual", previous_questions: List[str] = None) -> Tuple[str, str]`
Generate educational questions on a specific topic.

**Parameters:**
- `topic` (str): The topic for the question
- `difficulty` (str): Question difficulty ("easy", "medium", "hard")
- `question_type` (str): Type of question ("conceptual", "practical", "analytical")
- `previous_questions` (List[str]): Previously asked questions to avoid duplicates

**Returns:**
- `Tuple[str, str]`: (question, expected_answer)

##### `check_answer(question: str, student_answer: str, expected_answer: str = None) -> Tuple[bool, float, str]`
Evaluate student answers with detailed feedback.

**Parameters:**
- `question` (str): The original question
- `student_answer` (str): Student's answer
- `expected_answer` (str): Expected answer (optional)

**Returns:**
- `Tuple[bool, float, str]`: (is_correct, score, feedback)

##### `explain_concept(topic: str, detail_level: str = "standard") -> str`
Generate detailed explanations of concepts.

**Parameters:**
- `topic` (str): The concept to explain
- `detail_level` (str): Level of detail ("basic", "standard", "advanced")

**Returns:**
- `str`: Detailed explanation

##### `generate_example(topic: str, example_type: str = "practical") -> str`
Generate examples for better understanding.

**Parameters:**
- `topic` (str): The topic for examples
- `example_type` (str): Type of example ("practical", "theoretical", "real-world")

**Returns:**
- `str`: Generated example

### Advanced RAG System (`advanced_rag.py`)

The advanced RAG system provides sophisticated document retrieval and ranking capabilities.

#### Classes

##### `Document`
Enhanced document representation with metadata.

**Attributes:**
- `id` (str): Unique document identifier
- `text` (str): Document text content
- `source` (str): Source file path
- `page` (int): Page number (for PDFs)
- `chunk_index` (int): Chunk index within document
- `metadata` (Dict): Additional metadata
- `embedding` (np.ndarray): Vector embedding

##### `AdvancedRAGSystem`
Main RAG system with hybrid search and reranking.

**Constructor:**
```python
def __init__(self, docs_path: Path, embedding_model: str = 'all-MiniLM-L6-v2', 
             rerank_model: str = 'cross-encoder/ms-marco-MiniLM-L-6-v2', 
             chunk_size: int = 512, chunk_overlap: int = 128)
```

**Methods:**

##### `add_document(doc: Document) -> None`
Add a document to the RAG system.

##### `search(query: str, max_results: int = 10, min_score: float = 0.0, rerank: bool = True) -> List[Tuple[Document, float]]`
Perform hybrid search with optional reranking.

**Parameters:**
- `query` (str): Search query
- `max_results` (int): Maximum results to return
- `min_score` (float): Minimum relevance score
- `rerank` (bool): Whether to use reranking

**Returns:**
- `List[Tuple[Document, float]]`: List of (document, score) tuples

**Example:**
```python
from advanced_rag import AdvancedRAGSystem
from pathlib import Path

rag = AdvancedRAGSystem(Path('docs'))
results = rag.search("machine learning algorithms", max_results=5)
for doc, score in results:
    print(f"Score: {score:.2f}, Source: {doc.source}")
    print(f"Content: {doc.text[:100]}...")
```

##### `get_statistics() -> Dict`
Get system statistics including document count, chunk count, and index size.

### Enhanced Memory System (`enhanced_memory.py`)

The enhanced memory system provides detailed learning analytics and personalization.

#### Classes

##### `LearningPatternAnalyzer`
Analyzes learning patterns and provides insights.

**Constructor:**
```python
def __init__(self, username: str)
```

**Methods:**

##### `analyze_session(session_data: Dict) -> Dict`
Analyze a learning session and update patterns.

##### `get_learning_insights() -> Dict`
Get detailed learning insights and recommendations.

##### `update_mistake_patterns(topic: str, mistake_type: str, context: str) -> None`
Update mistake patterns for improved personalization.

##### `EnhancedMemorySystem`
Main enhanced memory system with comprehensive analytics.

**Constructor:**
```python
def __init__(self, username: str)
```

**Methods:**

##### `get_insights() -> Dict`
Get comprehensive learning insights including patterns, recommendations, and analytics.

**Returns:**
- `Dict`: Comprehensive insights including learning patterns, personalization settings, and recommendations

**Example:**
```python
from enhanced_memory import EnhancedMemorySystem

memory = EnhancedMemorySystem("john_doe")
insights = memory.get_insights()
recommendations = insights['personalized_recommendations']
```

### Interactive Session Management (`interactive_session.py`)

The interactive session module manages dynamic tutoring sessions.

#### Classes

##### `InteractionMode` (Enum)
Defines available interaction modes.

**Values:**
- `LEARNING`: Active learning mode
- `QUESTIONING`: Q&A mode
- `EXPLAINING`: Explanation mode
- `TESTING`: Assessment mode
- `PAUSED`: Session paused

##### `Command` (Enum)
Available interactive commands.

**Values:**
- `HELP`: Show help information
- `EXPLAIN_MORE`: Get detailed explanation
- `EXAMPLE`: Request examples
- `HINT`: Get hints
- `SKIP`: Skip current item
- `PAUSE`/`RESUME`: Pause/resume session
- `ASK`: Ask questions
- `DIFFICULTY`: Adjust difficulty
- `PROGRESS`: Show progress
- `QUIT`: End session

##### `InteractiveSession`
Manages interactive tutoring sessions.

**Constructor:**
```python
def __init__(self, username: str, topic: str)
```

**Methods:**

##### `start_session() -> str`
Start a new interactive session.

##### `process_input(user_input: str) -> Tuple[str, Dict]`
Process user input and return response with session state.

##### `execute_command(command: Command, args: str = "") -> str`
Execute an interactive command.

**Example:**
```python
from interactive_session import InteractiveSession

session = InteractiveSession("john_doe", "calculus")
welcome = session.start_session()
response, state = session.process_input("!explain derivatives")
```

### Planner Agent (`planner.py`)

The planner agent builds learning plans and drives learning loops.

#### Classes

##### `PlannerAgent`
Main planner agent for learning path management.

**Constructor:**
```python
def __init__(self, username: str)
```

**Methods:**

##### `suggest_mode() -> str`
Suggest the best learning mode based on user progress.

##### `create_learning_plan(topic: str, target_level: str = "intermediate") -> Dict`
Create a structured learning plan.

##### `get_next_topic() -> str`
Get the next recommended topic for study.

##### `update_progress(topic: str, performance: float) -> None`
Update user progress on a topic.

**Example:**
```python
from planner import PlannerAgent

planner = PlannerAgent("john_doe")
mode = planner.suggest_mode()
plan = planner.create_learning_plan("machine learning")
```

### Document Processing (`document_processor.py`)

The document processor handles PDF and text document processing with citation tracking.

#### Classes

##### `DocumentChunk`
Represents a chunk of text with metadata.

**Constructor:**
```python
def __init__(self, text: str, source: str, page: int = None, chunk_id: int = None)
```

**Methods:**

##### `get_citation() -> str`
Generate citation for the chunk.

##### `DocumentProcessor`
Main document processor with PDF support.

**Constructor:**
```python
def __init__(self, docs_path: Path = Path('docs'))
```

**Methods:**

##### `process_document(file_path: Path) -> List[DocumentChunk]`
Process a document and return chunks.

##### `search_documents(query: str, max_results: int = 10) -> List[Tuple[DocumentChunk, float]]`
Search through processed documents.

**Example:**
```python
from document_processor import DocumentProcessor
from pathlib import Path

processor = DocumentProcessor()
chunks = processor.process_document(Path('docs/textbook.pdf'))
results = processor.search_documents("machine learning")
```

### Flashcard System (`flashcards.py`)

The flashcard system implements spaced repetition learning.

#### Classes

##### `FlashcardDeck`
Manages flashcard decks with spaced repetition.

**Constructor:**
```python
def __init__(self, username: str, topic: str)
```

**Methods:**

##### `add_card(front: str, back: str, subtopic: str = None) -> Dict`
Add a new flashcard to the deck.

##### `get_due_cards() -> List[Dict]`
Get cards that are due for review.

##### `study_card(card_id: str, performance: str) -> Dict`
Study a card and update its scheduling.

**Parameters:**
- `card_id` (str): Unique card identifier
- `performance` (str): Performance rating ("again", "hard", "good", "easy")

**Returns:**
- `Dict`: Updated card information including next review date

##### `get_statistics() -> Dict`
Get deck statistics including study progress.

**Example:**
```python
from flashcards import FlashcardDeck

deck = FlashcardDeck("john_doe", "calculus")
deck.add_card("What is a derivative?", "Rate of change of a function")
due_cards = deck.get_due_cards()
stats = deck.get_statistics()
```

---

## Frontend Components Documentation

### React Components

#### `LoginForm.js`
User authentication component.

**Props:**
- None (uses context)

**State:**
- `username`: Current username input
- `loading`: Loading state
- `error`: Error message

**Methods:**
- `handleSubmit()`: Handle form submission
- `handleGuestLogin()`: Handle guest login

**Example:**
```jsx
import LoginForm from './components/LoginForm';

function App() {
  return <LoginForm />;
}
```

#### `Dashboard.js`
Main dashboard with learning overview.

**Props:**
- None (uses context)

**Features:**
- Progress overview
- Recent activity
- Recommended topics
- Quick actions

**State:**
- `userProfile`: User profile data
- `insights`: Learning insights
- `loading`: Loading state

#### `Learn.js`
Interactive learning interface.

**Props:**
- None (uses context)

**Features:**
- Topic selection
- Interactive explanations
- Example generation
- Progress tracking

**State:**
- `selectedTopic`: Currently selected topic
- `currentContent`: Current learning content
- `mode`: Learning mode
- `progress`: Learning progress

#### `Chat.js`
AI chat interface for questions and discussions.

**Props:**
- None (uses context)

**Features:**
- Real-time chat
- Context-aware responses
- Citation support
- Message history

**State:**
- `messages`: Chat message history
- `input`: Current input
- `isLoading`: Loading state

#### `Review.js`
Review mode with spaced repetition.

**Props:**
- None (uses context)

**Features:**
- Spaced repetition scheduling
- Flashcard interface
- Progress tracking
- Performance analytics

**State:**
- `currentCard`: Current flashcard
- `deck`: Flashcard deck
- `sessionStats`: Session statistics

#### `Test.js`
Assessment and testing interface.

**Props:**
- None (uses context)

**Features:**
- Question generation
- Answer evaluation
- Progress tracking
- Performance feedback

**State:**
- `currentQuestion`: Current question
- `userAnswer`: User's answer
- `results`: Test results

#### `Settings.js`
User preferences and configuration.

**Props:**
- None (uses context)

**Features:**
- LLM provider selection
- Difficulty preferences
- Learning style settings
- Account management

**State:**
- `settings`: User settings
- `providers`: Available LLM providers
- `saving`: Save state

#### `Sources.js`
Document source management.

**Props:**
- None (uses context)

**Features:**
- Document upload
- Source browsing
- Search functionality
- Citation tracking

**State:**
- `sources`: Available sources
- `searchResults`: Search results
- `uploading`: Upload state

### Context Providers

#### `UserContext`
Provides user authentication and profile management.

**Methods:**
- `login(username)`: Authenticate user
- `logout()`: Sign out user
- `updateProfile(data)`: Update user profile

**State:**
- `user`: Current user data
- `isAuthenticated`: Authentication status
- `loading`: Loading state

### Service Layer

#### `api.js`
Main API service layer.

**Modules:**

##### `userAPI`
- `createUser(username)`: Create new user
- `getUserProfile(username)`: Get user profile
- `getUserInsights(username)`: Get user insights

##### `contentAPI`
- `explainConcept(topic, detailLevel)`: Get concept explanation
- `generateQuestion(topic, difficulty, type)`: Generate question
- `checkAnswer(question, answer)`: Check answer
- `generateExample(topic, type)`: Generate example

##### `sessionAPI`
- `startSession(username, topic, mode)`: Start interactive session
- `sendCommand(sessionId, command, input)`: Send session command
- `endSession(sessionId)`: End session

##### `flashcardAPI`
- `getFlashcards(username, topic)`: Get flashcard deck
- `studyCard(username, topic, cardId, performance)`: Study card
- `createCard(username, topic, front, back)`: Create new card

##### `sourcesAPI`
- `getSources()`: Get available sources
- `queryDocuments(query, maxResults)`: Search documents
- `uploadDocument(file)`: Upload new document

**Example:**
```javascript
import { contentAPI } from './services/api';

const explanation = await contentAPI.explainConcept('machine learning', 'standard');
const question = await contentAPI.generateQuestion('calculus', 'medium', 'conceptual');
```

---

## Usage Examples

### Basic CLI Usage

```bash
# Start the chatbot
./start_chatbot.sh

# Run the main application
python main.py

# Start the API server
python api_server.py
```

### Python API Usage

```python
# Basic user management
from memory import load_user, save_user
from planner import PlannerAgent

# Load user and create planner
user = load_user("john_doe")
planner = PlannerAgent("john_doe")

# Get learning suggestions
mode = planner.suggest_mode()
plan = planner.create_learning_plan("calculus")

# Start interactive session
from interactive_session import InteractiveSession
session = InteractiveSession("john_doe", "calculus")
welcome = session.start_session()
```

### Advanced RAG Usage

```python
from advanced_rag import AdvancedRAGSystem
from pathlib import Path

# Initialize RAG system
rag = AdvancedRAGSystem(Path('docs'))

# Search documents
results = rag.search("machine learning algorithms", max_results=5)

# Process results
for doc, score in results:
    print(f"Relevance: {score:.2f}")
    print(f"Source: {doc.source}")
    print(f"Content: {doc.text[:200]}...")
    print(f"Citation: {doc.get_citation()}")
```

### LLM Provider Usage

```python
from llm_providers import llm_manager, OpenAIProvider

# Use default provider
response = llm_manager.generate("Explain quantum computing")

# Use specific provider
openai = OpenAIProvider(model="gpt-4")
response = openai.generate("What is machine learning?", temperature=0.3)

# Set system provider
llm_manager.set_provider("anthropic")
response = llm_manager.generate("Explain calculus")
```

### Frontend Integration

```jsx
import React, { useState, useEffect } from 'react';
import { contentAPI } from './services/api';

function ConceptExplainer() {
  const [topic, setTopic] = useState('');
  const [explanation, setExplanation] = useState('');
  const [loading, setLoading] = useState(false);

  const handleExplain = async () => {
    setLoading(true);
    try {
      const result = await contentAPI.explainConcept(topic, 'standard');
      setExplanation(result.explanation);
    } catch (error) {
      console.error('Error explaining concept:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <input 
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
        placeholder="Enter topic to explain"
      />
      <button onClick={handleExplain} disabled={loading}>
        {loading ? 'Explaining...' : 'Explain'}
      </button>
      {explanation && (
        <div>
          <h3>Explanation:</h3>
          <p>{explanation}</p>
        </div>
      )}
    </div>
  );
}
```

---

## Setup and Configuration

### Backend Setup

1. **Install Dependencies:**
```bash
pip install -r requirements.txt
```

2. **Configure Environment:**
```bash
# Copy environment template
cp .env.example .env

# Edit configuration
nano .env
```

3. **Set API Keys:**
```python
# Using the setup script
python set_api_key.py

# Or manually in environment
export OPENAI_API_KEY="your_key_here"
export ANTHROPIC_API_KEY="your_key_here"
```

4. **Initialize Database:**
```bash
# Create necessary directories
mkdir -p user_data docs rag_cache

# Process documents
python document_processor.py
```

### Frontend Setup

1. **Install Dependencies:**
```bash
cd frontend
npm install
```

2. **Configure Environment:**
```bash
# Create environment file
echo "REACT_APP_API_URL=http://localhost:8000" > .env
```

3. **Start Development Server:**
```bash
npm start
```

### API Server Configuration

The API server can be configured through environment variables:

```env
# Server settings
HOST=0.0.0.0
PORT=8000

# LLM Provider settings
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
DEFAULT_LLM_PROVIDER=openai

# Database settings
USER_DATA_DIR=user_data
DOCS_DIR=docs
RAG_CACHE_DIR=rag_cache

# Performance settings
MAX_CONCURRENT_SESSIONS=10
SESSION_TIMEOUT=3600
```

### Docker Setup

```dockerfile
# Dockerfile example
FROM python:3.9

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "api_server.py"]
```

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./user_data:/app/user_data
      - ./docs:/app/docs
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
```

---

## Error Handling

### Common Errors and Solutions

#### Backend Errors

1. **LLM Provider Unavailable:**
```python
# The system automatically falls back to available providers
# Check provider status
from llm_providers import llm_manager
available = llm_manager.get_available_providers()
```

2. **Document Processing Errors:**
```python
# Handle PDF processing errors
from document_processor import DocumentProcessor
try:
    processor = DocumentProcessor()
    chunks = processor.process_document(file_path)
except Exception as e:
    print(f"Processing error: {e}")
```

3. **Memory System Errors:**
```python
# Handle concurrent access
from memory import load_user, save_user
try:
    profile = load_user(username)
    # ... modify profile ...
    save_user(username, profile)
except Exception as e:
    print(f"Memory error: {e}")
```

#### Frontend Errors

1. **API Connection Errors:**
```javascript
// Handle API errors in service layer
import { api } from './services/api';

try {
  const result = await api.post('/endpoint', data);
} catch (error) {
  if (error.response?.status === 500) {
    // Handle server error
  } else if (error.response?.status === 404) {
    // Handle not found
  }
}
```

2. **Component State Errors:**
```javascript
// Safe state updates
const [data, setData] = useState(null);
const [loading, setLoading] = useState(false);
const [error, setError] = useState(null);

const fetchData = async () => {
  setLoading(true);
  setError(null);
  try {
    const result = await api.getData();
    setData(result);
  } catch (err) {
    setError(err.message);
  } finally {
    setLoading(false);
  }
};
```

---

This documentation provides comprehensive coverage of all public APIs, functions, and components in the AI Tutoring System. For additional support or specific use cases, please refer to the individual module documentation or contact the development team.