import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  CheckCircleIcon,
  XCircleIcon,
  LightBulbIcon,
  QuestionMarkCircleIcon,
} from "@heroicons/react/24/outline";
import ReactMarkdown from "react-markdown";

const QuestionCard = ({ question, onAnswer, loading, feedback, isCorrect }) => {
  // Support both {question: {...}} and flat or string
  const q = question?.question || question;
  const qText = q?.text || (typeof q === "string" ? q : "");
  const qType = q?.type || "";
  const qOptions = q?.options || [];
  const qExplanation = q?.explanation || "";

  const [answer, setAnswer] = useState("");
  const [selectedOption, setSelectedOption] = useState(null);
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (qType === "objective" && selectedOption === null) return;
    if (qType !== "objective" && !answer.trim()) return;
    setSubmitted(true);
    if (qType === "objective") {
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
          <ReactMarkdown>{qText}</ReactMarkdown>
        </div>
        <form onSubmit={handleSubmit} className="space-y-4">
          {qType === "objective" &&
          Array.isArray(qOptions) &&
          qOptions.length > 0 ? (
            <div className="space-y-2">
              {qOptions.map((option, index) => (
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
              loading ||
              feedback ||
              (qType === "objective" ? selectedOption === null : !answer.trim())
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
        {qType === "objective" && feedback && qExplanation && (
          <div className="mt-3 p-3 rounded bg-blue-50 border border-blue-200">
            <strong>Explanation:</strong>
            <div className="prose prose-sm max-w-none mt-1">
              <ReactMarkdown>{qExplanation}</ReactMarkdown>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  );
};

export default QuestionCard;
