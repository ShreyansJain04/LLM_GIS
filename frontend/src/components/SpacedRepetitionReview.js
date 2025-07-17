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
  ClockIcon,
} from "@heroicons/react/24/outline";
import ReactMarkdown from "react-markdown";
import { reviewAPI } from "../services/api";
import toast from "react-hot-toast";
import FlashcardCard from "./FlashcardCard";

const SpacedRepetitionReview = ({
  sessionId,
  onEndSession,
  onPauseSession,
}) => {
  const [session, setSession] = useState(null);
  const [currentItem, setCurrentItem] = useState(null); // holds question or flashcard
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [feedback, setFeedback] = useState(null);
  const [isCorrect, setIsCorrect] = useState(false);
  const [answer, setAnswer] = useState("");
  const [selectedOption, setSelectedOption] = useState(null);
  const [sessionState, setSessionState] = useState("active");
  const [readyForNext, setReadyForNext] = useState(false);
  const [itemIndex, setItemIndex] = useState(1); // Start at 1 for first item
  const [showFlashcardAnswer, setShowFlashcardAnswer] = useState(false);
  const [flashcardSubmitting, setFlashcardSubmitting] = useState(false);

  const maxItems = session?.max_questions || 10;

  useEffect(() => {
    loadSession();
  }, [sessionId]);

  const loadSession = async () => {
    try {
      const sessionData = await reviewAPI.getSession(sessionId);
      setSession(sessionData);
      setSessionState(sessionData.session_state);
      if (sessionData.session_state === "active") {
        await loadNextItem();
      }
    } catch (error) {
      console.error("Failed to load session:", error);
      toast.error("Failed to load spaced repetition session");
    } finally {
      setLoading(false);
    }
  };

  const loadNextItem = async () => {
    setLoading(true);
    try {
      const itemData = await reviewAPI.getNextQuestion(sessionId);
      setCurrentItem(itemData);
      setFeedback(null);
      setAnswer("");
      setSelectedOption(null);
      setShowFlashcardAnswer(false);
    } catch (error) {
      console.error("Failed to load item:", error);
      toast.error("Failed to load review item");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitAnswer = async (e) => {
    e.preventDefault();
    if (submitting) return;
    if (!currentItem) return;
    if (currentItem.type === "flashcard") return; // handled separately

    const userAnswer =
      currentItem.question?.type === "objective" ? selectedOption : answer;
    if (userAnswer === null || userAnswer === "") return;

    setSubmitting(true);
    try {
      const questionData = currentItem.question || currentItem;
      const response = await reviewAPI.submitAnswer(
        sessionId,
        questionData,
        String(userAnswer)
      );

      if (response && response.feedback !== undefined) {
        setFeedback(response.feedback);
        setIsCorrect(response.correct);
        setSession((prev) => ({
          ...prev,
          total_questions: response.total_questions,
          total_correct: response.total_correct,
          consecutive_correct: response.consecutive_correct,
          consecutive_wrong: response.consecutive_wrong,
          difficulty: response.new_difficulty,
        }));
        setReadyForNext(true);
      } else {
        toast.error("Failed to submit answer. Please try again.");
      }
    } catch (error) {
      console.error("Failed to submit answer:", error);
      toast.error("Failed to submit answer. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  // Handler for flashcard recall rating
  const handleFlashcardSelfAssessment = async (quality) => {
    if (!currentItem || !currentItem.card) return;
    setFlashcardSubmitting(true);
    try {
      console.log("sessionId", sessionId);
      console.log("currentItem card", currentItem.card);
      console.log("quality", quality, typeof quality);
      // Call backend to update flashcard schedule
      const response = await reviewAPI.submitFlashcardAnswer(
        sessionId,
        quality,
        currentItem.card.topic,
        currentItem.card.id
      );
      setShowFlashcardAnswer(false);
      setFeedback(null);
      setIsCorrect(null);
      setSession((prev) => ({
        ...prev,
        total_questions: response.total_questions,
        total_correct: response.total_correct,
      }));

      // Move to next item immediately
      handleNext();
    } catch (error) {
      console.error("Failed to submit flashcard assessment:", error);
      toast.error("Failed to submit assessment");
    } finally {
      setFlashcardSubmitting(false);
    }
  };

  const handleShowFlashcardAnswer = () => setShowFlashcardAnswer(true);

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
      await loadNextItem();
    } catch (error) {
      console.error("Failed to resume session:", error);
      toast.error("Failed to resume session");
    }
  };

  const handleEndSession = async () => {
    try {
      const result = await reviewAPI.endSession(sessionId);
      onEndSession?.(result);
      console.log("result", result);
    } catch (error) {
      console.error("Failed to end session:", error);
      toast.error("Failed to end session");
    }
  };

  const handleNext = async () => {
    setReadyForNext(false);
    setItemIndex((prev) => prev + 1);
    await loadNextItem();
  };

  const getProgressPercentage = () => {
    if (!session) return 0;
    const itemsAnswered = session.total_questions || 0;
    return (itemsAnswered / maxItems) * 100;
  };

  const getScorePercentage = () => {
    if (!session || session.total_questions === 0) return 0;
    return (session.total_correct / session.total_questions) * 100;
  };

  const getItemTypeIcon = () => {
    if (!currentItem)
      return <ChartBarIcon className="w-5 h-5 text-primary-600" />;
    return currentItem.type === "flashcard" ? (
      <ClockIcon className="w-5 h-5 text-blue-600" />
    ) : (
      <ChartBarIcon className="w-5 h-5 text-primary-600" />
    );
  };

  const getItemTypeLabel = () => {
    if (!currentItem) return "Loading...";
    return currentItem.type === "flashcard" ? "Flashcard" : "Question";
  };

  if (loading && !session) {
    return (
      <div className="space-y-6">
        {/* Session Header with Progress Bar */}
        <div className="bg-white rounded-xl shadow-sm border border-secondary-200 p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <LightBulbIcon className="w-5 h-5 text-primary-600" />
                <span className="font-medium text-secondary-900">
                  Spaced Repetition Review
                </span>
              </div>
              <div className="px-2 py-1 rounded-full text-xs font-medium text-gray-600 bg-gray-100">
                LOADING
              </div>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mt-4">
            <div className="flex justify-between text-sm text-secondary-600 mb-1">
              <span>Progress</span>
              <span>0/{maxItems} items</span>
            </div>
            <div className="w-full bg-secondary-200 rounded-full h-2">
              <div
                className="h-2 rounded-full bg-primary-600"
                style={{ width: "0%" }}
              ></div>
            </div>
            <div className="flex justify-between text-sm mt-2">
              <span className="text-secondary-600">Score: 0</span>
              <span className="font-medium text-primary-600">0%</span>
            </div>
          </div>
        </div>

        {/* Loading Content */}
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-secondary-200 rounded w-1/4"></div>
          <div className="h-64 bg-secondary-200 rounded"></div>
        </div>
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

  const isSessionComplete = session && session.total_questions >= maxItems;

  return (
    <div className="space-y-6">
      {/* Session Header */}
      <div className="bg-white rounded-xl shadow-sm border border-secondary-200 p-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <LightBulbIcon className="w-5 h-5 text-primary-600" />
              <span className="font-medium text-secondary-900">
                Spaced Repetition Review
              </span>
            </div>
            <div className="px-2 py-1 rounded-full text-xs font-medium text-blue-600 bg-blue-100">
              SPACED
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
            <span>
              {itemIndex}/{maxItems} items
            </span>
          </div>
          <div className="w-full bg-secondary-200 rounded-full h-2">
            <div
              className={`h-2 rounded-full transition-all duration-300 ${
                isSessionComplete ? "bg-green-600" : "bg-primary-600"
              }`}
              style={{ width: `${getProgressPercentage()}%` }}
            ></div>
          </div>
          <div className="flex justify-between text-sm mt-2">
            <span className="text-secondary-600">
              Score: {session?.total_correct || 0}
            </span>
            <span
              className={`font-medium ${
                isSessionComplete ? "text-green-600" : "text-primary-600"
              }`}
            >
              {isSessionComplete
                ? "Complete!"
                : `${getScorePercentage().toFixed(1)}%`}
            </span>
          </div>
        </div>
      </div>

      {/* Question or Flashcard Interface */}
      <AnimatePresence mode="wait">
        {loading && session ? (
          // Show loading indicator for next item while keeping session header
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-xl shadow-sm border border-secondary-200 p-6"
          >
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <ChartBarIcon className="w-5 h-5 text-primary-600" />
                  <span className="text-sm text-secondary-600">
                    Loading next item...
                  </span>
                </div>
                {session?.current_topic && (
                  <span className="text-sm text-secondary-500">
                    Topic: {session.current_topic}
                  </span>
                )}
              </div>

              <div className="animate-pulse space-y-4">
                <div className="h-4 bg-secondary-200 rounded w-3/4"></div>
                <div className="h-4 bg-secondary-200 rounded w-1/2"></div>
                <div className="h-4 bg-secondary-200 rounded w-2/3"></div>
                <div className="space-y-2">
                  <div className="h-12 bg-secondary-200 rounded"></div>
                  <div className="h-12 bg-secondary-200 rounded"></div>
                  <div className="h-12 bg-secondary-200 rounded"></div>
                  <div className="h-12 bg-secondary-200 rounded"></div>
                </div>
              </div>
            </div>
          </motion.div>
        ) : isSessionComplete ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-xl shadow-sm border border-secondary-200 p-6 text-center"
          >
            <CheckCircleIcon className="w-16 h-16 text-green-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-secondary-900 mb-2">
              Spaced Repetition Complete!
            </h3>
            <p className="text-secondary-600 mb-6">
              You've completed all {maxItems} items. Great job!
            </p>
            <button
              onClick={handleEndSession}
              className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700"
            >
              View Results
            </button>
          </motion.div>
        ) : currentItem && currentItem.type === "flashcard" ? (
          <FlashcardCard
            card={currentItem.card}
            loading={false}
            submitting={flashcardSubmitting}
            showAnswer={showFlashcardAnswer}
            onShowAnswer={handleShowFlashcardAnswer}
            onSelfAssessment={handleFlashcardSelfAssessment}
            progress={{ current: itemIndex, total: maxItems }}
          />
        ) : (
          currentItem && (
            <motion.div
              key={itemIndex}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="bg-white rounded-xl shadow-sm border border-secondary-200 p-6"
            >
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    {getItemTypeIcon()}
                    <span className="text-sm text-secondary-600">
                      {getItemTypeLabel()} {itemIndex}/{maxItems}
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
                    {currentItem.question?.text ||
                      currentItem.text ||
                      currentItem}
                  </ReactMarkdown>
                </div>

                <form onSubmit={handleSubmitAnswer} className="space-y-4">
                  {currentItem.question?.type === "objective" &&
                  currentItem.question?.options ? (
                    <div className="space-y-2">
                      {currentItem.question.options.map((option, index) => (
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
                      (currentItem.question?.type === "objective"
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

                {/* Next Item button appears only after feedback is shown and not at session end */}
                {readyForNext && !isSessionComplete && (
                  <button
                    onClick={handleNext}
                    className="mt-4 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
                    disabled={loading}
                  >
                    Next Item
                  </button>
                )}
              </div>
            </motion.div>
          )
        )}
      </AnimatePresence>
    </div>
  );
};

export default SpacedRepetitionReview;
