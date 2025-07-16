import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  ChartBarIcon,
  ArrowPathIcon,
  BookmarkIcon,
  TrophyIcon,
  ExclamationTriangleIcon,
} from "@heroicons/react/24/outline";
import { useUser } from "../contexts/UserContext";
import { userAPI, reviewAPI } from "../services/api";
import toast from "react-hot-toast";
import ReviewModeSelector from "../components/ReviewModeSelector";
import ReviewSession from "../components/ReviewSession";
import SpacedRepetitionReview from "../components/SpacedRepetitionReview";
import FlashcardTopicSelector from "../components/FlashcardTopicSelector";
import FlashcardReview from "../components/FlashcardReview";
import { useNavigate } from "react-router-dom";

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

const Review = () => {
  const { user } = useUser();
  const navigate = useNavigate();
  const [insights, setInsights] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedMode, setSelectedMode] = useState(null);
  const [sessionId, setSessionId] = useState(null);
  const [sessionResult, setSessionResult] = useState(null);
  const [flashcardMode, setFlashcardMode] = useState(false);
  const [weakTopics, setWeakTopics] = useState([]);
  const [progress, setProgress] = useState({});
  // const [currentQuestion, setCurrentQuestion] = useState(null);
  // const [feedback, setFeedback] = useState(null);
  // const [isCorrect, setIsCorrect] = useState(null);
  // const [selectedTopic, setSelectedTopic] = useState(null);
  const [dueItems, setDueItems] = useState([]);
  const [summary, setSummary] = useState(null);
  const [showIntensiveTopicSelector, setShowIntensiveTopicSelector] =
    useState(false);
  const [intensiveSelectedTopics, setIntensiveSelectedTopics] = useState([]);

  useEffect(() => {
    if (user?.username) {
      loadReviewInsights();
    }
  }, [user]);

  const loadReviewInsights = async () => {
    try {
      // Use existing user insights endpoint
      const userInsights = await userAPI.getUserInsights(user.username);

      // Process insights like main.py does
      const recommendations = userInsights.personalized_recommendations || {};

      // Get focus areas from enhanced memory
      const focusAreas = recommendations.focus_areas || [];

      // Check for due spaced repetition items
      const spacedSchedule = recommendations.spaced_repetition_schedule || [];

      const dueItemsData = spacedSchedule.filter(
        (item) => item.days_until_review <= 0
      );

      // Get performance summary
      const summaryData = userInsights.performance_summary || {
        topics_studied: 0,
        average_mastery: 0.0,
        study_streak: 0,
        weak_areas_count: 0,
      };

      setWeakTopics(focusAreas);
      setDueItems(dueItemsData);
      setSummary(summaryData);
      setInsights(userInsights);

      // Initialize progress from focus areas
      const progressMap = {};
      focusAreas.forEach((area) => {
        progressMap[area.topic] = area.mastery || 0;
      });
      setProgress(progressMap);
    } catch (error) {
      console.error("Failed to load user insights:", error);
      toast.error("Failed to load user insights");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectMode = async (mode) => {
    if (mode === "flashcards") {
      setFlashcardMode(true);
      setSelectedMode(mode);
      return;
    }
    if (mode === "intensive") {
      // Show topic selector for intensive mode
      setShowIntensiveTopicSelector(true);
      setSelectedMode(null);
      return;
    }
    setLoading(true);
    try {
      let sessionResponse;

      // Use specific endpoints for each review mode
      switch (mode) {
        case "adaptive":
          sessionResponse = await reviewAPI.startAdaptiveReview(user.username);
          break;
        case "spaced":
          sessionResponse = await reviewAPI.startSpacedReview(user.username);
          break;
        case "quick":
          sessionResponse = await reviewAPI.startQuickReview(user.username);
          break;
        default:
          // Fallback to generic endpoint
          sessionResponse = await reviewAPI.startSession(user.username, mode);
      }

      if (sessionResponse && sessionResponse.session_id) {
        console.log("sessionResponse", sessionResponse);
        setSessionId(sessionResponse.session_id);
        setSelectedMode(mode);
      } else {
        toast.error("Failed to start review session. Please try again.");
      }
    } catch (error) {
      console.error("Failed to start review session:", error);
      toast.error("Failed to start review session");
    } finally {
      setLoading(false);
    }
  };

  const handleStartFlashcardSession = (sessionId) => {
    setSessionId(sessionId);
    setFlashcardMode(false);
  };

  const handleBackToModeSelection = () => {
    setSessionId(null);
    setSelectedMode(null);
    setSessionResult(null);
    setFlashcardMode(false);
  };

  const handleEndSession = (result) => {
    console.log("handleEndSession", result);
    setSessionResult(result);
  };

  const handlePauseSession = () => {
    // Handle session pause
    toast.success("Session paused");
  };

  const getMasteryLevelColor = (level) => {
    switch (level.toLowerCase()) {
      case "mastered":
        return "bg-green-100 text-green-800";
      case "intermediate":
        return "bg-yellow-100 text-yellow-800";
      case "beginner":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  // New: Start intensive review after topic selection
  const handleStartIntensive = async () => {
    setLoading(true);
    setShowIntensiveTopicSelector(false);
    try {
      let topicsToSend = intensiveSelectedTopics;
      if (intensiveSelectedTopics.includes("__ALL__")) {
        topicsToSend = weakTopics.map((area) => area.topic);
      }
      const sessionResponse = await reviewAPI.startIntensiveReview(
        user.username,
        topicsToSend
      );
      if (sessionResponse && sessionResponse.session_id) {
        setSessionId(sessionResponse.session_id);
        setSelectedMode("intensive");
      } else {
        toast.error(
          "Failed to start intensive review session. Please try again."
        );
      }
    } catch (error) {
      console.error("Failed to start intensive review session:", error);
      toast.error("Failed to start intensive review session");
    } finally {
      setLoading(false);
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
              onClick={() => navigate("/dashboard")}
              className="bg-secondary-200 text-secondary-700 px-6 py-2 rounded-lg hover:bg-secondary-300"
            >
              Back to Dashboard
            </button>
          </div>
        </motion.div>
      </div>
    );
  }

  // Show flashcard topic selection
  if (flashcardMode) {
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

        <FlashcardTopicSelector
          username={user.username}
          onStartSession={handleStartFlashcardSession}
        />
      </div>
    );
  }

  // Show topic selector for intensive mode
  if (showIntensiveTopicSelector) {
    return (
      <div className="p-6 max-w-4xl mx-auto">
        <div className="mb-6">
          <button
            onClick={() => {
              setShowIntensiveTopicSelector(false);
              handleBackToModeSelection();
            }}
            className="flex items-center space-x-2 text-primary-600 hover:text-primary-700 mb-4"
          >
            <ArrowPathIcon className="w-5 h-5" />
            <span>Change Review Mode</span>
          </button>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-secondary-200 p-6">
          <h2 className="text-xl font-bold text-secondary-900 mb-2">
            Select Topic(s) for Intensive Review
          </h2>
          <p className="text-secondary-600 mb-4">
            Choose one or more topics to focus on. You can also select all
            topics.
          </p>
          <div className="mb-4">
            <button
              className={`mr-2 mb-2 px-4 py-2 rounded-lg border ${
                intensiveSelectedTopics.includes("__ALL__")
                  ? "bg-primary-600 text-white border-primary-600"
                  : "border-secondary-200"
              }`}
              onClick={() => setIntensiveSelectedTopics(["__ALL__"])}
            >
              All Focus Areas
            </button>
            {weakTopics.map((area, idx) => (
              <button
                key={area.topic}
                className={`mr-2 mb-2 px-4 py-2 rounded-lg border ${
                  intensiveSelectedTopics.includes(area.topic)
                    ? "bg-primary-600 text-white border-primary-600"
                    : "border-secondary-200"
                }`}
                onClick={() => {
                  if (intensiveSelectedTopics.includes("__ALL__")) {
                    setIntensiveSelectedTopics([area.topic]);
                  } else if (intensiveSelectedTopics.includes(area.topic)) {
                    setIntensiveSelectedTopics(
                      intensiveSelectedTopics.filter((t) => t !== area.topic)
                    );
                  } else {
                    setIntensiveSelectedTopics([
                      ...intensiveSelectedTopics,
                      area.topic,
                    ]);
                  }
                }}
              >
                {area.topic}
              </button>
            ))}
          </div>
          <button
            onClick={handleStartIntensive}
            disabled={intensiveSelectedTopics.length === 0}
            className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700 disabled:opacity-50"
          >
            Start Intensive Review
          </button>
        </div>
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

        {selectedMode === "flashcards" ? (
          <FlashcardReview
            sessionId={sessionId}
            onEndSession={handleEndSession}
            onPauseSession={handlePauseSession}
          />
        ) : selectedMode === "spaced" ? (
          <SpacedRepetitionReview
            sessionId={sessionId}
            onEndSession={handleEndSession}
            onPauseSession={handlePauseSession}
          />
        ) : (
          <ReviewSession
            sessionId={sessionId}
            mode={selectedMode}
            onEndSession={handleEndSession}
            onPauseSession={handlePauseSession}
            dueItems={dueItems}
          />
        )}
      </div>
    );
  }

  // Show mode selection with enhanced memory insights
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

      {/* Enhanced Memory Insights */}
      {summary && (
        <div className="mb-6 bg-white rounded-xl shadow-sm border border-secondary-200 p-6">
          <div className="flex items-center space-x-2 mb-4">
            <ChartBarIcon className="w-6 h-6 text-primary-600" />
            <h3 className="text-lg font-medium text-secondary-900">
              Your Learning Progress
            </h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="text-center">
              <div className="text-2xl font-bold text-primary-600">
                {summary.topics_studied || 0}
              </div>
              <div className="text-sm text-secondary-600">Topics Studied</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">
                {typeof summary.average_mastery === "number"
                  ? `${Math.round(summary.average_mastery * 100)}%`
                  : "0%"}
              </div>
              <div className="text-sm text-secondary-600">Average Mastery</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">
                {summary.study_streak || 0}
              </div>
              <div className="text-sm text-secondary-600">
                Study Streak (days)
              </div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">
                {summary.weak_areas_count || 0}
              </div>
              <div className="text-sm text-secondary-600">Weak Areas</div>
            </div>
          </div>
        </div>
      )}

      {/* Spaced Repetition Due Items */}
      {dueItems.length > 0 && (
        <div className="mb-6 bg-orange-50 border border-orange-200 rounded-xl p-6">
          <div className="flex items-center space-x-2 mb-4">
            <ExclamationTriangleIcon className="w-6 h-6 text-orange-600" />
            <h3 className="text-lg font-medium text-orange-900">
              Spaced Repetition Due
            </h3>
          </div>
          <p className="text-orange-700 mb-4">
            You have {dueItems.length} items due for spaced repetition review!
          </p>
          <div className="space-y-2">
            {dueItems.slice(0, 3).map((item, index) => (
              <div key={index} className="flex items-center space-x-2">
                <span className="text-orange-600">
                  {item.priority === "high" ? "🔴" : "🟡"}
                </span>
                <span className="text-orange-800">
                  {item.topic} - {item.subtopic}
                </span>
              </div>
            ))}
          </div>
          <button
            onClick={() => handleSelectMode("spaced")}
            className="mt-4 bg-orange-600 text-white px-4 py-2 rounded-lg hover:bg-orange-700"
          >
            Start Spaced Repetition Review
          </button>
        </div>
      )}

      {/* Focus Areas */}
      {weakTopics.length > 0 && (
        <div className="mb-6 bg-white rounded-xl shadow-sm border border-secondary-200 p-6">
          <div className="flex items-center space-x-2 mb-4">
            <BookmarkIcon className="w-6 h-6 text-primary-600" />
            <h3 className="text-lg font-medium text-secondary-900">
              Priority Focus Areas
            </h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {weakTopics.slice(0, 6).map((area, index) => (
              <div
                key={index}
                className="flex items-center justify-between p-3 bg-secondary-50 rounded-lg"
              >
                <div>
                  <div className="font-medium text-secondary-900">
                    {area.topic}
                  </div>
                  <div className="text-sm text-secondary-600">
                    {area.subtopic}
                  </div>
                </div>
                <div className="text-sm text-secondary-500">
                  Priority: {area.priority_score || "Medium"}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <ReviewModeSelector
        onSelectMode={handleSelectMode}
        insights={insights}
        loading={loading}
        dueItems={dueItems}
        focusAreas={weakTopics}
      />
    </div>
  );
};

export default Review;
