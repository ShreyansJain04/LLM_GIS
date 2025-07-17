import React from "react";
import { motion } from "framer-motion";
import { EyeIcon } from "@heroicons/react/24/outline";
import ReactMarkdown from "react-markdown";

const getQualityDescription = (quality) => {
  const descriptions = {
    0: "Complete blackout",
    1: "Incorrect, but remembered",
    2: "Incorrect, but seemed easy",
    3: "Correct, but difficult",
    4: "Correct",
    5: "Correct and easy",
  };
  return descriptions[quality] || "";
};

const FlashcardCard = ({
  card,
  loading = false,
  submitting = false,
  showAnswer = false,
  onShowAnswer,
  onSelfAssessment,
  progress = null, // { current, total }
  header = null, // optional custom header
}) => {
  if (!card) return null;

  return (
    <motion.div
      key={card.id}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className="bg-white rounded-xl shadow-sm border border-secondary-200 p-6"
    >
      <div className="space-y-6">
        {/* Card Progress/Header */}
        {header ? (
          header
        ) : progress ? (
          <div className="flex items-center justify-between">
            <span className="text-sm text-secondary-600">
              Card {progress.current} of {progress.total}
            </span>
            {card.topic && (
              <span className="text-sm text-secondary-500">
                Topic: {card.topic}
              </span>
            )}
          </div>
        ) : null}

        {/* Card Front/Back */}
        <div className="bg-gradient-to-br from-primary-50 to-primary-100 rounded-lg p-6 border border-primary-200">
          <div className="text-center">
            <h3 className="text-lg font-medium text-primary-900 mb-4">
              {showAnswer ? "Answer" : "Question"}
            </h3>
            <div className="prose prose-sm max-w-none text-primary-800">
              <ReactMarkdown>
                {showAnswer ? card.back : card.front}
              </ReactMarkdown>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        {!showAnswer ? (
          <button
            onClick={onShowAnswer}
            disabled={submitting || loading}
            className="w-full py-3 px-4 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 flex items-center justify-center space-x-2"
          >
            <EyeIcon className="w-5 h-5" />
            <span>Show Answer</span>
          </button>
        ) : (
          <div className="space-y-4">
            {/* Self Assessment */}
            <div className="text-center">
              <h4 className="text-lg font-medium text-secondary-900 mb-4">
                How well did you know this?
              </h4>
              <div className="grid grid-cols-3 gap-2">
                {[0, 1, 2, 3, 4, 5].map((quality) => (
                  <button
                    key={quality}
                    onClick={() => onSelfAssessment(quality)}
                    disabled={submitting || loading}
                    className={`p-3 rounded-lg border transition-all ${
                      quality >= 3
                        ? "border-green-200 hover:bg-green-50 text-green-700"
                        : "border-red-200 hover:bg-red-50 text-red-700"
                    } disabled:opacity-50`}
                  >
                    <div className="text-lg font-bold">{quality}</div>
                    <div className="text-xs">
                      {getQualityDescription(quality)}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default FlashcardCard;
