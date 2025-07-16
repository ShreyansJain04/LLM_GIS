import React, { useState, useEffect, useRef } from "react";
import { motion } from "framer-motion";
import {
  ChatBubbleLeftRightIcon,
  PaperAirplaneIcon,
  CommandLineIcon,
  TrashIcon,
  QuestionMarkCircleIcon,
  SparklesIcon,
} from "@heroicons/react/24/outline";
import { useUser } from "../contexts/UserContext";
import { chatAPI } from "../services/api";
import toast from "react-hot-toast";
import MessageBubble from "../components/MessageBubble";
import SuggestionChip from "../components/SuggestionChip";
import CommandHelp from "../components/CommandHelp";

const Chat = () => {
  const { user } = useUser();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [showCommandHelp, setShowCommandHelp] = useState(false);
  const [currentQuizQuestion, setCurrentQuizQuestion] = useState(null);
  const [currentQuizTopic, setCurrentQuizTopic] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Load chat history and suggestions on mount
  useEffect(() => {
    if (user?.username) {
      loadChatHistory();
      loadSuggestions();
    }
  }, [user]);

  const loadChatHistory = async () => {
    try {
      const historyData = await chatAPI.getChatHistory(user.username, 50);
      setMessages(historyData.history || []);
    } catch (error) {
      console.error("Failed to load chat history:", error);
    }
  };

  const loadSuggestions = async () => {
    try {
      const suggestionsData = await chatAPI.getSuggestions(user.username);
      setSuggestions(suggestionsData.suggestions.slice(0, 3) || []);
    } catch (error) {
      console.error("Failed to load suggestions:", error);
    }
  };

  const handleSendMessage = async (messageText = inputMessage) => {
    if (!messageText.trim() || isLoading) return;

    const userMessage = {
      type: "user",
      message: messageText,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputMessage("");
    setIsLoading(true);

    try {
      // Check if it's a command
      if (messageText.startsWith("!")) {
        await handleCommand(messageText);
      } else {
        // Regular chat message
        const response = await chatAPI.sendMessage(user.username, messageText);

        const assistantMessage = {
          type: "assistant",
          message: response.response,
          citations: response.citations,
          timestamp: new Date().toISOString(),
        };

        setMessages((prev) => [...prev, assistantMessage]);
      }
    } catch (error) {
      console.error("Failed to send message:", error);
      toast.error("Failed to send message");

      const errorMessage = {
        type: "assistant",
        message: "Sorry, I encountered an error. Please try again.",
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCommand = async (command) => {
    const [cmd, ...args] = command.slice(1).split(" ");

    try {
      switch (cmd.toLowerCase()) {
        case "help":
          toast.success("Check the commands panel for available commands");
          break;
        case "explain":
          if (args.length > 0) {
            const topic = args.join(" ");
            const response = await chatAPI.sendMessage(
              user.username,
              `Please explain ${topic}`
            );
            const assistantMessage = {
              type: "assistant",
              message: response.response,
              citations: response.citations,
              timestamp: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, assistantMessage]);
          }
          break;
        case "quiz":
          if (args.length > 0) {
            const topic = args.join(" ");
            const quizData = await chatAPI.startQuiz(user.username, topic);
            setCurrentQuizQuestion(quizData.question);
            setCurrentQuizTopic(topic);
            const assistantMessage = {
              type: "assistant",
              message: `Quiz started for "${topic}":\n\n${quizData.question}`,
              timestamp: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, assistantMessage]);
          }
          break;
        default:
          toast.error(`Unknown command: ${cmd}`);
      }
    } catch (error) {
      console.error("Command error:", error);
      toast.error("Failed to execute command");
    }
  };

  // const handleQuizAnswer = async (answer) => {
  //   if (!currentQuizQuestion || !currentQuizTopic) return;

  //   setIsLoading(true);
  //   try {
  //     const result = await chatAPI.submitQuizAnswer(
  //       user.username,
  //       currentQuizTopic,
  //       answer
  //     );

  //     const assistantMessage = {
  //       type: "assistant",
  //       message: result.feedback,
  //       timestamp: new Date().toISOString(),
  //     };

  //     setMessages((prev) => [...prev, assistantMessage]);
  //     setCurrentQuizQuestion(null);
  //     setCurrentQuizTopic(null);
  //   } catch (error) {
  //     console.error("Failed to submit quiz answer:", error);
  //     toast.error("Failed to submit answer");
  //   } finally {
  //     setIsLoading(false);
  //   }
  // };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (inputMessage.trim() && !isLoading) {
        handleSendMessage();
      }
    }
  };

  const clearChat = async () => {
    try {
      await chatAPI.clearChatHistory(user.username);
      setMessages([]);
      setCurrentQuizQuestion(null);
      setCurrentQuizTopic(null);
      toast.success("Chat history cleared");
    } catch (error) {
      console.error("Failed to clear chat:", error);
      toast.error("Failed to clear chat");
    }
  };

  const handleSuggestionClick = (suggestion) => {
    handleSendMessage(suggestion);
  };

  return (
    <div className="flex flex-col h-screen bg-secondary-50">
      {/* Header */}
      <div className="bg-white border-b border-secondary-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-gradient-to-r from-primary-500 to-primary-600 rounded-full flex items-center justify-center">
              <ChatBubbleLeftRightIcon className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-secondary-900">
                AI Tutor Chat
              </h1>
              <p className="text-sm text-secondary-600">
                Ask questions, get explanations, or use commands (type ! for
                help)
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={() => setShowCommandHelp(!showCommandHelp)}
              className="btn-secondary text-sm"
              title="Show commands"
            >
              <CommandLineIcon className="w-4 h-4 mr-1" />
              Commands
            </button>
            <button
              onClick={clearChat}
              className="text-red-600 hover:bg-red-50 p-2 rounded-lg transition-colors duration-200"
              title="Clear chat"
            >
              <TrashIcon className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Current Quiz Indicator */}
        {currentQuizQuestion && (
          <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div className="flex items-center space-x-2">
              <QuestionMarkCircleIcon className="w-5 h-5 text-yellow-600" />
              <span className="text-sm font-medium text-yellow-800">
                Quiz Mode: {currentQuizTopic}
              </span>
            </div>
            <p className="text-xs text-yellow-700 mt-1">
              Answer the question above to continue
            </p>
          </div>
        )}
      </div>

      {/* Messages Area */}
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
                      onClick={handleSuggestionClick}
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
        <CommandHelp
          isVisible={showCommandHelp}
          onClose={() => setShowCommandHelp(false)}
        />

        <div className="flex items-end space-x-3">
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder={
                currentQuizQuestion
                  ? "Type your answer to the quiz question..."
                  : "Ask a question, request help, or type ! for commands..."
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
                onClick={handleSuggestionClick}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Chat;
