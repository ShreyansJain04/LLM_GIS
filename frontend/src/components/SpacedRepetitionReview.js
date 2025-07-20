import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  PauseIcon,
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
  const [dueItems, setDueItems] = useState([]);

  const maxItems = session?.max_questions || 10;

  // Simplified: always pop the first due item, and for questions call getNextQuestion
  const loadAndSetNextItem = async (items) => {
    console.log("[DEBUG] dueItems before processing:", items);
    if (!items || items.length === 0) {
      setCurrentItem(null);
      // Optionally call handleEndSession() or show a completion message here
      handleEndSession();
      return;
    }
    const [next, ...rest] = items;
    setDueItems(rest);
    setItemIndex((prev) => prev + 1);
    setReadyForNext(false);
    setAnswer("");
    setSelectedOption(null);
    setShowFlashcardAnswer(false);
    setFeedback(null);
    setIsCorrect(false);
    if (next.type === "flashcard") {
      setCurrentItem(next);
    } else if (next.type === "question") {
      setLoading(true);
      try {
        console.log(
          "[DEBUG] Calling getNextQuestion with sessionId:",
          sessionId
        );
        const questionData = await reviewAPI.getNextQuestion(sessionId);
        console.log("[DEBUG] getNextQuestion response:", questionData);
        setCurrentItem(questionData);
      } catch (error) {
        console.error("[ERROR] Failed to load next question:", error);
        toast.error("Failed to load next question");
      } finally {
        setLoading(false);
      }
    } else {
      // Unknown type, just skip
      setCurrentItem(null);
    }
  };

  // On initial load, load the first item
  useEffect(() => {
    const init = async () => {
      await loadSession();
      if (sessionState === "active" && dueItems.length > 0) {
        await loadAndSetNextItem(dueItems);
      }
    };
    init();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sessionId]);

  const loadSession = async () => {
    try {
      console.log("[DEBUG] Calling getSession with sessionId:", sessionId);
      const sessionData = await reviewAPI.getSession(sessionId);
      console.log("[DEBUG] getSession response:", sessionData);
      setSession(sessionData);
      setSessionState(sessionData.session_state);
      if (
        sessionData.session_state === "active" &&
        sessionData.due_items &&
        sessionData.due_items.length > 0
      ) {
        setDueItems(sessionData.due_items);
        setCurrentItem(sessionData.due_items[0]);
      } else if (
        sessionData.session_state === "active" &&
        (!sessionData.due_items || sessionData.due_items.length === 0)
      ) {
        toast("There are no due items for review at this time.");
      }
    } catch (error) {
      console.error("[ERROR] Failed to load session:", error);
      toast.error("Failed to load spaced repetition session");
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
      console.log("[DEBUG] Submitting answer:", {
        sessionId,
        questionData,
        userAnswer,
      });
      const response = await reviewAPI.submitAnswer(
        sessionId,
        questionData,
        String(userAnswer)
      );
      console.log("[DEBUG] submitAnswer response:", response);

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
      console.error("[ERROR] Failed to submit answer:", error);
      toast.error("Failed to submit answer. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleFlashcardSelfAssessment = async (quality) => {
    if (!currentItem || !currentItem.card) return;
    setFlashcardSubmitting(true);
    try {
      console.log("[DEBUG] Submitting flashcard assessment:", {
        sessionId,
        quality,
        topic: currentItem.card.topic,
        cardId: currentItem.card.id,
      });
      const response = await reviewAPI.submitFlashcardAnswer(
        sessionId,
        quality,
        currentItem.card.topic,
        currentItem.card.id
      );
      console.log("[DEBUG] submitFlashcardAnswer response:", response);
      setShowFlashcardAnswer(false);
      setFeedback(null);
      setIsCorrect(null);
      // Move to next item in the queue
      loadAndSetNextItem(dueItems);
    } catch (error) {
      console.error("[ERROR] Failed to submit assessment:", error);
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
      await loadSession(); // Reload session to get new due items
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

  // Next item handler
  const handleNext = () => {
    loadAndSetNextItem(dueItems);
  };

  const getProgressPercentage = () => {
    if (!session) return 0;
    const itemsAnswered = session.total_questions || 0;
    return (itemsAnswered / maxItems) * 100;
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

  // In the completion UI, use session.total_correct and session.total_questions directly
  // Replace any use of displayTotalCorrect, displayTotalQuestions, displayScore with session.total_correct, session.total_questions, and their calculation

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

  if (
    session &&
    sessionState === "active" &&
    Array.isArray(session.due_items) &&
    session.due_items.length === 0
  ) {
    return (
      <div className="flex flex-col items-center text-center justify-center py-16">
        <CheckCircleIcon className="w-16 h-16 text-green-400 mb-4" />
        <h2 className="text-2xl font-semibold text-secondary-900 mb-2">
          No items due for review!
        </h2>
        <p className="text-secondary-600 mb-6">
          You have completed all your scheduled reviews. Check back later for
          new items!
        </p>
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
                : `${(
                    ((session?.total_correct || 0) /
                      (session?.total_questions || 1)) *
                    100
                  ).toFixed(1)}%`}
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
        ) : (
          currentItem &&
          (currentItem.type === "flashcard" ? (
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
                    <ChartBarIcon className="w-5 h-5 text-primary-600" />
                    <span className="text-sm text-secondary-600">
                      Question {itemIndex}/{maxItems}
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

                {/* Next Item button appears only after feedback is shown */}
                {readyForNext && (
                  <button
                    onClick={isSessionComplete ? handleEndSession : handleNext}
                    className="mt-4 bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700"
                    disabled={loading}
                  >
                    {isSessionComplete ? "See Results" : "Next Item"}
                  </button>
                )}
              </div>
            </motion.div>
          ))
        )}
      </AnimatePresence>
    </div>
  );
};

export default SpacedRepetitionReview;
