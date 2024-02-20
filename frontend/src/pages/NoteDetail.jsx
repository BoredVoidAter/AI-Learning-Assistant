import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { LayoutDashboard, BookOpen, Brain, FileText, Lightbulb, Settings, LogOut, ArrowLeft, Star } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const NoteDetail = () => {
  const { id } = useParams();
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [note, setNote] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchNoteDetail();
  }, [id, user]);

  const fetchNoteDetail = async () => {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_URL}/notes/${id}`);
      setNote(response.data);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch note details');
    }
    setLoading(false);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading note...</div>;
  }

  if (error) {
    return <div className="flex items-center justify-center min-h-screen text-red-500">Error: {error}</div>;
  }

  if (!note) {
    return <div className="flex items-center justify-center min-h-screen">Note not found.</div>;
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
          <Button variant="ghost" onClick={() => navigate('/notes')} className="mr-4">
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">{note.title}</h1>
        </div>

        <Card className="w-full max-w-3xl mx-auto">
          <CardHeader>
            <CardTitle className="text-xl font-semibold">{note.title}</CardTitle>
            {note.resource_title && <p className="text-sm text-gray-500 dark:text-gray-400">Resource: {note.resource_title}</p>}
          </CardHeader>
          <CardContent>
            <p className="text-gray-700 dark:text-gray-300 mb-4 whitespace-pre-wrap">{note.content}</p>
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
      </main>
    </div>
  );
};

export default NoteDetail;

