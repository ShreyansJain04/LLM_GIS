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
import toast from "react-hot-toast";
import { learningAPI, contentAPI, chatAPI } from "../services/api";
import MessageBubble from "../components/MessageBubble";
import SuggestionChip from "../components/SuggestionChip";
import CommandHelp from "../components/CommandHelp";

const Learn = () => {
  const { user } = useUser();
  const [topic, setTopic] = useState("");
  const [plan, setPlan] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [sessionState, setSessionState] = useState("input");
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [showCommandHelp, setShowCommandHelp] = useState(false);
  const [currentQuizQuestion, setCurrentQuizQuestion] = useState(null);
  const [currentQuizTopic, setCurrentQuizTopic] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const [sessionId, setSessionId] = useState(null);

  // Combined question state
  const [questionState, setQuestionState] = useState({
    text: "",
    options: [],
    type: null,
  });

  // Separate state for selected option
  const [selectedOption, setSelectedOption] = useState("");

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
      { ...msg, timestamp: new Date().toISOString() },
    ]);
  };

  // Helper to add a message with continue button
  const addMessageWithContinue = (msg, continueAction) => {
    setMessages((prev) => [
      ...prev,
      {
        ...msg,
        timestamp: new Date().toISOString(),
        showContinueButton: msg.showContinueButton !== false, // Default to true unless explicitly false
        onContinue: continueAction,
        continueClicked: false,
      },
    ]);
  };

  // Helper to handle continue button click
  const handleContinueClick = (messageIndex, continueAction) => {
    setMessages((prev) =>
      prev.map((msg, index) =>
        index === messageIndex ? { ...msg, continueClicked: true } : msg
      )
    );
    continueAction();
  };

  // Simple function to add messages sequentially with delays
  const addMessagesSequentially = async (messages) => {
    for (const msg of messages) {
      if (msg.pauseAfter === "name") {
        addMessage(msg);
        await new Promise((resolve) => setTimeout(resolve, 1000));
      } else if (
        msg.pauseAfter === "explanation" ||
        msg.pauseAfter === "example"
      ) {
        // Set appropriate session state and turn off loading
        if (msg.pauseAfter === "explanation") {
          setSessionState("waitingForUserAfterExplanation");
          setIsLoading(false);
        } else if (msg.pauseAfter === "example") {
          setSessionState("waitingForUserAfterExample");
        }

        addMessageWithContinue(msg, () => {
          // Continue to next message after user clicks continue
          setTimeout(() => {
            const nextIndex = messages.indexOf(msg) + 1;
            if (nextIndex < messages.length) {
              addMessagesSequentially(messages.slice(nextIndex));
            }
          }, 100);
        });
        break; // Stop here and wait for user to continue
      } else if (msg.pauseAfter === "question") {
        addMessage(msg);
        setSessionState("awaitingAnswer");
        setQuestionState({
          text: msg.questionText,
          options: msg.options || [],
          type: msg.questionType || "objective",
          correct_option: msg.correct_option || 0,
          explanation: msg.explanation || "",
        });
        break; // Stop here and wait for user to answer
      } else {
        addMessage(msg);
        await new Promise((resolve) => setTimeout(resolve, 500));
      }
    }
  };

  // Start learning session
  const startLearningSession = async (topicText) => {
    setIsLoading(true);
    setPlan(null);
    setCurrentStep(0);
    setSessionState("revealing");
    setQuestionState({ text: "", options: [], type: null });
    setSelectedOption("");
    setSessionId(null);

    try {
      // Add initial message
      addMessage({
        type: "assistant",
        message: `Creating a learning plan for: **${topicText}** ...`,
      });

      const result = await learningAPI.startLearningSession(
        user.username,
        topicText
      );
      setSessionId(result.session_id);
      setPlan(result.plan);

      addMessage({
        type: "assistant",
        message: `✅ Learning plan created! ${
          result.plan.subtopics?.length || 0
        } subtopics to cover.`,
      });

      if (result.plan.subtopics?.length > 0) {
        await buildSubtopicMessages(result.plan.subtopics[0], 0, true);
      }
    } catch (error) {
      addMessage({
        type: "assistant",
        message: `Failed to create learning plan.`,
      });
      setSessionState("input");
    } finally {
      setIsLoading(false);
    }
  };

  // Build subtopic messages
  const buildSubtopicMessages = async (
    subtopic,
    stepIdx,
    autoRevealFirst = false
  ) => {
    const messages = [
      {
        type: "assistant",
        message: `**Subtopic ${stepIdx + 1}: ${subtopic.name}**`,
        auto: true,
        pauseAfter: "name",
      },
    ];

    // Add explanation
    try {
      const explainData = await contentAPI.explainConcept(
        subtopic.name,
        "standard"
      );
      messages.push({
        type: "assistant",
        message: `**Explanation:**\n${explainData.explanation}`,
        pauseAfter: "explanation",
        showContinueButton: true,
      });
    } catch {
      messages.push({
        type: "assistant",
        message: `Failed to load explanation for ${subtopic.name}.`,
        pauseAfter: "explanation",
        showContinueButton: true,
      });
    }

    // Add example
    try {
      const exampleData = await contentAPI.generateExample(
        subtopic.name,
        "medium"
      );
      messages.push({
        type: "assistant",
        message: `**Example:**\n${exampleData.example}`,
        pauseAfter: "example",
        showContinueButton: true,
      });
    } catch {
      messages.push({
        type: "assistant",
        message: `Failed to load example for ${subtopic.name}.`,
        pauseAfter: "example",
        showContinueButton: true,
      });
    }

    // Add question
    try {
      const questionData = await contentAPI.generateQuestion(
        subtopic.name,
        [],
        "medium",
        "objective"
      );
      messages.push({
        type: "assistant",
        message: `**Question:**\n${questionData.question.text}`,
        pauseAfter: "question",
        isQuestion: true,
        questionText: questionData.question.text,
        options: questionData.question.options || [],
        showOptions: true,
        questionType: questionData.question.type || "objective",
        correct_option: questionData.question.correct_option || 0,
        explanation: questionData.question.explanation || "",
        questionObj: questionData.question,
      });
    } catch {
      messages.push({
        type: "assistant",
        message: `Failed to load question for ${subtopic.name}.`,
        pauseAfter: "question",
        isQuestion: true,
        questionText: "",
        options: [],
      });
    }

    // Start processing messages sequentially
    addMessagesSequentially(messages);
  };

  // Handle user input
  const handleSendMessage = async (messageText = inputMessage) => {
    if (isLoading) return;

    // Handle commands (always allow commands)
    if (messageText.trim().startsWith("!")) {
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

    // Handle different session states
    if (sessionState === "input" && messageText.trim()) {
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

    // Handle continue button clicks for explanation/example/feedback messages
    if (
      sessionState === "waitingForUserAfterExplanation" ||
      sessionState === "waitingForUserAfterExample" ||
      sessionState === "waitingForUserAfterFeedback"
    ) {
      // User pressed enter to continue - this should trigger the continue button
      if (messageText.trim() === "") {
        // Find the last message with a continue button and trigger it
        const lastMessageWithContinue = messages
          .slice()
          .reverse()
          .find((msg) => msg.showContinueButton && !msg.continueClicked);

        if (lastMessageWithContinue) {
          const messageIndex = messages.findIndex(
            (msg) => msg === lastMessageWithContinue
          );
          handleContinueClick(messageIndex, lastMessageWithContinue.onContinue);
        }
      } else {
        // User tried to send a regular message - show error
        toast.error(
          "Please click 'Continue' or press Enter to proceed, or use commands (type ! for help)"
        );
      }
      return;
    }

    // Handle invalid input during question
    if (sessionState === "awaitingAnswer" && messageText.trim()) {
      setInputMessage("");
      const errorMsg =
        questionState.type === "objective"
          ? "Please select an option from the question above or use a command (type ! for help)"
          : "Please answer the question above or use a command (type ! for help)";
      toast.error(errorMsg);
      return;
    }
  };

  // Handle commands
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
            addMessage({
              type: "assistant",
              message: explainResponse.response,
              citations: explainResponse.citations,
            });
          }
          break;
        case "quiz":
          if (args.length > 0) {
            const topic = args.join(" ");
            const quizResponse = await contentAPI.generateQuestion(topic);
            setCurrentQuizQuestion(quizResponse.text);
            setCurrentQuizTopic(topic);
            addMessage({
              type: "assistant",
              message: `Quiz started for "${topic}":\n\n${quizResponse.text}`,
            });
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

  // Clear chat <-- this is for chat instead of learn mode
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

  // Handle answer submission
  const handleAnswer = async (answer) => {
    setIsLoading(true);
    setSessionState("checkingAnswer");

    try {
      let answerToSend;
      if (
        questionState.options.length > 0 &&
        typeof parseInt(answer) === "number" &&
        parseInt(answer) >= 0 &&
        parseInt(answer) < questionState.options.length
      ) {
        answerToSend = answer;
      } else {
        answerToSend = answer;
      }
      const cleanQuestion = {
        text: questionState.text,
        type: questionState.type,
        options: questionState.options || [],
        correct_option: parseInt(questionState.correct_option) || 0,
        explanation: questionState.explanation || "",
      };
      if (!cleanQuestion.text) {
        addMessage({
          type: "assistant",
          message: "Error: Question text is missing.",
        });
        return;
      }
      if (!cleanQuestion.type) {
        addMessage({
          type: "assistant",
          message: "Error: Question type is missing.",
        });
        return;
      }
      const result = await contentAPI.checkAnswer(cleanQuestion, answerToSend);
      // Build performance entry
      const performanceEntry = {
        subtopic: plan?.subtopics?.[currentStep]?.name || topic,
        question: cleanQuestion.text,
        answer: answerToSend,
        correct: result.correct,
        question_type: cleanQuestion.type,
        difficulty: "medium",
        timestamp: new Date().toISOString(),
        options: cleanQuestion.options,
        correct_option: cleanQuestion.correct_option,
        selected_option: parseInt(answerToSend),
        explanation: cleanQuestion.explanation,
      };
      // Update session incrementally
      if (sessionId) {
        await learningAPI.updateLearningSession(sessionId, {
          question: cleanQuestion,
          correct: result.correct,
          performance_entry: performanceEntry,
          subtopic: plan?.subtopics?.[currentStep]?.name || topic,
          current_subtopic_index: currentStep,
        });
      }
      addMessageWithContinue(
        {
          type: "assistant",
          message: `**Feedback:** ${result.feedback}`,
          showContinueButton: true,
        },
        async () => {
          if (plan && currentStep < plan.subtopics.length - 1) {
            const nextStep = currentStep + 1;
            addMessage({
              type: "assistant",
              message: `⏳ AI is preparing subtopic ${nextStep + 1}...`,
            });
            setSessionState("preparingSubtopic");
            setIsLoading(true);
            await buildSubtopicMessages(
              plan.subtopics[nextStep],
              nextStep,
              false
            );
            setCurrentStep(nextStep);
            setQuestionState({
              text: "",
              options: [],
              type: null,
            });
            setSelectedOption("");
          } else {
            addMessage({
              type: "assistant",
              message: `🎉 **Learning session completed!** You can now ask more questions or use ! commands.`,
            });
            setSessionState("completed");
            setQuestionState({
              text: "",
              options: [],
              type: null,
            });
            setSelectedOption("");
            // End and record session
            if (sessionId) {
              try {
                await learningAPI.endLearningSession(sessionId);
              } catch (err) {
                console.error("Failed to end session", err);
              }
            }
          }
        }
      );
      setSessionState("waitingForUserAfterFeedback");
    } catch (error) {
      addMessage({ type: "assistant", message: `Failed to check answer.` });
      setSessionState("waitingForUserAfterQuestion");
    } finally {
      setIsLoading(false);
    }
  };

  // Utility functions
  const isSpecialCommand = (message) => message.trim().startsWith("!");

  const shouldDisableSubmit = () => {
    if (isLoading) return true;

    // Allow empty input for continue actions
    if (
      sessionState === "waitingForUserAfterExplanation" ||
      sessionState === "waitingForUserAfterExample" ||
      sessionState === "waitingForUserAfterFeedback"
    ) {
      return false; // Allow empty input to trigger continue
    }

    if (!inputMessage.trim()) return true;

    if (
      sessionState === "awaitingAnswer" &&
      questionState.type === "objective"
    ) {
      // For objective questions, only allow special commands
      return !isSpecialCommand(inputMessage);
    }
    return false;
  };

  const getPlaceholder = () => {
    if (
      sessionState === "awaitingAnswer" &&
      questionState.type === "objective"
    ) {
      return "Select an option above or use commands (type ! for help)...";
    }
    if (sessionState === "awaitingAnswer") {
      return "Type your answer or use commands (type ! for help)...";
    }
    if (
      sessionState === "waitingForUserAfterExplanation" ||
      sessionState === "waitingForUserAfterExample" ||
      sessionState === "waitingForUserAfterFeedback"
    ) {
      return "Press Enter to continue, or use commands (type ! for help)...";
    }
    return "Ask a question, request help, or type ! for commands...";
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
                      onClick={(suggestion) => handleSendMessage(suggestion)}
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
                showContinueButton={message.showContinueButton}
                onContinue={
                  message.onContinue
                    ? () => handleContinueClick(index, message.onContinue)
                    : undefined
                }
                continueClicked={message.continueClicked}
                showOptions={message.showOptions}
                options={message.options}
                selectedOptionIndex={selectedOption}
                onOptionSelect={(selectedOptionIndex) => {
                  console.log("Selected option index:", selectedOptionIndex);
                  setSelectedOption(selectedOptionIndex.toString()); // Save as string
                  // Submit immediately when option is selected
                  handleAnswer(selectedOptionIndex.toString());
                }}
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
            {/* Helper text for objective questions */}
            {sessionState === "awaitingAnswer" &&
              questionState.type === "objective" && (
                <div className="text-xs text-secondary-500 mb-2 px-1">
                  💡 For objective questions, please select an option above or
                  use commands (type ! for help)
                </div>
              )}
            {/* Single textarea for all states - MCQ options are handled in message bubbles */}
            <textarea
              ref={inputRef}
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => {
                if (e.key === "Enter" && !isLoading) {
                  // Allow Enter for continue actions even with empty input
                  if (
                    inputMessage.trim() ||
                    sessionState === "waitingForUserAfterExplanation" ||
                    sessionState === "waitingForUserAfterExample"
                  ) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }
              }}
              placeholder={getPlaceholder()}
              className="w-full resize-none px-4 py-3 pr-12 border border-secondary-300 rounded-2xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all duration-200 max-h-32"
              rows={1}
            />
            {/* Submit button */}
            <button
              onClick={() => handleSendMessage()}
              disabled={shouldDisableSubmit()}
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
                onClick={(suggestion) => handleSendMessage(suggestion)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Learn;
