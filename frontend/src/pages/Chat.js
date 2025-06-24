import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
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
} from '@heroicons/react/24/outline';
import { useUser } from '../contexts/UserContext';
import { chatAPI } from '../services/api';
import toast from 'react-hot-toast';

const MessageBubble = ({ message, isUser, citations, timestamp }) => (
  <motion.div
    initial={{ opacity: 0, y: 10 }}
    animate={{ opacity: 1, y: 0 }}
    className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}
  >
    <div className={`max-w-3xl ${isUser ? 'order-2' : 'order-1'}`}>
      <div
        className={`px-4 py-3 rounded-2xl ${
          isUser
            ? 'bg-primary-600 text-white rounded-br-sm'
            : 'bg-white border border-secondary-200 text-secondary-900 rounded-bl-sm'
        }`}
      >
        <div className="prose prose-sm max-w-none">
          {isUser ? (
            <p className="text-white mb-0">{message}</p>
          ) : (
            <ReactMarkdown
              components={{
                p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
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
                <div key={index} className="text-xs text-secondary-600 bg-secondary-50 px-2 py-1 rounded">
                  📄 {citation}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
      
      {/* Timestamp */}
      <div className={`text-xs text-secondary-500 mt-1 ${isUser ? 'text-right' : 'text-left'}`}>
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
            <div><code className="text-primary-600">!help</code> - Show all commands</div>
            <div><code className="text-primary-600">!explain topic</code> - Get explanation</div>
            <div><code className="text-primary-600">!example topic</code> - Get example</div>
            <div><code className="text-primary-600">!question topic</code> - Practice question</div>
          </div>
          <div className="space-y-1">
            <div><code className="text-primary-600">!quiz topic</code> - Start quiz</div>
            <div><code className="text-primary-600">!sources</code> - Show documents</div>
            <div><code className="text-primary-600">!progress</code> - View progress</div>
            <div><code className="text-primary-600">!hint</code> - Get hint</div>
          </div>
        </div>
      </motion.div>
    )}
  </AnimatePresence>
);

const Chat = () => {
  const { user } = useUser();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);
  const [showCommandHelp, setShowCommandHelp] = useState(false);
  const [currentQuizQuestion, setCurrentQuizQuestion] = useState(null);
  const [currentQuizTopic, setCurrentQuizTopic] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
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
      console.error('Failed to load chat history:', error);
    }
  };

  const loadSuggestions = async () => {
    try {
      const suggestionsData = await chatAPI.getChatSuggestions(user.username);
      setSuggestions(suggestionsData.suggestions || []);
    } catch (error) {
      console.error('Failed to load suggestions:', error);
    }
  };

  const handleSendMessage = async (messageText = inputMessage) => {
    if (!messageText.trim() || isLoading) return;

    const userMessage = {
      type: 'user',
      message: messageText,
      timestamp: new Date().toISOString(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Check if it's a command
      if (messageText.startsWith('!')) {
        await handleCommand(messageText);
      } else {
        // Regular chat message
        const response = await chatAPI.sendMessage(user.username, messageText);
        
        const assistantMessage = {
          type: 'assistant',
          message: response.response,
          citations: response.citations,
          timestamp: new Date().toISOString(),
        };

        setMessages(prev => [...prev, assistantMessage]);

        // Update suggestions if provided
        if (response.suggestions && response.suggestions.length > 0) {
          setSuggestions(response.suggestions);
        }
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      toast.error('Failed to send message');
      
      const errorMessage = {
        type: 'assistant',
        message: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCommand = async (command) => {
    const [cmd, ...args] = command.split(' ');
    const argsString = args.join(' ');

    try {
      const response = await chatAPI.executeCommand(
        user.username,
        cmd,
        argsString,
        currentQuizTopic
      );

      if (response.error) {
        const errorMessage = {
          type: 'assistant',
          message: `❌ ${response.error}`,
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, errorMessage]);
        return;
      }

      const assistantMessage = {
        type: 'assistant',
        message: response.response,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, assistantMessage]);

      // Handle special command types
      if (response.type === 'quiz_start') {
        setCurrentQuizQuestion(response.question);
        setCurrentQuizTopic(response.topic);
      }
    } catch (error) {
      console.error('Command failed:', error);
      toast.error('Command failed');
    }
  };

  const handleQuizAnswer = async (answer) => {
    if (!currentQuizQuestion) return;

    try {
      const response = await chatAPI.submitQuizAnswer(currentQuizQuestion, answer);
      
      const feedbackMessage = {
        type: 'assistant',
        message: `${response.correct ? '✅' : '❌'} ${response.feedback}`,
        timestamp: new Date().toISOString(),
      };

      setMessages(prev => [...prev, feedbackMessage]);
      
      // Clear current quiz question
      setCurrentQuizQuestion(null);
      setCurrentQuizTopic(null);
    } catch (error) {
      console.error('Failed to submit quiz answer:', error);
      toast.error('Failed to submit answer');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (currentQuizQuestion && inputMessage.trim()) {
        // If there's an active quiz question, treat input as quiz answer
        const userMessage = {
          type: 'user',
          message: inputMessage,
          timestamp: new Date().toISOString(),
        };
        setMessages(prev => [...prev, userMessage]);
        handleQuizAnswer(inputMessage);
        setInputMessage('');
      } else {
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
      toast.success('Chat history cleared');
    } catch (error) {
      console.error('Failed to clear chat:', error);
      toast.error('Failed to clear chat');
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
              <h1 className="text-xl font-semibold text-secondary-900">AI Tutor Chat</h1>
              <p className="text-sm text-secondary-600">
                Ask questions, get explanations, or use commands (type ! for help)
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
      <div className="flex-1 overflow-auto px-6 py-4">
        {messages.length === 0 ? (
          <div className="flex flex-col items-center justify-center h-full text-center">
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
                <p className="text-sm font-medium text-secondary-700">Try asking:</p>
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
                isUser={message.type === 'user'}
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
                      <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-primary-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                    <span className="text-xs text-secondary-500">AI is thinking...</span>
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
            <span className="text-xs text-secondary-600 py-2">Quick suggestions:</span>
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