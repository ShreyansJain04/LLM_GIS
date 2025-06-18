import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// User Management API
export const userAPI = {
  createUser: async (username) => {
    const response = await api.post('/api/users/create', { username });
    return response.data;
  },

  getUserProfile: async (username) => {
    const response = await api.get(`/api/users/${username}/profile`);
    return response.data;
  },

  getUserInsights: async (username) => {
    const response = await api.get(`/api/users/${username}/insights`);
    return response.data;
  },
};

// Learning Content API
export const contentAPI = {
  explainConcept: async (topic, detailLevel = 'standard') => {
    const response = await api.post('/api/content/explain', {
      topic,
      detail_level: detailLevel,
    });
    return response.data;
  },

  generateExample: async (topic, difficulty = 'medium') => {
    const response = await api.post('/api/content/example', {
      topic,
      difficulty,
    });
    return response.data;
  },

  generateQuestion: async (topic, previousQuestions = [], difficulty = 'medium', questionType = 'conceptual') => {
    const response = await api.post('/api/content/question', {
      topic,
      previous_questions: previousQuestions,
      difficulty,
      question_type: questionType,
    });
    return response.data;
  },

  checkAnswer: async (question, answer) => {
    const response = await api.post('/api/content/check-answer', {
      question,
      answer,
    });
    return response.data;
  },

  getSummary: async (topic, length = 'medium') => {
    const response = await api.get(`/api/content/summary/${encodeURIComponent(topic)}`, {
      params: { length },
    });
    return response.data;
  },
};

// Learning Session API
export const learningAPI = {
  getLearningPlan: async (username, topic) => {
    const response = await api.get(`/api/learning/${username}/plan/${encodeURIComponent(topic)}`);
    return response.data;
  },

  recordSession: async (sessionData) => {
    const response = await api.post('/api/learning/record-session', sessionData);
    return response.data;
  },

  startInteractiveSession: async (username, topic) => {
    const response = await api.post(`/api/sessions/${username}/start/${encodeURIComponent(topic)}`);
    return response.data;
  },

  getSessionStatus: async (sessionId) => {
    const response = await api.get(`/api/sessions/${sessionId}/status`);
    return response.data;
  },

  endSession: async (sessionId) => {
    const response = await api.delete(`/api/sessions/${sessionId}`);
    return response.data;
  },
};

// Document Sources API
export const sourcesAPI = {
  getSources: async () => {
    const response = await api.get('/api/sources');
    return response.data;
  },
};

// LLM Management API
export const llmAPI = {
  getProviders: async () => {
    const response = await api.get('/api/llm/providers');
    return response.data;
  },

  setProvider: async (provider) => {
    const response = await api.post('/api/llm/set-provider', { provider });
    return response.data;
  },

  addApiKey: async (provider, apiKey) => {
    const response = await api.post('/api/llm/add-key', {
      provider,
      api_key: apiKey,
    });
    return response.data;
  },

  testProvider: async (provider) => {
    const response = await api.post(`/api/llm/test/${provider}`);
    return response.data;
  },
};

// Health check
export const healthAPI = {
  check: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api; 