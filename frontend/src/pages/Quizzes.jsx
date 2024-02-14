import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '../components/ui/dialog';
import { Label } from '../components/ui/label';
import { LayoutDashboard, BookOpen, Brain, FileText, Lightbulb, Settings, LogOut, PlusCircle, Search, Filter } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const Quizzes = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [quizzes, setQuizzes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newQuizData, setNewQuizData] = useState({
    topic_id: '',
    title: '',
    description: '',
    difficulty_level: 'intermediate',
    time_limit_minutes: 15,
  });
  const [topics, setTopics] = useState([]); // To populate topic dropdown
  const [searchQuery, setSearchQuery] = useState('');
  const [filterDifficulty, setFilterDifficulty] = useState('');
  const [filterTopic, setFilterTopic] = useState('');

  useEffect(() => {
    fetchQuizzes();
    fetchTopicsForQuizCreation();
  }, [user, searchQuery, filterDifficulty, filterTopic]);

  const fetchQuizzes = async () => {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      const params = {
        search: searchQuery,
        difficulty: filterDifficulty,
        topic_id: filterTopic,
      };
      const response = await axios.get(`${API_URL}/quizzes`, { params });
      setQuizzes(response.data.quizzes);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch quizzes');
    }
    setLoading(false);
  };

  const fetchTopicsForQuizCreation = async () => {
    if (!user) return;
    try {
      // Fetch all topics from user's learning paths
      const response = await axios.get(`${API_URL}/learning-paths`);
      const allTopics = [];
      response.data.learning_paths.forEach(path => {
        path.topics.forEach(topic => {
          allTopics.push({ id: topic.id, title: topic.title, learning_path_title: path.title });
        });
      });
      setTopics(allTopics);
    } catch (err) {
      console.error('Failed to fetch topics for quiz creation:', err);
    }
  };

  const handleNewQuizChange = (e) => {
    const { id, value } = e.target;
    setNewQuizData((prevData) => ({
      ...prevData,
      [id]: value,
    }));
  };

  const handleNewQuizSelectChange = (name, value) => {
    setNewQuizData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleCreateQuiz = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/quizzes`, newQuizData);
      setIsModalOpen(false);
      setNewQuizData({
        topic_id: '',
        title: '',
        description: '',
        difficulty_level: 'intermediate',
        time_limit_minutes: 15,
      });
      fetchQuizzes();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create quiz');
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading quizzes...</div>;
  }

  if (error) {
    return <div className="flex items-center justify-center min-h-screen text-red-500">Error: {error}</div>;
  }

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
        <h1 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white">Your Quizzes</h1>
        
        <div className="flex justify-between items-center mb-6">
          <div className="flex space-x-4">
            <div className="relative">
              <Input
                type="text"
                placeholder="Search quizzes..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
            </div>
            <Select value={filterDifficulty} onValueChange={setFilterDifficulty}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Filter by Difficulty" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Difficulties</SelectItem>
                <SelectItem value="beginner">Beginner</SelectItem>
                <SelectItem value="intermediate">Intermediate</SelectItem>
                <SelectItem value="advanced">Advanced</SelectItem>
              </SelectContent>
            </Select>
            <Select value={filterTopic} onValueChange={setFilterTopic}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Filter by Topic" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Topics</SelectItem>
                {topics.map(topic => (
                  <SelectItem key={topic.id} value={topic.id.toString()}>{topic.title} ({topic.learning_path_title})</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          <Button onClick={() => setIsModalOpen(true)}>
            <PlusCircle className="mr-2 h-4 w-4" /> Create New Quiz
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {quizzes.length > 0 ? (
            quizzes.map((quiz) => (
              <Card key={quiz.id} className="hover:shadow-lg transition-shadow duration-200">
                <CardHeader>
                  <CardTitle className="text-xl font-semibold">{quiz.title}</CardTitle>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{quiz.topic_title} - {quiz.difficulty_level}</p>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 dark:text-gray-300 mb-4">{quiz.description}</p>
                  <div className="flex justify-between items-center text-sm text-gray-600 dark:text-gray-400">
                    <span>Best Score: {quiz.best_score ? `${quiz.best_score}%` : 'N/A'}</span>
                    <span>Time Limit: {quiz.time_limit_minutes} mins</span>
                  </div>
                  <Button className="w-full mt-4" onClick={() => navigate(`/quizzes/${quiz.id}`)}>
                    Start Quiz
                  </Button>
                </CardContent>
              </Card>
            ))
          ) : (
            <p className="col-span-full text-center text-gray-500 dark:text-gray-400">No quizzes found. Create one to get started!</p>
          )}
        </div>
      </main>

      {/* Create New Quiz Modal */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Create New Quiz</DialogTitle>
            <DialogDescription>Fill in the details for your new quiz.</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleCreateQuiz} className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="topic_id" className="text-right">Topic</Label>
              <Select value={newQuizData.topic_id} onValueChange={(value) => handleNewQuizSelectChange('topic_id', value)} required>
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder="Select a topic" />
                </SelectTrigger>
                <SelectContent>
                  {topics.map(topic => (
                    <SelectItem key={topic.id} value={topic.id.toString()}>{topic.title} ({topic.learning_path_title})</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="title" className="text-right">Title</Label>
              <Input id="title" value={newQuizData.title} onChange={handleNewQuizChange} className="col-span-3" required />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="description" className="text-right">Description</Label>
              <Input id="description" value={newQuizData.description} onChange={handleNewQuizChange} className="col-span-3" />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="difficulty_level" className="text-right">Difficulty</Label>
              <Select value={newQuizData.difficulty_level} onValueChange={(value) => handleNewQuizSelectChange('difficulty_level', value)}>
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder="Select difficulty" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="beginner">Beginner</SelectItem>
                  <SelectItem value="intermediate">Intermediate</SelectItem>
                  <SelectItem value="advanced">Advanced</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="time_limit_minutes" className="text-right">Time Limit (mins)</Label>
              <Input id="time_limit_minutes" type="number" value={newQuizData.time_limit_minutes} onChange={handleNewQuizChange} className="col-span-3" min="1" />
            </div>
            <DialogFooter>
              <Button type="submit">Create Quiz</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Quizzes;

