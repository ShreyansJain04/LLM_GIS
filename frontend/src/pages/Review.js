import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  AcademicCapIcon,
  ChartBarIcon,
  CheckCircleIcon,
  XCircleIcon,
  LightBulbIcon,
  ArrowPathIcon,
  BookmarkIcon,
} from '@heroicons/react/24/outline';
import ReactMarkdown from 'react-markdown';
import { useUser } from '../contexts/UserContext';
import { contentAPI, userAPI } from '../services/api';
import toast from 'react-hot-toast';

const ReviewCard = ({ topic, progress, onSelect }) => (
  <motion.div
    whileHover={{ scale: 1.02 }}
    className="bg-white rounded-xl shadow-sm border border-secondary-200 p-4 cursor-pointer"
    onClick={() => onSelect(topic)}
  >
    <div className="flex items-start justify-between">
      <div className="flex items-center space-x-3">
        <div className="p-2 bg-primary-100 rounded-lg">
          <BookmarkIcon className="w-5 h-5 text-primary-600" />
        </div>
        <div>
          <h3 className="font-medium text-secondary-900">{topic}</h3>
          <p className="text-sm text-secondary-600">
            Mastery: {Math.round(progress * 100)}%
          </p>
        </div>
      </div>
      <div className="w-16 h-16">
        <svg className="transform -rotate-90">
          <circle
            cx="32"
            cy="32"
            r="28"
            stroke="#E2E8F0"
            strokeWidth="4"
            fill="none"
          />
          <circle
            cx="32"
            cy="32"
            r="28"
            stroke="#4F46E5"
            strokeWidth="4"
            fill="none"
            strokeDasharray={`${progress * 175.93} 175.93`}
            strokeLinecap="round"
          />
        </svg>
      </div>
    </div>
  </motion.div>
);

const QuestionCard = ({ question, onAnswer, loading, feedback, isCorrect }) => {
  const [answer, setAnswer] = useState('');
  const [selectedOption, setSelectedOption] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (question.type === 'objective') {
      onAnswer(selectedOption);
    } else {
      onAnswer(answer);
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-white rounded-xl shadow-sm border border-secondary-200 p-6"
    >
      <div className="space-y-4">
        <div className="flex items-center space-x-2">
          <LightBulbIcon className="w-5 h-5 text-yellow-500" />
          <h3 className="text-lg font-medium text-secondary-900">Question</h3>
        </div>

        <div className="prose prose-sm max-w-none">
          <ReactMarkdown>{question.text}</ReactMarkdown>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {question.type === 'objective' ? (
            <div className="space-y-2">
              {question.options.map((option, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => setSelectedOption(index)}
                  className={`w-full text-left p-3 rounded-lg border ${
                    selectedOption === index
                      ? 'border-primary-500 bg-primary-50 text-primary-700'
                      : 'border-secondary-200 hover:bg-secondary-50'
                  }`}
                  disabled={loading || feedback}
                >
                  {option}
                </button>
              ))}
            </div>
          ) : (
            <textarea
              value={answer}
              onChange={(e) => setAnswer(e.target.value)}
              placeholder="Type your answer here..."
              className="w-full h-32 p-3 rounded-lg border border-secondary-200 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              disabled={loading || feedback}
            />
          )}

          <button
            type="submit"
            disabled={loading || feedback || (!answer && selectedOption === null)}
            className="w-full py-2 px-4 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
          >
            {loading ? 'Checking...' : 'Submit Answer'}
          </button>
        </form>

        <AnimatePresence>
          {feedback && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className={`p-4 rounded-lg ${
                isCorrect
                  ? 'bg-green-50 border border-green-200'
                  : 'bg-red-50 border border-red-200'
              }`}
            >
              <div className="flex items-start space-x-2">
                {isCorrect ? (
                  <CheckCircleIcon className="w-5 h-5 text-green-500 flex-shrink-0" />
                ) : (
                  <XCircleIcon className="w-5 h-5 text-red-500 flex-shrink-0" />
                )}
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown>{feedback}</ReactMarkdown>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

const Review = () => {
  const { user } = useUser();
  const [weakTopics, setWeakTopics] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [loading, setLoading] = useState(true);
  const [feedback, setFeedback] = useState(null);
  const [isCorrect, setIsCorrect] = useState(false);
  const [progress, setProgress] = useState({});

  useEffect(() => {
    if (user?.username) {
      loadWeakTopics();
    }
  }, [user]);

  const loadWeakTopics = async () => {
    try {
      const insights = await userAPI.getUserInsights(user.username);
      const topics = insights.personalized_recommendations?.focus_areas || [];
      setWeakTopics(topics);
      
      // Initialize progress
      const progressMap = {};
      topics.forEach(topic => {
        progressMap[topic.topic] = topic.mastery || 0;
      });
      setProgress(progressMap);
      
    } catch (error) {
      console.error('Failed to load weak topics:', error);
      toast.error('Failed to load review topics');
    } finally {
      setLoading(false);
    }
  };

  const handleTopicSelect = async (topic) => {
    setSelectedTopic(topic);
    await loadQuestion(topic);
  };

  const loadQuestion = async (topic) => {
    setLoading(true);
    try {
      const question = await contentAPI.generateQuestion(topic);
      setCurrentQuestion(question);
      setFeedback(null);
    } catch (error) {
      console.error('Failed to load question:', error);
      toast.error('Failed to load question');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = async (answer) => {
    try {
      const result = await contentAPI.checkAnswer(currentQuestion, answer);
      setFeedback(result.feedback);
      setIsCorrect(result.correct);

      // Update progress
      if (result.correct) {
        setProgress(prev => ({
          ...prev,
          [selectedTopic]: Math.min(1, (prev[selectedTopic] || 0) + 0.1)
        }));
      }

      // Load next question after delay
      setTimeout(() => {
        loadQuestion(selectedTopic);
      }, 2000);

    } catch (error) {
      console.error('Failed to check answer:', error);
      toast.error('Failed to check answer');
    }
  };

  if (loading && !selectedTopic) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-secondary-200 rounded w-1/4"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-secondary-200 rounded"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-secondary-900">Review Mode</h1>
            <p className="text-secondary-600">
              Focus on your weak areas and improve your understanding
            </p>
          </div>
          {selectedTopic && (
            <button
              onClick={() => setSelectedTopic(null)}
              className="flex items-center space-x-2 text-primary-600 hover:text-primary-700"
            >
              <ArrowPathIcon className="w-5 h-5" />
              <span>Change Topic</span>
            </button>
          )}
        </div>
      </div>

      {!selectedTopic ? (
        <div className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {weakTopics.map((topic, index) => (
              <ReviewCard
                key={index}
                topic={topic.topic}
                progress={progress[topic.topic] || 0}
                onSelect={handleTopicSelect}
              />
            ))}
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <h2 className="text-xl font-semibold text-secondary-900">
              Reviewing: {selectedTopic}
            </h2>
            <div className="flex items-center space-x-2">
              <ChartBarIcon className="w-5 h-5 text-primary-600" />
              <span className="text-secondary-700">
                Progress: {Math.round((progress[selectedTopic] || 0) * 100)}%
              </span>
            </div>
          </div>

          {currentQuestion && (
            <QuestionCard
              question={currentQuestion}
              onAnswer={handleAnswer}
              loading={loading}
              feedback={feedback}
              isCorrect={isCorrect}
            />
          )}
        </div>
      )}
    </div>
  );
};

export default Review; 