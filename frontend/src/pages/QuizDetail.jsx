import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { RadioGroup, RadioGroupItem } from '../components/ui/radio-group';
import { Label } from '../components/ui/label';
import { LayoutDashboard, BookOpen, Brain, FileText, Lightbulb, Settings, LogOut, ArrowLeft } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const QuizDetail = () => {
  const { id } = useParams();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [quiz, setQuiz] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState({});
  const [quizSubmitted, setQuizSubmitted] = useState(false);
  const [quizResult, setQuizResult] = useState(null);

  useEffect(() => {
    fetchQuizDetail();
  }, [id, user]);

  const fetchQuizDetail = async () => {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_URL}/quizzes/${id}`);
      setQuiz(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch quiz details');
    }
    setLoading(false);
  };

  const handleAnswerChange = (questionId, answer) => {
    setUserAnswers((prevAnswers) => ({
      ...prevAnswers,
      [questionId]: answer,
    }));
  };

  const handleNextQuestion = () => {
    if (currentQuestionIndex < quiz.questions.length - 1) {
      setCurrentQuestionIndex((prevIndex) => prevIndex + 1);
    }
  };

  const handlePreviousQuestion = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex((prevIndex) => prevIndex - 1);
    }
  };

  const handleSubmitQuiz = async () => {
    try {
      const submissionData = {
        quiz_id: quiz.id,
        answers: Object.entries(userAnswers).map(([question_id, answer]) => ({
          question_id: parseInt(question_id),
          selected_answer: answer,
        })),
      };
      const response = await axios.post(`${API_URL}/quizzes/${id}/submit`, submissionData);
      setQuizResult(response.data);
      setQuizSubmitted(true);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to submit quiz');
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading quiz...</div>;
  }

  if (error) {
    return <div className="flex items-center justify-center min-h-screen text-red-500">Error: {error}</div>;
  }

  if (!quiz) {
    return <div className="flex items-center justify-center min-h-screen">Quiz not found.</div>;
  }

  const currentQuestion = quiz.questions[currentQuestionIndex];

  return (
    <div className="flex min-h-screen bg-gray-100 dark:bg-gray-900">
      {/* Sidebar */}
      <aside className="w-64 bg-white dark:bg-gray-800 shadow-md p-4 flex flex-col">
        <div className="text-2xl font-bold text-gray-900 dark:text-white mb-8">AI Learning</div>
        <nav className="flex-grow">
          <ul>
            <li className="mb-2">
              <Button variant="ghost" className="w-full justify-start" onClick={() => navigate('/dashboard')}>
                <LayoutDashboard className="mr-2 h-4 w-4" /> Dashboard
              </Button>
            </li>
            <li className="mb-2">
              <Button variant="ghost" className="w-full justify-start" onClick={() => navigate('/learning-paths')}>
                <BookOpen className="mr-2 h-4 w-4" /> Learning Paths
              </Button>
            </li>
            <li className="mb-2">
              <Button variant="ghost" className="w-full justify-start" onClick={() => navigate('/quizzes')}>
                <Brain className="mr-2 h-4 w-4" /> Quizzes
              </Button>
            </li>
            <li className="mb-2">
              <Button variant="ghost" className="w-full justify-start" onClick={() => navigate('/resources')}>
                <Lightbulb className="mr-2 h-4 w-4" /> Resources
              </Button>
            </li>
            <li className="mb-2">
              <Button variant="ghost" className="w-full justify-start" onClick={() => navigate('/notes')}>
                <FileText className="mr-2 h-4 w-4" /> Notes
              </Button>
            </li>
          </ul>
        </nav>
        <div className="mt-auto">
          <Button variant="ghost" className="w-full justify-start mb-2" onClick={() => navigate('/settings')}>
            <Settings className="mr-2 h-4 w-4" /> Settings
          </Button>
          <Button variant="ghost" className="w-full justify-start text-red-500 hover:text-red-600" onClick={handleLogout}>
            <LogOut className="mr-2 h-4 w-4" /> Logout
          </Button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8">
        <div className="flex items-center mb-6">
          <Button variant="ghost" onClick={() => navigate('/quizzes')} className="mr-4">
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">{quiz.title}</h1>
        </div>

        {!quizSubmitted ? (
          <Card className="w-full max-w-2xl mx-auto">
            <CardHeader>
              <CardTitle className="text-xl font-semibold">Question {currentQuestionIndex + 1} of {quiz.questions.length}</CardTitle>
              <p className="text-gray-700 dark:text-gray-300 text-lg mt-2">{currentQuestion.question_text}</p>
            </CardHeader>
            <CardContent>
              <RadioGroup
                onValueChange={(value) => handleAnswerChange(currentQuestion.id, value)}
                value={userAnswers[currentQuestion.id] || ''}
              >
                {currentQuestion.options.map((option, index) => (
                  <div key={index} className="flex items-center space-x-2 mb-2">
                    <RadioGroupItem value={option} id={`option-${index}`} />
                    <Label htmlFor={`option-${index}`}>{option}</Label>
                  </div>
                ))}
              </RadioGroup>
              <div className="flex justify-between mt-6">
                <Button onClick={handlePreviousQuestion} disabled={currentQuestionIndex === 0}>
                  Previous
                </Button>
                {currentQuestionIndex === quiz.questions.length - 1 ? (
                  <Button onClick={handleSubmitQuiz} disabled={!userAnswers[currentQuestion.id]}>
                    Submit Quiz
                  </Button>
                ) : (
                  <Button onClick={handleNextQuestion} disabled={!userAnswers[currentQuestion.id]}>
                    Next
                  </Button>
                )}
              </div>
            </CardContent>
          </Card>
        ) : (
          <Card className="w-full max-w-2xl mx-auto text-center">
            <CardHeader>
              <CardTitle className="text-2xl font-bold">Quiz Completed!</CardTitle>
            </CardHeader>
            <CardContent>
              {quizResult && (
                <div className="space-y-4">
                  <p className="text-lg">Your Score: <span className="font-bold text-blue-600">{quizResult.score}%</span></p>
                  <p className="text-lg">Correct Answers: <span className="font-bold text-green-600">{quizResult.correct_answers}</span></p>
                  <p className="text-lg">Incorrect Answers: <span className="font-bold text-red-600">{quizResult.incorrect_answers}</span></p>
                  <Button onClick={() => navigate('/quizzes')} className="mt-4">
                    Back to Quizzes
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        )}
      </main>
    </div>
  );
};

export default QuizDetail;

