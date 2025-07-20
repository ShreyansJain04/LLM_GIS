import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add request interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API Error:", error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// User Management API
export const userAPI = {
  createUser: async (username) => {
    const response = await api.post("/api/users/create", { username });
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

  startReviewSession: async (username, mode) => {
    const response = await api.post("/api/review/session/start", {
      username,
      mode,
    });
    return response.data;
  },
};

// Learning Content API
export const contentAPI = {
  explainConcept: async (topic, detailLevel = "standard") => {
    const response = await api.post("/api/content/explain", {
      topic,
      detail_level: detailLevel,
    });
    return response.data;
  },

  generateExplanation: async (topic, detailLevel = "standard") => {
    const response = await api.post("/api/content/explain", {
      topic,
      detail_level: detailLevel,
    });
    return response.data;
  },

  generateExample: async (topic, difficulty = "medium") => {
    const response = await api.post("/api/content/example", {
      topic,
      difficulty,
    });
    return response.data;
  },

  generateQuestion: async (
    topic,
    previousQuestions = [],
    difficulty = "medium",
    questionType = "objective"
  ) => {
    const response = await api.post("/api/content/question", {
      topic,
      previous_questions: previousQuestions,
      difficulty,
      question_type: questionType,
    });
    return response.data;
  },

  checkAnswer: async (question, answer) => {
    const response = await api.post("/api/content/check-answer", {
      question,
      answer,
    });
    return response.data;
  },

  getSummary: async (topic, length = "medium") => {
    const response = await api.get(
      `/api/content/summary/${encodeURIComponent(topic)}`,
      {
        params: { length },
      }
    );
    return response.data;
  },
};

// Learning Session API
export const learningAPI = {
  getLearningPlan: async (username, topic) => {
    const response = await api.get(
      `/api/learning/${username}/plan/${encodeURIComponent(topic)}`
    );
    return response.data;
  },

  createLearningPlan: async (topic) => {
    const response = await api.post("/api/learning/create-plan", { topic });
    return response.data;
  },

  startLearningSession: async (username, topic) => {
    const response = await api.post("/api/learning/session/start", {
      username,
      topic,
    });
    return response.data;
  },

  getLearningSession: async (sessionId) => {
    const response = await api.get(`/api/learning/session/${sessionId}`);
    return response.data;
  },

  updateLearningSession: async (sessionId, data) => {
    const response = await api.put(`/api/learning/session/${sessionId}`, data);
    return response.data;
  },

  endLearningSession: async (sessionId) => {
    const response = await api.delete(`/api/learning/session/${sessionId}`);
    return response.data;
  },
};

// Document Sources API
export const sourcesAPI = {
  getSources: async () => {
    const response = await api.get("/api/sources");
    return response.data;
  },
};

// LLM Management API
export const llmAPI = {
  getProviders: async () => {
    const response = await api.get("/api/llm/providers");
    return response.data;
  },

  setProvider: async (provider) => {
    const response = await api.post("/api/llm/set-provider", { provider });
    return response.data;
  },

  addApiKey: async (provider, apiKey) => {
    const response = await api.post("/api/llm/add-key", {
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
    const response = await api.get("/health");
    return response.data;
  },
};

// Chat API
export const chatAPI = {
  sendMessage: async (username, message, context = null) => {
    const response = await api.post("/api/chat/message", {
      username,
      message,
      context,
    });
    return response.data;
  },

  getChatHistory: async (username, limit = 20) => {
    const response = await api.get(`/api/chat/${username}/history`, {
      params: { limit },
    });
    return response.data;
  },

  clearChatHistory: async (username) => {
    const response = await api.delete(`/api/chat/${username}/history`);
    return response.data;
  },

  executeCommand: async (username, command, args = "", topic = null) => {
    const response = await api.post("/api/chat/command", {
      username,
      command,
      args,
      topic,
    });
    return response.data;
  },

  submitQuizAnswer: async (question, answer) => {
    const response = await api.post("/api/chat/quiz/answer", {
      question,
      answer,
    });
    return response.data;
  },

  getSuggestions: async (username) => {
    const response = await api.get(`/api/chat/suggestions/${username}`);
    return response.data;
  },
};

// Review Session API
export const reviewAPI = {
  startSession: async (username, mode, topics = [], adaptive = false) => {
    const response = await api.post("/api/review/session/start", {
      username,
      mode,
      topics,
      adaptive,
    });
    return response.data;
  },

  startAdaptiveReview: async (username) => {
    const response = await api.post("/api/review/adaptive", {
      username,
      mode: "adaptive",
    });
    return response.data;
  },

  startIntensiveReview: async (username, topics = []) => {
    const response = await api.post("/api/review/intensive", {
      username,
      mode: "intensive",
      topics,
    });
    return response.data;
  },

  startSpacedReview: async (username) => {
    const response = await api.post("/api/review/spaced", {
      username,
      mode: "spaced",
    });
    return response.data;
  },

  startQuickReview: async (username) => {
    const response = await api.post("/api/review/quick", {
      username,
      mode: "quick",
    });
    return response.data;
  },

  startFlashcardReview: async (username, topics = []) => {
    const response = await api.post("/api/review/flashcards", {
      username,
      mode: "flashcards",
      topics,
    });
    return response.data;
  },

  getFlashcardTopics: async (username) => {
    const response = await api.get(`/api/review/flashcards/topics/${username}`);
    return response.data;
  },

  getNextFlashcard: async (sessionId, topic = null) => {
    const response = await api.post(
      `/api/review/session/${sessionId}/flashcard`,
      {
        topic,
      }
    );
    return response.data;
  },

  submitFlashcardAnswer: async (sessionId, quality, topic, cardId) => {
    const response = await api.post(
      `/api/review/session/${sessionId}/flashcard/answer`,
      {
        session_id: sessionId,
        quality,
        topic,
        card_id: cardId,
      }
    );
    return response.data;
  },

  getSession: async (sessionId) => {
    const response = await api.get(`/api/review/session/${sessionId}`);
    return response.data;
  },

  pauseSession: async (sessionId) => {
    const response = await api.put(`/api/review/session/${sessionId}/pause`);
    return response.data;
  },

  resumeSession: async (sessionId) => {
    const response = await api.put(`/api/review/session/${sessionId}/resume`);
    return response.data;
  },

  endSession: async (sessionId) => {
    const response = await api.delete(`/api/review/session/${sessionId}`);
    return response.data;
  },

  getNextQuestion: async (sessionId, topic = null) => {
    const response = await api.post(
      `/api/review/session/${sessionId}/question`,
      {
        topic,
      }
    );
    return response.data;
  },

  submitAnswer: async (sessionId, questionId, answer, timeSpent = null) => {
    const response = await api.post(`/api/review/session/${sessionId}/answer`, {
      question_id: questionId,
      answer,
      time_spent: timeSpent,
    });
    return response.data;
  },
};

export default api;
