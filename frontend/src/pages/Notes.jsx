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
import { LayoutDashboard, BookOpen, Brain, FileText, Lightbulb, Settings, LogOut, PlusCircle, Search, Tag, Star } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const Notes = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [notes, setNotes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newNoteData, setNewNoteData] = useState({
    title: '',
    content: '',
    resource_id: '',
    tags: [],
    is_favorite: false,
  });
  const [resources, setResources] = useState([]); // To populate resource dropdown
  const [searchQuery, setSearchQuery] = useState('');
  const [filterResource, setFilterResource] = useState('');
  const [filterFavorite, setFilterFavorite] = useState('');
  const [filterTag, setFilterTag] = useState('');

  useEffect(() => {
    fetchNotes();
    fetchResourcesForNoteCreation();
  }, [user, searchQuery, filterResource, filterFavorite, filterTag]);

  const fetchNotes = async () => {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      const params = {
        search: searchQuery,
        resource_id: filterResource,
        is_favorite: filterFavorite === 'true' ? true : filterFavorite === 'false' ? false : undefined,
        tag: filterTag,
      };
      const response = await axios.get(`${API_URL}/notes`, { params });
      setNotes(response.data.notes);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch notes');
    }
    setLoading(false);
  };

  const fetchResourcesForNoteCreation = async () => {
    if (!user) return;
    try {
      // Fetch all resources from user's learning paths
      const response = await axios.get(`${API_URL}/resources`);
      setResources(response.data.resources);
    } catch (err) {
      console.error('Failed to fetch resources for note creation:', err);
    }
  };

  const handleNewNoteChange = (e) => {
    const { id, value } = e.target;
    setNewNoteData((prevData) => ({
      ...prevData,
      [id]: value,
    }));
  };

  const handleNewNoteSelectChange = (name, value) => {
    setNewNoteData((prevData) => ({
      ...prevData,
      [name]: value,
    }));
  };

  const handleCreateNote = async (e) => {
    e.preventDefault();
    try {
      const noteToCreate = { ...newNoteData };
      if (noteToCreate.tags) {
        noteToCreate.tags = noteToCreate.tags.split(',').map(tag => tag.trim()).filter(tag => tag);
      }
      await axios.post(`${API_URL}/notes`, noteToCreate);
      setIsModalOpen(false);
      setNewNoteData({
        title: '',
        content: '',
        resource_id: '',
        tags: [],
        is_favorite: false,
      });
      fetchNotes();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to create note');
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading notes...</div>;
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
        <h1 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white">Your Notes</h1>
        
        <div className="flex justify-between items-center mb-6">
          <div className="flex space-x-4">
            <div className="relative">
              <Input
                type="text"
                placeholder="Search notes..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10"
              />
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
            </div>
            <Select value={filterResource} onValueChange={setFilterResource}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Filter by Resource" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Resources</SelectItem>
                {resources.map(resource => (
                  <SelectItem key={resource.id} value={resource.id.toString()}>{resource.title}</SelectItem>
                ))}
              </SelectContent>
            </Select>
            <Select value={filterFavorite} onValueChange={setFilterFavorite}>
              <SelectTrigger className="w-[180px]">
                <SelectValue placeholder="Filter by Favorite" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="">All Notes</SelectItem>
                <SelectItem value="true">Favorites</SelectItem>
                <SelectItem value="false">Non-Favorites</SelectItem>
              </SelectContent>
            </Select>
            <Input
              type="text"
              placeholder="Filter by Tag..."
              value={filterTag}
              onChange={(e) => setFilterTag(e.target.value)}
              className="w-[180px]"
            />
          </div>
          <Button onClick={() => setIsModalOpen(true)}>
            <PlusCircle className="mr-2 h-4 w-4" /> Create New Note
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {notes.length > 0 ? (
            notes.map((note) => (
              <Card key={note.id} className="hover:shadow-lg transition-shadow duration-200">
                <CardHeader>
                  <CardTitle className="text-xl font-semibold">{note.title}</CardTitle>
                  {note.resource_title && <p className="text-sm text-gray-500 dark:text-gray-400">Resource: {note.resource_title}</p>}
                </CardHeader>
                <CardContent>
                  <p className="text-gray-700 dark:text-gray-300 mb-4">{note.content.substring(0, 150)}{note.content.length > 150 ? '...' : ''}</p>
                  {note.tags && note.tags.length > 0 && (
                    <div className="flex flex-wrap gap-2 mb-2">
                      {note.tags.map((tag, index) => (
                        <span key={index} className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded dark:bg-blue-900 dark:text-blue-300">
                          {tag}
                        </span>
                      ))}
                    </div>
                  )}
                  {note.is_favorite && (
                    <div className="flex items-center text-yellow-500 text-sm">
                      <Star className="h-4 w-4 mr-1" fill="currentColor" /> Favorite
                    </div>
                  )}
                </CardContent>
              </Card>
            ))
          ) : (
            <p className="col-span-full text-center text-gray-500 dark:text-gray-400">No notes found. Create one to get started!</p>
          )}
        </div>
      </main>

      {/* Create New Note Modal */}
      <Dialog open={isModalOpen} onOpenChange={setIsModalOpen}>
        <DialogContent className="sm:max-w-[425px]">
          <DialogHeader>
            <DialogTitle>Create New Note</DialogTitle>
            <DialogDescription>Write down your thoughts and insights.</DialogDescription>
          </DialogHeader>
          <form onSubmit={handleCreateNote} className="grid gap-4 py-4">
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="title" className="text-right">Title</Label>
              <Input id="title" value={newNoteData.title} onChange={handleNewNoteChange} className="col-span-3" required />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="content" className="text-right">Content</Label>
              <Textarea id="content" value={newNoteData.content} onChange={handleNewNoteChange} className="col-span-3" required />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="resource_id" className="text-right">Related Resource</Label>
              <Select value={newNoteData.resource_id} onValueChange={(value) => handleNewNoteSelectChange('resource_id', value)}>
                <SelectTrigger className="col-span-3">
                  <SelectValue placeholder="Select a resource (optional)" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="">None</SelectItem>
                  {resources.map(resource => (
                    <SelectItem key={resource.id} value={resource.id.toString()}>{resource.title}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="tags" className="text-right">Tags (comma-separated)</Label>
              <Input id="tags" value={newNoteData.tags} onChange={handleNewNoteChange} className="col-span-3" placeholder="e.g., python, webdev, ai" />
            </div>
            <div className="grid grid-cols-4 items-center gap-4">
              <Label htmlFor="is_favorite" className="text-right">Favorite</Label>
              <input
                type="checkbox"
                id="is_favorite"
                checked={newNoteData.is_favorite}
                onChange={(e) => setNewNoteData(prev => ({ ...prev, is_favorite: e.target.checked }))}
                className="col-span-3 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
            </div>
            <DialogFooter>
              <Button type="submit">Create Note</Button>
            </DialogFooter>
          </form>
        </DialogContent>
      </Dialog>
    </div>
  );
};

export default Notes;

