import React, { useEffect, useState } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { LayoutDashboard, BookOpen, Brain, FileText, Lightbulb, Settings, LogOut, TrendingUp, BarChart, Clock } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

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
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Learning Paths</CardTitle>
                <BookOpen className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{dashboardData.overview.total_learning_paths}</div>
                <p className="text-xs text-muted-foreground">{dashboardData.overview.completed_learning_paths} completed</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Average Quiz Score</CardTitle>
                <Brain className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{dashboardData.overview.average_quiz_score}%</div>
                <p className="text-xs text-muted-foreground">Across {dashboardData.overview.total_quizzes_taken} quizzes</p>
              </CardContent>
            </Card>
            <Card>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium">Total Study Time</CardTitle>
                <Clock className="h-4 w-4 text-muted-foreground" />
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold">{dashboardData.overview.total_study_time_hours} hours</div>
                <p className="text-xs text-muted-foreground">Learning streak: {dashboardData.overview.learning_streak_days} days</p>
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
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Daily Study Time</CardTitle>
                </CardHeader>
                <CardContent>
                  {studyTimeAnalytics.daily_study_time.map((day) => (
                    <p key={day.date}>{day.date}: {day.hours} hours</p>
                  ))}
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>Study Time by Subject</CardTitle>
                </CardHeader>
                <CardContent>
                  {studyTimeAnalytics.subject_study_time.map((subject) => (
                    <p key={subject.subject}>{subject.subject}: {subject.total_hours} hours</p>
                  ))}
                </CardContent>
              </Card>
              <Card>
                <CardHeader>
                  <CardTitle>Weekly Averages</CardTitle>
                </CardHeader>
                <CardContent>
                  {studyTimeAnalytics.weekly_averages.map((week) => (
                    <p key={week.week_start}>Week of {week.week_start}: {week.daily_average.toFixed(1)} hours/day</p>
                  ))}
                </CardContent>
              </Card>
            </div>
          </div>
        )}

        {userActivities && userActivities.length > 0 && (
          <div className="mb-8">
            <h2 className="text-2xl font-bold mb-4">Recent Activities</h2>
            <div className="grid grid-cols-1 gap-4">
              {userActivities.map((activity) => (
                <Card key={activity.id} className="shadow-sm">
                  <CardHeader>
                    <CardTitle className="text-lg font-semibold">{activity.activity_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</CardTitle>
                    <p className="text-sm text-gray-500 dark:text-gray-400">{new Date(activity.timestamp).toLocaleString()}</p>
                  </CardHeader>
                  <CardContent>
                    {activity.activity_details && (
                      <p className="text-gray-700 dark:text-gray-300">Details: {JSON.stringify(activity.activity_details)}</p>
                    )}
                  </CardContent>
                </Card>
              ))}
            </div>
            <div className="text-right mt-4">
              <Button variant="link" onClick={() => navigate("/activities")}>View All Activities</Button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default AnalyticsDashboard;



