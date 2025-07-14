import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  AcademicCapIcon,
  ChartBarIcon,
  CheckCircleIcon,
  XCircleIcon,
  LightBulbIcon,
  ArrowPathIcon,
  BookmarkIcon,
} from "@heroicons/react/24/outline";
import ReactMarkdown from "react-markdown";
import { useUser } from "../contexts/UserContext";
import { contentAPI, userAPI } from "../services/api";
import toast from "react-hot-toast";

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
  const [answer, setAnswer] = useState("");
  const [selectedOption, setSelectedOption] = useState(null);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (question.type === "objective") {
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
          {question.type === "objective" ? (
            <div className="space-y-2">
              {question.options.map((option, index) => (
                <button
                  key={index}
                  type="button"
                  onClick={() => setSelectedOption(index)}
                  className={`w-full text-left p-3 rounded-lg border ${
                    selectedOption === index
                      ? "border-primary-500 bg-primary-50 text-primary-700"
                      : "border-secondary-200 hover:bg-secondary-50"
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
            disabled={
              loading || feedback || (!answer && selectedOption === null)
            }
            className="w-full py-2 px-4 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
          >
            {loading ? "Checking..." : "Submit Answer"}
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
                  ? "bg-green-50 border border-green-200"
                  : "bg-red-50 border border-red-200"
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
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedMode, setSelectedMode] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [sessionResult, setSessionResult] = useState(null);

  useEffect(() => {
    if (user?.username) {
      loadReviewInsights();
    }
  }, [user]);

  const loadReviewInsights = async () => {
    try {
      const insights = await userAPI.getUserInsights(user.username);
      const topics = insights.personalized_recommendations?.focus_areas || [];
      setWeakTopics(topics);

      // Initialize progress
      const progressMap = {};
      topics.forEach((topic) => {
        progressMap[topic.topic] = topic.mastery || 0;
      });
      setProgress(progressMap);
    } catch (error) {
      console.error("Failed to load weak topics:", error);
      toast.error("Failed to load review topics");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectMode = async (mode) => {
    setLoading(true);
    try {
      const response = await contentAPI.generateQuestion(topic);
      setCurrentQuestion(response.question);
      setFeedback(null);
    } catch (error) {
      console.error("Failed to load question:", error);
      toast.error("Failed to load question");
    } finally {
      setLoading(false);
    }
  };

  const handleAnswer = async (answer) => {
    try {
      // Create a clean question object with only the fields the backend expects
      const cleanQuestion = {
        text: currentQuestion.text,
        type: currentQuestion.type,
        options: currentQuestion.options || [],
        correct_option: currentQuestion.correct_option || 0,
        explanation: currentQuestion.explanation || "",
      };

      const result = await contentAPI.checkAnswer(cleanQuestion, answer);
      setFeedback(result.feedback);
      setIsCorrect(result.correct);

      // Update progress
      if (result.correct) {
        setProgress((prev) => ({
          ...prev,
          [selectedTopic]: Math.min(1, (prev[selectedTopic] || 0) + 0.1),
        }));
      }

      // Load next question after delay
      setTimeout(() => {
        loadQuestion(selectedTopic);
      }, 2000);
    } catch (error) {
      console.error("Failed to check answer:", error);
      toast.error("Failed to check answer");
    }
  };

  // Show session results
  if (sessionResult) {
    return (
      <div className="p-6 max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-xl shadow-sm border border-secondary-200 p-8 text-center"
        >
          <div className="mb-6">
            <TrophyIcon className="w-16 h-16 text-primary-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-secondary-900 mb-2">
              Review Session Complete!
            </h2>
            <p className="text-secondary-600">
              Great job completing your review session
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="text-center">
              <div className="text-3xl font-bold text-primary-600">
                {(sessionResult.final_score * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-secondary-600">Final Score</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-secondary-900">
                {sessionResult.total_questions}
              </div>
              <div className="text-sm text-secondary-600">
                Questions Answered
              </div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-green-600">
                {sessionResult.total_correct}
              </div>
              <div className="text-sm text-secondary-600">Correct Answers</div>
            </div>
          </div>

          <div className="mb-8">
            <div
              className={`inline-block px-4 py-2 rounded-full text-sm font-medium ${getMasteryLevelColor(
                sessionResult.mastery_level
              )}`}
            >
              {sessionResult.mastery_level.toUpperCase()} LEVEL
            </div>
          </div>

          <div className="space-x-4">
            <button
              onClick={handleBackToModeSelection}
              className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700"
            >
              Start Another Review
            </button>
            <button
              onClick={() => window.history.back()}
              className="bg-secondary-200 text-secondary-700 px-6 py-2 rounded-lg hover:bg-secondary-300"
            >
              Back to Dashboard
            </button>
          </div>
        </motion.div>
      </div>
    );
  }

  // Show active session
  if (sessionId && selectedMode) {
    return (
      <div className="p-6 max-w-4xl mx-auto">
        <div className="mb-6">
          <button
            onClick={handleBackToModeSelection}
            className="flex items-center space-x-2 text-primary-600 hover:text-primary-700 mb-4"
          >
            <ArrowPathIcon className="w-5 h-5" />
            <span>Change Review Mode</span>
          </button>
        </div>

        <ReviewSession
          sessionId={sessionId}
          mode={selectedMode}
          onEndSession={handleEndSession}
          onPauseSession={handlePauseSession}
        />
      </div>
    );
  }

  // Show mode selection
  return (
    <div className="p-6 max-w-7xl mx-auto">
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-secondary-900">
              Review Mode
            </h1>
            <p className="text-secondary-600">
              Choose how you'd like to review your weak areas and improve your
              understanding
            </p>
          </div>
        </div>
      </div>

      <ReviewModeSelector
        onSelectMode={handleSelectMode}
        insights={insights}
        loading={loading}
      />
    </div>
  );
};

export default Review;
