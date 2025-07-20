import React, { useState, useEffect, useCallback } from "react";
import { AnimatePresence } from "framer-motion";
import { LightBulbIcon, XMarkIcon } from "@heroicons/react/24/outline";
import { reviewAPI } from "../services/api";
import toast from "react-hot-toast";
import FlashcardCard from "./FlashcardCard";

const FlashcardReview = ({ sessionId, onEndSession, onPauseSession }) => {
  const [session, setSession] = useState(null);
  const [currentCard, setCurrentCard] = useState(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [showAnswer, setShowAnswer] = useState(false);
  const [sessionState, setSessionState] = useState("active");

  const handleEndSession = useCallback(async () => {
    try {
      const result = await reviewAPI.endSession(sessionId);
      onEndSession?.(result);
    } catch (error) {
      console.error("Failed to end session:", error);
      toast.error("Failed to end session");
    }
  }, [sessionId, onEndSession]);

  const loadNextCard = useCallback(async () => {
    setLoading(true);
    try {
      const cardData = await reviewAPI.getNextFlashcard(sessionId);
      setCurrentCard(cardData);
      setShowAnswer(false);
    } catch (error) {
      console.error("Failed to load card:", error);
      if (
        error.response?.status === 400 &&
        error.response?.data?.detail?.includes("No more cards")
      ) {
        // Session complete
        handleEndSession();
      } else {
        toast.error("Failed to load flashcard");
      }
    } finally {
      setLoading(false);
    }
  }, [sessionId, handleEndSession]);

  const loadSession = useCallback(async () => {
    try {
      const sessionData = await reviewAPI.getSession(sessionId);
      setSession(sessionData);
      setSessionState(sessionData.session_state);

      if (sessionData.session_state === "active") {
        await loadNextCard();
      }
    } catch (error) {
      console.error("Failed to load session:", error);
      toast.error("Failed to load flashcard session");
    } finally {
      setLoading(false);
    }
  }, [sessionId, loadNextCard]);

  useEffect(() => {
    loadSession();
  }, [loadSession]);

  const handleShowAnswer = () => {
    setShowAnswer(true);
  };

  const handleSelfAssessment = async (quality) => {
    if (submitting) return;

    setSubmitting(true);
    try {
      console.log("sessionId", sessionId);
      console.log("currentCard card", currentCard.card);
      console.log("currentCard card topic", currentCard.card.topic);
      const result = await reviewAPI.submitFlashcardAnswer(
        sessionId,
        quality,
        currentCard.card.topic,
        currentCard.card.id
      );

      // Update session state
      setSession((prev) => ({
        ...prev,
        cards_reviewed: result.cards_reviewed,
        total_correct: result.total_correct,
      }));

      // Show feedback briefly
      const feedback = quality >= 3 ? "✅ Good recall!" : "📝 Keep practicing!";
      toast.success(feedback);

      // Load next card after delay
      setTimeout(() => {
        if (result.session_complete) {
          handleEndSession();
        } else {
          loadNextCard();
        }
      }, 1500);
    } catch (error) {
      console.error("Failed to submit assessment:", error);
      toast.error("Failed to submit assessment");
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
      await loadNextCard();
    } catch (error) {
      console.error("Failed to resume session:", error);
      toast.error("Failed to resume session");
    }
  };

  const getProgressPercentage = () => {
    if (!session || session.total_cards === 0) return 0;
    return (session.cards_reviewed / session.total_cards) * 100;
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
        <XMarkIcon className="w-16 h-16 text-secondary-400 mx-auto mb-4" />
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
                Flashcard Review
              </span>
            </div>
            {currentCard?.card?.difficulty_level && (
              <div className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-600">
                {currentCard.card.difficulty_level.toUpperCase()}
              </div>
            )}
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handlePauseSession}
              className="p-2 text-secondary-600 hover:text-secondary-800 hover:bg-secondary-100 rounded-lg"
            >
              <XMarkIcon className="w-5 h-5" />
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
              {session?.cards_reviewed || 0}/{session?.total_cards || 0} cards
            </span>
          </div>
          <div className="w-full bg-secondary-200 rounded-full h-2">
            <div
              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${getProgressPercentage()}%` }}
            ></div>
          </div>
          <div className="flex justify-between text-sm mt-2">
            <span className="text-secondary-600">
              Accuracy: {session?.total_correct || 0}/
              {session?.cards_reviewed || 0}
            </span>
            <span className="text-primary-600 font-medium">
              {getProgressPercentage().toFixed(1)}%
            </span>
          </div>
        </div>
      </div>

      {/* Flashcard Interface */}
      <AnimatePresence mode="wait">
        {currentCard && (
          <FlashcardCard
            card={currentCard.card}
            loading={loading}
            submitting={submitting}
            showAnswer={showAnswer}
            onShowAnswer={handleShowAnswer}
            onSelfAssessment={handleSelfAssessment}
            progress={{
              current: (session?.cards_reviewed || 0) + 1,
              total: session?.total_cards || 0,
            }}
          />
        )}
      </AnimatePresence>
    </div>
  );
};

export default FlashcardReview;
