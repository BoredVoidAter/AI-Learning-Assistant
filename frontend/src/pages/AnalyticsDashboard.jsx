import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
import { Badge } from '../components/ui/badge';
import { LayoutDashboard, BookOpen, Brain, FileText, Lightbulb, Settings, LogOut, TrendingUp, BarChart, Clock, Activity, Target, Award, Calendar } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart as RechartsBarChart, Bar, PieChart, Pie, Cell } from 'recharts';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D'];

const getActivityIcon = (activityType) => {
  switch (activityType) {
    case 'learning_path_started':
    case 'learning_path_completed':
      return <BookOpen className="h-4 w-4" />;
    case 'quiz_completed':
    case 'quiz_started':
      return <Brain className="h-4 w-4" />;
    case 'resource_viewed':
    case 'resource_created':
      return <Lightbulb className="h-4 w-4" />;
    case 'note_created':
    case 'note_updated':
      return <FileText className="h-4 w-4" />;
    case 'login':
      return <Activity className="h-4 w-4" />;
    default:
      return <Activity className="h-4 w-4" />;
  }
};

const getActivityColor = (activityType) => {
  switch (activityType) {
    case 'learning_path_completed':
    case 'quiz_completed':
      return 'bg-green-100 text-green-800 border-green-200';
    case 'learning_path_started':
    case 'quiz_started':
      return 'bg-blue-100 text-blue-800 border-blue-200';
    case 'resource_viewed':
    case 'resource_created':
      return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    case 'note_created':
    case 'note_updated':
      return 'bg-purple-100 text-purple-800 border-purple-200';
    default:
      return 'bg-gray-100 text-gray-800 border-gray-200';
  }
};

const AnalyticsDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [dashboardData, setDashboardData] = useState(null);
  const [learningProgress, setLearningProgress] = useState(null);
  const [quizAnalytics, setQuizAnalytics] = useState(null);
  const [studyTimeAnalytics, setStudyTimeAnalytics] = useState(null);
  const [userActivities, setUserActivities] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (user) {
      fetchAllAnalytics();
    }
  }, [user]);

  const fetchAllAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const [dashboardRes, learningRes, quizRes, studyTimeRes, activitiesRes] = await Promise.all([
        axios.get(`${API_URL}/analytics/dashboard`),
        axios.get(`${API_URL}/analytics/learning-progress`),
        axios.get(`${API_URL}/analytics/quiz-analytics`),
        axios.get(`${API_URL}/analytics/study-time`),
        axios.get(`${API_URL}/activities?per_page=5`) // Fetch last 5 activities
      ]);
      setDashboardData(dashboardRes.data);
      setLearningProgress(learningRes.data);
      setQuizAnalytics(quizRes.data);
      setStudyTimeAnalytics(studyTimeRes.data);
      setUserActivities(activitiesRes.data.activities);
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch analytics data');
    }
    setLoading(false);
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading analytics...</div>;
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
        <h1 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white">Your Learning Analytics</h1>

        {dashboardData && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-blue-100">Learning Paths</CardTitle>
                <BookOpen className="h-4 w-4 text-blue-200" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{dashboardData.overview.total_learning_paths}</div>
                <div className="mt-2">
                  <Progress 
                    value={(dashboardData.overview.completed_learning_paths / dashboardData.overview.total_learning_paths) * 100} 
                    className="h-2 bg-blue-400"
                  />
                  <p className="text-xs text-blue-100 mt-1">
                    {dashboardData.overview.completed_learning_paths} of {dashboardData.overview.total_learning_paths} completed
                  </p>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-gradient-to-r from-green-500 to-green-600 text-white">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-green-100">Quiz Performance</CardTitle>
                <Brain className="h-4 w-4 text-green-200" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{dashboardData.overview.average_quiz_score}%</div>
                <div className="mt-2">
                  <Progress 
                    value={dashboardData.overview.average_quiz_score} 
                    className="h-2 bg-green-400"
                  />
                  <p className="text-xs text-green-100 mt-1">
                    Across {dashboardData.overview.total_quizzes_taken} quizzes
                  </p>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-gradient-to-r from-purple-500 to-purple-600 text-white">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-purple-100">Study Time</CardTitle>
                <Clock className="h-4 w-4 text-purple-200" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{dashboardData.overview.total_study_time_hours}h</div>
                <div className="flex items-center mt-2">
                  <Target className="h-3 w-3 text-purple-200 mr-1" />
                  <p className="text-xs text-purple-100">
                    {dashboardData.overview.learning_streak_days} day streak
                  </p>
                </div>
              </CardContent>
            </Card>
            
            <Card className="bg-gradient-to-r from-orange-500 to-orange-600 text-white">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-orange-100">Achievement</CardTitle>
                <Award className="h-4 w-4 text-orange-200" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">
                  {dashboardData.overview.completed_learning_paths + dashboardData.overview.total_quizzes_taken}
                </div>
                <p className="text-xs text-orange-100 mt-2">
                  Total completions
                </p>
              </CardContent>
            </Card>
          </div>
        )}

        {learningProgress && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold mb-4">Learning Path Progress</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {learningProgress.learning_progress.map((lp) => (
                <Card key={lp.learning_path.id}>
                  <CardHeader>
                    <CardTitle>{lp.learning_path.title}</CardTitle>
                    <p className="text-sm text-muted-foreground">{lp.learning_path.subject} - {lp.learning_path.difficulty_level}</p>
                  </CardHeader>
                  <CardContent>
                    <p>Topics Completed: {lp.topics_progress.completed} / {lp.topics_progress.total} ({lp.topics_progress.percentage.toFixed(1)}%)</p>
                    <p>Resources Completed: {lp.resources_progress.completed} / {lp.resources_progress.total} ({lp.resources_progress.percentage.toFixed(1)}%)</p>
                    <p>Time Spent: {lp.time_spent_hours} hours</p>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        )}

        {quizAnalytics && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold mb-4">Quiz Performance</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Overall Quiz Performance</CardTitle>
                </CardHeader>
                <CardContent>
                  <p>Total Attempts: {quizAnalytics.total_attempts}</p>
                  <p>Average Score: {quizAnalytics.average_score}%</p>
                  <p>Best Score: {quizAnalytics.best_score}%</p>
                  <p>Improvement Trend: {quizAnalytics.improvement_trend > 0 ? `+${quizAnalytics.improvement_trend.toFixed(1)}%` : `${quizAnalytics.improvement_trend.toFixed(1)}%`}</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>Performance by Difficulty</CardTitle>
                </CardHeader>
                <CardContent>
                  {quizAnalytics.performance_by_difficulty.map((perf) => (
                    <p key={perf.difficulty}>{perf.difficulty}: {perf.average_score.toFixed(1)}% (Attempts: {perf.attempts_count})</p>
                  ))}
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>Performance by Subject</CardTitle>
                </CardHeader>
                <CardContent>
                  {quizAnalytics.performance_by_subject.map((perf) => (
                    <p key={perf.subject}>{perf.subject}: {perf.average_score.toFixed(1)}% (Attempts: {perf.attempts_count})</p>
                  ))}
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>Recent Quiz Attempts</CardTitle>
                </CardHeader>
                <CardContent>
                  {quizAnalytics.recent_attempts.map((attempt) => (
                    <p key={attempt.id} className="text-sm">{attempt.quiz_title} ({attempt.subject}): {attempt.percentage}% on {new Date(attempt.completed_at).toLocaleDateString()}</p>
                  ))}
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {studyTimeAnalytics && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold mb-4">Study Time Analytics</h2>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
              <Card>
                <CardHeader>
                  <CardTitle>Daily Study Time Trend</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={studyTimeAnalytics.daily_study_time}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" />
                      <YAxis />
                      <Tooltip />
                      <Line type="monotone" dataKey="hours" stroke="#8884d8" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle>Study Time by Subject</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={studyTimeAnalytics.subject_study_time}
                        cx="50%"
                        cy="50%"
                        labelLine={false}
                        label={({ subject, total_hours }) => `${subject}: ${total_hours}h`}
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="total_hours"
                      >
                        {studyTimeAnalytics.subject_study_time.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Weekly Study Averages</CardTitle>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={200}>
                    <RechartsBarChart data={studyTimeAnalytics.weekly_averages}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="week_start" />
                      <YAxis />
                      <Tooltip />
                      <Bar dataKey="daily_average" fill="#82ca9d" />
                    </RechartsBarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader>
                  <CardTitle>Study Time Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {studyTimeAnalytics.subject_study_time.map((subject, index) => (
                      <div key={subject.subject} className="flex items-center justify-between">
                        <div className="flex items-center">
                          <div 
                            className="w-3 h-3 rounded-full mr-2" 
                            style={{ backgroundColor: COLORS[index % COLORS.length] }}
                          ></div>
                          <span className="font-medium">{subject.subject}</span>
                        </div>
                        <span className="text-gray-600">{subject.total_hours} hours</span>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {userActivities && userActivities.length > 0 && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold mb-4 flex items-center">
              <Activity className="mr-2 h-6 w-6" />
              Recent Activities
            </h2>
            <div className="grid grid-cols-1 gap-4">
              {userActivities.map((activity) => (
                <Card key={activity.id} className="shadow-sm hover:shadow-md transition-shadow">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3">
                        <div className={`p-2 rounded-full border ${getActivityColor(activity.activity_type)}`}>
                          {getActivityIcon(activity.activity_type)}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center space-x-2">
                            <h3 className="font-semibold text-gray-900 dark:text-white">
                              {activity.activity_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </h3>
                            <Badge variant="outline" className="text-xs">
                              {new Date(activity.timestamp).toLocaleDateString()}
                            </Badge>
                          </div>
                          <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                            {new Date(activity.timestamp).toLocaleTimeString()}
                          </p>
                          {activity.activity_details && (
                            <div className="mt-2 p-2 bg-gray-50 dark:bg-gray-800 rounded text-sm">
                              <pre className="text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                                {JSON.stringify(activity.activity_details, null, 2)}
                              </pre>
                            </div>
                          )}
                        </div>
                      </div>
                      <div className="text-right">
                        <Calendar className="h-4 w-4 text-gray-400" />
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
            <div className="text-center mt-6">
              <Button variant="outline" onClick={() => navigate("/activities")} className="px-6">
                <Activity className="mr-2 h-4 w-4" />
                View All Activities
              </Button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default AnalyticsDashboard;



