import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
import { LayoutDashboard, BookOpen, Brain, FileText, Lightbulb, Settings, LogOut, ArrowLeft, CheckCircle, XCircle, PlusCircle } from 'lucide-react';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '../components/ui/dialog';
import { Label } from '../components/ui/label';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const LearningPathDetail = () => {
  const { id } = useParams();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [learningPath, setLearningPath] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isTopicModalOpen, setIsTopicModalOpen] = useState(false);
  const [newTopicData, setNewTopicData] = useState({
    title: '',
    description: '',
    estimated_time_minutes: 60,
  });

  useEffect(() => {
    fetchLearningPathDetail();
  }, [id, user]);

  const fetchLearningPathDetail = async () => {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_URL}/learning-paths/${id}`);
      setLearningPath(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch learning path details');
    }
    setLoading(false);
  };

  const handleNewTopicChange = (e) => {
    const { id, value } = e.target;
    setNewTopicData((prevData) => ({
      ...prevData,
      [id]: value,
    }));
  };

  const handleCreateTopic = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/learning-paths/${id}/topics`, newTopicData);
      setIsTopicModalOpen(false);
      setNewTopicData({
        title: '',
        description: '',
        estimated_time_minutes: 60,
      });
      fetchLearningPathDetail(); // Refresh data
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create topic');
    }
  };

  const handleMarkTopicComplete = async (topicId, isCompleted) => {
    try {
      await axios.put(`${API_URL}/topics/${topicId}/complete`, { is_completed: !isCompleted });
      fetchLearningPathDetail(); // Refresh data
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update topic status');
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading learning path...</div>;
  }

  if (error) {
    return <div className="flex items-center justify-center min-h-screen text-red-500">Error: {error}</div>;
  }

  if (!learningPath) {
    return <div className="flex items-center justify-center min-h-screen">Learning path not found.</div>;
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
        <div className="flex items-center mb-6">
          <Button variant="ghost" onClick={() => navigate('/learning-paths')} className="mr-4">
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">{learningPath.title}</h1>
        </div>
        
        <div className="mb-6">
          <p className="text-gray-700 dark:text-gray-300 mb-2">{learningPath.description}</p>
          <div className="flex items-center text-sm text-gray-600 dark:text-gray-400">
            <span>Subject: {learningPath.subject}</span>
            <span className="mx-2">•</span>
            <span>Difficulty: {learningPath.difficulty_level}</span>
            <span className="mx-2">•</span>
            <span>Estimated: {learningPath.estimated_hours} hours</span>
          </div>
          <div className="mt-4">
            <Label>Progress</Label>
            <Progress value={learningPath.progress_percentage} className="w-full" />
            <span className="text-sm text-gray-600 dark:text-gray-400">{learningPath.progress_percentage}% Completed</span>
          </div>
        </div>

        <div className="flex justify-between items-center mb-4">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Topics</h2>
          <Button onClick={() => setIsTopicModalOpen(true)}>
            <PlusCircle className="mr-2 h-4 w-4" /> Add New Topic
          </Button>
        </div>

        <div className="space-y-4">
          {learningPath.topics && learningPath.topics.length > 0 ? (
            learningPath.topics.map((topic) => (
              <Card key={topic.id} className="flex items-center justify-between p-4">
                <div>
                  <CardTitle className="text-lg font-semibold">{topic.title}</CardTitle>
                  <p className="text-gray-700 dark:text-gray-300 text-sm">{topic.description}</p>
                  <p className="text-gray-500 dark:text-gray-400 text-xs">Est. Time: {topic.estimated_time_minutes} mins</p>
                </div>
                <Button
                  variant="outline"
                  onClick={() => handleMarkTopicComplete(topic.id, topic.is_completed)}
                  className={topic.is_completed ? "text-green-600 border-green-600 hover:bg-green-50" : "text-red-600 border-red-600 hover:bg-red-50"}
                >
                  {topic.is_completed ? <CheckCircle className="mr-2 h-4 w-4" /> : <XCircle className="mr-2 h-4 w-4" />}
                  {topic.is_completed ? 'Completed' : 'Mark as Complete'}
                </Button>
              </Card>
            ))
          ) : (
            <p className="text-center text-gray-500 dark:text-gray-400">No topics in this learning path yet. Add some!</p>
          )}
        </div>
      </main>

      {/* Add New Topic Modal */}
      <Dialog open={isTopicModalOpen} onOpenChange={setIsTopicModalOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Add New Topic</DialogTitle>
            <DialogDescription>Fill in the details for your new topic.</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleCreateTopic} className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="title" className="text-right">Title</Label>
              <Input id="title" value={newTopicData.title} onChange={handleNewTopicChange} className="col-span-3" required />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="description" className="text-right">Description</Label>
              <Textarea id="description" value={newTopicData.description} onChange={handleNewTopicChange} className="col-span-3" />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="estimated_time_minutes" className="text-right">Estimated Time (mins)</Label>
              <Input id="estimated_time_minutes" type="number" value={newTopicData.estimated_time_minutes} onChange={handleNewTopicChange} className="col-span-3" min="1" />
            </div>
            <DialogFooter>
              <Button type="submit">Create Topic</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default LearningPathDetail;

