# Troubleshooting and FAQ

## Table of Contents

1. [Common Issues](#common-issues)
2. [Installation Problems](#installation-problems)
3. [Configuration Issues](#configuration-issues)
4. [Runtime Errors](#runtime-errors)
5. [Performance Issues](#performance-issues)
6. [API and Integration Problems](#api-and-integration-problems)
7. [Frontend Issues](#frontend-issues)
8. [Database Issues](#database-issues)
9. [Deployment Problems](#deployment-problems)
10. [Frequently Asked Questions](#frequently-asked-questions)

---

## Common Issues

### 1. System Won't Start

**Problem**: Application fails to start with various error messages.

**Common Causes**:
- Missing dependencies
- Incorrect environment variables
- Port conflicts
- Missing API keys

**Solutions**:

```bash
# Check Python environment
python --version
which python

# Verify virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Check installed packages
pip list

# Reinstall dependencies
pip install -r requirements.txt

# Check environment variables
echo $OPENAI_API_KEY
echo $ANTHROPIC_API_KEY

# Set API keys if missing
python set_api_key.py
```

### 2. Module Import Errors

**Problem**: `ImportError: No module named 'module_name'`

**Solutions**:

```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Check if module is installed
pip show module_name

# Install missing module
pip install module_name

# Reinstall all dependencies
pip install -r requirements.txt

# Check PYTHONPATH
echo $PYTHONPATH

# Add current directory to path if needed
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### 3. Permission Errors

**Problem**: Permission denied when accessing files or directories.

**Solutions**:

```bash
# Check file permissions
ls -la user_data/
ls -la docs/

# Fix permissions
chmod -R 755 user_data/
chmod -R 755 docs/
chmod -R 755 rag_cache/

# Create directories if missing
mkdir -p user_data docs rag_cache

# Change ownership if needed
chown -R $USER:$USER user_data/
```

---

## Installation Problems

### Backend Installation Issues

#### 1. pip install fails

**Problem**: Package installation fails with compilation errors.

**Solutions**:

```bash
# Update pip and setuptools
pip install --upgrade pip setuptools wheel

# Install system dependencies (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install build-essential python3-dev python3-pip

# Install system dependencies (CentOS/RHEL)
sudo yum install gcc python3-devel python3-pip

# Install system dependencies (macOS)
xcode-select --install
brew install python3

# Use binary packages if available
pip install --only-binary=all package_name

# Clear pip cache
pip cache purge
rm -rf ~/.cache/pip
```

#### 2. Virtual Environment Issues

**Problem**: Virtual environment creation or activation fails.

**Solutions**:

```bash
# Create virtual environment
python -m venv venv

# If venv module is missing
sudo apt-get install python3-venv  # Ubuntu/Debian
# or
pip install virtualenv
virtualenv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Check activation
which python
python --version

# Deactivate if needed
deactivate
```

### Frontend Installation Issues

#### 1. npm install fails

**Problem**: Node.js package installation fails.

**Solutions**:

```bash
# Update npm
npm install -g npm@latest

# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall packages
npm install

# Use yarn as alternative
npm install -g yarn
yarn install

# Check Node.js version
node --version
npm --version
```

#### 2. Node.js Version Issues

**Problem**: Incompatible Node.js version.

**Solutions**:

```bash
# Check current version
node --version

# Install Node Version Manager (nvm)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc

# Install and use specific Node.js version
nvm install 16
nvm use 16

# Set default version
nvm alias default 16

# Update npm
npm install -g npm@latest
```

---

## Configuration Issues

### 1. Environment Variables

**Problem**: Missing or incorrect environment variables.

**Solutions**:

```bash
# Check current environment variables
env | grep -E "(OPENAI|ANTHROPIC|API)"

# Create .env file from template
cp .env.example .env

# Edit .env file
nano .env

# Set environment variables manually
export OPENAI_API_KEY="your_key_here"
export ANTHROPIC_API_KEY="your_key_here"
export DATABASE_URL="sqlite:///tutoring.db"

# Make changes permanent
echo 'export OPENAI_API_KEY="your_key_here"' >> ~/.bashrc
source ~/.bashrc
```

### 2. API Key Configuration

**Problem**: API keys not working or invalid.

**Solutions**:

```bash
# Use the setup script
python set_api_key.py

# Test API keys
python test_openai_api.py
python test_llm.py

# Check API key format
# OpenAI: sk-...
# Anthropic: sk-ant-...

# Verify API key permissions
curl -H "Authorization: Bearer $OPENAI_API_KEY" \
     https://api.openai.com/v1/models
```

### 3. Database Configuration

**Problem**: Database connection or initialization issues.

**Solutions**:

```python
# Test database connection
import sqlite3
try:
    conn = sqlite3.connect('data/tutoring.db')
    print("Database connected successfully")
    conn.close()
except Exception as e:
    print(f"Database error: {e}")

# Initialize database
python scripts/setup_database.py

# Check database file permissions
ls -la data/tutoring.db
chmod 644 data/tutoring.db
```

---

## Runtime Errors

### 1. Memory Errors

**Problem**: Out of memory errors during operation.

**Solutions**:

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
    
    # Check memory after cleanup
    memory_after = process.memory_info().rss / 1024 / 1024
    print(f"Memory after GC: {memory_after:.2f} MB")

# Optimize memory usage
# - Process documents in smaller chunks
# - Clear unused variables
# - Use generators instead of lists
# - Implement caching with TTL
```

### 2. Timeout Errors

**Problem**: API calls or operations timeout.

**Solutions**:

```python
# Increase timeout values
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def create_session_with_retries():
    session = requests.Session()
    retry = Retry(total=3, backoff_factor=0.3, status_forcelist=[500, 502, 503, 504])
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

# Use async operations for better performance
import asyncio
import aiohttp

async def async_api_call(url, data):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, timeout=30) as response:
            return await response.json()
```

### 3. File Access Errors

**Problem**: Cannot read/write files.

**Solutions**:

```python
# Check file permissions
import os
import stat

def check_file_permissions(file_path):
    if os.path.exists(file_path):
        st = os.stat(file_path)
        print(f"File permissions: {stat.filemode(st.st_mode)}")
        print(f"Owner: {st.st_uid}, Group: {st.st_gid}")
    else:
        print("File does not exist")

# Use proper file handling
import fcntl
import json

def safe_file_write(file_path, data):
    try:
        with open(file_path, 'w') as f:
            fcntl.flock(f.fileno(), fcntl.LOCK_EX)
            json.dump(data, f, indent=2)
    except IOError as e:
        print(f"File write error: {e}")
```

---

## Performance Issues

### 1. Slow Response Times

**Problem**: API responses are slow.

**Diagnosis**:

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

# Time specific operations
import time

def time_operation(operation_name):
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            end = time.time()
            print(f"{operation_name} took {end - start:.2f} seconds")
            return result
        return wrapper
    return decorator
```

**Solutions**:

```python
# Implement caching
from functools import lru_cache
import time

@lru_cache(maxsize=128)
def cached_function(param):
    # Expensive operation
    time.sleep(1)
    return f"Result for {param}"

# Use database indexing
# CREATE INDEX idx_username ON users(username);
# CREATE INDEX idx_topic ON sessions(topic);

# Optimize queries
def get_user_sessions(username, limit=10):
    # Use LIMIT to reduce data transfer
    query = "SELECT * FROM sessions WHERE username = ? ORDER BY created_at DESC LIMIT ?"
    return execute_query(query, (username, limit))
```

### 2. High Memory Usage

**Problem**: Memory consumption grows over time.

**Solutions**:

```python
# Monitor memory usage
import psutil
import gc
import tracemalloc

def memory_monitor():
    process = psutil.Process()
    memory_info = process.memory_info()
    
    print(f"RSS: {memory_info.rss / 1024 / 1024:.2f} MB")
    print(f"VMS: {memory_info.vms / 1024 / 1024:.2f} MB")
    
    # Track memory allocations
    tracemalloc.start()
    
    # Your code here
    
    current, peak = tracemalloc.get_traced_memory()
    print(f"Current memory usage: {current / 1024 / 1024:.2f} MB")
    print(f"Peak memory usage: {peak / 1024 / 1024:.2f} MB")
    tracemalloc.stop()

# Clear unused objects
def cleanup_memory():
    # Clear large objects
    large_objects = None
    
    # Force garbage collection
    gc.collect()
    
    # Check for circular references
    if gc.garbage:
        print(f"Circular references: {len(gc.garbage)}")
        gc.garbage.clear()
```

### 3. Database Performance

**Problem**: Database operations are slow.

**Solutions**:

```sql
-- Add indexes
CREATE INDEX idx_user_topic ON user_sessions(username, topic);
CREATE INDEX idx_timestamp ON user_sessions(timestamp);

-- Optimize queries
-- Use specific columns instead of SELECT *
SELECT username, topic, performance FROM user_sessions WHERE username = ?;

-- Use LIMIT for large datasets
SELECT * FROM user_sessions ORDER BY timestamp DESC LIMIT 100;
```

```python
# Use connection pooling
import sqlite3
from contextlib import contextmanager

class DatabasePool:
    def __init__(self, db_path, max_connections=5):
        self.db_path = db_path
        self.connections = []
        self.max_connections = max_connections
    
    @contextmanager
    def get_connection(self):
        if self.connections:
            conn = self.connections.pop()
        else:
            conn = sqlite3.connect(self.db_path)
        
        try:
            yield conn
        finally:
            if len(self.connections) < self.max_connections:
                self.connections.append(conn)
            else:
                conn.close()
```

---

## API and Integration Problems

### 1. LLM Provider Issues

**Problem**: LLM API calls fail or return errors.

**Solutions**:

```python
# Test LLM providers
from llm_providers import llm_manager

def test_providers():
    providers = llm_manager.get_available_providers()
    print(f"Available providers: {providers}")
    
    for provider_name in providers:
        try:
            llm_manager.set_provider(provider_name)
            response = llm_manager.generate("Test message")
            print(f"{provider_name}: OK - {response[:50]}...")
        except Exception as e:
            print(f"{provider_name}: ERROR - {e}")

# Implement fallback logic
def robust_llm_call(prompt, max_retries=3):
    providers = ["openai", "anthropic", "ollama"]
    
    for provider in providers:
        for attempt in range(max_retries):
            try:
                llm_manager.set_provider(provider)
                return llm_manager.generate(prompt)
            except Exception as e:
                print(f"Attempt {attempt + 1} failed for {provider}: {e}")
                time.sleep(1)
    
    raise Exception("All providers failed")
```

### 2. Rate Limiting

**Problem**: API rate limits exceeded.

**Solutions**:

```python
import time
from functools import wraps

def rate_limit(calls_per_minute=60):
    def decorator(func):
        last_called = [0.0]
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            left_to_wait = 60.0 / calls_per_minute - elapsed
            
            if left_to_wait > 0:
                time.sleep(left_to_wait)
            
            last_called[0] = time.time()
            return func(*args, **kwargs)
        
        return wrapper
    return decorator

@rate_limit(calls_per_minute=30)
def api_call(prompt):
    # Your API call here
    pass
```

### 3. Network Connectivity

**Problem**: Network timeouts or connection errors.

**Solutions**:

```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def create_robust_session():
    session = requests.Session()
    
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "OPTIONS", "POST"]
    )
    
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    return session

# Test network connectivity
def test_network():
    try:
        response = requests.get("https://httpbin.org/get", timeout=5)
        print(f"Network test: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Network error: {e}")
```

---

## Frontend Issues

### 1. Build Failures

**Problem**: Frontend build process fails.

**Solutions**:

```bash
# Clear cache and dependencies
rm -rf node_modules package-lock.json
npm cache clean --force

# Reinstall dependencies
npm install

# Check for syntax errors
npm run lint

# Fix linting issues
npm run lint -- --fix

# Build with verbose output
npm run build -- --verbose

# Check disk space
df -h
```

### 2. Runtime JavaScript Errors

**Problem**: JavaScript errors in browser console.

**Solutions**:

```javascript
// Add error boundary
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
      return <h1>Something went wrong.</h1>;
    }
    return this.props.children;
  }
}

// Use error boundary
<ErrorBoundary>
  <App />
</ErrorBoundary>
```

### 3. API Connection Issues

**Problem**: Frontend cannot connect to backend API.

**Solutions**:

```javascript
// Check API URL configuration
console.log('API URL:', process.env.REACT_APP_API_URL);

// Test API connectivity
const testAPI = async () => {
  try {
    const response = await fetch('/api/health');
    console.log('API Status:', response.status);
  } catch (error) {
    console.error('API Error:', error);
  }
};

// Handle CORS issues
// Add proxy to package.json
{
  "proxy": "http://localhost:8000"
}

// Or configure CORS on backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Database Issues

### 1. Database Corruption

**Problem**: Database file is corrupted or inaccessible.

**Solutions**:

```bash
# Check database integrity
sqlite3 data/tutoring.db "PRAGMA integrity_check;"

# Repair database
sqlite3 data/tutoring.db ".recover" | sqlite3 data/tutoring_recovered.db

# Backup database
cp data/tutoring.db data/tutoring_backup_$(date +%Y%m%d_%H%M%S).db

# Restore from backup
cp data/tutoring_backup_YYYYMMDD_HHMMSS.db data/tutoring.db
```

### 2. Database Locks

**Problem**: Database is locked or connection issues.

**Solutions**:

```python
import sqlite3
import time

def safe_database_operation(db_path, operation):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            conn = sqlite3.connect(db_path, timeout=10)
            result = operation(conn)
            conn.close()
            return result
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e) and attempt < max_retries - 1:
                time.sleep(0.1 * (2 ** attempt))  # Exponential backoff
                continue
            raise
        except Exception as e:
            if conn:
                conn.close()
            raise
```

### 3. Performance Issues

**Problem**: Database queries are slow.

**Solutions**:

```sql
-- Analyze query performance
EXPLAIN QUERY PLAN SELECT * FROM user_sessions WHERE username = ?;

-- Add missing indexes
CREATE INDEX IF NOT EXISTS idx_username ON user_sessions(username);
CREATE INDEX IF NOT EXISTS idx_topic ON user_sessions(topic);
CREATE INDEX IF NOT EXISTS idx_timestamp ON user_sessions(timestamp);

-- Update statistics
ANALYZE;

-- Vacuum database
VACUUM;
```

```python
# Use connection pooling
import sqlite3
from contextlib import contextmanager

class DatabasePool:
    def __init__(self, db_path, max_connections=5):
        self.db_path = db_path
        self.connections = []
        self.max_connections = max_connections
    
    @contextmanager
    def get_connection(self):
        if self.connections:
            conn = self.connections.pop()
        else:
            conn = sqlite3.connect(self.db_path)
        
        try:
            yield conn
        finally:
            if len(self.connections) < self.max_connections:
                self.connections.append(conn)
            else:
                conn.close()
```

---

## Deployment Problems

### 1. Docker Issues

**Problem**: Docker containers fail to start or build.

**Solutions**:

```bash
# Check Docker status
docker --version
docker-compose --version

# Build with no cache
docker-compose build --no-cache

# Check container logs
docker-compose logs backend
docker-compose logs frontend

# Fix permission issues
chown -R $USER:$USER .
chmod -R 755 .

# Clean Docker system
docker system prune -a
docker volume prune
```

### 2. Port Conflicts

**Problem**: Ports are already in use.

**Solutions**:

```bash
# Check port usage
netstat -tlnp | grep :8000
lsof -i :8000

# Kill process using port
sudo kill -9 $(lsof -t -i:8000)

# Use different ports
export PORT=8001
docker-compose up -d
```

### 3. Environment Variables

**Problem**: Environment variables not set in production.

**Solutions**:

```bash
# Check environment variables
docker-compose exec backend env

# Set environment variables
docker-compose --env-file .env.production up -d

# Use secrets management
docker secret create openai_key openai_key.txt
docker service create --secret openai_key your_service
```

---

## Frequently Asked Questions

### General Questions

**Q: What are the system requirements?**
A: 
- Python 3.8+
- Node.js 16+
- 4GB RAM minimum (8GB recommended)
- 10GB free disk space
- Internet connection for API calls

**Q: Which LLM providers are supported?**
A: The system supports:
- OpenAI (GPT-4, GPT-3.5-turbo)
- Anthropic (Claude)
- Ollama (local models)
- DeepSeek
- Custom providers can be added

**Q: How much does it cost to run?**
A: Costs depend on:
- LLM API usage (varies by provider)
- Server hosting costs
- Storage requirements
- Usage volume

### Setup Questions

**Q: How do I get API keys?**
A: 
1. OpenAI: Sign up at https://platform.openai.com/
2. Anthropic: Sign up at https://console.anthropic.com/
3. Run `python set_api_key.py` to configure

**Q: Can I run without internet?**
A: Partial functionality is available:
- Local LLM providers (Ollama)
- Pre-processed documents
- Cached responses
- Some features require internet

**Q: How do I add new documents?**
A: 
1. Place PDF or text files in the `docs/` folder
2. Restart the application
3. Documents are automatically processed and indexed

### Usage Questions

**Q: How do I create a new user?**
A: 
- CLI: Run `python main.py` and follow prompts
- Web: Access the frontend and use the login form
- API: POST to `/api/users/create`

**Q: How is user data stored?**
A: 
- User profiles: JSON files in `user_data/`
- Session data: SQLite database
- RAG cache: Vector embeddings in `rag_cache/`

**Q: Can I backup my data?**
A: Yes, backup these directories:
- `user_data/` - User profiles
- `rag_cache/` - RAG system cache
- `data/` - Database files

### Technical Questions

**Q: How do I customize the LLM prompts?**
A: Edit the prompt templates in:
- `domain_expert.py` for explanations
- `planner.py` for learning plans
- `flashcards.py` for flashcard generation

**Q: How do I add custom document processors?**
A: Extend the `DocumentProcessor` class in `document_processor.py`:

```python
class CustomProcessor(DocumentProcessor):
    def process_custom_format(self, file_path):
        # Your custom processing logic
        return chunks
```

**Q: How do I monitor system performance?**
A: Use the built-in monitoring:
- Health check endpoint: `/health`
- Metrics endpoint: `/metrics`
- Log files in `logs/` directory

### Troubleshooting Questions

**Q: Why are responses slow?**
A: Common causes:
- Network latency to LLM APIs
- Large document processing
- Insufficient system resources
- Database query optimization needed

**Q: How do I fix memory issues?**
A: 
1. Increase system RAM
2. Optimize document chunk sizes
3. Enable caching with TTL
4. Use database connection pooling

**Q: What if an LLM provider is down?**
A: The system automatically falls back to available providers. Configure multiple providers for redundancy.

### Development Questions

**Q: How do I contribute to the project?**
A: 
1. Fork the repository
2. Create a feature branch
3. Follow the development guide
4. Submit a pull request

**Q: How do I run tests?**
A: 
```bash
# Backend tests
pytest tests/

# Frontend tests
cd frontend && npm test

# Integration tests
pytest integration_tests/
```

**Q: How do I add a new LLM provider?**
A: 
1. Create a new provider class extending `LLMProvider`
2. Implement required methods
3. Register in `llm_providers.py`
4. Add configuration options

### Security Questions

**Q: How are API keys stored?**
A: API keys are stored as environment variables and never logged or exposed in the interface.

**Q: Is user data encrypted?**
A: User data is stored locally. For production, implement encryption at rest and in transit.

**Q: How do I secure the API?**
A: 
- Use HTTPS in production
- Implement authentication
- Add rate limiting
- Use API keys for external access

---

## Getting Help

### Support Channels

1. **Documentation**: Check the comprehensive documentation files
2. **Issues**: Report bugs on the project repository
3. **Discussions**: Join community discussions
4. **Logs**: Check application logs for error details

### Diagnostic Information

When reporting issues, include:

```bash
# System information
python --version
node --version
npm --version

# Package versions
pip list
npm list

# Error logs
tail -50 logs/app.log

# System resources
free -h
df -h
```

### Log Locations

- Application logs: `logs/app.log`
- Error logs: `logs/error.log`
- Frontend logs: Browser console
- Database logs: SQLite doesn't log by default

---

This troubleshooting guide covers the most common issues and their solutions. For additional help, consult the other documentation files or seek community support.