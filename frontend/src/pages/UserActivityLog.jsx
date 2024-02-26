import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { LayoutDashboard, BookOpen, Brain, FileText, Lightbulb, Settings, LogOut, Activity } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const UserActivityLog = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [activities, setActivities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchActivities();
  }, [user]);

  const fetchActivities = async () => {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_URL}/activities`, {
        headers: { Authorization: `Bearer ${user.token}` },
      });
      setActivities(response.data.activities);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch activities');
    }
    setLoading(false);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading activities...</div>;
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
            <li className="mb-2">
              <Button variant="ghost" className="w-full justify-start" onClick={() => navigate('/activities')}>
                <Activity className="mr-2 h-4 w-4" /> Activities
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
        <h1 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white">Your Recent Activities</h1>
        
        <div className="grid grid-cols-1 gap-4">
          {activities.length > 0 ? (
            activities.map((activity) => (
              <Card key={activity.id} className="shadow-sm">
                <CardHeader>
                  <CardTitle className="text-lg font-semibold">{activity.activity_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</CardTitle>
                  <p className="text-sm text-gray-500 dark:text-gray-400">{format(new Date(activity.timestamp), 'PPP p')}</p>
                </CardHeader>
                <CardContent>
                  {activity.activity_details && (
                    <p className="text-gray-700 dark:text-gray-300">Details: {JSON.stringify(activity.activity_details)}</p>
                  )}
                </CardContent>
              </Card>
            ))
          ) : (
            <p className="text-center text-gray-500 dark:text-gray-400">No activities logged yet.</p>
          )}
        </div>
      </main>
    </div>
  );
};

export default UserActivityLog;


