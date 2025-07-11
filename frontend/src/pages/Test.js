import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import {
  BookOpenIcon,
  PlayIcon,
  PauseIcon,
  ArrowRightIcon,
  LightBulbIcon,
  QuestionMarkCircleIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
} from "@heroicons/react/24/outline";
import { useUser } from "../contexts/UserContext";
import toast from "react-hot-toast";

const TestingPlan = ({ plan, onStartSubtopic, currentStep, totalSteps }) => (
  <div className="card mb-6">
    <div className="flex items-center justify-between mb-4">
      <h2 className="text-xl font-semibold text-secondary-900">{plan.topic}</h2>
      <div className="flex items-center space-x-2 text-sm text-secondary-600">
        <ClockIcon className="w-4 h-4" />
        <span>{plan.estimated_time} min</span>
      </div>
    </div>

    <div className="space-y-3">
      {plan.subtopics?.map((subtopic, index) => (
        <motion.div
          key={index}
          className={`p-4 rounded-lg border transition-all duration-200 cursor-pointer ${
            index === currentStep
              ? "border-primary-200 bg-primary-50"
              : index < currentStep
              ? "border-green-200 bg-green-50"
              : "border-secondary-200 bg-white hover:bg-secondary-50"
          }`}
          onClick={() => onStartSubtopic(index)}
          whileHover={{ scale: 1.01 }}
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div
                className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium ${
                  index === currentStep
                    ? "bg-primary-600 text-white"
                    : index < currentStep
                    ? "bg-green-600 text-white"
                    : "bg-secondary-200 text-secondary-600"
                }`}
              >
                {index < currentStep ? (
                  <CheckCircleIcon className="w-5 h-5" />
                ) : (
                  index + 1
                )}
              </div>
              <div>
                <h3 className="font-medium text-secondary-900">
                  {subtopic.name}
                </h3>
                <p className="text-sm text-secondary-600">
                  {subtopic.description}
                </p>
              </div>
            </div>
            <ArrowRightIcon className="w-5 h-5 text-secondary-400" />
          </div>
        </motion.div>
      ))}
    </div>
  </div>
);

const ContentSection = ({ title, content, type, loading }) => (
  <motion.div
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    className="card mb-6"
  >
    <div className="flex items-center space-x-2 mb-4">
      {type === "explanation" && (
        <BookOpenIcon className="w-5 h-5 text-primary-600" />
      )}
      {type === "example" && (
        <LightBulbIcon className="w-5 h-5 text-yellow-600" />
      )}
      {type === "question" && (
        <QuestionMarkCircleIcon className="w-5 h-5 text-purple-600" />
      )}
      <h3 className="text-lg font-semibold text-secondary-900">{title}</h3>
    </div>

    {loading ? (
      <div className="animate-pulse">
        <div className="h-4 bg-secondary-200 rounded w-3/4 mb-2"></div>
        <div className="h-4 bg-secondary-200 rounded w-1/2 mb-2"></div>
        <div className="h-4 bg-secondary-200 rounded w-2/3"></div>
      </div>
    ) : (
      <div className="prose prose-secondary max-w-none">
        <ReactMarkdown>{content}</ReactMarkdown>
      </div>
    )}
  </motion.div>
);

const QuestionCard = ({ question, onAnswer, loading, feedback, isCorrect }) => {
  const [answer, setAnswer] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!answer.trim()) return;

    setSubmitted(true);
    onAnswer(answer);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="card mb-6"
    >
      <div className="flex items-center space-x-2 mb-4">
        <QuestionMarkCircleIcon className="w-5 h-5 text-purple-600" />
        <h3 className="text-lg font-semibold text-secondary-900">
          Check Your Understanding
        </h3>
      </div>

      <div className="space-y-4">
        <p className="text-secondary-700">{question}</p>

        <form onSubmit={handleSubmit}>
          <textarea
            value={answer}
            onChange={(e) => setAnswer(e.target.value)}
            placeholder="Type your answer here..."
            className="input-field h-24 resize-none"
            disabled={submitted || loading}
            required
          />

          <button
            type="submit"
            disabled={!answer.trim() || submitted || loading}
            className="mt-3 btn-primary disabled:opacity-50"
          >
            {loading ? "Checking..." : "Submit Answer"}
          </button>
        </form>

        <AnimatePresence>
          {feedback && (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.95 }}
              className={`p-4 rounded-lg border ${
                isCorrect
                  ? "border-green-200 bg-green-50 text-green-800"
                  : "border-yellow-200 bg-yellow-50 text-yellow-800"
              }`}
            >
              <div className="flex items-start space-x-2">
                {isCorrect ? (
                  <CheckCircleIcon className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                ) : (
                  <XCircleIcon className="w-5 h-5 text-yellow-600 flex-shrink-0 mt-0.5" />
                )}
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown>{feedback}</ReactMarkdown>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </motion.div>
  );
};

const Test = () => {
  const { user } = useUser();
  const [topic, setTopic] = useState("");
  const [plan, setPlan] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [sessionState, setSessionState] = useState("input"); // input, planning, learning, question
  const [loading, setLoading] = useState(false);

  // Content states
  const [explanation, setExplanation] = useState("");
  const [example, setExample] = useState("");
  const [question, setQuestion] = useState("");
  const [feedback, setFeedback] = useState("");
  const [isCorrect, setIsCorrect] = useState(false);

  const [loadingContent, setLoadingContent] = useState({
    explanation: false,
    example: false,
    question: false,
    answer: false,
  });

  // Mock plan data
  const mockPlan = {
    topic: topic || "Sample Test Topic",
    estimated_time: 10,
    subtopics: [
      { name: "Test Subtopic 1", description: "Description for subtopic 1" },
      { name: "Test Subtopic 2", description: "Description for subtopic 2" },
    ],
  };

  const handleStartTest = (e) => {
    e.preventDefault();
    if (!topic.trim()) return;
    setLoading(true);
    setSessionState("planning");
    setTimeout(() => {
      setPlan(mockPlan);
      setCurrentStep(0);
      setSessionState("learning");
      loadSubtopicContent(mockPlan.subtopics[0]);
      setLoading(false);
    }, 1000);
  };

  const loadSubtopicContent = (subtopic) => {
    setExplanation("");
    setExample("");
    setQuestion("");
    setFeedback("");
    setLoadingContent({
      explanation: true,
      example: true,
      question: true,
      answer: false,
    });
    setTimeout(() => {
      setExplanation(`This is a sample explanation for ${subtopic.name}.`);
      setLoadingContent((prev) => ({ ...prev, explanation: false }));
    }, 600);
    setTimeout(() => {
      setExample(`This is a sample example for ${subtopic.name}.`);
      setLoadingContent((prev) => ({ ...prev, example: false }));
    }, 900);
    setTimeout(() => {
      setQuestion(
        `What is the answer to the sample test question for ${subtopic.name}?`
      );
      setLoadingContent((prev) => ({ ...prev, question: false }));
    }, 1200);
  };

  const handleAnswer = (answer) => {
    setLoadingContent((prev) => ({ ...prev, answer: true }));
    setTimeout(() => {
      const correct = answer.toLowerCase().includes("sample");
      setFeedback(
        correct
          ? "Correct! This is a sample correct answer."
          : "Not quite. Try including the word 'sample' in your answer."
      );
      setIsCorrect(correct);
      setLoadingContent((prev) => ({ ...prev, answer: false }));
      setTimeout(() => {
        if (currentStep < (plan?.subtopics?.length || 0) - 1) {
          setCurrentStep((prev) => prev + 1);
          loadSubtopicContent(plan.subtopics[currentStep + 1]);
          setFeedback("");
        } else {
          // Test complete (could show a message or reset)
        }
      }, 2000);
    }, 800);
  };

  const handleSubtopicClick = (index) => {
    if (index <= currentStep && plan?.subtopics?.[index]) {
      setCurrentStep(index);
      loadSubtopicContent(plan.subtopics[index]);
      setFeedback("");
    }
  };

  const resetSession = () => {
    setSessionState("input");
    setPlan(null);
    setCurrentStep(0);
    setTopic("");
    setExplanation("");
    setExample("");
    setQuestion("");
    setFeedback("");
  };

  if (sessionState === "input") {
    return (
      <div className="p-6">
        <div className="max-w-2xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-8"
          >
            <BookOpenIcon className="w-16 h-16 text-primary-600 mx-auto mb-4" />
            <h1 className="text-3xl font-bold text-secondary-900 mb-2">
              Start Testing
            </h1>
            <p className="text-secondary-600">
              Enter a topic to begin testing your understanding
            </p>
          </motion.div>

          <motion.form
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            onSubmit={handleStartTest}
            className="card"
          >
            <label
              htmlFor="topic"
              className="block text-sm font-medium text-secondary-700 mb-2"
            >
              What would you like to learn?
            </label>
            <input
              type="text"
              id="topic"
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., GIS Coordinates, Geocoding, Geospatial Data, etc."
              className="input-field mb-4"
              disabled={loading}
              required
            />

            <button
              type="submit"
              disabled={!topic.trim() || loading}
              className="w-full btn-primary flex items-center justify-center space-x-2"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Creating Test...</span>
                </>
              ) : (
                <>
                  <PlayIcon className="w-5 h-5" />
                  <span>Start Testing</span>
                </>
              )}
            </button>
          </motion.form>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-secondary-900">
          Testing: {plan?.topic}
        </h1>
        <button onClick={resetSession} className="btn-secondary">
          New Topic
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Learning Plan Sidebar */}
        <div className="lg:col-span-1">
          {plan && (
            <TestingPlan
              plan={plan}
              onStartSubtopic={handleSubtopicClick}
              currentStep={currentStep}
              totalSteps={plan.subtopics?.length || 0}
            />
          )}
        </div>

        {/* Content Area */}
        <div className="lg:col-span-2">
          {explanation && (
            <ContentSection
              title="Explanation"
              content={explanation}
              type="explanation"
              loading={loadingContent.explanation}
            />
          )}

          {example && (
            <ContentSection
              title="Example"
              content={example}
              type="example"
              loading={loadingContent.example}
            />
          )}

          {question && (
            <QuestionCard
              question={question}
              onAnswer={handleAnswer}
              loading={loadingContent.answer}
              feedback={feedback}
              isCorrect={isCorrect}
            />
          )}
        </div>
      </div>
    </div>
  );
};

export default Test;
