# Component Usage Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Backend Component Usage](#backend-component-usage)
3. [Frontend Component Usage](#frontend-component-usage)
4. [Integration Patterns](#integration-patterns)
5. [Best Practices](#best-practices)
6. [Common Use Cases](#common-use-cases)
7. [Performance Optimization](#performance-optimization)

---

## Getting Started

### Quick Start Example

```python
# Backend quick start
from memory import load_user, save_user
from planner import PlannerAgent
from domain_expert import explain_concept, generate_question
from llm_providers import llm_manager

# Set up user
username = "student123"
user_profile = load_user(username)
planner = PlannerAgent(username)

# Get concept explanation
explanation = explain_concept("machine learning", "standard")
print(f"Explanation: {explanation}")

# Generate a question
question, answer = generate_question("machine learning", "medium", "conceptual")
print(f"Question: {question}")
print(f"Expected Answer: {answer}")
```

```jsx
// Frontend quick start
import React, { useState } from 'react';
import { contentAPI } from './services/api';

function QuickStart() {
  const [topic, setTopic] = useState('');
  const [explanation, setExplanation] = useState('');

  const handleExplain = async () => {
    try {
      const result = await contentAPI.explainConcept(topic, 'standard');
      setExplanation(result.explanation);
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div>
      <input 
        value={topic}
        onChange={(e) => setTopic(e.target.value)}
        placeholder="Enter topic"
      />
      <button onClick={handleExplain}>Explain</button>
      {explanation && <div>{explanation}</div>}
    </div>
  );
}
```

---

## Backend Component Usage

### Memory Management

#### Basic User Operations

```python
from memory import load_user, save_user, get_weak_areas, get_performance_summary

# Load user profile
profile = load_user("john_doe")

# Check weak areas
weak_areas = get_weak_areas("john_doe")
print(f"Areas needing improvement: {weak_areas}")

# Get performance summary
summary = get_performance_summary("john_doe")
print(f"Topics studied: {summary['total_topics_studied']}")
print(f"Topics mastered: {summary['topics_mastered']}")
```

#### Recording Learning Sessions

```python
from memory import record_learning_session

# Record a completed session
record_learning_session(
    username="john_doe",
    topic="calculus",
    performance=0.85,  # 85% performance
    duration=25        # 25 minutes
)
```

### LLM Provider Management

#### Setting Up Multiple Providers

```python
from llm_providers import llm_manager, OpenAIProvider, AnthropicProvider

# Initialize providers
openai = OpenAIProvider(model="gpt-4")
anthropic = AnthropicProvider(model="claude-3-sonnet-20240229")

# Check available providers
available = llm_manager.get_available_providers()
print(f"Available providers: {available}")

# Set active provider
llm_manager.set_provider("openai")

# Generate with fallback
response = llm_manager.generate("Explain quantum computing")
```

#### Custom Provider Configuration

```python
from llm_providers import OpenAIProvider

# Configure with custom settings
provider = OpenAIProvider(
    model="gpt-4",
    api_key="your_api_key_here"
)

# Generate with specific parameters
response = provider.generate(
    prompt="Explain machine learning",
    temperature=0.3,
    max_tokens=1000
)
```

### Advanced RAG System

#### Basic Document Search

```python
from advanced_rag import AdvancedRAGSystem
from pathlib import Path

# Initialize RAG system
rag = AdvancedRAGSystem(
    docs_path=Path('docs'),
    embedding_model='all-MiniLM-L6-v2',
    chunk_size=512
)

# Search documents
results = rag.search("machine learning algorithms", max_results=5)

# Process results
for doc, score in results:
    print(f"Relevance: {score:.2f}")
    print(f"Source: {doc.source}")
    print(f"Content: {doc.text[:200]}...")
    print(f"Citation: {doc.get_citation()}")
    print("---")
```

#### Advanced Search with Filtering

```python
# Search with minimum score threshold
results = rag.search(
    query="neural networks",
    max_results=10,
    min_score=0.7,
    rerank=True
)

# Filter by source
ml_results = [
    (doc, score) for doc, score in results
    if 'machine_learning' in doc.source.lower()
]
```

### Domain Expert Functions

#### Concept Explanation

```python
from domain_expert import explain_concept, generate_example

# Basic explanation
explanation = explain_concept("derivatives", "standard")

# Advanced explanation with examples
advanced_explanation = explain_concept("quantum computing", "advanced")
example = generate_example("quantum computing", "practical")

print(f"Explanation: {explanation}")
print(f"Example: {example}")
```

#### Question Generation and Checking

```python
from domain_expert import generate_question, check_answer

# Generate question
question, expected_answer = generate_question(
    topic="calculus",
    difficulty="medium",
    question_type="conceptual"
)

# Check student answer
student_answer = "A derivative represents the rate of change"
is_correct, score, feedback = check_answer(
    question=question,
    student_answer=student_answer,
    expected_answer=expected_answer
)

print(f"Question: {question}")
print(f"Student Answer: {student_answer}")
print(f"Correct: {is_correct}, Score: {score:.2f}")
print(f"Feedback: {feedback}")
```

### Interactive Sessions

#### Starting and Managing Sessions

```python
from interactive_session import InteractiveSession, Command

# Start session
session = InteractiveSession("john_doe", "calculus")
welcome_message = session.start_session()

# Process user input
response, state = session.process_input("!explain derivatives")
print(f"Response: {response}")
print(f"Session state: {state}")

# Execute specific commands
help_response = session.execute_command(Command.HELP)
example_response = session.execute_command(Command.EXAMPLE)
```

#### Custom Session Handling

```python
# Custom session with specific configuration
session = InteractiveSession("john_doe", "machine learning")

# Set custom difficulty
session.execute_command(Command.DIFFICULTY, "hard")

# Process learning loop
while True:
    user_input = input("Enter command or question: ")
    if user_input.lower() == 'quit':
        break
    
    response, state = session.process_input(user_input)
    print(f"AI: {response}")
    
    # Check session progress
    if state.get('progress', 0) >= 0.8:
        print("Session completed successfully!")
        break
```

### Flashcard System

#### Creating and Managing Decks

```python
from flashcards import FlashcardDeck

# Create deck
deck = FlashcardDeck("john_doe", "calculus")

# Add cards
deck.add_card(
    front="What is a derivative?",
    back="The rate of change of a function with respect to its variable",
    subtopic="derivatives"
)

deck.add_card(
    front="What is the derivative of x²?",
    back="2x",
    subtopic="derivatives"
)

# Get due cards
due_cards = deck.get_due_cards()
print(f"Cards due for review: {len(due_cards)}")

# Study a card
if due_cards:
    card = due_cards[0]
    result = deck.study_card(card['id'], 'good')
    print(f"Next review: {result['next_review']}")
```

#### Spaced Repetition Study Session

```python
# Complete study session
deck = FlashcardDeck("john_doe", "calculus")
due_cards = deck.get_due_cards()

for card in due_cards:
    print(f"Question: {card['front']}")
    user_answer = input("Your answer: ")
    
    print(f"Correct answer: {card['back']}")
    performance = input("Rate your performance (again/hard/good/easy): ")
    
    result = deck.study_card(card['id'], performance)
    print(f"Card scheduled for next review: {result['next_review']}")
    print("---")

# Get statistics
stats = deck.get_statistics()
print(f"Session complete! Total cards studied: {stats['cards_studied']}")
```

### Enhanced Memory System

#### Getting Learning Insights

```python
from enhanced_memory import EnhancedMemorySystem

# Initialize system
memory = EnhancedMemorySystem("john_doe")

# Get comprehensive insights
insights = memory.get_insights()

# Access different insight types
learning_patterns = insights['learning_patterns']
personalization = insights['personalization']
recommendations = insights['personalized_recommendations']

print(f"Preferred learning style: {personalization['preferred_learning_style']}")
print(f"Optimal session length: {personalization['optimal_session_length']} minutes")
print(f"Best time of day: {personalization['best_time_of_day']}")

# Process recommendations
if 'spaced_repetition_schedule' in recommendations:
    schedule = recommendations['spaced_repetition_schedule']
    for item in schedule[:3]:  # Show top 3
        print(f"Review: {item['topic']} - {item['subtopic']}")
        print(f"Priority: {item['priority']}")
```

---

## Frontend Component Usage

### User Authentication

#### Login Component

```jsx
import React, { useState } from 'react';
import { useUser } from '../contexts/UserContext';

function CustomLogin() {
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useUser();

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(username);
    } catch (error) {
      console.error('Login failed:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleLogin}>
      <input
        type="text"
        value={username}
        onChange={(e) => setUsername(e.target.value)}
        placeholder="Enter username"
        required
      />
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
  );
}
```

### Dashboard Integration

#### Custom Dashboard Component

```jsx
import React, { useState, useEffect } from 'react';
import { userAPI, contentAPI } from '../services/api';
import { useUser } from '../contexts/UserContext';

function CustomDashboard() {
  const { user } = useUser();
  const [profile, setProfile] = useState(null);
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [profileData, insightsData] = await Promise.all([
          userAPI.getUserProfile(user.username),
          userAPI.getUserInsights(user.username)
        ]);
        setProfile(profileData);
        setInsights(insightsData);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    if (user) {
      fetchData();
    }
  }, [user]);

  if (loading) return <div>Loading...</div>;

  return (
    <div className="dashboard">
      <h1>Welcome, {user.username}!</h1>
      
      <div className="stats">
        <div className="stat">
          <h3>Weak Areas</h3>
          <p>{profile?.weak_areas?.length || 0}</p>
        </div>
        <div className="stat">
          <h3>Topics Mastered</h3>
          <p>{Object.keys(profile?.topic_mastery || {}).length}</p>
        </div>
      </div>

      <div className="recommendations">
        <h3>Personalized Recommendations</h3>
        {insights?.personalized_recommendations?.spaced_repetition_schedule?.slice(0, 3).map((item, index) => (
          <div key={index} className="recommendation">
            <h4>{item.topic}</h4>
            <p>{item.subtopic}</p>
            <span className={`priority ${item.priority}`}>{item.priority}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### Learning Interface

#### Interactive Learning Component

```jsx
import React, { useState } from 'react';
import { contentAPI } from '../services/api';

function InteractiveLearning() {
  const [topic, setTopic] = useState('');
  const [currentContent, setCurrentContent] = useState(null);
  const [mode, setMode] = useState('explanation');
  const [loading, setLoading] = useState(false);

  const handleExplain = async () => {
    setLoading(true);
    try {
      const result = await contentAPI.explainConcept(topic, 'standard');
      setCurrentContent(result);
      setMode('explanation');
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateQuestion = async () => {
    setLoading(true);
    try {
      const result = await contentAPI.generateQuestion(topic, 'medium', 'conceptual');
      setCurrentContent(result);
      setMode('question');
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateExample = async () => {
    setLoading(true);
    try {
      const result = await contentAPI.generateExample(topic, 'practical');
      setCurrentContent(result);
      setMode('example');
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="learning-interface">
      <div className="controls">
        <input
          type="text"
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          placeholder="Enter topic to study"
        />
        <div className="buttons">
          <button onClick={handleExplain} disabled={loading}>
            Explain
          </button>
          <button onClick={handleGenerateQuestion} disabled={loading}>
            Generate Question
          </button>
          <button onClick={handleGenerateExample} disabled={loading}>
            Show Example
          </button>
        </div>
      </div>

      {loading && <div className="loading">Loading...</div>}

      {currentContent && (
        <div className="content">
          {mode === 'explanation' && (
            <div className="explanation">
              <h3>Explanation</h3>
              <p>{currentContent.explanation}</p>
              {currentContent.citations && (
                <div className="citations">
                  <h4>Sources:</h4>
                  <ul>
                    {currentContent.citations.map((citation, index) => (
                      <li key={index}>{citation}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {mode === 'question' && (
            <div className="question">
              <h3>Practice Question</h3>
              <p>{currentContent.question}</p>
              <div className="question-meta">
                <span className="difficulty">{currentContent.difficulty}</span>
                <span className="type">{currentContent.question_type}</span>
              </div>
            </div>
          )}

          {mode === 'example' && (
            <div className="example">
              <h3>Example</h3>
              <p>{currentContent.example}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
```

### Chat Interface

#### AI Chat Component

```jsx
import React, { useState, useEffect, useRef } from 'react';
import { sessionAPI } from '../services/api';
import { useUser } from '../contexts/UserContext';

function AIChat() {
  const { user } = useUser();
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    // Start chat session
    const startSession = async () => {
      try {
        const session = await sessionAPI.startSession(user.username, 'general', 'learning');
        setSessionId(session.session_id);
        setMessages([{ type: 'ai', content: session.initial_content }]);
      } catch (error) {
        console.error('Error starting session:', error);
      }
    };

    startSession();
  }, [user]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !sessionId) return;

    const userMessage = { type: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await sessionAPI.sendCommand(sessionId, 'chat', input);
      const aiMessage = { type: 'ai', content: response.response };
      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = { type: 'ai', content: 'Sorry, I encountered an error. Please try again.' };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-interface">
      <div className="messages">
        {messages.map((message, index) => (
          <div key={index} className={`message ${message.type}`}>
            <div className="content">{message.content}</div>
          </div>
        ))}
        {loading && <div className="message ai loading">AI is typing...</div>}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-area">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSend()}
          placeholder="Ask me anything..."
        />
        <button onClick={handleSend} disabled={loading}>
          Send
        </button>
      </div>
    </div>
  );
}
```

### Flashcard Review

#### Flashcard Study Component

```jsx
import React, { useState, useEffect } from 'react';
import { flashcardAPI } from '../services/api';
import { useUser } from '../contexts/UserContext';

function FlashcardReview({ topic }) {
  const { user } = useUser();
  const [deck, setDeck] = useState(null);
  const [currentCard, setCurrentCard] = useState(null);
  const [showAnswer, setShowAnswer] = useState(false);
  const [sessionStats, setSessionStats] = useState({ correct: 0, total: 0 });

  useEffect(() => {
    const loadDeck = async () => {
      try {
        const deckData = await flashcardAPI.getFlashcards(user.username, topic);
        setDeck(deckData);
        const dueCards = deckData.cards.filter(card => new Date(card.next_review) <= new Date());
        if (dueCards.length > 0) {
          setCurrentCard(dueCards[0]);
        }
      } catch (error) {
        console.error('Error loading deck:', error);
      }
    };

    loadDeck();
  }, [user, topic]);

  const handlePerformance = async (performance) => {
    if (!currentCard) return;

    try {
      await flashcardAPI.studyCard(user.username, topic, currentCard.id, performance);
      
      // Update session stats
      const isCorrect = performance === 'good' || performance === 'easy';
      setSessionStats(prev => ({
        correct: prev.correct + (isCorrect ? 1 : 0),
        total: prev.total + 1
      }));

      // Move to next card
      const remainingCards = deck.cards.filter(card => 
        card.id !== currentCard.id && new Date(card.next_review) <= new Date()
      );
      
      if (remainingCards.length > 0) {
        setCurrentCard(remainingCards[0]);
        setShowAnswer(false);
      } else {
        setCurrentCard(null);
        alert('Review session completed!');
      }
    } catch (error) {
      console.error('Error studying card:', error);
    }
  };

  if (!deck) return <div>Loading deck...</div>;
  if (!currentCard) return <div>No cards due for review!</div>;

  return (
    <div className="flashcard-review">
      <div className="stats">
        <span>Topic: {topic}</span>
        <span>Progress: {sessionStats.total} cards studied</span>
        <span>Accuracy: {sessionStats.total > 0 ? (sessionStats.correct / sessionStats.total * 100).toFixed(1) : 0}%</span>
      </div>

      <div className="card">
        <div className="front">
          <h3>Question</h3>
          <p>{currentCard.front}</p>
        </div>
        
        {showAnswer && (
          <div className="back">
            <h3>Answer</h3>
            <p>{currentCard.back}</p>
          </div>
        )}
      </div>

      <div className="controls">
        {!showAnswer ? (
          <button onClick={() => setShowAnswer(true)}>Show Answer</button>
        ) : (
          <div className="performance-buttons">
            <button onClick={() => handlePerformance('again')} className="again">
              Again
            </button>
            <button onClick={() => handlePerformance('hard')} className="hard">
              Hard
            </button>
            <button onClick={() => handlePerformance('good')} className="good">
              Good
            </button>
            <button onClick={() => handlePerformance('easy')} className="easy">
              Easy
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
```

---

## Integration Patterns

### Backend-Frontend Integration

#### API Service Layer Pattern

```javascript
// services/api.js
class APIService {
  constructor() {
    this.baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    };

    try {
      const response = await fetch(url, config);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // User management
  async createUser(username) {
    return this.request('/api/users/create', {
      method: 'POST',
      body: JSON.stringify({ username })
    });
  }

  async getUserProfile(username) {
    return this.request(`/api/users/${username}/profile`);
  }

  // Learning content
  async explainConcept(topic, detailLevel = 'standard') {
    return this.request('/api/content/explain', {
      method: 'POST',
      body: JSON.stringify({ topic, detail_level: detailLevel })
    });
  }

  async generateQuestion(topic, difficulty = 'medium', questionType = 'conceptual') {
    return this.request('/api/content/question', {
      method: 'POST',
      body: JSON.stringify({ 
        topic, 
        difficulty, 
        question_type: questionType 
      })
    });
  }
}

export const apiService = new APIService();
```

#### React Context Integration

```jsx
// contexts/LearningContext.js
import React, { createContext, useContext, useState, useEffect } from 'react';
import { apiService } from '../services/api';
import { useUser } from './UserContext';

const LearningContext = createContext();

export const LearningProvider = ({ children }) => {
  const { user } = useUser();
  const [currentTopic, setCurrentTopic] = useState('');
  const [learningHistory, setLearningHistory] = useState([]);
  const [insights, setInsights] = useState(null);

  useEffect(() => {
    if (user) {
      loadUserInsights();
    }
  }, [user]);

  const loadUserInsights = async () => {
    try {
      const data = await apiService.getUserInsights(user.username);
      setInsights(data);
    } catch (error) {
      console.error('Error loading insights:', error);
    }
  };

  const explainConcept = async (topic, detailLevel = 'standard') => {
    try {
      const result = await apiService.explainConcept(topic, detailLevel);
      
      // Update learning history
      setLearningHistory(prev => [...prev, {
        type: 'explanation',
        topic,
        timestamp: new Date().toISOString(),
        content: result.explanation
      }]);

      return result;
    } catch (error) {
      console.error('Error explaining concept:', error);
      throw error;
    }
  };

  const generateQuestion = async (topic, difficulty, questionType) => {
    try {
      const result = await apiService.generateQuestion(topic, difficulty, questionType);
      
      // Update learning history
      setLearningHistory(prev => [...prev, {
        type: 'question',
        topic,
        timestamp: new Date().toISOString(),
        content: result.question
      }]);

      return result;
    } catch (error) {
      console.error('Error generating question:', error);
      throw error;
    }
  };

  const value = {
    currentTopic,
    setCurrentTopic,
    learningHistory,
    insights,
    explainConcept,
    generateQuestion,
    refreshInsights: loadUserInsights
  };

  return (
    <LearningContext.Provider value={value}>
      {children}
    </LearningContext.Provider>
  );
};

export const useLearning = () => {
  const context = useContext(LearningContext);
  if (!context) {
    throw new Error('useLearning must be used within a LearningProvider');
  }
  return context;
};
```

### Full-Stack Component Integration

#### Complete Learning Dashboard

```jsx
import React, { useState, useEffect } from 'react';
import { useLearning } from '../contexts/LearningContext';
import { useUser } from '../contexts/UserContext';

function CompleteLearningDashboard() {
  const { user } = useUser();
  const { 
    currentTopic, 
    setCurrentTopic, 
    learningHistory, 
    insights, 
    explainConcept, 
    generateQuestion 
  } = useLearning();
  
  const [currentContent, setCurrentContent] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [userAnswer, setUserAnswer] = useState('');
  const [loading, setLoading] = useState(false);

  const handleExplain = async () => {
    if (!currentTopic) return;
    
    setLoading(true);
    try {
      const result = await explainConcept(currentTopic);
      setCurrentContent(result);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateQuestion = async () => {
    if (!currentTopic) return;
    
    setLoading(true);
    try {
      const result = await generateQuestion(currentTopic, 'medium', 'conceptual');
      setCurrentQuestion(result);
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitAnswer = async () => {
    if (!currentQuestion || !userAnswer.trim()) return;
    
    try {
      const result = await apiService.checkAnswer(
        currentQuestion.question,
        userAnswer,
        user.username
      );
      
      alert(`Score: ${result.score}, Feedback: ${result.feedback}`);
      setUserAnswer('');
      setCurrentQuestion(null);
    } catch (error) {
      console.error('Error checking answer:', error);
    }
  };

  return (
    <div className="complete-learning-dashboard">
      <header>
        <h1>Learning Dashboard</h1>
        <p>Welcome, {user.username}!</p>
      </header>

      <div className="topic-selector">
        <input
          type="text"
          value={currentTopic}
          onChange={(e) => setCurrentTopic(e.target.value)}
          placeholder="Enter topic to study"
        />
        <button onClick={handleExplain} disabled={loading}>
          Explain
        </button>
        <button onClick={handleGenerateQuestion} disabled={loading}>
          Generate Question
        </button>
      </div>

      {currentContent && (
        <div className="content-section">
          <h2>Explanation</h2>
          <p>{currentContent.explanation}</p>
          {currentContent.citations && (
            <div className="citations">
              <h3>Sources:</h3>
              <ul>
                {currentContent.citations.map((citation, index) => (
                  <li key={index}>{citation}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      {currentQuestion && (
        <div className="question-section">
          <h2>Practice Question</h2>
          <p>{currentQuestion.question}</p>
          <textarea
            value={userAnswer}
            onChange={(e) => setUserAnswer(e.target.value)}
            placeholder="Enter your answer..."
            rows="4"
          />
          <button onClick={handleSubmitAnswer}>Submit Answer</button>
        </div>
      )}

      <div className="history-section">
        <h2>Learning History</h2>
        <div className="history-items">
          {learningHistory.slice(-5).map((item, index) => (
            <div key={index} className="history-item">
              <span className="type">{item.type}</span>
              <span className="topic">{item.topic}</span>
              <span className="timestamp">{new Date(item.timestamp).toLocaleString()}</span>
            </div>
          ))}
        </div>
      </div>

      {insights && (
        <div className="insights-section">
          <h2>Learning Insights</h2>
          <div className="insights-grid">
            <div className="insight">
              <h3>Preferred Learning Style</h3>
              <p>{insights.personalization.preferred_learning_style}</p>
            </div>
            <div className="insight">
              <h3>Optimal Session Length</h3>
              <p>{insights.personalization.optimal_session_length} minutes</p>
            </div>
            <div className="insight">
              <h3>Best Time of Day</h3>
              <p>{insights.personalization.best_time_of_day}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
```

---

## Best Practices

### Backend Best Practices

#### Error Handling

```python
import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_operation(func):
    """Decorator for safe operation execution with error handling."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            return None
    return wrapper

@safe_operation
def get_user_data(username: str) -> Optional[dict]:
    """Safely retrieve user data."""
    from memory import load_user
    return load_user(username)
```

#### Performance Optimization

```python
import functools
import time

def cache_with_expiry(expiry_seconds=300):
    """Cache function results with expiry."""
    def decorator(func):
        cache = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = str(args) + str(sorted(kwargs.items()))
            now = time.time()
            
            if key in cache:
                result, timestamp = cache[key]
                if now - timestamp < expiry_seconds:
                    return result
            
            result = func(*args, **kwargs)
            cache[key] = (result, now)
            return result
        
        return wrapper
    return decorator

@cache_with_expiry(600)  # Cache for 10 minutes
def get_concept_explanation(topic: str) -> str:
    """Get cached concept explanation."""
    from domain_expert import explain_concept
    return explain_concept(topic)
```

### Frontend Best Practices

#### Error Boundaries

```jsx
import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h2>Something went wrong.</h2>
          <details>
            <summary>Error details</summary>
            <pre>{this.state.error?.toString()}</pre>
          </details>
          <button onClick={() => window.location.reload()}>
            Reload Page
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

// Usage
function App() {
  return (
    <ErrorBoundary>
      <YourComponents />
    </ErrorBoundary>
  );
}
```

#### Custom Hooks for API Calls

```jsx
import { useState, useEffect, useCallback } from 'react';

function useAPI(apiCall, dependencies = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const execute = useCallback(async (...args) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiCall(...args);
      setData(result);
      return result;
    } catch (err) {
      setError(err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, dependencies);

  useEffect(() => {
    execute();
  }, [execute]);

  return { data, loading, error, execute };
}

// Usage
function ConceptExplainer() {
  const { data, loading, error, execute } = useAPI(
    (topic) => apiService.explainConcept(topic),
    []
  );

  const handleExplain = (topic) => {
    execute(topic);
  };

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error.message}</div>;

  return (
    <div>
      <button onClick={() => handleExplain('machine learning')}>
        Explain Machine Learning
      </button>
      {data && <p>{data.explanation}</p>}
    </div>
  );
}
```

---

## Common Use Cases

### 1. Personalized Learning Path

```python
# Backend: Create personalized learning path
from planner import PlannerAgent
from enhanced_memory import EnhancedMemorySystem

def create_personalized_path(username: str, target_topic: str):
    planner = PlannerAgent(username)
    memory = EnhancedMemorySystem(username)
    
    # Get user insights
    insights = memory.get_insights()
    weak_areas = insights.get('weak_areas', [])
    
    # Create adaptive plan
    plan = planner.create_learning_plan(target_topic, "intermediate")
    
    # Adjust for weak areas
    if weak_areas:
        plan['prerequisite_review'] = weak_areas
    
    return plan
```

```jsx
// Frontend: Display personalized learning path
function PersonalizedLearningPath() {
  const { user } = useUser();
  const [learningPath, setLearningPath] = useState(null);

  useEffect(() => {
    const fetchPath = async () => {
      try {
        const path = await apiService.createPersonalizedPath(user.username, 'machine learning');
        setLearningPath(path);
      } catch (error) {
        console.error('Error creating path:', error);
      }
    };

    fetchPath();
  }, [user]);

  return (
    <div className="learning-path">
      <h2>Your Personalized Learning Path</h2>
      {learningPath && (
        <div>
          <h3>Prerequisites to Review:</h3>
          <ul>
            {learningPath.prerequisite_review?.map((topic, index) => (
              <li key={index}>{topic}</li>
            ))}
          </ul>
          
          <h3>Learning Modules:</h3>
          <div className="modules">
            {learningPath.modules?.map((module, index) => (
              <div key={index} className="module">
                <h4>{module.title}</h4>
                <p>{module.description}</p>
                <span className="duration">{module.estimated_duration}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

### 2. Adaptive Assessment System

```python
# Backend: Adaptive assessment
from domain_expert import generate_question, check_answer
from memory import load_user, save_user

def adaptive_assessment(username: str, topic: str, max_questions: int = 10):
    user_profile = load_user(username)
    current_performance = user_profile.get('topic_mastery', {}).get(topic, 0.5)
    
    questions = []
    difficulty = "easy" if current_performance < 0.3 else "medium" if current_performance < 0.7 else "hard"
    
    for i in range(max_questions):
        question, expected_answer = generate_question(
            topic=topic,
            difficulty=difficulty,
            question_type="conceptual",
            previous_questions=[q['question'] for q in questions]
        )
        
        questions.append({
            'question': question,
            'expected_answer': expected_answer,
            'difficulty': difficulty
        })
    
    return questions

def evaluate_assessment(username: str, topic: str, answers: list):
    results = []
    total_score = 0
    
    for answer_data in answers:
        is_correct, score, feedback = check_answer(
            question=answer_data['question'],
            student_answer=answer_data['student_answer'],
            expected_answer=answer_data['expected_answer']
        )
        
        results.append({
            'question': answer_data['question'],
            'is_correct': is_correct,
            'score': score,
            'feedback': feedback
        })
        
        total_score += score
    
    # Update user mastery
    avg_score = total_score / len(answers)
    user_profile = load_user(username)
    user_profile['topic_mastery'][topic] = avg_score
    save_user(username, user_profile)
    
    return {
        'results': results,
        'total_score': total_score,
        'average_score': avg_score,
        'mastery_level': avg_score
    }
```

```jsx
// Frontend: Adaptive assessment interface
function AdaptiveAssessment({ topic }) {
  const { user } = useUser();
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState([]);
  const [currentAnswer, setCurrentAnswer] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const startAssessment = async () => {
      setLoading(true);
      try {
        const assessmentQuestions = await apiService.getAdaptiveAssessment(user.username, topic);
        setQuestions(assessmentQuestions);
      } catch (error) {
        console.error('Error starting assessment:', error);
      } finally {
        setLoading(false);
      }
    };

    startAssessment();
  }, [user, topic]);

  const handleAnswerSubmit = () => {
    const newAnswer = {
      question: questions[currentQuestionIndex].question,
      student_answer: currentAnswer,
      expected_answer: questions[currentQuestionIndex].expected_answer
    };

    setAnswers([...answers, newAnswer]);
    setCurrentAnswer('');

    if (currentQuestionIndex < questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    } else {
      finishAssessment([...answers, newAnswer]);
    }
  };

  const finishAssessment = async (allAnswers) => {
    setLoading(true);
    try {
      const assessmentResults = await apiService.evaluateAssessment(
        user.username,
        topic,
        allAnswers
      );
      setResults(assessmentResults);
    } catch (error) {
      console.error('Error evaluating assessment:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;

  if (results) {
    return (
      <div className="assessment-results">
        <h2>Assessment Results</h2>
        <div className="overall-score">
          <h3>Overall Score: {(results.average_score * 100).toFixed(1)}%</h3>
          <div className="mastery-level">
            Mastery Level: {(results.mastery_level * 100).toFixed(1)}%
          </div>
        </div>
        
        <div className="question-results">
          {results.results.map((result, index) => (
            <div key={index} className={`result-item ${result.is_correct ? 'correct' : 'incorrect'}`}>
              <h4>Question {index + 1}</h4>
              <p className="question">{result.question}</p>
              <p className="feedback">{result.feedback}</p>
              <div className="score">Score: {(result.score * 100).toFixed(1)}%</div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (questions.length === 0) return <div>No questions available.</div>;

  const currentQuestion = questions[currentQuestionIndex];

  return (
    <div className="adaptive-assessment">
      <div className="progress">
        Question {currentQuestionIndex + 1} of {questions.length}
      </div>
      
      <div className="question-container">
        <h3>{currentQuestion.question}</h3>
        <div className="difficulty-indicator">
          Difficulty: {currentQuestion.difficulty}
        </div>
        
        <textarea
          value={currentAnswer}
          onChange={(e) => setCurrentAnswer(e.target.value)}
          placeholder="Enter your answer here..."
          rows="4"
        />
        
        <button 
          onClick={handleAnswerSubmit}
          disabled={!currentAnswer.trim()}
        >
          {currentQuestionIndex === questions.length - 1 ? 'Finish Assessment' : 'Next Question'}
        </button>
      </div>
    </div>
  );
}
```

### 3. Intelligent Document Search

```python
# Backend: Enhanced document search
from advanced_rag import AdvancedRAGSystem
from domain_expert import query_domain_expert

def intelligent_search(query: str, user_context: dict = None):
    rag = AdvancedRAGSystem(Path('docs'))
    
    # Get initial search results
    results = rag.search(query, max_results=10, rerank=True)
    
    # Enhance with user context
    if user_context:
        weak_areas = user_context.get('weak_areas', [])
        if weak_areas:
            # Boost results related to weak areas
            context_query = f"{query} focusing on {', '.join(weak_areas)}"
            context_results = rag.search(context_query, max_results=5)
            results = context_results + results
    
    # Generate contextualized summary
    if results:
        context_text = '\n\n'.join([doc.text for doc, _ in results[:3]])
        citations = [doc.get_citation() for doc, _ in results[:3]]
        
        summary = query_domain_expert(
            prompt=f"Based on this context, provide a comprehensive answer to: {query}",
            context=context_text,
            citations=citations
        )
        
        return {
            'summary': summary,
            'results': results,
            'citations': citations
        }
    
    return {'summary': 'No relevant documents found.', 'results': [], 'citations': []}
```

```jsx
// Frontend: Intelligent search interface
function IntelligentSearch() {
  const { user } = useUser();
  const [query, setQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    try {
      const userProfile = await apiService.getUserProfile(user.username);
      const results = await apiService.intelligentSearch(query, {
        weak_areas: userProfile.weak_areas
      });
      setSearchResults(results);
    } catch (error) {
      console.error('Error searching:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="intelligent-search">
      <div className="search-input">
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          placeholder="Search documents intelligently..."
        />
        <button onClick={handleSearch} disabled={loading}>
          {loading ? 'Searching...' : 'Search'}
        </button>
      </div>

      {searchResults && (
        <div className="search-results">
          <div className="summary">
            <h3>AI Summary</h3>
            <p>{searchResults.summary}</p>
            
            {searchResults.citations.length > 0 && (
              <div className="citations">
                <h4>Sources:</h4>
                <ul>
                  {searchResults.citations.map((citation, index) => (
                    <li key={index}>{citation}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          <div className="document-results">
            <h3>Related Documents</h3>
            {searchResults.results.map((result, index) => (
              <div key={index} className="result-item">
                <div className="score">Relevance: {(result.score * 100).toFixed(1)}%</div>
                <h4>{result.document.source}</h4>
                <p>{result.document.text.substring(0, 200)}...</p>
                <div className="citation">{result.document.get_citation()}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
```

---

## Performance Optimization

### Backend Optimization

#### Caching Strategy

```python
from functools import lru_cache
import redis
import json

# Redis cache setup
redis_client = redis.Redis(host='localhost', port=6379, db=0)

class CacheManager:
    def __init__(self):
        self.redis_client = redis_client
        
    def get(self, key: str):
        """Get cached value."""
        try:
            value = self.redis_client.get(key)
            return json.loads(value) if value else None
        except:
            return None
    
    def set(self, key: str, value, expiry: int = 3600):
        """Set cached value with expiry."""
        try:
            self.redis_client.setex(key, expiry, json.dumps(value))
        except:
            pass
    
    def delete(self, key: str):
        """Delete cached value."""
        try:
            self.redis_client.delete(key)
        except:
            pass

cache_manager = CacheManager()

# Cached explanation function
def cached_explain_concept(topic: str, detail_level: str = "standard"):
    cache_key = f"explanation:{topic}:{detail_level}"
    cached_result = cache_manager.get(cache_key)
    
    if cached_result:
        return cached_result
    
    from domain_expert import explain_concept
    result = explain_concept(topic, detail_level)
    
    cache_manager.set(cache_key, result, expiry=3600)  # Cache for 1 hour
    return result
```

#### Database Optimization

```python
import sqlite3
from contextlib import contextmanager

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    @contextmanager
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def init_database(self):
        with self.get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    performance REAL NOT NULL,
                    duration INTEGER NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_user_topic 
                ON user_sessions(username, topic)
            ''')
            
            conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_timestamp 
                ON user_sessions(timestamp)
            ''')
    
    def record_session(self, username: str, topic: str, performance: float, duration: int):
        with self.get_connection() as conn:
            conn.execute('''
                INSERT INTO user_sessions (username, topic, performance, duration)
                VALUES (?, ?, ?, ?)
            ''', (username, topic, performance, duration))
            conn.commit()
    
    def get_user_performance(self, username: str, topic: str = None, limit: int = 100):
        with self.get_connection() as conn:
            if topic:
                cursor = conn.execute('''
                    SELECT * FROM user_sessions 
                    WHERE username = ? AND topic = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (username, topic, limit))
            else:
                cursor = conn.execute('''
                    SELECT * FROM user_sessions 
                    WHERE username = ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                ''', (username, limit))
            
            return cursor.fetchall()
```

### Frontend Optimization

#### Component Memoization

```jsx
import React, { memo, useMemo, useCallback } from 'react';

const OptimizedComponent = memo(({ data, onUpdate }) => {
  const processedData = useMemo(() => {
    return data.map(item => ({
      ...item,
      processed: true,
      timestamp: new Date(item.timestamp).toLocaleString()
    }));
  }, [data]);

  const handleUpdate = useCallback((id) => {
    onUpdate(id);
  }, [onUpdate]);

  return (
    <div>
      {processedData.map(item => (
        <div key={item.id} onClick={() => handleUpdate(item.id)}>
          {item.content}
        </div>
      ))}
    </div>
  );
});

// Usage with proper memoization
function ParentComponent() {
  const [data, setData] = useState([]);
  
  const handleUpdate = useCallback((id) => {
    setData(prev => prev.map(item => 
      item.id === id ? { ...item, updated: true } : item
    ));
  }, []);

  return (
    <OptimizedComponent 
      data={data} 
      onUpdate={handleUpdate}
    />
  );
}
```

#### Virtual Scrolling for Large Lists

```jsx
import React, { useState, useEffect, useMemo } from 'react';

function VirtualizedList({ items, itemHeight = 50, containerHeight = 400 }) {
  const [scrollTop, setScrollTop] = useState(0);

  const visibleItems = useMemo(() => {
    const startIndex = Math.floor(scrollTop / itemHeight);
    const endIndex = Math.min(
      startIndex + Math.ceil(containerHeight / itemHeight) + 1,
      items.length
    );

    return items.slice(startIndex, endIndex).map((item, index) => ({
      ...item,
      index: startIndex + index
    }));
  }, [items, itemHeight, containerHeight, scrollTop]);

  const totalHeight = items.length * itemHeight;
  const offsetY = Math.floor(scrollTop / itemHeight) * itemHeight;

  return (
    <div 
      style={{ height: containerHeight, overflow: 'auto' }}
      onScroll={(e) => setScrollTop(e.target.scrollTop)}
    >
      <div style={{ height: totalHeight, position: 'relative' }}>
        <div style={{ transform: `translateY(${offsetY}px)` }}>
          {visibleItems.map(item => (
            <div 
              key={item.id}
              style={{ height: itemHeight }}
            >
              {item.content}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
```

#### Lazy Loading Components

```jsx
import React, { lazy, Suspense } from 'react';

// Lazy load heavy components
const HeavyDashboard = lazy(() => import('./HeavyDashboard'));
const ComplexChart = lazy(() => import('./ComplexChart'));

function App() {
  return (
    <div>
      <Suspense fallback={<div>Loading dashboard...</div>}>
        <HeavyDashboard />
      </Suspense>
      
      <Suspense fallback={<div>Loading charts...</div>}>
        <ComplexChart />
      </Suspense>
    </div>
  );
}
```

---

This comprehensive component usage guide provides detailed examples, integration patterns, and best practices for effectively using all components in the AI Tutoring System. The examples demonstrate real-world usage patterns and optimization techniques for both backend and frontend development.