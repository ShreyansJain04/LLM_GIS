# AI Tutoring System - React UI Setup

This guide will help you set up the React frontend for the AI Tutoring System.

## Prerequisites

- Python 3.8+
- Node.js 16+ and npm
- Your existing CLI tutoring system

## Setup Instructions

### 1. Backend API Setup

First, install the additional dependencies for the FastAPI server:

```bash
pip install -r requirements.txt
```

The new requirements.txt already includes FastAPI dependencies:
- `fastapi>=0.104.0`
- `uvicorn[standard]>=0.24.0`
- `python-multipart>=0.0.6`

### 2. Start the Backend Server

Run the FastAPI server:

```bash
python api_server.py
```

The API will be available at `http://localhost:8000`

You can view the auto-generated API documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 3. Frontend Setup

Navigate to the frontend directory and install dependencies:

```bash
cd frontend
npm install
```

### 4. Start the React Development Server

```bash
npm start
```

The React app will be available at `http://localhost:3000`

## Architecture Overview

### Backend (FastAPI)
- **api_server.py**: Main FastAPI application
- Exposes REST endpoints for all tutoring functionality
- Handles CORS for React app communication
- Integrates with all existing modules (memory, planner, domain_expert, etc.)

### Frontend (React)
- **Modern React 18** with hooks and functional components
- **Tailwind CSS** for styling with custom design system
- **Framer Motion** for smooth animations
- **React Hot Toast** for notifications
- **Axios** for API communication
- **React Markdown** for rich content rendering

### Key Features

1. **User Authentication**: Simple username-based system
2. **Dashboard**: Overview with stats and quick actions
3. **Learning Mode**: Interactive learning sessions with explanations, examples, and questions
4. **Review Mode**: Focus on weak areas (placeholder)
5. **Test Mode**: Practice questions and assessments (placeholder)
6. **Insights**: Learning analytics and personalized recommendations (placeholder)
7. **Sources**: Document management (placeholder)
8. **Settings**: LLM provider configuration (placeholder)

## API Endpoints

### User Management
- `POST /api/users/create` - Create/get user profile
- `GET /api/users/{username}/profile` - Get user profile and stats
- `GET /api/users/{username}/insights` - Get learning insights

### Learning Content
- `POST /api/content/explain` - Get concept explanations
- `POST /api/content/example` - Generate examples
- `POST /api/content/question` - Generate questions
- `POST /api/content/check-answer` - Check answer correctness
- `GET /api/content/summary/{topic}` - Get topic summaries

### Learning Sessions
- `GET /api/learning/{username}/plan/{topic}` - Get learning plan
- `POST /api/learning/record-session` - Record learning session
- `POST /api/sessions/{username}/start/{topic}` - Start interactive session

### Document Sources
- `GET /api/sources` - Get available document sources

### LLM Management
- `GET /api/llm/providers` - Get LLM provider info
- `POST /api/llm/set-provider` - Set active provider
- `POST /api/llm/add-key` - Add API key
- `POST /api/llm/test/{provider}` - Test provider

## Development Features

### Component Structure
```
src/
├── components/          # Reusable UI components
│   ├── LoginForm.js
│   └── Sidebar.js
├── contexts/           # React contexts for state management
│   └── UserContext.js
├── pages/             # Main page components
│   ├── Dashboard.js
│   └── Learn.js
├── services/          # API communication layer
│   └── api.js
├── App.js            # Main app component
└── index.js          # React entry point
```

### Styling System
- Custom Tailwind configuration with tutoring-focused design
- Primary color scheme (blues) and secondary grays
- Responsive design for desktop and mobile
- Smooth animations and transitions
- Custom component classes for consistency

### State Management
- React Context for user authentication and profile data
- Local state for page-specific data
- Optimistic updates for better UX
- Error handling with toast notifications

## Customization

### Adding New Pages
1. Create a new component in `src/pages/`
2. Add route to `src/App.js`
3. Add navigation item to `src/components/Sidebar.js`

### Adding New API Endpoints
1. Add endpoint to `api_server.py`
2. Add API function to `src/services/api.js`
3. Use in components with error handling

### Styling Customization
- Modify `tailwind.config.js` for design system changes
- Update `src/index.css` for global styles
- Use Tailwind classes for component-specific styling

## Production Deployment

### Backend
```bash
# Install production server
pip install gunicorn

# Run with gunicorn
gunicorn api_server:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend
```bash
# Build for production
npm run build

# Serve static files (use nginx, apache, or similar)
```

## Troubleshooting

### Common Issues

1. **CORS Errors**: Ensure the API server is running on port 8000
2. **Module Import Errors**: Check that all Python dependencies are installed
3. **React Build Errors**: Ensure Node.js version is 16+ and dependencies are installed
4. **API Connection**: Verify the API_BASE_URL in `src/services/api.js`

### Environment Variables
Create a `.env` file in the frontend directory for customization:
```
REACT_APP_API_URL=http://localhost:8000
```

## Next Steps

The foundation is now set up! You can:

1. **Complete the placeholder pages** (Review, Test, Insights, Sources, Settings)
2. **Add real-time features** with WebSockets
3. **Implement file upload** for document sources
4. **Add user management** with proper authentication
5. **Deploy to production** with proper infrastructure

The system is designed to be modular and extensible, so you can easily add new features while maintaining the existing CLI functionality. 