# Development Guide

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Project Structure](#project-structure)
3. [Development Workflow](#development-workflow)
4. [Testing Framework](#testing-framework)
5. [Debugging Guide](#debugging-guide)
6. [Code Quality Standards](#code-quality-standards)
7. [Deployment Procedures](#deployment-procedures)
8. [Contributing Guidelines](#contributing-guidelines)
9. [Troubleshooting](#troubleshooting)

---

## Development Environment Setup

### Prerequisites

- Python 3.8+
- Node.js 16+
- Git
- Docker (optional)
- Redis (optional, for caching)

### Backend Setup

```bash
# Clone the repository
git clone <repository-url>
cd ai-tutoring-system

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize directories
mkdir -p user_data docs rag_cache

# Set up API keys
python set_api_key.py
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set up environment variables
echo "REACT_APP_API_URL=http://localhost:8000" > .env

# Start development server
npm start
```

### Development Tools

#### IDE Configuration (VSCode)

```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"],
  "eslint.workingDirectories": ["frontend"]
}
```

#### Useful Extensions

- Python
- Pylance
- Black Formatter
- ESLint
- Prettier
- GitLens
- Thunder Client (for API testing)

### Database Setup

```python
# scripts/setup_database.py
import sqlite3
from pathlib import Path

def setup_database():
    """Set up development database."""
    db_path = Path('data/tutoring.db')
    db_path.parent.mkdir(exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    
    # Create tables
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_active DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            topic TEXT NOT NULL,
            performance REAL,
            duration INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database setup complete!")

if __name__ == "__main__":
    setup_database()
```

---

## Project Structure

```
ai-tutoring-system/
├── backend/
│   ├── api_server.py          # FastAPI server
│   ├── main.py                # CLI entry point
│   ├── memory.py              # User memory management
│   ├── planner.py             # Learning planner
│   ├── domain_expert.py       # Domain expert system
│   ├── interactive_session.py # Interactive sessions
│   ├── enhanced_memory.py     # Enhanced memory system
│   ├── advanced_rag.py        # Advanced RAG system
│   ├── llm_providers.py       # LLM provider management
│   ├── document_processor.py  # Document processing
│   ├── flashcards.py          # Flashcard system
│   ├── utils.py               # Utility functions
│   └── tests/                 # Backend tests
│       ├── test_memory.py
│       ├── test_planner.py
│       ├── test_domain_expert.py
│       └── test_api.py
├── frontend/
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/            # Page components
│   │   ├── contexts/         # React contexts
│   │   ├── services/         # API services
│   │   ├── utils/            # Utility functions
│   │   └── styles/           # CSS/styling
│   ├── public/               # Public assets
│   └── tests/                # Frontend tests
├── docs/                     # Documentation
├── user_data/               # User data storage
├── rag_cache/               # RAG system cache
├── crawl4ai/                # Web crawling
├── scrapping/               # Web scraping
├── eval/                    # Evaluation scripts
├── scripts/                 # Development scripts
├── requirements.txt         # Python dependencies
├── package.json            # Node.js dependencies
├── .env.example            # Environment template
├── .gitignore             # Git ignore rules
└── README.md              # Project documentation
```

---

## Development Workflow

### Git Workflow

```bash
# Feature development workflow
git checkout -b feature/new-feature
git add .
git commit -m "feat: add new feature"
git push origin feature/new-feature

# Create pull request
# After review and approval, merge to main
```

### Commit Message Convention

```
feat: add new feature
fix: resolve bug in component
docs: update documentation
style: format code
refactor: restructure code
test: add test cases
chore: update dependencies
```

### Branch Strategy

- `main`: Production-ready code
- `develop`: Integration branch for features
- `feature/*`: Feature development branches
- `hotfix/*`: Emergency fixes
- `release/*`: Release preparation

### Development Scripts

```bash
# scripts/dev.sh
#!/bin/bash
# Start development environment

# Start backend
python api_server.py &
BACKEND_PID=$!

# Start frontend
cd frontend
npm start &
FRONTEND_PID=$!

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
```

```bash
# scripts/test.sh
#!/bin/bash
# Run all tests

echo "Running backend tests..."
python -m pytest tests/ -v

echo "Running frontend tests..."
cd frontend
npm test --coverage

echo "Running integration tests..."
python -m pytest integration_tests/ -v
```

---

## Testing Framework

### Backend Testing

#### Unit Tests

```python
# tests/test_memory.py
import pytest
import tempfile
import os
from pathlib import Path
from memory import load_user, save_user, get_weak_areas

@pytest.fixture
def temp_user_dir():
    """Create temporary user data directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        original_dir = os.environ.get('USER_DATA_DIR', 'user_data')
        os.environ['USER_DATA_DIR'] = tmpdir
        yield tmpdir
        os.environ['USER_DATA_DIR'] = original_dir

def test_load_new_user(temp_user_dir):
    """Test loading a new user creates default profile."""
    username = "test_user"
    profile = load_user(username)
    
    assert profile['weak_areas'] == []
    assert profile['topic_mastery'] == {}
    assert profile['history'] == []
    assert 'last_active' in profile

def test_save_and_load_user(temp_user_dir):
    """Test saving and loading user data."""
    username = "test_user"
    profile = load_user(username)
    
    # Modify profile
    profile['weak_areas'] = ['calculus', 'statistics']
    profile['topic_mastery'] = {'algebra': 0.8}
    
    save_user(username, profile)
    
    # Load again and verify
    loaded_profile = load_user(username)
    assert loaded_profile['weak_areas'] == ['calculus', 'statistics']
    assert loaded_profile['topic_mastery'] == {'algebra': 0.8}

def test_get_weak_areas(temp_user_dir):
    """Test getting weak areas for a user."""
    username = "test_user"
    profile = load_user(username)
    profile['weak_areas'] = ['calculus', 'physics']
    save_user(username, profile)
    
    weak_areas = get_weak_areas(username)
    assert weak_areas == ['calculus', 'physics']

# Mock tests for external dependencies
@pytest.fixture
def mock_llm_provider():
    """Mock LLM provider for testing."""
    class MockLLMProvider:
        def generate(self, prompt, **kwargs):
            return f"Mock response for: {prompt}"
        
        def is_available(self):
            return True
        
        def get_info(self):
            return {"name": "mock", "model": "mock-model"}
    
    return MockLLMProvider()

def test_domain_expert_with_mock(mock_llm_provider):
    """Test domain expert with mocked LLM."""
    from domain_expert import explain_concept
    
    # Mock the LLM provider
    import domain_expert
    domain_expert.llm_manager.active_provider = mock_llm_provider
    
    explanation = explain_concept("test topic")
    assert "Mock response" in explanation
```

#### Integration Tests

```python
# tests/test_api_integration.py
import pytest
from fastapi.testclient import TestClient
from api_server import app

client = TestClient(app)

def test_create_user():
    """Test user creation endpoint."""
    response = client.post(
        "/api/users/create",
        json={"username": "test_user"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "test_user"
    assert "profile" in data

def test_explain_concept():
    """Test concept explanation endpoint."""
    response = client.post(
        "/api/content/explain",
        json={"topic": "machine learning", "detail_level": "standard"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "explanation" in data

def test_generate_question():
    """Test question generation endpoint."""
    response = client.post(
        "/api/content/question",
        json={
            "topic": "calculus",
            "difficulty": "medium",
            "question_type": "conceptual"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "question" in data
    assert "difficulty" in data
    assert data["difficulty"] == "medium"
```

#### Performance Tests

```python
# tests/test_performance.py
import pytest
import time
from concurrent.futures import ThreadPoolExecutor
from memory import load_user, save_user

def test_concurrent_user_access():
    """Test concurrent access to user data."""
    username = "test_user"
    
    def worker(worker_id):
        profile = load_user(username)
        profile['worker_id'] = worker_id
        save_user(username, profile)
        return profile
    
    # Run concurrent workers
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(worker, i) for i in range(10)]
        results = [future.result() for future in futures]
    
    # Verify no corruption
    assert len(results) == 10
    final_profile = load_user(username)
    assert 'worker_id' in final_profile

def test_response_time():
    """Test API response time."""
    from api_server import app
    from fastapi.testclient import TestClient
    
    client = TestClient(app)
    
    start_time = time.time()
    response = client.post(
        "/api/content/explain",
        json={"topic": "test", "detail_level": "standard"}
    )
    end_time = time.time()
    
    assert response.status_code == 200
    assert end_time - start_time < 5.0  # Should respond within 5 seconds
```

### Frontend Testing

#### Component Tests

```jsx
// frontend/src/components/__tests__/LoginForm.test.js
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { UserProvider } from '../../contexts/UserContext';
import LoginForm from '../LoginForm';

const MockUserProvider = ({ children }) => (
  <UserProvider>
    {children}
  </UserProvider>
);

describe('LoginForm', () => {
  test('renders login form', () => {
    render(
      <MockUserProvider>
        <LoginForm />
      </MockUserProvider>
    );
    
    expect(screen.getByPlaceholderText('Enter username')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  test('handles form submission', async () => {
    const mockLogin = jest.fn();
    
    render(
      <MockUserProvider>
        <LoginForm onLogin={mockLogin} />
      </MockUserProvider>
    );
    
    const usernameInput = screen.getByPlaceholderText('Enter username');
    const loginButton = screen.getByRole('button', { name: /login/i });
    
    fireEvent.change(usernameInput, { target: { value: 'testuser' } });
    fireEvent.click(loginButton);
    
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith('testuser');
    });
  });

  test('shows loading state', () => {
    render(
      <MockUserProvider>
        <LoginForm />
      </MockUserProvider>
    );
    
    const loginButton = screen.getByRole('button', { name: /login/i });
    fireEvent.click(loginButton);
    
    expect(screen.getByText('Logging in...')).toBeInTheDocument();
  });
});
```

#### API Service Tests

```javascript
// frontend/src/services/__tests__/api.test.js
import { apiService } from '../api';

// Mock fetch
global.fetch = jest.fn();

describe('API Service', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('creates user successfully', async () => {
    const mockResponse = {
      username: 'testuser',
      profile: { weak_areas: [] }
    };
    
    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse
    });
    
    const result = await apiService.createUser('testuser');
    
    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/users/create',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: 'testuser' })
      })
    );
    
    expect(result).toEqual(mockResponse);
  });

  test('handles API errors', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error'
    });
    
    await expect(apiService.createUser('testuser')).rejects.toThrow();
  });
});
```

#### E2E Tests

```javascript
// frontend/cypress/integration/learning-flow.spec.js
describe('Learning Flow', () => {
  beforeEach(() => {
    // Set up test user
    cy.request('POST', '/api/users/create', { username: 'testuser' });
    cy.visit('/');
  });

  it('completes full learning flow', () => {
    // Login
    cy.get('input[placeholder="Enter username"]').type('testuser');
    cy.get('button').contains('Login').click();
    
    // Navigate to Learn page
    cy.get('nav').contains('Learn').click();
    
    // Select topic
    cy.get('input[placeholder="Enter topic to study"]').type('machine learning');
    cy.get('button').contains('Explain').click();
    
    // Verify explanation appears
    cy.contains('Machine learning', { timeout: 10000 });
    
    // Generate question
    cy.get('button').contains('Generate Question').click();
    
    // Verify question appears
    cy.contains('Question:', { timeout: 10000 });
    
    // Answer question
    cy.get('textarea').type('Machine learning is a subset of AI');
    cy.get('button').contains('Submit').click();
    
    // Verify feedback
    cy.contains('Score:', { timeout: 10000 });
  });
});
```

### Test Configuration

```javascript
// frontend/jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1'
  },
  collectCoverageFrom: [
    'src/**/*.{js,jsx}',
    '!src/index.js',
    '!src/reportWebVitals.js'
  ],
  coverageThreshold: {
    global: {
      branches: 70,
      functions: 70,
      lines: 70,
      statements: 70
    }
  }
};
```

```python
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --cov=.
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

---

## Debugging Guide

### Backend Debugging

#### Logging Configuration

```python
# logging_config.py
import logging
from pathlib import Path

def setup_logging():
    """Set up logging configuration."""
    log_dir = Path('logs')
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / 'app.log'),
            logging.StreamHandler()
        ]
    )
    
    # Set specific loggers
    logging.getLogger('uvicorn').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

logger = setup_logging()
```

#### Debug Utilities

```python
# debug_utils.py
import functools
import time
from typing import Any, Callable

def debug_timer(func: Callable) -> Callable:
    """Decorator to time function execution."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    return wrapper

def debug_args(func: Callable) -> Callable:
    """Decorator to log function arguments."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned: {result}")
        return result
    return wrapper

class DebugContext:
    """Context manager for debugging sections."""
    def __init__(self, name: str):
        self.name = name
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        print(f"Starting {self.name}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start_time
        print(f"Finished {self.name} in {elapsed:.4f} seconds")
        if exc_type:
            print(f"Exception in {self.name}: {exc_val}")
```

#### Memory Profiling

```python
# memory_profiler.py
import psutil
import tracemalloc
from functools import wraps

def profile_memory(func):
    """Decorator to profile memory usage."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        tracemalloc.start()
        
        # Get initial memory
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        result = func(*args, **kwargs)
        
        # Get final memory
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Get tracemalloc stats
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        print(f"Memory usage for {func.__name__}:")
        print(f"  Initial: {initial_memory:.2f} MB")
        print(f"  Final: {final_memory:.2f} MB")
        print(f"  Delta: {final_memory - initial_memory:.2f} MB")
        print(f"  Peak traced: {peak / 1024 / 1024:.2f} MB")
        
        return result
    return wrapper
```

### Frontend Debugging

#### React DevTools Integration

```jsx
// debug/ReactDevTools.js
import React, { useEffect } from 'react';

const ReactDevTools = ({ children }) => {
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      // Enable React DevTools
      window.__REACT_DEVTOOLS_GLOBAL_HOOK__ = window.__REACT_DEVTOOLS_GLOBAL_HOOK__ || {};
      
      // Add debug helpers
      window.debugReactState = (component) => {
        console.log('Component state:', component.state);
        console.log('Component props:', component.props);
      };
    }
  }, []);

  return children;
};

export default ReactDevTools;
```

#### Console Debugging Utilities

```javascript
// debug/console-utils.js
export const debugAPI = {
  log: (message, data) => {
    if (process.env.NODE_ENV === 'development') {
      console.log(`[API] ${message}`, data);
    }
  },
  
  error: (message, error) => {
    if (process.env.NODE_ENV === 'development') {
      console.error(`[API ERROR] ${message}`, error);
    }
  },
  
  time: (label) => {
    if (process.env.NODE_ENV === 'development') {
      console.time(label);
    }
  },
  
  timeEnd: (label) => {
    if (process.env.NODE_ENV === 'development') {
      console.timeEnd(label);
    }
  }
};

// Usage in API calls
export const apiWithDebug = async (endpoint, options = {}) => {
  debugAPI.time(`API Call: ${endpoint}`);
  debugAPI.log(`Making request to ${endpoint}`, options);
  
  try {
    const response = await fetch(endpoint, options);
    debugAPI.log(`Response from ${endpoint}`, response.status);
    return response;
  } catch (error) {
    debugAPI.error(`Error in ${endpoint}`, error);
    throw error;
  } finally {
    debugAPI.timeEnd(`API Call: ${endpoint}`);
  }
};
```

### Common Issues and Solutions

#### Backend Issues

1. **Memory Leaks**
```python
# Use context managers for file operations
with open('file.txt', 'r') as f:
    content = f.read()

# Clear caches periodically
import gc
gc.collect()
```

2. **Performance Issues**
```python
# Use profiling to identify bottlenecks
import cProfile
import pstats

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # Your code here
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # Top 10 functions
```

3. **Database Issues**
```python
# Always use connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'sqlite:///database.db',
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10
)
```

#### Frontend Issues

1. **State Management**
```jsx
// Use React DevTools to inspect state
const MyComponent = () => {
  const [state, setState] = useState(initialState);
  
  // Debug state changes
  useEffect(() => {
    console.log('State changed:', state);
  }, [state]);
  
  return <div>{/* component */}</div>;
};
```

2. **API Integration**
```jsx
// Handle loading and error states
const useAPICall = (apiFunction) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);
  
  const execute = async (...args) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiFunction(...args);
      setData(result);
    } catch (err) {
      setError(err);
      console.error('API call failed:', err);
    } finally {
      setLoading(false);
    }
  };
  
  return { loading, error, data, execute };
};
```

---

## Code Quality Standards

### Python Code Standards

#### Linting Configuration

```python
# .pylintrc
[MASTER]
extension-pkg-whitelist=pydantic

[MESSAGES CONTROL]
disable=C0114,C0115,C0116,R0903,R0913,W0613

[FORMAT]
max-line-length=88
indent-string='    '

[VARIABLES]
good-names=i,j,k,ex,Run,_,id,pk

[DESIGN]
max-args=8
max-locals=15
max-returns=6
max-branches=12
max-statements=50
```

#### Code Formatting

```python
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.mypy_cache
  | \.tox
  | \.venv
  | _build
  | buck-out
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
```

#### Type Hints

```python
from typing import Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
from pydantic import BaseModel

@dataclass
class UserProfile:
    username: str
    weak_areas: List[str]
    topic_mastery: Dict[str, float]
    last_active: Optional[str] = None

def process_user_data(
    username: str,
    performance_data: Dict[str, float],
    session_duration: int = 30
) -> Tuple[bool, str]:
    """Process user learning data.
    
    Args:
        username: The user's username
        performance_data: Dictionary of topic -> performance scores
        session_duration: Session duration in minutes
        
    Returns:
        Tuple of (success, message)
    """
    # Implementation
    return True, "Success"
```

### JavaScript Code Standards

#### ESLint Configuration

```javascript
// .eslintrc.js
module.exports = {
  extends: [
    'react-app',
    'react-app/jest',
    'eslint:recommended',
    '@typescript-eslint/recommended'
  ],
  plugins: ['react', 'react-hooks'],
  rules: {
    'react/prop-types': 'warn',
    'react-hooks/rules-of-hooks': 'error',
    'react-hooks/exhaustive-deps': 'warn',
    'no-unused-vars': 'warn',
    'no-console': 'warn',
    'prefer-const': 'error',
    'no-var': 'error'
  },
  parserOptions: {
    ecmaVersion: 2020,
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true
    }
  }
};
```

#### Prettier Configuration

```javascript
// .prettierrc
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 80,
  "tabWidth": 2,
  "useTabs": false,
  "bracketSpacing": true,
  "jsxBracketSameLine": false,
  "arrowParens": "avoid"
}
```

### Documentation Standards

```python
def complex_function(
    param1: str,
    param2: Dict[str, Any],
    param3: Optional[List[str]] = None
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    Complex function with comprehensive documentation.
    
    This function demonstrates proper documentation standards including
    parameter descriptions, return value descriptions, examples, and
    notes about behavior.
    
    Args:
        param1: Description of the first parameter
        param2: Dictionary containing configuration data with keys:
            - 'setting1': Description of setting1
            - 'setting2': Description of setting2
        param3: Optional list of strings for additional processing
        
    Returns:
        Tuple containing:
            - bool: Success status
            - str: Status message
            - Dict[str, Any]: Result data
            
    Raises:
        ValueError: If param1 is empty
        KeyError: If required keys are missing from param2
        
    Examples:
        >>> result = complex_function(
        ...     "test",
        ...     {"setting1": "value1", "setting2": "value2"},
        ...     ["item1", "item2"]
        ... )
        >>> print(result)
        (True, "Success", {"processed": True})
        
    Notes:
        - This function is thread-safe
        - Performance is O(n) where n is the length of param3
        - Uses caching for repeated calls with same parameters
    """
    # Implementation
    pass
```

---

## Deployment Procedures

### Environment Configuration

```bash
# Production environment variables
export ENVIRONMENT=production
export DEBUG=false
export DATABASE_URL=postgresql://user:pass@localhost/db
export REDIS_URL=redis://localhost:6379
export SECRET_KEY=your-secret-key
export OPENAI_API_KEY=your-openai-key
export ANTHROPIC_API_KEY=your-anthropic-key
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start application
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
      - ./logs:/app/logs
    environment:
      - ENVIRONMENT=production
      - DATABASE_URL=postgresql://user:pass@db:5432/tutoring
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    restart: unless-stopped

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    restart: unless-stopped

  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=tutoring
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    restart: unless-stopped

volumes:
  postgres_data:
```

### CI/CD Pipeline

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
          
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
          
      - name: Run tests
        run: |
          pytest tests/ --cov=. --cov-report=xml
          
      - name: Upload coverage
        uses: codecov/codecov-action@v1

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    
    steps:
      - uses: actions/checkout@v2
      
      - name: Deploy to server
        uses: appleboy/ssh-action@v0.1.4
        with:
          host: ${{ secrets.HOST }}
          username: ${{ secrets.USERNAME }}
          key: ${{ secrets.SSH_KEY }}
          script: |
            cd /app/ai-tutoring-system
            git pull origin main
            docker-compose down
            docker-compose build
            docker-compose up -d
            
      - name: Health check
        run: |
          sleep 30
          curl -f ${{ secrets.HEALTH_CHECK_URL }} || exit 1
```

### Production Monitoring

```python
# monitoring.py
import logging
import time
from functools import wraps
from typing import Dict, Any
import psutil

class ApplicationMonitor:
    def __init__(self):
        self.metrics = {
            'request_count': 0,
            'error_count': 0,
            'response_times': [],
            'memory_usage': [],
            'cpu_usage': []
        }
        
    def track_request(self, func):
        """Decorator to track request metrics."""
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            self.metrics['request_count'] += 1
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                self.metrics['error_count'] += 1
                logging.error(f"Request failed: {e}")
                raise
            finally:
                response_time = time.time() - start_time
                self.metrics['response_times'].append(response_time)
                
                # Keep only last 1000 response times
                if len(self.metrics['response_times']) > 1000:
                    self.metrics['response_times'] = self.metrics['response_times'][-1000:]
                    
        return wrapper
    
    def collect_system_metrics(self):
        """Collect system metrics."""
        process = psutil.Process()
        
        memory_info = process.memory_info()
        cpu_percent = process.cpu_percent()
        
        self.metrics['memory_usage'].append(memory_info.rss / 1024 / 1024)  # MB
        self.metrics['cpu_usage'].append(cpu_percent)
        
        # Keep only last 100 measurements
        for key in ['memory_usage', 'cpu_usage']:
            if len(self.metrics[key]) > 100:
                self.metrics[key] = self.metrics[key][-100:]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get application health status."""
        avg_response_time = sum(self.metrics['response_times'][-100:]) / len(self.metrics['response_times'][-100:]) if self.metrics['response_times'] else 0
        error_rate = self.metrics['error_count'] / max(self.metrics['request_count'], 1)
        
        return {
            'status': 'healthy' if error_rate < 0.05 and avg_response_time < 2.0 else 'unhealthy',
            'request_count': self.metrics['request_count'],
            'error_count': self.metrics['error_count'],
            'error_rate': error_rate,
            'avg_response_time': avg_response_time,
            'memory_usage_mb': self.metrics['memory_usage'][-1] if self.metrics['memory_usage'] else 0,
            'cpu_usage_percent': self.metrics['cpu_usage'][-1] if self.metrics['cpu_usage'] else 0
        }

# Global monitor instance
monitor = ApplicationMonitor()
```

---

## Contributing Guidelines

### Pull Request Process

1. **Fork and Branch**
```bash
git fork origin
git checkout -b feature/your-feature-name
```

2. **Development**
   - Write code following style guidelines
   - Add comprehensive tests
   - Update documentation
   - Test locally

3. **Pre-commit Checks**
```bash
# Run tests
pytest tests/
cd frontend && npm test

# Check code quality
black .
pylint *.py
cd frontend && npm run lint

# Check types
mypy .
```

4. **Submit PR**
   - Clear description of changes
   - Link to related issues
   - Include screenshots if UI changes
   - Ensure CI passes

### Code Review Guidelines

**For Authors:**
- Keep PRs focused and small
- Provide clear descriptions
- Respond to feedback promptly
- Update based on review comments

**For Reviewers:**
- Be constructive and helpful
- Focus on code quality, not style preferences
- Test the changes locally
- Approve only when satisfied

### Release Process

```bash
# Create release branch
git checkout -b release/v1.2.0

# Update version numbers
# Update CHANGELOG.md
# Final testing

# Merge to main
git checkout main
git merge release/v1.2.0

# Tag release
git tag v1.2.0
git push origin v1.2.0

# Deploy to production
```

---

## Troubleshooting

### Common Issues

#### Backend Issues

1. **ImportError: No module named 'module_name'**
```bash
# Check virtual environment
which python
pip list

# Reinstall dependencies
pip install -r requirements.txt
```

2. **Database connection errors**
```python
# Check database connection
import sqlite3
try:
    conn = sqlite3.connect('database.db')
    print("Database connected successfully")
except Exception as e:
    print(f"Database connection failed: {e}")
```

3. **API key issues**
```bash
# Check environment variables
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# Reset API keys
python set_api_key.py
```

#### Frontend Issues

1. **npm install fails**
```bash
# Clear cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

2. **Build fails**
```bash
# Check for syntax errors
npm run lint

# Clear build cache
rm -rf build
npm run build
```

3. **API connection issues**
```javascript
// Check API URL
console.log('API URL:', process.env.REACT_APP_API_URL);

// Test API connectivity
fetch('/api/health')
  .then(response => console.log('API Status:', response.status))
  .catch(error => console.error('API Error:', error));
```

### Performance Issues

#### Memory Leaks

```python
# Monitor memory usage
import psutil
import gc

def check_memory():
    process = psutil.Process()
    memory_mb = process.memory_info().rss / 1024 / 1024
    print(f"Memory usage: {memory_mb:.2f} MB")
    
    # Force garbage collection
    gc.collect()
    
    # Check for memory leaks
    objects = gc.get_objects()
    print(f"Objects in memory: {len(objects)}")
```

#### Slow Response Times

```python
# Profile slow functions
import cProfile
import pstats
import io

def profile_function(func):
    pr = cProfile.Profile()
    pr.enable()
    result = func()
    pr.disable()
    
    s = io.StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()
    
    print(s.getvalue())
    return result
```

### Debugging Tools

```bash
# Backend debugging
python -m pdb script.py          # Python debugger
python -c "import pdb; pdb.set_trace()"  # Breakpoint

# Frontend debugging
console.log()                    # Basic logging
console.table()                  # Table format
console.time() / console.timeEnd()  # Performance timing
debugger;                        # JavaScript breakpoint
```

### Log Analysis

```bash
# Analyze logs
tail -f logs/app.log
grep "ERROR" logs/app.log
grep "slow" logs/app.log | head -20

# System monitoring
top -p $(pgrep python)
htop
iostat -x 1
```

---

This comprehensive development guide provides detailed procedures for setting up, developing, testing, debugging, and deploying the AI Tutoring System. Follow these guidelines to ensure high code quality, proper testing coverage, and smooth deployment processes.