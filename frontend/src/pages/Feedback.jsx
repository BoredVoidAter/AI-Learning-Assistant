import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from '../components/ui/dialog';
import { Label } from '../components/ui/label';
import { 
  LayoutDashboard, BookOpen, Brain, FileText, Lightbulb, Settings, LogOut,
  MessageSquare, Bug, Lightbulb as FeatureIcon, Star, AlertCircle, 
  CheckCircle, Clock, Send, Plus, Eye, MessageCircle
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const Feedback = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [feedbackList, setFeedbackList] = useState([]);
  const [feedbackStats, setFeedbackStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showSubmitDialog, setShowSubmitDialog] = useState(false);
  const [selectedFeedback, setSelectedFeedback] = useState(null);
  const [showDetailDialog, setShowDetailDialog] = useState(false);

  // Form state
  const [formData, setFormData] = useState({
    feedback_type: '',
    title: '',
    description: '',
    category: '',
    priority: 'medium',
    related_learning_path_id: '',
    related_quiz_id: '',
    related_resource_id: '',
    url_context: window.location.href,
    browser_info: navigator.userAgent,
    device_info: `${screen.width}x${screen.height}`
  });

  useEffect(() => {
    if (user) {
      fetchFeedback();
      fetchFeedbackStats();
    }
  }, [user]);

  const fetchFeedback = async () => {
    try {
      const response = await axios.get(`${API_URL}/feedback`);
      setFeedbackList(response.data.feedback);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch feedback');
    }
  };

  const fetchFeedbackStats = async () => {
    try {
      const response = await axios.get(`${API_URL}/feedback/stats`);
      setFeedbackStats(response.data);
    } catch (err) {
      console.error('Failed to fetch feedback stats:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitFeedback = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    
    try {
      await axios.post(`${API_URL}/feedback`, formData);
      setShowSubmitDialog(false);
      setFormData({
        feedback_type: '',
        title: '',
        description: '',
        category: '',
        priority: 'medium',
        related_learning_path_id: '',
        related_quiz_id: '',
        related_resource_id: '',
        url_context: window.location.href,
        browser_info: navigator.userAgent,
        device_info: `${screen.width}x${screen.height}`
      });
      fetchFeedback();
      fetchFeedbackStats();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to submit feedback');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleViewDetail = async (feedback) => {
    try {
      const response = await axios.get(`${API_URL}/feedback/${feedback.id}`);
      setSelectedFeedback(response.data.feedback);
      setShowDetailDialog(true);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch feedback details');
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'open':
        return <Clock className="h-4 w-4" />;
      case 'in_progress':
        return <AlertCircle className="h-4 w-4" />;
      case 'resolved':
        return <CheckCircle className="h-4 w-4" />;
      case 'closed':
        return <CheckCircle className="h-4 w-4" />;
      default:
        return <Clock className="h-4 w-4" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'open':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'in_progress':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      case 'resolved':
        return 'bg-green-100 text-green-800 border-green-200';
      case 'closed':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'bug_report':
        return <Bug className="h-4 w-4" />;
      case 'feature_request':
        return <FeatureIcon className="h-4 w-4" />;
      case 'content_feedback':
        return <Star className="h-4 w-4" />;
      case 'general':
        return <MessageSquare className="h-4 w-4" />;
      default:
        return <MessageSquare className="h-4 w-4" />;
    }
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading feedback...</div>;
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
              <Button variant="default" className="w-full justify-start" onClick={() => navigate('/feedback')}>
                <MessageSquare className="mr-2 h-4 w-4" /> Feedback
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
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Feedback & Support</h1>
          <Dialog open={showSubmitDialog} onOpenChange={setShowSubmitDialog}>
            <DialogTrigger asChild>
              <Button className="bg-blue-600 hover:bg-blue-700">
                <Plus className="mr-2 h-4 w-4" />
                Submit Feedback
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl">
              <DialogHeader>
                <DialogTitle>Submit Feedback</DialogTitle>
              </DialogHeader>
              <form onSubmit={handleSubmitFeedback} className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="feedback_type">Feedback Type</Label>
                    <Select value={formData.feedback_type} onValueChange={(value) => setFormData({...formData, feedback_type: value})}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select type" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="bug_report">Bug Report</SelectItem>
                        <SelectItem value="feature_request">Feature Request</SelectItem>
                        <SelectItem value="content_feedback">Content Feedback</SelectItem>
                        <SelectItem value="general">General Feedback</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="category">Category</Label>
                    <Select value={formData.category} onValueChange={(value) => setFormData({...formData, category: value})}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select category" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="ui_ux">UI/UX</SelectItem>
                        <SelectItem value="performance">Performance</SelectItem>
                        <SelectItem value="content_quality">Content Quality</SelectItem>
                        <SelectItem value="functionality">Functionality</SelectItem>
                        <SelectItem value="other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
                <div>
                  <Label htmlFor="title">Title</Label>
                  <Input
                    id="title"
                    value={formData.title}
                    onChange={(e) => setFormData({...formData, title: e.target.value})}
                    placeholder="Brief description of the issue or suggestion"
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    value={formData.description}
                    onChange={(e) => setFormData({...formData, description: e.target.value})}
                    placeholder="Detailed description of your feedback"
                    rows={4}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="priority">Priority</Label>
                  <Select value={formData.priority} onValueChange={(value) => setFormData({...formData, priority: value})}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                      <SelectItem value="critical">Critical</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="flex justify-end space-x-2">
                  <Button type="button" variant="outline" onClick={() => setShowSubmitDialog(false)}>
                    Cancel
                  </Button>
                  <Button type="submit" disabled={isSubmitting}>
                    {isSubmitting ? 'Submitting...' : 'Submit Feedback'}
                    <Send className="ml-2 h-4 w-4" />
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {/* Feedback Stats */}
        {feedbackStats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Feedback</CardTitle>
                <MessageSquare className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{feedbackStats.total_feedback}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Resolved</CardTitle>
                <CheckCircle className="h-4 w-4 text-green-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold text-green-600">{feedbackStats.resolved_feedback}</div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Bug Reports</CardTitle>
                <Bug className="h-4 w-4 text-red-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {feedbackStats.feedback_by_type.find(item => item.type === 'bug_report')?.count || 0}
                </div>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Feature Requests</CardTitle>
                <FeatureIcon className="h-4 w-4 text-blue-600" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {feedbackStats.feedback_by_type.find(item => item.type === 'feature_request')?.count || 0}
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Feedback List */}
        <Card>
          <CardHeader>
            <CardTitle>Your Feedback Submissions</CardTitle>
          </CardHeader>
          <CardContent>
            {feedbackList.length === 0 ? (
              <div className="text-center py-8">
                <MessageSquare className="mx-auto h-12 w-12 text-gray-400 mb-4" />
                <p className="text-gray-500">No feedback submitted yet</p>
                <Button 
                  className="mt-4" 
                  onClick={() => setShowSubmitDialog(true)}
                >
                  Submit Your First Feedback
                </Button>
              </div>
            ) : (
              <div className="space-y-4">
                {feedbackList.map((feedback) => (
                  <Card key={feedback.id} className="hover:shadow-md transition-shadow">
                    <CardContent className="p-4">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-3 flex-1">
                          <div className="p-2 bg-gray-100 rounded-full">
                            {getTypeIcon(feedback.feedback_type)}
                          </div>
                          <div className="flex-1">
                            <div className="flex items-center space-x-2 mb-2">
                              <h3 className="font-semibold text-gray-900">{feedback.title}</h3>
                              <Badge className={getStatusColor(feedback.status)}>
                                {getStatusIcon(feedback.status)}
                                <span className="ml-1">{feedback.status.replace('_', ' ')}</span>
                              </Badge>
                              <Badge variant="outline">
                                {feedback.feedback_type.replace('_', ' ')}
                              </Badge>
                            </div>
                            <p className="text-gray-600 text-sm mb-2">{feedback.description.substring(0, 150)}...</p>
                            <div className="flex items-center space-x-4 text-xs text-gray-500">
                              <span>Created: {new Date(feedback.created_at).toLocaleDateString()}</span>
                              {feedback.category && <span>Category: {feedback.category}</span>}
                              <span>Priority: {feedback.priority}</span>
                            </div>
                          </div>
                        </div>
                        <div className="flex space-x-2">
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => handleViewDetail(feedback)}
                          >
                            <Eye className="h-4 w-4 mr-1" />
                            View
                          </Button>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Feedback Detail Dialog */}
        <Dialog open={showDetailDialog} onOpenChange={setShowDetailDialog}>
          <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
            {selectedFeedback && (
              <>
                <DialogHeader>
                  <DialogTitle className="flex items-center space-x-2">
                    {getTypeIcon(selectedFeedback.feedback_type)}
                    <span>{selectedFeedback.title}</span>
                    <Badge className={getStatusColor(selectedFeedback.status)}>
                      {selectedFeedback.status.replace('_', ' ')}
                    </Badge>
                  </DialogTitle>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <h4 className="font-semibold mb-2">Description</h4>
                    <p className="text-gray-700 bg-gray-50 p-3 rounded">{selectedFeedback.description}</p>
                  </div>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-semibold mb-1">Type</h4>
                      <p>{selectedFeedback.feedback_type.replace('_', ' ')}</p>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-1">Category</h4>
                      <p>{selectedFeedback.category || 'Not specified'}</p>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-1">Priority</h4>
                      <p>{selectedFeedback.priority}</p>
                    </div>
                    <div>
                      <h4 className="font-semibold mb-1">Created</h4>
                      <p>{new Date(selectedFeedback.created_at).toLocaleString()}</p>
                    </div>
                  </div>

                  {selectedFeedback.admin_response && (
                    <div>
                      <h4 className="font-semibold mb-2">Admin Response</h4>
                      <p className="text-gray-700 bg-blue-50 p-3 rounded border-l-4 border-blue-400">
                        {selectedFeedback.admin_response}
                      </p>
                    </div>
                  )}

                  {selectedFeedback.comments && selectedFeedback.comments.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2 flex items-center">
                        <MessageCircle className="mr-2 h-4 w-4" />
                        Comments ({selectedFeedback.comments.length})
                      </h4>
                      <div className="space-y-3">
                        {selectedFeedback.comments.map((comment) => (
                          <div key={comment.id} className={`p-3 rounded ${comment.is_admin_comment ? 'bg-blue-50 border-l-4 border-blue-400' : 'bg-gray-50'}`}>
                            <div className="flex justify-between items-start mb-2">
                              <span className="font-medium">
                                {comment.user.username}
                                {comment.is_admin_comment && <Badge className="ml-2" variant="secondary">Admin</Badge>}
                              </span>
                              <span className="text-xs text-gray-500">
                                {new Date(comment.created_at).toLocaleString()}
                              </span>
                            </div>
                            <p className="text-gray-700">{comment.comment}</p>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </>
            )}
          </DialogContent>
        </Dialog>
      </main>
    </div>
  );
};

export default Feedback;

