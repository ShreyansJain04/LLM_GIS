import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import ReactMarkdown from "react-markdown";
import {
  ChatBubbleLeftRightIcon,
  PaperAirplaneIcon,
  CommandLineIcon,
  TrashIcon, 
  QuestionMarkCircleIcon,
  SparklesIcon,
  XCircleIcon,
} from "@heroicons/react/24/outline";
import { useUser } from "../contexts/UserContext";
import toast from "react-hot-toast";
import { learningAPI, contentAPI, chatAPI } from "../services/api";


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
  const [topic, setTopic] = useState("");
  const [plan, setPlan] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [sessionState, setSessionState] = useState("input");
  const [messages, setMessages] = useState([]);
  const [messageQueue, setMessageQueue] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [showCommandHelp, setShowCommandHelp] = useState(false);
  const [currentQuizQuestion, setCurrentQuizQuestion] = useState(null);
  const [currentQuizTopic, setCurrentQuizTopic] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const [loadingContent, setLoadingContent] = useState({
    explanation: false,
    example: false,
    question: false,
    answer: false,
  });


  // Content states
  const [explanation, setExplanation] = useState("");
  const [example, setExample] = useState("");
  const [question, setQuestion] = useState("");
  const [feedback, setFeedback] = useState("");
  const [isCorrect, setIsCorrect] = useState(false);


  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };


  useEffect(() => {
    scrollToBottom();
  }, [messages]);


  // Helper to add a message to chat
  const addMessage = (msg) => {
    setMessages((prev) => [
      ...prev,
      {
        ...msg,
        timestamp: new Date().toISOString(),
      },
    ]);
  };


  // Helper to queue messages
  const queueMessages = (msgs) => {
    setMessageQueue((prev) => [...prev, ...msgs]);
  };


  // When messageQueue changes, if not empty and sessionState is 'revealing', pop and show next message
  useEffect(() => {
    if (messageQueue.length > 0 && sessionState === "revealing") {
      const [nextMsg, ...rest] = messageQueue;
      addMessage(nextMsg);
      setMessageQueue(rest);
      // Only auto-reveal the subtopic name, then pause for user after each step
      if (nextMsg.auto && nextMsg.pauseAfter === "name") {
        setTimeout(() => {
          setSessionState("waitingForUserAfterName");
        }, Math.floor(500 + Math.random() * 500));
      } else if (nextMsg.pauseAfter === "explanation") {
        setIsLoading(false);
        setSessionState("waitingForUserAfterExplanation");
      } else if (nextMsg.pauseAfter === "example") {
        setSessionState("waitingForUserAfterExample");
      } else if (nextMsg.pauseAfter === "question") {
        setSessionState("awaitingAnswer");
        setQuestion(nextMsg.questionText);
      }
    }
  }, [messageQueue, sessionState]);


  // Start learning session when topic is submitted
  const startLearningSession = async (topicText) => {
    setIsLoading(true);
    setMessages([]);
    setPlan(null);
    setCurrentStep(0);
    setSessionState("revealing");
    try {
      queueMessages([
        {
          type: "assistant",
          message: `Creating a learning plan for: **${topicText}** ...`,
        },
      ]);
      const learningPlan = await learningAPI.getLearningPlan(
        user.username,
        topicText
      );
      setPlan(learningPlan);
      addMessage({
        type: "assistant",
        message: `✅ Learning plan created! ${
          learningPlan.subtopics?.length || 0
        } subtopics to cover.`,
      });
      setCurrentStep(0);
      // Immediately auto-reveal the first subtopic
      if (learningPlan.subtopics?.length > 0) {
        await buildSubtopicQueue(learningPlan.subtopics[0], 0, true); // true = auto-reveal
      }
    } catch (error) {
      queueMessages([
        { type: "assistant", message: `Failed to create learning plan.` },
      ]);
      setSessionState("input");
    } finally {
      setIsLoading(false);
    }
  };


  // buildSubtopicQueue: only auto-reveal subtopic name and explanation, then pause for user before example, then pause for user before question, then pause for user before feedback
  const buildSubtopicQueue = async (
    subtopic,
    stepIdx,
    autoRevealFirst = false
  ) => {
    const queue = [];
    queue.push({
      type: "assistant",
      message: `**Subtopic ${stepIdx + 1}: ${subtopic.name}**`,
      auto: true,
      pauseAfter: "name",
    });
    try {
      const explainData = await contentAPI.explainConcept(
        subtopic.name,
        "standard"
      );
      queue.push({
        type: "assistant",
        message: `**Explanation:**\n${explainData.explanation}`,
        pauseAfter: "explanation",
      });
    } catch {
      queue.push({
        type: "assistant",
        message: `Failed to load explanation for ${subtopic.name}.`,
        pauseAfter: "explanation",
      });
    }
    try {
      const exampleData = await contentAPI.generateExample(
        subtopic.name,
        "medium"
      );
      queue.push({
        type: "assistant",
        message: `**Example:**\n${exampleData.example}`,
        pauseAfter: "example",
      });
    } catch {
      queue.push({
        type: "assistant",
        message: `Failed to load example for ${subtopic.name}.`,
        pauseAfter: "example",
      });
    }
    try {
      const questionData = await contentAPI.generateQuestion(
        subtopic.name,
        [],
        "medium",
        "analytical"
      );
      queue.push({
        type: "assistant",
        message: `**Question:**\n${questionData.question}`,
        pauseAfter: "question",
        isQuestion: true,
        questionText: questionData.question,
      });
    } catch {
      queue.push({
        type: "assistant",
        message: `Failed to load question for ${subtopic.name}.`,
        pauseAfter: "question",
        isQuestion: true,
        questionText: "",
      });
    }
    setMessageQueue(queue); // Replace queue for new subtopic
    setSessionState("revealing"); // Always start with auto-reveal of name
  };


  // Handle user input (answer, !command, or Enter to reveal next)
  const handleSendMessage = async (messageText = inputMessage) => {
    if (isLoading) return;
    if (messageText.trim().startsWith("!")) {
      // Handle command
      addMessage({ type: "user", message: messageText });
      setInputMessage("");
      setIsLoading(true);
      try {
        await handleCommand(messageText);
      } finally {
        setIsLoading(false);
      }
      return;
    }
    if (sessionState === "input" && messageText.trim()) {
      // User is submitting a topic
      setTopic(messageText.trim());
      addMessage({ type: "user", message: messageText.trim() });
      setInputMessage("");
      await startLearningSession(messageText.trim());
      return;
    }
    if (sessionState === "awaitingAnswer" && messageText.trim()) {
      // User is answering the question
      addMessage({ type: "user", message: messageText.trim() });
      setInputMessage("");
      await handleAnswer(messageText.trim());
      return;
    }
    if (sessionState === "waitingForUserAfterName" && !messageText.trim()) {
      setSessionState("revealing"); // Reveal explanation
      return;
    }
    if (
      sessionState === "waitingForUserAfterExplanation" &&
      !messageText.trim()
    ) {
      setSessionState("revealing"); // Reveal example
      return;
    }
    if (sessionState === "waitingForUserAfterExample" && !messageText.trim()) {
      setSessionState("revealing"); // Reveal question
      return;
    }
    if (sessionState === "waitingForUserAfterFeedback" && !messageText.trim()) {
      // Move to next subtopic
      if (plan && currentStep < plan.subtopics.length - 1) {
        const nextStep = currentStep + 1;
        // Notify user that AI is preparing the next subtopic and disable input
        addMessage({
          type: "assistant",
          message: `⏳ AI is preparing subtopic ${nextStep + 1}...`,
        });
        setSessionState("preparingSubtopic");
        setIsLoading(true);
        await buildSubtopicQueue(plan.subtopics[nextStep], nextStep, false);
        setCurrentStep(nextStep);
        // Input will be re-enabled after explanation is displayed (see useEffect below)
      } else {
        queueMessages([
          {
            type: "assistant",
            message: `🎉 **Learning session completed!** You can now ask more questions or use ! commands.`,
          },
        ]);
        setSessionState("completed");
      }
      return;
    }
    // Otherwise, treat as a normal chat message
    // if (messageText.trim()) {
    //   addMessage({ type: "user", message: messageText.trim() });
    //   setInputMessage("");
    //   setIsLoading(true);
    //   try {
    //     const response = await chatAPI.sendMessage(
    //       user.username,
    //       messageText.trim()
    //     );
    //     addMessage({
    //       type: "assistant",
    //       message: response.response,
    //       citations: response.citations,
    //     });
    //   } finally {
    //     setIsLoading(false);
    //   }
    // }
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
            const explainResponse = await chatAPI.sendMessage(
              user.username,
              `Please explain ${topic}`
            );
            const assistantMessage = {
              type: "assistant",
              message: explainResponse.response,
              citations: explainResponse.citations,
              timestamp: new Date().toISOString(),
            };
            setMessages((prev) => [...prev, assistantMessage]);
          }
          break;
        case "quiz":
          if (args.length > 0) {
            const topic = args.join(" ");
            const quizResponse = await contentAPI.generateQuestion(topic);
            setCurrentQuizQuestion(quizResponse.question);
            setCurrentQuizTopic(topic);
            const assistantMessage = {
              type: "assistant",
              message: `Quiz started for "${topic}":\n\n${quizResponse.question}`,
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


  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (inputMessage.trim() && !isLoading) {
        handleSendMessage();
      } else if (
        !inputMessage.trim() &&
        [
          "waitingForUserAfterName",
          "waitingForUserAfterExplanation",
          "waitingForUserAfterExample",
          "waitingForUserAfterQuestion",
          "waitingForUserAfterFeedback",
          "waitingForUser",
          "revealing",
        ].includes(sessionState)
      ) {
        handleSendMessage("");
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


  // In handleAnswer, after feedback, set sessionState to waitingForUserAfterFeedback
  const handleAnswer = async (answer) => {
    setIsLoading(true);
    setSessionState("checkingAnswer");
    try {
      const result = await contentAPI.checkAnswer(question, answer);
      addMessage({
        type: "assistant",
        message: `**Feedback:** ${result.feedback}`,
      });
      setSessionState("waitingForUserAfterFeedback");
    } catch (error) {
      addMessage({ type: "assistant", message: `Failed to check answer.` });
      setSessionState("waitingForUserAfterQuestion");
    } finally {
      setIsLoading(false);
    }
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
                Learn with AI Tutor
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
              disabled={
                (isLoading && !plan) ||
                (sessionState === "revealing" && !plan) ||
                sessionState === "planning" ||
                sessionState === "preparingSubtopic"
              }
            />
            <button
              onClick={() => handleSendMessage()}
              disabled={
                (isLoading && !plan) ||
                (sessionState === "revealing" && !plan) ||
                sessionState === "planning" ||
                sessionState === "preparingSubtopic"
              }
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


export default Learn;





