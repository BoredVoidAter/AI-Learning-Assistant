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
import { Textarea } from '../components/ui/textarea';
import { LayoutDashboard, BookOpen, Brain, FileText, Lightbulb, Settings, LogOut, PlusCircle, Search, Filter } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const LearningPaths = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [learningPaths, setLearningPaths] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newPathData, setNewPathData] = useState({
    title: '',
    description: '',
    subject: '',
    difficulty_level: 'beginner',
    estimated_hours: 10,
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [filterDifficulty, setFilterDifficulty] = useState('');
  const [filterSubject, setFilterSubject] = useState('');

  useEffect(() => {
    fetchLearningPaths();
  }, [user, searchQuery, filterDifficulty, filterSubject]);

  const fetchLearningPaths = async () => {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      const params = {
        search: searchQuery,
        difficulty: filterDifficulty,
        subject: filterSubject,
      };
      const response = await axios.get(`${API_URL}/learning-paths`, { params });
      setLearningPaths(response.data.learning_paths);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch learning paths');
    }
    setLoading(false);
  };

  const handleNewPathChange = (e) => {
    const { id, value } = e.target;
    setNewPathData((prevData) => ({
      ...prevData,
      [id]: value,
    }));
  };

  const handleNewPathSelectChange = (name, value) => {
    setNewPathData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleCreatePath = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/learning-paths`, newPathData);
      setIsModalOpen(false);
      setNewPathData({
        title: '',
        description: '',
        subject: '',
        difficulty_level: 'beginner',
        estimated_hours: 10,
      });
      fetchLearningPaths();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create learning path');
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading learning paths...</div>;
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
        <h1 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white">Your Learning Paths</h1>
        
        <div className="flex justify-between items-center mb-6">
          <div className="flex space-x-4">
            <div className="relative">
              <Input
                type="text"
                placeholder="Search paths..."
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
            <Input
              type="text"
              placeholder="Filter by Subject..."
              value={filterSubject}
              onChange={(e) => setFilterSubject(e.target.value)}
              className="w-[180px]"
            />
          </div>
          <Button onClick={() => setIsModalOpen(true)}>
            <PlusCircle className="mr-2 h-4 w-4" /> Create New Path
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {learningPaths.length > 0 ? (
            learningPaths.map((path) => (
              <Card key={path.id} className="hover:shadow-lg transition-shadow duration-200">
                <CardHeader>
                  <CardTitle className="text-xl font-semibold">{path.title}</CardTitle>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{path.subject} - {path.difficulty_level}</p>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 dark:text-gray-300 mb-4">{path.description}</p>
                  <div className="flex justify-between items-center text-sm text-gray-600 dark:text-gray-400">
                    <span>Progress: {path.progress_percentage}%</span>
                    <span>Est. Hours: {path.estimated_hours}</span>
                  </div>
                  <Button className="w-full mt-4" onClick={() => navigate(`/learning-paths/${path.id}`)}>
                    View Path
                  </Button>
                </CardContent>
              </Card>
            ))
          ) : (
            <p className="col-span-full text-center text-gray-500 dark:text-gray-400">No learning paths found. Create one to get started!</p>
          )}
        </div>
      </main>

      {/* Create New Learning Path Modal */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Create New Learning Path</DialogTitle>
            <DialogDescription>Fill in the details for your new learning path.</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleCreatePath} className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="title" className="text-right">Title</Label>
              <Input id="title" value={newPathData.title} onChange={handleNewPathChange} className="col-span-3" required />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="description" className="text-right">Description</Label>
              <Textarea id="description" value={newPathData.description} onChange={handleNewPathChange} className="col-span-3" />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="subject" className="text-right">Subject</Label>
              <Input id="subject" value={newPathData.subject} onChange={handleNewPathChange} className="col-span-3" required />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="difficulty_level" className="text-right">Difficulty</Label>
              <Select value={newPathData.difficulty_level} onValueChange={(value) => handleNewPathSelectChange('difficulty_level', value)}>
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
              <Label htmlFor="estimated_hours" className="text-right">Estimated Hours</Label>
              <Input id="estimated_hours" type="number" value={newPathData.estimated_hours} onChange={handleNewPathChange} className="col-span-3" min="1" />
            </div>
            <DialogFooter>
              <Button type="submit">Create Path</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default LearningPaths;

