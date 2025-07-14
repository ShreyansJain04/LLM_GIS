import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  PauseIcon,
  PlayIcon,
  XMarkIcon,
  ChartBarIcon,
  LightBulbIcon,
  CheckCircleIcon,
  XCircleIcon,
} from "@heroicons/react/24/outline";
import ReactMarkdown from "react-markdown";
import { reviewAPI } from "../services/api";
import toast from "react-hot-toast";

const ReviewSession = ({ sessionId, mode, onEndSession, onPauseSession }) => {
  const [session, setSession] = useState(null);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [isCorrect, setIsCorrect] = useState(false);
  const [answer, setAnswer] = useState("");
  const [selectedOption, setSelectedOption] = useState(null);
  const [sessionState, setSessionState] = useState("active");

  useEffect(() => {
    loadSession();
  }, [sessionId]);

  const loadSession = async () => {
    try {
      const sessionData = await reviewAPI.getSession(sessionId);
      setSession(sessionData);
      setSessionState(sessionData.session_state);

      if (sessionData.session_state === "active") {
        await loadNextQuestion();
      }
    } catch (error) {
      console.error("Failed to load session:", error);
      toast.error("Failed to load review session");
    } finally {
      setLoading(false);
    }
  };

  const loadNextQuestion = async () => {
    setLoading(true);
    try {
      const questionData = await reviewAPI.getNextQuestion(sessionId);
      setCurrentQuestion(questionData);
      setFeedback(null);
      setAnswer("");
      setSelectedOption(null);
    } catch (error) {
      console.error("Failed to load question:", error);
      toast.error("Failed to load question");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitAnswer = async (e) => {
    e.preventDefault();
    if (submitting) return;

    const userAnswer =
      currentQuestion.question?.type === "objective" ? selectedOption : answer;
    if (userAnswer === null || userAnswer === "") return;

    setSubmitting(true);
    try {
      // Send the full question object to the API
      const questionData = currentQuestion.question || currentQuestion;
      console.log("ReviewSession.js sessionId", sessionId);
      console.log("ReviewSession.js questionData", questionData);
      console.log("ReviewSession.js userAnswer", userAnswer);
      const result = await reviewAPI.submitAnswer(
        sessionId,
        questionData,
        String(userAnswer)
      );

      setFeedback(result.feedback);
      setIsCorrect(result.correct);

      // Update session state
      setSession((prev) => ({
        ...prev,
        total_questions: result.total_questions,
        total_correct: result.total_correct,
        consecutive_correct: result.consecutive_correct,
        consecutive_wrong: result.consecutive_wrong,
        difficulty: result.new_difficulty,
      }));

      // Load next question after delay
      setTimeout(() => {
        loadNextQuestion();
      }, 2000);
    } catch (error) {
      console.error("Failed to submit answer:", error);
      toast.error("Failed to submit answer");
    } finally {
      setSubmitting(false);
    }
  };

  const handlePauseSession = async () => {
    try {
      await reviewAPI.pauseSession(sessionId);
      setSessionState("paused");
      onPauseSession?.();
    } catch (error) {
      console.error("Failed to pause session:", error);
      toast.error("Failed to pause session");
    }
  };

  const handleResumeSession = async () => {
    try {
      await reviewAPI.resumeSession(sessionId);
      setSessionState("active");
      await loadNextQuestion();
    } catch (error) {
      console.error("Failed to resume session:", error);
      toast.error("Failed to resume session");
    }
  };

  const handleEndSession = async () => {
    try {
      const result = await reviewAPI.endSession(sessionId);
      onEndSession?.(result);
    } catch (error) {
      console.error("Failed to end session:", error);
      toast.error("Failed to end session");
    }
  };

  const getProgressPercentage = () => {
    if (!session || session.total_questions === 0) return 0;
    return (session.total_correct / session.total_questions) * 100;
  };

  const getDifficultyColor = (difficulty) => {
    switch (difficulty) {
      case "easy":
        return "text-green-600 bg-green-100";
      case "medium":
        return "text-yellow-600 bg-yellow-100";
      case "hard":
        return "text-red-600 bg-red-100";
      default:
        return "text-gray-600 bg-gray-100";
    }
  };

  if (loading && !session) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-8 bg-secondary-200 rounded w-1/4"></div>
        <div className="h-64 bg-secondary-200 rounded"></div>
      </div>
    );
  }

  if (sessionState === "paused") {
    return (
      <div className="text-center py-12">
        <PauseIcon className="w-16 h-16 text-secondary-400 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-secondary-900 mb-2">
          Session Paused
        </h3>
        <p className="text-secondary-600 mb-6">Your progress has been saved.</p>
        <button
          onClick={handleResumeSession}
          className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700"
        >
          Resume Session
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Session Header */}
      <div className="bg-white rounded-xl shadow-sm border border-secondary-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <LightBulbIcon className="w-5 h-5 text-primary-600" />
              <span className="font-medium text-secondary-900">
                {mode.charAt(0).toUpperCase() + mode.slice(1)} Review
              </span>
            </div>
            <div
              className={`px-2 py-1 rounded-full text-xs font-medium ${getDifficultyColor(
                session?.difficulty
              )}`}
            >
              {session?.difficulty?.toUpperCase() || "MEDIUM"}
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handlePauseSession}
              className="p-2 text-secondary-600 hover:text-secondary-800 hover:bg-secondary-100 rounded-lg"
            >
              <PauseIcon className="w-5 h-5" />
            </button>
            <button
              onClick={handleEndSession}
              className="p-2 text-red-600 hover:text-red-800 hover:bg-red-100 rounded-lg"
            >
              <XMarkIcon className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="mt-4">
          <div className="flex justify-between text-sm text-secondary-600 mb-1">
            <span>Progress</span>
            <span>{session?.total_questions || 0} questions</span>
          </div>
          <div className="w-full bg-secondary-200 rounded-full h-2">
            <div
              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${getProgressPercentage()}%` }}
            ></div>
          </div>
          <div className="flex justify-between text-sm mt-2">
            <span className="text-secondary-600">
              Score: {session?.total_correct || 0}/
              {session?.total_questions || 0}
            </span>
            <span className="text-primary-600 font-medium">
              {getProgressPercentage().toFixed(1)}%
            </span>
          </div>
        </div>
      </div>

      {/* Question Interface */}
      <AnimatePresence mode="wait">
        {currentQuestion && (
          <motion.div
            key={currentQuestion.id || currentQuestion}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="bg-white rounded-xl shadow-sm border border-secondary-200 p-6"
          >
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <ChartBarIcon className="w-5 h-5 text-primary-600" />
                  <span className="text-sm text-secondary-600">
                    Question {session?.total_questions + 1}
                  </span>
                </div>
                {session?.current_topic && (
                  <span className="text-sm text-secondary-500">
                    Topic: {session.current_topic}
                  </span>
                )}
              </div>

              <div className="prose prose-sm max-w-none">
                <ReactMarkdown>
                  {currentQuestion.question?.text ||
                    currentQuestion.text ||
                    currentQuestion}
                </ReactMarkdown>
              </div>

              <form onSubmit={handleSubmitAnswer} className="space-y-4">
                {currentQuestion.question?.type === "objective" &&
                currentQuestion.question?.options ? (
                  <div className="space-y-2">
                    {currentQuestion.question.options.map((option, index) => (
                      <button
                        key={index}
                        type="button"
                        onClick={() => setSelectedOption(index)}
                        className={`w-full text-left p-3 rounded-lg border transition-all ${
                          selectedOption === index
                            ? "border-primary-500 bg-primary-50 text-primary-700"
                            : "border-secondary-200 hover:bg-secondary-50"
                        }`}
                        disabled={submitting || feedback}
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
                    disabled={submitting || feedback}
                  />
                )}

                <button
                  type="submit"
                  disabled={
                    submitting ||
                    feedback ||
                    (currentQuestion.question?.type === "objective"
                      ? selectedOption === null
                      : !answer)
                  }
                  className="w-full py-2 px-4 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
                >
                  {submitting ? "Checking..." : "Submit Answer"}
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
                        <ReactMarkdown>
                          {typeof feedback === "string"
                            ? feedback
                            : JSON.stringify(feedback)}
                        </ReactMarkdown>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default ReviewSession;
