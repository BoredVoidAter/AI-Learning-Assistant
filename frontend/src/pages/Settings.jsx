import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { Input } from '../components/ui/input';
import { Button } from '../components/ui/button';
import { Label } from '../components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Switch } from '../components/ui/switch';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { LayoutDashboard, BookOpen, Brain, FileText, Lightbulb, Settings as SettingsIcon, LogOut } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const Settings = () => {
  const { user, logout, fetchUser } = useAuth();
  const navigate = useNavigate();
  const [profileData, setProfileData] = useState({
    first_name: '',
    last_name: '',
    learning_style: '',
    preferred_difficulty: '',
    daily_goal_minutes: 0,
    study_reminders_enabled: false,
    notification_email: false,
  });
  const [passwordData, setPasswordData] = useState({
    old_password: '',
    new_password: '',
    confirm_new_password: '',
  });
  const [message, setMessage] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (user) {
      setProfileData({
        first_name: user.first_name || '',
        last_name: user.last_name || '',
        learning_style: user.learning_style || '',
        preferred_difficulty: user.preferred_difficulty || 'intermediate',
        daily_goal_minutes: user.daily_goal_minutes || 30,
        study_reminders_enabled: user.study_reminders_enabled || false,
        notification_email: user.notification_email || false,
      });
    }
  }, [user]);

  const handleProfileChange = (e) => {
    const { id, value } = e.target;
    setProfileData((prevData) => ({
      ...prevData,
      [id]: value,
    }));
  };

  const handleProfileSelectChange = (id, value) => {
    setProfileData((prevData) => ({
      ...prevData,
      [id]: value,
    }));
  };

  const handleProfileSwitchChange = (id, checked) => {
    setProfileData((prevData) => ({
      ...prevData,
      [id]: checked,
    }));
  };

  const handlePasswordChange = (e) => {
    const { id, value } = e.target;
    setPasswordData((prevData) => ({
      ...prevData,
      [id]: value,
    }));
  };

  const handleUpdateProfile = async (e) => {
    e.preventDefault();
    setMessage(null);
    setError(null);
    try {
      const token = localStorage.getItem('token');
      await axios.put(`${API_URL}/user/profile`, profileData, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      await fetchUser(); // Refresh user data in context
      setMessage('Profile updated successfully!');
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update profile');
    }
  };

  const handleUpdatePassword = async (e) => {
    e.preventDefault();
    setMessage(null);
    setError(null);
    if (passwordData.new_password !== passwordData.confirm_new_password) {
      setError('New passwords do not match');
      return;
    }
    try {
      const token = localStorage.getItem('token');
      await axios.put(`${API_URL}/user/profile/password`, passwordData, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      setMessage('Password updated successfully!');
      setPasswordData({ old_password: '', new_password: '', confirm_new_password: '' });
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to update password');
    }
  };

  const handleDeleteAccount = async () => {
    if (window.confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      setMessage(null);
      setError(null);
      try {
        const token = localStorage.getItem('token');
        await axios.delete(`${API_URL}/user/profile/delete`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        logout();
        navigate('/register'); // Redirect to register page after deletion
        setMessage('Account deleted successfully.');
      } catch (err) {
        setError(err.response?.data?.error || 'Failed to delete account');
      }
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

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
            <SettingsIcon className="mr-2 h-4 w-4" /> Settings
          </Button>
          <Button variant="ghost" className="w-full justify-start text-red-500 hover:text-red-600" onClick={handleLogout}>
            <LogOut className="mr-2 h-4 w-4" /> Logout
          </Button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8">
        <h1 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white">Settings</h1>

        {message && <div className="bg-green-100 text-green-700 p-3 rounded-md mb-4">{message}</div>}
        {error && <div className="bg-red-100 text-red-700 p-3 rounded-md mb-4">{error}</div>}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Profile Settings */}
          <Card>
            <CardHeader>
              <CardTitle>Profile Information</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleUpdateProfile} className="space-y-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="first_name" className="text-right">First Name</Label>
                  <Input id="first_name" value={profileData.first_name} onChange={handleProfileChange} className="col-span-3" />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="last_name" className="text-right">Last Name</Label>
                  <Input id="last_name" value={profileData.last_name} onChange={handleProfileChange} className="col-span-3" />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="learning_style" className="text-right">Learning Style</Label>
                  <Select value={profileData.learning_style} onValueChange={(value) => handleProfileSelectChange('learning_style', value)}>
                    <SelectTrigger className="col-span-3">
                      <SelectValue placeholder="Select a style" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="visual">Visual</SelectItem>
                      <SelectItem value="auditory">Auditory</SelectItem>
                      <SelectItem value="kinesthetic">Kinesthetic</SelectItem>
                      <SelectItem value="reading">Reading/Writing</SelectItem>
                      <SelectItem value="">Not specified</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="preferred_difficulty" className="text-right">Preferred Difficulty</Label>
                  <Select value={profileData.preferred_difficulty} onValueChange={(value) => handleProfileSelectChange('preferred_difficulty', value)}>
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
                  <Label htmlFor="daily_goal_minutes" className="text-right">Daily Goal (minutes)</Label>
                  <Input id="daily_goal_minutes" type="number" value={profileData.daily_goal_minutes} onChange={handleProfileChange} className="col-span-3" min="0" />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="study_reminders_enabled" className="text-right">Study Reminders</Label>
                  <Switch
                    id="study_reminders_enabled"
                    checked={profileData.study_reminders_enabled}
                    onCheckedChange={(checked) => handleProfileSwitchChange('study_reminders_enabled', checked)}
                    className="col-span-3"
                  />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="notification_email" className="text-right">Email Notifications</Label>
                  <Switch
                    id="notification_email"
                    checked={profileData.notification_email}
                    onCheckedChange={(checked) => handleProfileSwitchChange('notification_email', checked)}
                    className="col-span-3"
                  />
                </div>
                <Button type="submit" className="w-full">Update Profile</Button>
              </form>
            </CardContent>
          </Card>

          {/* Password Settings */}
          <Card>
            <CardHeader>
              <CardTitle>Change Password</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleUpdatePassword} className="space-y-4">
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="old_password" className="text-right">Old Password</Label>
                  <Input id="old_password" type="password" value={passwordData.old_password} onChange={handlePasswordChange} className="col-span-3" required />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="new_password" className="text-right">New Password</Label>
                  <Input id="new_password" type="password" value={passwordData.new_password} onChange={handlePasswordChange} className="col-span-3" required />
                </div>
                <div className="grid grid-cols-4 items-center gap-4">
                  <Label htmlFor="confirm_new_password" className="text-right">Confirm New Password</Label>
                  <Input id="confirm_new_password" type="password" value={passwordData.confirm_new_password} onChange={handlePasswordChange} className="col-span-3" required />
                </div>
                <Button type="submit" className="w-full">Change Password</Button>
              </form>
            </CardContent>
          </Card>

          {/* Danger Zone */}
          <Card className="col-span-1 lg:col-span-2 border-red-500">
            <CardHeader>
              <CardTitle className="text-red-600">Danger Zone</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-red-500 mb-4">Permanently delete your account and all associated data.</p>
              <Button variant="destructive" onClick={handleDeleteAccount} className="w-full">
                Delete Account
              </Button>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  );
};

export default Settings;


