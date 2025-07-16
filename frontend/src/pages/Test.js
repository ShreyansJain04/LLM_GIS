import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  BookOpenIcon,
  PlayIcon,
  TrophyIcon,
} from "@heroicons/react/24/outline";
import { useUser } from "../contexts/UserContext";
import toast from "react-hot-toast";
import { contentAPI, learningAPI } from "../services/api";
import QuestionCard from "../components/QuestionCard";

const Test = () => {
  const { user } = useUser();
  const [topic, setTopic] = useState("");
  const [plan, setPlan] = useState(null);
  const [currentStep, setCurrentStep] = useState(0);
  const [sessionState, setSessionState] = useState("input"); // input, testing, summary
  const [loading, setLoading] = useState(false);
  const [question, setQuestion] = useState(null);
  const [askedQuestions, setAskedQuestions] = useState([]);
  const [subtopicsPerformance, setSubtopicsPerformance] = useState([]);
  const [feedback, setFeedback] = useState("");
  const [isCorrect, setIsCorrect] = useState(false);
  const [loadingQuestion, setLoadingQuestion] = useState(false);
  const [loadingAnswer, setLoadingAnswer] = useState(false);
  const [testComplete, setTestComplete] = useState(false);
  const [finalScore, setFinalScore] = useState(0);
  const [masteryLevel, setMasteryLevel] = useState("");
  const numQuestions = 3;

  // Start test: reset state and load first question
  const handleStartTest = async (e) => {
    e.preventDefault();
    if (!topic.trim()) return;
    setLoading(true);
    setSessionState("testing");
    setAskedQuestions([]);
    setSubtopicsPerformance([]);
    setCurrentStep(0);
    setTestComplete(false);
    setFinalScore(0);
    setMasteryLevel("");
    setFeedback("");
    setIsCorrect(false);
    try {
      await loadNextQuestion([]);
    } catch (err) {
      toast.error("Failed to start test");
      setSessionState("input");
    } finally {
      setLoading(false);
    }
  };

  // Load next question from backend
  const loadNextQuestion = async (prevQuestions) => {
    setLoadingQuestion(true);
    setQuestion(null);
    setFeedback("");
    setIsCorrect(false);
    console.log("prevQuestions", prevQuestions);
    try {
      const res = await contentAPI.generateQuestion(
        topic,
        prevQuestions,
        "medium",
        "objective"
      );
      // Accept both {question: ...} and string
      const q = res.question || res;
      setQuestion(q);
    } catch (err) {
      toast.error("Failed to load question");
    } finally {
      setLoadingQuestion(false);
    }
  };

  // Handle answer submission
  const handleAnswer = async (answer) => {
    setLoadingAnswer(true);
    try {
      const qObj = question;
      let answerToSend = answer;
      let questionText = qObj;
      let options = qObj && qObj.options ? qObj.options : null;
      if (options) {
        // answer is index (0-3), send as string and send question text
        answerToSend = String(answer);
        questionText = { ...qObj, text: qObj.text, options: qObj.options };
      }
      const res = await contentAPI.checkAnswer(questionText, answerToSend);
      setFeedback(res.feedback);
      setIsCorrect(res.correct);
      // Track asked questions and performance
      setAskedQuestions((prev) => [...prev, qObj]);
      setSubtopicsPerformance((prev) => [
        ...prev,
        {
          subtopic: `Test Question ${currentStep + 1}`,
          question: qObj,
          user_answer: answerToSend,
          correct: res.correct,
          score: res.correct ? 1 : 0,
          feedback: res.feedback,
        },
      ]);
      // After delay, go to next or finish
      setTimeout(async () => {
        if (currentStep + 1 < numQuestions) {
          setCurrentStep((prev) => prev + 1);
          await loadNextQuestion([...askedQuestions, qObj]);
        } else {
          // Test complete
          const totalCorrect = [
            ...subtopicsPerformance,
            {
              subtopic: `Test Question ${currentStep + 1}`,
              question: qObj,
              user_answer: answerToSend,
              correct: res.correct,
              score: res.correct ? 1 : 0,
              feedback: res.feedback,
            },
          ].filter((p) => p.correct).length;
          const score = totalCorrect / numQuestions;
          setFinalScore(score);
          let mastery = "beginner";
          if (score >= 0.8) mastery = "mastered";
          else if (score >= 0.6) mastery = "intermediate";
          setMasteryLevel(mastery);
          setTestComplete(true);
          setSessionState("summary");
          // Record session
          if (user?.username) {
            try {
              await learningAPI.recordSession({
                username: user.username,
                topic,
                subtopics_performance: [
                  ...subtopicsPerformance,
                  {
                    subtopic: `Test Question ${currentStep + 1}`,
                    question: qObj,
                    user_answer: answerToSend,
                    correct: res.correct,
                    score: res.correct ? 1 : 0,
                    feedback: res.feedback,
                  },
                ],
                final_score: score,
                mastery_level: mastery,
              });
            } catch (err) {
              // Don't block UI on error
            }
          }
        }
      }, 1500);
    } catch (err) {
      toast.error("Failed to check answer");
    } finally {
      setLoadingAnswer(false);
    }
  };

  // Reset test
  const resetSession = () => {
    setSessionState("input");
    setPlan(null);
    setCurrentStep(0);
    setTopic("");
    setQuestion(null);
    setAskedQuestions([]);
    setSubtopicsPerformance([]);
    setTestComplete(false);
    setFinalScore(0);
    setMasteryLevel("");
    setFeedback("");
    setIsCorrect(false);
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

  if (sessionState === "summary") {
    return (
      <div className="p-6 max-w-xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white rounded-xl shadow-sm border border-secondary-200 p-8 text-center"
        >
          <div className="mb-6">
            <TrophyIcon className="w-16 h-16 text-primary-600 mx-auto mb-4" />
            <h2 className="text-2xl font-bold text-secondary-900 mb-2">
              Test Complete!
            </h2>
            <p className="text-secondary-600">
              You scored {(finalScore * 100).toFixed(1)}%<br />
              Mastery Level:{" "}
              <span className="font-semibold">
                {masteryLevel.toUpperCase()}
              </span>
            </p>
          </div>
          <div className="mb-8 text-left">
            <h3 className="text-lg font-medium mb-2">Your Answers:</h3>
            <ul className="space-y-2">
              {subtopicsPerformance.map((perf, idx) => (
                <li
                  key={idx}
                  className="p-3 rounded bg-secondary-50 border border-secondary-200"
                >
                  <div className="font-medium">
                    Q{idx + 1}:{" "}
                    {typeof perf.question === "object" && perf.question.text
                      ? perf.question.text
                      : perf.question}
                  </div>
                  <div>
                    Your answer:{" "}
                    <span className="font-mono">{perf.user_answer}</span>
                  </div>
                  <div>Correct: {perf.correct ? "✅" : "❌"}</div>
                  <div className="text-sm text-secondary-600">
                    Feedback: {perf.feedback}
                  </div>
                </li>
              ))}
            </ul>
          </div>
          <button
            onClick={resetSession}
            className="bg-primary-600 text-white px-6 py-2 rounded-lg hover:bg-primary-700"
          >
            New Test
          </button>
        </motion.div>
      </div>
    );
  }

  // Testing state
  return (
    <div className="p-6 max-w-xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-secondary-900">
          Testing: {topic}
        </h1>
        <button onClick={resetSession} className="btn-secondary">
          New Topic
        </button>
      </div>
      <div className="mb-4 text-secondary-700">
        Question {currentStep + 1} of {numQuestions}
      </div>
      {loadingQuestion ? (
        <div className="animate-pulse h-24 bg-secondary-200 rounded mb-6" />
      ) : (
        question && (
          <QuestionCard
            question={question}
            onAnswer={handleAnswer}
            loading={loadingAnswer}
            feedback={feedback}
            isCorrect={isCorrect}
          />
        )
      )}
    </div>
  );
};

export default Test;
