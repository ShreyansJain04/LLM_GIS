import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  BookmarkIcon,
  CalendarIcon,
  CheckCircleIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";
import { reviewAPI } from "../services/api";
import toast from "react-hot-toast";

const FlashcardTopicSelector = ({ username, onStartSession }) => {
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedTopics, setSelectedTopics] = useState([]);
  const [startingSession, setStartingSession] = useState(false);

  useEffect(() => {
    loadTopics();
  }, [username]);

  const loadTopics = async () => {
    try {
      const data = await reviewAPI.getFlashcardTopics(username);
      setTopics(data.topics || []);

      if (!data.has_due_cards) {
        toast.error("No flashcards are due for review. Check back later!");
      }
    } catch (error) {
      console.error("Failed to load flashcard topics:", error);
      toast.error("Failed to load flashcard topics");
    } finally {
      setLoading(false);
    }
  };

  const handleTopicToggle = (topic) => {
    setSelectedTopics((prev) => {
      if (prev.includes(topic)) {
        return prev.filter((t) => t !== topic);
      } else {
        return [...prev, topic];
      }
    });
  };

  const handleSelectAll = () => {
    const allTopics = topics.map((topic) => topic.topic);
    setSelectedTopics(allTopics);
  };

  const handleStartSession = async () => {
    if (selectedTopics.length === 0) {
      toast.error("Please select at least one topic");
      return;
    }

    setStartingSession(true);
    try {
      const sessionResponse = await reviewAPI.startFlashcardReview(
        username,
        selectedTopics
      );
      onStartSession(sessionResponse.session_id);
    } catch (error) {
      console.error("Failed to start flashcard session:", error);
      if (error.response?.status === 400) {
        toast.error(
          error.response.data.detail || "No cards are due for review"
        );
      } else {
        toast.error("Failed to start flashcard session");
      }
    } finally {
      setStartingSession(false);
    }
  };

  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-8 bg-secondary-200 rounded w-1/3"></div>
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-secondary-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  if (topics.length === 0) {
    return (
      <div className="text-center py-12">
        <CheckCircleIcon className="w-16 h-16 text-green-500 mx-auto mb-4" />
        <h3 className="text-xl font-semibold text-secondary-900 mb-2">
          All Caught Up!
        </h3>
        <p className="text-secondary-600 mb-6">
          You have no flashcards due for review right now. Check back later for
          your next review session.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="text-center">
        <h2 className="text-2xl font-bold text-secondary-900 mb-2">
          Flashcard Review
        </h2>
        <p className="text-secondary-600">
          Select topics with due flashcards to review
        </p>
      </div>

      {/* Due Cards Alert */}
      <div className="bg-orange-50 border border-orange-200 rounded-xl p-4">
        <div className="flex items-center space-x-2 mb-2">
          <ExclamationTriangleIcon className="w-5 h-5 text-orange-600" />
          <span className="font-medium text-orange-900">
            {topics.reduce((sum, topic) => sum + topic.due_count, 0)} cards due
            for review
          </span>
        </div>
        <p className="text-orange-700 text-sm">
          These cards are ready for spaced repetition review
        </p>
      </div>

      {/* Topic Selection */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-medium text-secondary-900">
            Available Topics
          </h3>
          <button
            onClick={handleSelectAll}
            className="text-sm text-primary-600 hover:text-primary-700"
          >
            Select All
          </button>
        </div>

        <div className="space-y-3">
          {topics.map((topic) => (
            <motion.div
              key={topic.topic}
              whileHover={{ scale: 1.02 }}
              className={`border rounded-lg p-4 cursor-pointer transition-all ${
                selectedTopics.includes(topic.topic)
                  ? "border-primary-500 bg-primary-50"
                  : "border-secondary-200 hover:border-secondary-300"
              }`}
              onClick={() => handleTopicToggle(topic.topic)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <BookmarkIcon className="w-5 h-5 text-primary-600" />
                  <div>
                    <h4 className="font-medium text-secondary-900">
                      {topic.topic}
                    </h4>
                    <div className="flex items-center space-x-4 text-sm text-secondary-600">
                      <span className="flex items-center space-x-1">
                        <CalendarIcon className="w-4 h-4" />
                        <span>{topic.due_count} due</span>
                      </span>
                      <span>{topic.total_cards} total cards</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {selectedTopics.includes(topic.topic) && (
                    <CheckCircleIcon className="w-5 h-5 text-primary-600" />
                  )}
                  <div className="text-right">
                    <div className="text-sm font-medium text-secondary-900">
                      {topic.due_count}
                    </div>
                    <div className="text-xs text-secondary-500">due</div>
                  </div>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex space-x-4">
        <button
          onClick={handleStartSession}
          disabled={selectedTopics.length === 0 || startingSession}
          className="flex-1 py-3 px-4 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {startingSession
            ? "Starting..."
            : `Start Review (${selectedTopics.length} topics)`}
        </button>
      </div>

      {/* Summary */}
      {selectedTopics.length > 0 && (
        <div className="bg-secondary-50 rounded-lg p-4">
          <h4 className="font-medium text-secondary-900 mb-2">
            Selected Topics
          </h4>
          <div className="flex flex-wrap gap-2">
            {selectedTopics.map((topic) => {
              const topicData = topics.find((t) => t.topic === topic);
              return (
                <span
                  key={topic}
                  className="px-2 py-1 bg-primary-100 text-primary-700 rounded text-sm"
                >
                  {topic} ({topicData?.due_count || 0})
                </span>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default FlashcardTopicSelector;
