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
  PlayIcon,
  ClockIcon,
  StarIcon,
  CogIcon,
} from "@heroicons/react/24/outline";
import ReactMarkdown from "react-markdown";
import { useUser } from "../contexts/UserContext";
import { contentAPI, userAPI, reviewAPI } from "../services/api";
import toast from "react-hot-toast";

// Review Mode Selector Component
const ReviewModeSelector = ({ onModeSelect, insights }) => {
  const modes = [
    {
      id: "adaptive",
      title: "Adaptive Review",
      description: "AI adjusts difficulty based on your performance",
      icon: AcademicCapIcon,
      color: "bg-blue-500",
      recommended: true,
    },
    {
      id: "spaced",
      title: "Spaced Repetition",
      description: "Review items due for spaced repetition",
      icon: ClockIcon,
      color: "bg-green-500",
    },
    {
      id: "flashcard",
      title: "Flashcard Review",
      description: "Review with flashcards and spaced repetition",
      icon: BookmarkIcon,
      color: "bg-purple-500",
    },
    {
      id: "intensive",
      title: "Intensive Focus",
      description: "Deep dive into your weakest areas",
      icon: StarIcon,
      color: "bg-orange-500",
    },
  ];

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-secondary-900 mb-2">
          Choose Review Mode
        </h2>
        <p className="text-secondary-600">
          Select the review mode that best fits your learning goals
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {modes.map((mode) => {
          const IconComponent = mode.icon;
          return (
            <motion.div
              key={mode.id}
              whileHover={{ scale: 1.02 }}
              className={`relative bg-white rounded-xl shadow-sm border-2 cursor-pointer transition-all ${
                mode.recommended
                  ? "border-primary-500 bg-primary-50"
                  : "border-secondary-200 hover:border-primary-300"
              }`}
              onClick={() => onModeSelect(mode.id)}
            >
              {mode.recommended && (
                <div className="absolute -top-2 -right-2 bg-primary-500 text-white text-xs px-2 py-1 rounded-full">
                  Recommended
                </div>
              )}
              <div className="p-6">
                <div className="flex items-start space-x-4">
                  <div className={`p-3 rounded-lg ${mode.color} text-white`}>
                    <IconComponent className="w-6 h-6" />
                  </div>
                  <div className="flex-1">
                    <h3 className="font-semibold text-secondary-900 mb-1">
                      {mode.title}
                    </h3>
                    <p className="text-sm text-secondary-600">
                      {mode.description}
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {insights && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-start space-x-3">
            <ChartBarIcon className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-medium text-blue-900 mb-2">
                Review Insights
              </h4>
              <div className="text-sm text-blue-700 space-y-1">
                <p>• {insights.weak_areas_count} weak areas identified</p>
                <p>• {insights.due_items_count} items due for review</p>
                <p>• Recommended focus: {insights.recommended_focus}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Review Session Component
const ReviewSession = ({
  session,
  onEndSession,
  onNextQuestion,
  onAnswerSubmit,
}) => {
  const [currentAnswer, setCurrentAnswer] = useState("");
  const [selectedOption, setSelectedOption] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);
  const [feedback, setFeedback] = useState(null);

  const handleAnswerSubmit = async () => {
    if (!currentAnswer && selectedOption === null) return;

    setIsSubmitting(true);
    try {
      const answer =
        session.current_question.type === "objective"
          ? selectedOption
          : currentAnswer;

      const result = await onAnswerSubmit(answer);
      setFeedback(result);
      setShowFeedback(true);

      // Auto-advance after delay
      setTimeout(() => {
        setShowFeedback(false);
        setCurrentAnswer("");
        setSelectedOption(null);
        onNextQuestion();
      }, 3000);
    } catch (error) {
      toast.error("Failed to submit answer");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !isSubmitting) {
      handleAnswerSubmit();
    }
  };

  return (
    <div className="space-y-6">
      {/* Session Header */}
      <div className="bg-white rounded-xl shadow-sm border border-secondary-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="p-2 bg-primary-100 rounded-lg">
              <PlayIcon className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <h3 className="font-semibold text-secondary-900">
                {session.mode} Review Session
              </h3>
              <p className="text-sm text-secondary-600">
                Question {session.current_question_index + 1} of{" "}
                {session.total_questions}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-right">
              <p className="text-sm font-medium text-secondary-900">
                Score: {session.correct_answers}/{session.total_questions}
              </p>
              <p className="text-xs text-secondary-600">
                {Math.round(
                  (session.correct_answers / session.total_questions) * 100
                )}
                % accuracy
              </p>
            </div>
            <button
              onClick={onEndSession}
              className="px-3 py-1 text-sm text-red-600 hover:text-red-700 border border-red-200 hover:border-red-300 rounded-lg transition-colors"
            >
              End Session
            </button>
          </div>
        </div>
      </div>

      {/* Question Card */}
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
            <ReactMarkdown>{session.current_question.text}</ReactMarkdown>
          </div>

          <div className="space-y-4">
            {session.current_question.type === "objective" ? (
              <div className="space-y-2">
                {session.current_question.options.map((option, index) => (
                  <button
                    key={index}
                    type="button"
                    onClick={() => setSelectedOption(index)}
                    className={`w-full text-left p-3 rounded-lg border transition-colors ${
                      selectedOption === index
                        ? "border-primary-500 bg-primary-50 text-primary-700"
                        : "border-secondary-200 hover:bg-secondary-50"
                    }`}
                    disabled={isSubmitting || showFeedback}
                  >
                    {option}
                  </button>
                ))}
              </div>
            ) : (
              <textarea
                value={currentAnswer}
                onChange={(e) => setCurrentAnswer(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Type your answer here..."
                className="w-full h-32 p-3 rounded-lg border border-secondary-200 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                disabled={isSubmitting || showFeedback}
              />
            )}

            <button
              onClick={handleAnswerSubmit}
              disabled={
                isSubmitting ||
                showFeedback ||
                (!currentAnswer && selectedOption === null)
              }
              className="w-full py-3 px-4 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 transition-colors"
            >
              {isSubmitting ? "Checking..." : "Submit Answer"}
            </button>
          </div>

          <AnimatePresence>
            {showFeedback && feedback && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className={`p-4 rounded-lg ${
                  feedback.correct
                    ? "bg-green-50 border border-green-200"
                    : "bg-red-50 border border-red-200"
                }`}
              >
                <div className="flex items-start space-x-2">
                  {feedback.correct ? (
                    <CheckCircleIcon className="w-5 h-5 text-green-500 flex-shrink-0" />
                  ) : (
                    <XCircleIcon className="w-5 h-5 text-red-500 flex-shrink-0" />
                  )}
                  <div className="prose prose-sm max-w-none">
                    <ReactMarkdown>{feedback.feedback}</ReactMarkdown>
                  </div>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>
    </div>
  );
};

// Main Review Component
const Review = () => {
  const { user } = useUser();
  const [insights, setInsights] = useState(null);
  const [selectedMode, setSelectedMode] = useState(null);
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.username) {
      loadReviewInsights();
    }
  }, [user]);

  const loadReviewInsights = async () => {
    try {
      const userInsights = await userAPI.getUserInsights(user.username);
      const reviewInsights = await reviewAPI.getReviewInsights(user.username);

      setInsights({
        ...userInsights,
        ...reviewInsights,
      });
    } catch (error) {
      console.error("Failed to load review insights:", error);
      toast.error("Failed to load review insights");
    } finally {
      setLoading(false);
    }
  };

  const handleModeSelect = async (mode) => {
    setLoading(true);
    try {
      const sessionData = await reviewAPI.startReviewSession(
        user.username,
        mode
      );
      setSession(sessionData);
      setSelectedMode(mode);
    } catch (error) {
      console.error("Failed to start review session:", error);
      toast.error("Failed to start review session");
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerSubmit = async (answer) => {
    try {
      const result = await reviewAPI.submitAnswer(session.session_id, answer);

      // Update session state
      setSession((prev) => ({
        ...prev,
        correct_answers: prev.correct_answers + (result.correct ? 1 : 0),
        total_questions: prev.total_questions + 1,
      }));

      return result;
    } catch (error) {
      console.error("Failed to submit answer:", error);
      toast.error("Failed to submit answer");
      throw error;
    }
  };

  const handleNextQuestion = async () => {
    try {
      const nextQuestion = await reviewAPI.getNextQuestion(session.session_id);
      setSession((prev) => ({
        ...prev,
        current_question: nextQuestion.question,
        current_question_index: prev.current_question_index + 1,
      }));
    } catch (error) {
      console.error("Failed to get next question:", error);
      toast.error("Failed to load next question");
    }
  };

  const handleEndSession = async () => {
    try {
      await reviewAPI.endReviewSession(session.session_id);
      setSession(null);
      setSelectedMode(null);
      await loadReviewInsights(); // Refresh insights
      toast.success("Review session completed!");
    } catch (error) {
      console.error("Failed to end session:", error);
      toast.error("Failed to end session");
    }
  };

  if (loading) {
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
            <h1 className="text-2xl font-bold text-secondary-900">
              Review Mode
            </h1>
            <p className="text-secondary-600">
              Choose your review mode and improve your understanding
            </p>
          </div>
          {session && (
            <button
              onClick={() => {
                setSession(null);
                setSelectedMode(null);
              }}
              className="flex items-center space-x-2 text-primary-600 hover:text-primary-700"
            >
              <ArrowPathIcon className="w-5 h-5" />
              <span>Change Mode</span>
            </button>
          )}
        </div>
      </div>

      {!session ? (
        <ReviewModeSelector
          onModeSelect={handleModeSelect}
          insights={insights}
        />
      ) : (
        <ReviewSession
          session={session}
          onEndSession={handleEndSession}
          onNextQuestion={handleNextQuestion}
          onAnswerSubmit={handleAnswerSubmit}
        />
      )}
    </div>
  );
};

export default Review;
