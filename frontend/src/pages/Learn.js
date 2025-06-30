import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import {
  ChatBubbleLeftRightIcon,
  PaperAirplaneIcon,
  CommandLineIcon,
  LightBulbIcon,
  TrashIcon,
  BookOpenIcon,
  QuestionMarkCircleIcon,
  SparklesIcon,
  ExclamationTriangleIcon,
  CheckCircleIcon,
  XCircleIcon,
  ClockIcon,
} from "@heroicons/react/24/outline";
import { useUser } from "../contexts/UserContext";
import { contentAPI, learningAPI } from "../services/api";
import toast from "react-hot-toast";

const MessageBubble = ({ message, isUser, citations, timestamp }) => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}
  >
    <div className={`max-w-3xl ${isUser ? "order-2" : "order-1"}`}>
      <div
        className={`px-4 py-3 rounded-2xl ${
          isUser
            ? "bg-primary-600 text-white rounded-br-sm"
            : "bg-white border border-secondary-200 text-secondary-900 rounded-bl-sm"
        }`}
      >
        <div className="prose prose-sm max-w-none">
          {isUser ? (
            <p className="text-white mb-0">{message}</p>
          ) : (
            <ReactMarkdown
              components={{
                p: ({ children }) => (
                  <p className="mb-2 last:mb-0">{children}</p>
                ),
                ul: ({ children }) => <ul className="ml-4 mb-2">{children}</ul>,
                ol: ({ children }) => <ol className="ml-4 mb-2">{children}</ol>,
                li: ({ children }) => <li className="mb-1">{children}</li>,
                code: ({ children }) => (
                  <code className="bg-secondary-100 px-1 py-0.5 rounded text-xs">
                    {children}
                  </code>
                ),
              }}
            >
              {message}
            </ReactMarkdown>
          )}
        </div>

        {/* Citations */}
        {citations && citations.length > 0 && (
          <div className="mt-3 pt-2 border-t border-secondary-200">
            <p className="text-xs text-secondary-500 mb-1">Sources:</p>
            <div className="space-y-1">
              {citations.map((citation, index) => (
                <div
                  key={index}
                  className="text-xs text-secondary-600 bg-secondary-50 px-2 py-1 rounded"
                >
                  📄 {citation}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Timestamp */}
      <div
        className={`text-xs text-secondary-500 mt-1 ${
          isUser ? "text-right" : "text-left"
        }`}
      >
        {new Date(timestamp).toLocaleTimeString()}
      </div>
    </div>
  </motion.div>
);

const SuggestionChip = ({ suggestion, onClick }) => (
  <motion.button
    whileHover={{ scale: 1.02 }}
    whileTap={{ scale: 0.98 }}
    onClick={() => onClick(suggestion)}
    className="px-3 py-2 bg-primary-50 hover:bg-primary-100 text-primary-700 rounded-full text-sm border border-primary-200 transition-colors duration-200"
  >
    {suggestion}
  </motion.button>
);

const CommandHelp = ({ isVisible, onClose }) => (
  <AnimatePresence>
    {isVisible && (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="absolute bottom-full left-0 right-0 mb-2 bg-white border border-secondary-200 rounded-lg shadow-lg p-4 z-10"
      >
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-medium text-secondary-900">Quick Commands</h3>
          <button
            onClick={onClose}
            className="text-secondary-400 hover:text-secondary-600"
          >
            <XCircleIcon className="w-5 h-5" />
          </button>
        </div>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="space-y-1">
            <div>
              <code className="text-primary-600">!help</code> - Show all
              commands
            </div>
            <div>
              <code className="text-primary-600">!explain topic</code> - Get
              explanation
            </div>
            <div>
              <code className="text-primary-600">!example topic</code> - Get
              example
            </div>
            <div>
              <code className="text-primary-600">!question topic</code> -
              Practice question
            </div>
          </div>
          <div className="space-y-1">
            <div>
              <code className="text-primary-600">!quiz topic</code> - Start quiz
            </div>
            <div>
              <code className="text-primary-600">!sources</code> - Show
              documents
            </div>
            <div>
              <code className="text-primary-600">!progress</code> - View
              progress
            </div>
            <div>
              <code className="text-primary-600">!hint</code> - Get hint
            </div>
          </div>
        </div>
      </motion.div>
    )}
  </AnimatePresence>
);

const Learn = () => {
  const { user } = useUser();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [showCommandHelp, setShowCommandHelp] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [learningPlan, setLearningPlan] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [isLearning, setIsLearning] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load suggestions on mount
  useEffect(() => {
    setSuggestions([
      "Learn about GIS coordinates",
      "Start learning about map projections",
      "Teach me about spatial data",
    ]);
  }, []);

  // Handle sending a message
  const handleSendMessage = async (messageText = inputMessage) => {
    if (!messageText.trim() || isLoading) return;
    setInputMessage("");
    const userMessage = {
      type: "user",
      message: messageText,
      timestamp: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      if (messageText.startsWith("!")) {
        // Pause learning and process command
        setIsLearning(false);
        await handleCommand(messageText);
      } else if (!isLearning) {
        // Start learning session with topic
        await startLearningSession(messageText);
      } else {
        // In learning session, treat as answer
        await handleLearningAnswer(messageText);
      }
    } catch (error) {
      toast.error("Something went wrong");
    } finally {
      setIsLoading(false);
    }
  };

  // Start a new learning session
  const startLearningSession = async (topic) => {
    setIsLearning(true);
    setCurrentStep(0);
    setLearningPlan(null);
    setMessages((prev) => [
      ...prev,
      {
        type: "assistant",
        message: `Great! Let's start learning about **${topic}**. Generating your learning plan...`,
        timestamp: new Date().toISOString(),
      },
    ]);
    try {
      const planData = await learningAPI.getLearningPlan(user.username, topic);
      setLearningPlan(planData);
      presentSubtopic(planData, 0);
    } catch (error) {
      setMessages((prev) => [
        ...prev,
        {
          type: "assistant",
          message: "Sorry, I couldn't generate a learning plan for that topic.",
          timestamp: new Date().toISOString(),
        },
      ]);
      setIsLearning(false);
    }
  };

  // Present a subtopic as chat messages
  const presentSubtopic = async (plan, step) => {
    if (!plan || !plan.subtopics || step >= plan.subtopics.length) {
      setMessages((prev) => [
        ...prev,
        {
          type: "assistant",
          message:
            "🎉 You've completed the learning session! Type a new topic to start again.",
          timestamp: new Date().toISOString(),
        },
      ]);
      setIsLearning(false);
      return;
    }
    setCurrentStep(step);
    const subtopic = plan.subtopics[step];
    setMessages((prev) => [
      ...prev,
      {
        type: "assistant",
        message: `**Step ${step + 1}: ${subtopic.name}**\n${
          subtopic.description
        }`,
        timestamp: new Date().toISOString(),
      },
    ]);
    // Explanation
    try {
      const explanationData = await contentAPI.generateExplanation(
        subtopic.name,
        "medium"
      );
      setMessages((prev) => [
        ...prev,
        {
          type: "assistant",
          message: `**Explanation:**\n${explanationData.explanation}`,
          timestamp: new Date().toISOString(),
        },
      ]);
    } catch {}
    // Example
    try {
      const exampleData = await contentAPI.generateExample(
        subtopic.name,
        "medium"
      );
      setMessages((prev) => [
        ...prev,
        {
          type: "assistant",
          message: `**Example:**\n${exampleData.example}`,
          timestamp: new Date().toISOString(),
        },
      ]);
    } catch {}
    // Question
    try {
      const questionData = await contentAPI.generateQuestion(
        subtopic.name,
        [],
        "medium",
        "analytical"
      );
      setMessages((prev) => [
        ...prev,
        {
          type: "assistant",
          message: `**Practice Question:**\n${questionData.question}\n\nPlease provide your answer below.`,
          timestamp: new Date().toISOString(),
          expectAnswer: true,
        },
      ]);
    } catch {}
  };

  // Handle answer in learning session
  const handleLearningAnswer = async (answer) => {
    setMessages((prev) => [
      ...prev,
      {
        type: "user",
        message: answer,
        timestamp: new Date().toISOString(),
      },
    ]);
    try {
      const lastSubtopic = learningPlan.subtopics[currentStep];
      const questionData = await contentAPI.generateQuestion(
        lastSubtopic.name,
        [],
        "medium",
        "analytical"
      );
      const result = await contentAPI.checkAnswer(
        questionData.question,
        answer
      );
      setMessages((prev) => [
        ...prev,
        {
          type: "assistant",
          message: result.feedback,
          timestamp: new Date().toISOString(),
        },
      ]);
      // Move to next subtopic
      presentSubtopic(learningPlan, currentStep + 1);
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          type: "assistant",
          message: "Sorry, I couldn't check your answer. Let's move on.",
          timestamp: new Date().toISOString(),
        },
      ]);
      presentSubtopic(learningPlan, currentStep + 1);
    }
  };

  // Handle commands (pause learning)
  const handleCommand = async (command) => {
    setIsLearning(false);
    setMessages((prev) => [
      ...prev,
      {
        type: "assistant",
        message: `Learning paused. Processed command: ${command}`,
        timestamp: new Date().toISOString(),
      },
    ]);
    // You can add more command handling logic here
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (inputMessage.trim() && !isLoading) {
        handleSendMessage();
      }
    }
  };

  return (
    <div className="flex flex-col h-screen bg-secondary-50">
      {/* Top bar with Quick Commands button */}
      <div className="flex items-center justify-end px-6 pt-4">
        <button
          className="flex items-center space-x-2 px-3 py-1 bg-secondary-100 text-secondary-700 rounded hover:bg-secondary-200 transition-colors"
          onClick={() => setShowCommandHelp((v) => !v)}
        >
          <CommandLineIcon className="w-5 h-5" />
          <span>Quick Commands</span>
        </button>
        <CommandHelp
          isVisible={showCommandHelp}
          onClose={() => setShowCommandHelp(false)}
        />
      </div>

      {/* Chat area */}
      <div className="flex-1 overflow-y-auto px-6 py-8">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center text-center mt-24 mb-8">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ delay: 0.2 }}
              className="w-20 h-20 bg-gradient-to-r from-primary-500 to-primary-600 rounded-full flex items-center justify-center mb-4"
            >
              <SparklesIcon className="w-10 h-10 text-white" />
            </motion.div>
            <h2 className="text-2xl font-bold text-secondary-900 mb-2">
              Welcome to your AI Tutor!
            </h2>
            <p className="text-secondary-600 mb-6 max-w-md">
              I'm here to help you learn. Ask me anything, request explanations,
              or use commands like !quiz or !explain.
            </p>
            {/* Suggestion chips */}
            {suggestions.length > 0 && (
              <div className="space-y-3">
                <p className="text-sm font-medium text-secondary-700">
                  Try asking:
                </p>
                <div className="flex flex-wrap gap-2 justify-center">
                  {suggestions.map((suggestion, index) => (
                    <SuggestionChip
                      key={index}
                      suggestion={suggestion}
                      onClick={handleSendMessage}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        ) : (
          <div className="space-y-1">
            {messages.map((message, index) => (
              <MessageBubble
                key={index}
                message={message.message}
                isUser={message.type === "user"}
                citations={message.citations}
                timestamp={message.timestamp}
              />
            ))}
            {/* Loading indicator */}
            {isLoading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="flex justify-start mb-4"
              >
                <div className="bg-white border border-secondary-200 rounded-2xl rounded-bl-sm px-4 py-3">
                  <div className="flex items-center space-x-2">
                    <div className="flex space-x-1">
                      <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce"></div>
                      <div
                        className="w-2 h-2 bg-primary-500 rounded-full animate-bounce"
                        style={{ animationDelay: "0.1s" }}
                      ></div>
                      <div
                        className="w-2 h-2 bg-primary-500 rounded-full animate-bounce"
                        style={{ animationDelay: "0.2s" }}
                      ></div>
                    </div>
                    <span className="text-xs text-secondary-500">
                      AI is thinking...
                    </span>
                  </div>
                </div>
              </motion.div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>
      {/* Input Area */}
      <div className="bg-white border-t border-secondary-200 p-4 relative">
        <div className="flex items-end space-x-3">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={
                isLearning
                  ? "Type your answer to the question or enter a command..."
                  : "Type a topic to start learning, or enter a command..."
              }
              className="w-full resize-none px-4 py-3 pr-12 border border-secondary-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 max-h-32"
              rows={1}
              disabled={isLoading}
            />
            <button
              onClick={() => handleSendMessage()}
              disabled={!inputMessage.trim() || isLoading}
              className="absolute right-2 bottom-2 p-2 bg-primary-600 hover:bg-primary-700 disabled:bg-secondary-300 disabled:cursor-not-allowed text-white rounded-full transition-colors duration-200"
            >
              <PaperAirplaneIcon className="w-4 h-4" />
            </button>
          </div>
        </div>
        {/* Quick suggestions */}
        {suggestions.length > 0 && messages.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            <span className="text-xs text-secondary-600 py-2">
              Quick suggestions:
            </span>
            {suggestions.slice(0, 3).map((suggestion, index) => (
              <SuggestionChip
                key={index}
                suggestion={suggestion}
                onClick={handleSendMessage}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Learn;
