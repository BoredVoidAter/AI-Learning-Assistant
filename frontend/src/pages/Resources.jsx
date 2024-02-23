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
import { LayoutDashboard, BookOpen, Brain, FileText, Lightbulb, Settings, LogOut, PlusCircle, Search, Filter, Wand2 } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const Resources = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [resources, setResources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isAIGenModalOpen, setIsAIGenModalOpen] = useState(false);
  const [aiGenPrompt, setAiGenPrompt] = useState('');
  const [aiGenContentType, setAiGenContentType] = useState('article');
  const [aiGenLoading, setAiGenLoading] = useState(false);
  const [aiGenError, setAiGenError] = useState(null);
  const [aiGeneratedContent, setAiGeneratedContent] = useState('');
  const [newResourceData, setNewResourceData] = useState({
    topic_id: '',
    title: '',
    description: '',
    resource_type: 'article',
    url: '',
    content: '',
    duration_minutes: 0,
    difficulty_level: 'intermediate',
  });
  const [topics, setTopics] = useState([]); // To populate topic dropdown
  const [searchQuery, setSearchQuery] = useState('');
  const [filterDifficulty, setFilterDifficulty] = useState('');
  const [filterTopic, setFilterTopic] = useState('');
  const [filterResourceType, setFilterResourceType] = useState('');

  useEffect(() => {
    fetchResources();
    fetchTopicsForResourceCreation();
  }, [user, searchQuery, filterDifficulty, filterTopic, filterResourceType]);

  const fetchResources = async () => {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      const params = {
        search_query: searchQuery,
        difficulty: filterDifficulty,
        topic_id: filterTopic,
        resource_type: filterResourceType,
      };
      const response = await axios.get(`${API_URL}/resources`, { params });
      setResources(response.data.resources);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch resources');
    }
    setLoading(false);
  };

  const fetchTopicsForResourceCreation = async () => {
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
      console.error('Failed to fetch topics for resource creation:', err);
    }
  };

  const handleNewResourceChange = (e) => {
    const { id, value } = e.target;
    setNewResourceData((prevData) => ({
      ...prevData,
      [id]: value,
    }));
  };

  const handleNewResourceSelectChange = (name, value) => {
    setNewResourceData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleCreateResource = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/resources`, newResourceData);
      setIsModalOpen(false);
      setNewResourceData({
        topic_id: '',
        title: '',
        description: '',
        resource_type: 'article',
        url: '',
        content: '',
        duration_minutes: 0,
        difficulty_level: 'intermediate',
      });
      fetchResources();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create resource');
    }
  };

  const handleGenerateAIContent = async () => {
    setAiGenLoading(true);
    setAiGenError(null);
    setAiGeneratedContent("");
    try {
      const response = await axios.post(`${API_URL}/ai/generate-content`, {
        prompt: aiGenPrompt,
        content_type: aiGenContentType,
      });
      setAiGeneratedContent(response.data.generated_content);
    } catch (err) {
      setAiGenError(err.response?.data?.error || "Failed to generate AI content");
    }
    setAiGenLoading(false);
  };

  const handleUseGeneratedContent = () => {
    setNewResourceData((prevData) => ({
      ...prevData,
      content: aiGeneratedContent,
      title: aiGenPrompt.substring(0, 50), // Use prompt as a base for title
      description: aiGeneratedContent.substring(0, 100) + "...", // Use generated content as description
      resource_type: aiGenContentType === "article" ? "article" : "other",
    }));
    setIsAIGenModalOpen(false);
    setIsModalOpen(true); // Open the add resource modal with pre-filled data
  };

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading resources...</div>;
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
              <Button variant="ghost" className="w-full justify-start" onClick={() => navigate("/dashboard")}>
                <LayoutDashboard className="mr-2 h-4 w-4" /> Dashboard
              </Button>
            </li>
            <li className="mb-2">
              <Button variant="ghost" className="w-full justify-start" onClick={() => navigate("/learning-paths")}>
                <BookOpen className="mr-2 h-4 w-4" /> Learning Paths
              </Button>
            </li>
            <li className="mb-2">
              <Button variant="ghost" className="w-full justify-start" onClick={() => navigate("/quizzes")}>
                <Brain className="mr-2 h-4 w-4" /> Quizzes
              </Button>
            </li>
            <li className="mb-2">
              <Button variant="ghost" className="w-full justify-start" onClick={() => navigate("/resources")}>
                <Lightbulb className="mr-2 h-4 w-4" /> Resources
              </Button>
            </li>
            <li className="mb-2">
              <Button variant="ghost" className="w-full justify-start" onClick={() => navigate("/notes")}>
                <FileText className="mr-2 h-4 w-4" /> Notes
              </Button>
            </li>
          </ul>
        </nav>
        <div className="mt-auto">
          <Button variant="ghost" className="w-full justify-start mb-2" onClick={() => navigate("/settings")}>
            <Settings className="mr-2 h-4 w-4" /> Settings
          </Button>
          <Button variant="ghost" className="w-full justify-start text-red-500 hover:text-red-600" onClick={handleLogout}>
            <LogOut className="mr-2 h-4 w-4" /> Logout
          </Button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8">
        <h1 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white">Your Resources</h1>
        
        <div className="flex justify-between items-center mb-6">
          <div className="flex space-x-4">
            <div className="relative">
              <Input
                type="text"
                placeholder="Search resources..."
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
            <Select value={filterResourceType} onValueChange={setFilterResourceType}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Filter by Type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Types</SelectItem>
                <SelectItem value="video">Video</SelectItem>
                <SelectItem value="article">Article</SelectItem>
                <SelectItem value="book">Book</SelectItem>
                <SelectItem value="course">Course</SelectItem>
                <SelectItem value="exercise">Exercise</SelectItem>
                <SelectItem value="other">Other</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="flex space-x-2">
            <Button onClick={() => setIsAIGenModalOpen(true)} variant="outline">
              <Wand2 className="mr-2 h-4 w-4" /> Generate with AI
            </Button>
            <Button onClick={() => setIsModalOpen(true)}>
              <PlusCircle className="mr-2 h-4 w-4" /> Add New Resource
            </Button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {resources.length > 0 ? (
            resources.map((resource) => (
              <Card key={resource.id} className="hover:shadow-lg transition-shadow duration-200">
                <CardHeader>
                  <CardTitle className="text-xl font-semibold">{resource.title}</CardTitle>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{resource.resource_type} - {resource.difficulty_level}</p>
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 dark:text-gray-300 mb-4">{resource.description}</p>
                  <div className="flex justify-between items-center text-sm text-gray-600 dark:text-gray-400">
                    <span>Topic: {resource.topic_title}</span>
                    {resource.duration_minutes > 0 && <span>Duration: {resource.duration_minutes} mins</span>}
                  </div>
                  {resource.url && (
                    <a href={resource.url} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline text-sm mt-2 block">
                      View Resource
                    </a>
                  )}
                </CardContent>
              </Card>
            ))
          ) : (
            <p className="col-span-full text-center text-gray-500 dark:text-gray-400">No resources found. Add one to get started!</p>
          )}
        </div>
      </main>

      {/* Add New Resource Modal */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Add New Resource</DialogTitle>
            <DialogDescription>Fill in the details for your new learning resource.</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleCreateResource} className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="topic_id" className="text-right">Topic</Label>
              <Select value={newResourceData.topic_id} onValueChange={(value) => handleNewResourceSelectChange("topic_id", value)} required>
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
              <Input id="title" value={newResourceData.title} onChange={handleNewResourceChange} className="col-span-3" required />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="description" className="text-right">Description</Label>
              <Textarea id="description" value={newResourceData.description} onChange={handleNewResourceChange} className="col-span-3" />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="resource_type" className="text-right">Type</Label>
              <Select value={newResourceData.resource_type} onValueChange={(value) => handleNewResourceSelectChange("resource_type", value)} required>
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder="Select resource type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="video">Video</SelectItem>
                  <SelectItem value="article">Article</SelectItem>
                  <SelectItem value="book">Book</SelectItem>
                  <SelectItem value="course">Course</SelectItem>
                  <SelectItem value="exercise">Exercise</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="url" className="text-right">URL</Label>
              <Input id="url" value={newResourceData.url} onChange={handleNewResourceChange} className="col-span-3" />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="content" className="text-right">Content (Optional)</Label>
              <Textarea id="content" value={newResourceData.content} onChange={handleNewResourceChange} className="col-span-3" />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="duration_minutes" className="text-right">Duration (mins)</Label>
              <Input id="duration_minutes" type="number" value={newResourceData.duration_minutes} onChange={handleNewResourceChange} className="col-span-3" min="0" />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="difficulty_level" className="text-right">Difficulty</Label>
              <Select value={newResourceData.difficulty_level} onValueChange={(value) => handleNewResourceSelectChange("difficulty_level", value)}>
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
            <DialogFooter>
              <Button type="submit">Add Resource</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>

      {/* AI Generation Modal */}
      <Dialog open={isAIGenModalOpen} onOpenChange={setIsAIGenModalOpen}>
        <DialogContent className="sm:max-w-[600px]">
          <DialogHeader>
            <DialogTitle>Generate Content with AI</DialogTitle>
            <DialogDescription>Enter a prompt to generate new learning content.</DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="ai-prompt" className="text-right">Prompt</Label>
              <Textarea
                id="ai-prompt"
                value={aiGenPrompt}
                onChange={(e) => setAiGenPrompt(e.target.value)}
                className="col-span-3"
                placeholder="e.g., 'Explain quantum physics for beginners' or 'Write an article on the history of AI'"
              />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="ai-content-type" className="text-right">Content Type</Label>
              <Select value={aiGenContentType} onValueChange={setAiGenContentType}>
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder="Select content type" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="article">Article</SelectItem>
                  <SelectItem value="summary">Summary</SelectItem>
                  <SelectItem value="explanation">Explanation</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <Button onClick={handleGenerateAIContent} disabled={aiGenLoading || !aiGenPrompt}>
              {aiGenLoading ? "Generating..." : "Generate"}
            </Button>
            {aiGenError && <p className="text-red-500 text-center">Error: {aiGenError}</p>}
            {aiGeneratedContent && (
              <div className="mt-4 p-4 border rounded-md bg-gray-50 dark:bg-gray-700 max-h-60 overflow-y-auto">
                <h3 className="font-semibold mb-2">Generated Content:</h3>
                <p className="whitespace-pre-wrap text-sm">{aiGeneratedContent}</p>
              </div>
            )}
          </div>
          <DialogFooter>
            <Button onClick={handleUseGeneratedContent} disabled={!aiGeneratedContent}>
              Use Generated Content
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Resources;