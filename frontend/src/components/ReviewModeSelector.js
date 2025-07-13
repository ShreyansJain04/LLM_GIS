import React from "react";
import { motion } from "framer-motion";
import {
  AcademicCapIcon,
  ChartBarIcon,
  ClockIcon,
  BoltIcon,
  BookOpenIcon,
} from "@heroicons/react/24/outline";

const ReviewModeSelector = ({ onSelectMode, insights, loading }) => {
  const reviewModes = [
    {
      id: "adaptive",
      title: "Adaptive Review",
      description: "AI adjusts difficulty based on your performance",
      icon: ChartBarIcon,
      color: "bg-blue-500",
      recommended: true,
    },
    {
      id: "intensive",
      title: "Intensive Review",
      description: "Deep dive into specific weak areas",
      icon: AcademicCapIcon,
      color: "bg-purple-500",
    },
    {
      id: "spaced",
      title: "Spaced Repetition",
      description: "Review items due for spaced repetition",
      icon: ClockIcon,
      color: "bg-green-500",
    },
    {
      id: "quick",
      title: "Quick Review",
      description: "Rapid review of all weak areas",
      icon: BoltIcon,
      color: "bg-orange-500",
    },
    {
      id: "flashcards",
      title: "Flashcard Review",
      description: "Traditional flashcard interface",
      icon: BookOpenIcon,
      color: "bg-indigo-500",
    },
  ];

  const getDueItemsCount = () => {
    if (!insights?.due_items) return 0;
    return insights.due_items.length;
  };

  const getFocusAreasCount = () => {
    if (!insights?.focus_areas) return 0;
    return insights.focus_areas.length;
  };

  if (loading) {
    return (
      <div className="animate-pulse space-y-4">
        <div className="h-8 bg-secondary-200 rounded w-1/4"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[...Array(5)].map((_, i) => (
            <div key={i} className="h-32 bg-secondary-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="text-center">
        <h2 className="text-2xl font-bold text-secondary-900">
          Choose Review Mode
        </h2>
        <p className="text-secondary-600 mt-2">
          Select how you'd like to review your weak areas
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {reviewModes.map((mode) => {
          const Icon = mode.icon;
          const dueItems = mode.id === "spaced" ? getDueItemsCount() : null;
          const focusAreas =
            mode.id === "adaptive" || mode.id === "quick"
              ? getFocusAreasCount()
              : null;

          return (
            <motion.div
              key={mode.id}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className={`relative bg-white rounded-xl shadow-sm border border-secondary-200 p-6 cursor-pointer transition-all duration-200 hover:shadow-md ${
                mode.recommended ? "ring-2 ring-blue-500 ring-opacity-50" : ""
              }`}
              onClick={() => onSelectMode(mode.id)}
            >
              {mode.recommended && (
                <div className="absolute -top-2 -right-2 bg-blue-500 text-white text-xs px-2 py-1 rounded-full">
                  Recommended
                </div>
              )}

              <div className="flex items-start space-x-4">
                <div className={`p-3 rounded-lg ${mode.color} bg-opacity-10`}>
                  <Icon
                    className={`w-6 h-6 ${mode.color.replace("bg-", "text-")}`}
                  />
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-secondary-900">
                    {mode.title}
                  </h3>
                  <p className="text-sm text-secondary-600 mt-1">
                    {mode.description}
                  </p>

                  {/* Show relevant counts */}
                  {dueItems !== null && dueItems > 0 && (
                    <div className="mt-2 flex items-center space-x-1">
                      <ClockIcon className="w-4 h-4 text-green-500" />
                      <span className="text-sm text-green-600 font-medium">
                        {dueItems} items due
                      </span>
                    </div>
                  )}

                  {focusAreas !== null && focusAreas > 0 && (
                    <div className="mt-2 flex items-center space-x-1">
                      <ChartBarIcon className="w-4 h-4 text-orange-500" />
                      <span className="text-sm text-orange-600 font-medium">
                        {focusAreas} focus areas
                      </span>
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Show insights summary */}
      {insights && (
        <div className="bg-blue-50 rounded-lg p-4">
          <h3 className="font-medium text-blue-900 mb-2">
            Your Learning Status
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div>
              <span className="text-blue-600 font-medium">Topics Studied:</span>
              <span className="ml-1 text-blue-800">
                {insights.summary?.total_topics_studied || 0}
              </span>
            </div>
            <div>
              <span className="text-blue-600 font-medium">Weak Areas:</span>
              <span className="ml-1 text-blue-800">
                {insights.summary?.weak_areas_count || 0}
              </span>
            </div>
            <div>
              <span className="text-blue-600 font-medium">Due Items:</span>
              <span className="ml-1 text-blue-800">{getDueItemsCount()}</span>
            </div>
            <div>
              <span className="text-blue-600 font-medium">Focus Areas:</span>
              <span className="ml-1 text-blue-800">{getFocusAreasCount()}</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ReviewModeSelector;
