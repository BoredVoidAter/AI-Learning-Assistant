import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Progress } from '../components/ui/progress';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { 
  LayoutDashboard, BookOpen, Brain, FileText, Lightbulb, Settings, LogOut,
  Trophy, Award, Star, Crown, Target, Flame, Shield, Gem, TrendingUp,
  Medal, Users, Calendar, BarChart3, Zap, Gift
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

const Gamification = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [achievements, setAchievements] = useState([]);
  const [badges, setBadges] = useState([]);
  const [leaderboards, setLeaderboards] = useState({});
  const [stats, setStats] = useState(null);
  const [levelProgress, setLevelProgress] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    if (user) {
      fetchGamificationData();
    }
  }, [user]);

  const fetchGamificationData = async () => {
    setLoading(true);
    try {
      const [profileRes, achievementsRes, badgesRes, statsRes, levelRes] = await Promise.all([
        axios.get(`${API_URL}/gamification/profile`),
        axios.get(`${API_URL}/gamification/achievements`),
        axios.get(`${API_URL}/gamification/badges`),
        axios.get(`${API_URL}/gamification/stats`),
        axios.get(`${API_URL}/gamification/level-progress`)
      ]);

      setProfile(profileRes.data.profile);
      setAchievements(achievementsRes.data.achievements);
      setBadges(badgesRes.data.badges);
      setStats(statsRes.data.stats);
      setLevelProgress(levelRes.data);

      // Fetch leaderboards
      await fetchLeaderboards();
    } catch (err) {
      setError(err.response?.data?.error || 'Failed to fetch gamification data');
    } finally {
      setLoading(false);
    }
  };

  const fetchLeaderboards = async () => {
    try {
      const leaderboardTypes = ['weekly', 'monthly', 'all_time'];
      const categories = ['points', 'quizzes'];
      const leaderboardData = {};

      for (const type of leaderboardTypes) {
        for (const category of categories) {
          try {
            const response = await axios.get(`${API_URL}/gamification/leaderboard/${type}/${category}?limit=10`);
            leaderboardData[`${type}_${category}`] = response.data;
          } catch (err) {
            console.error(`Failed to fetch ${type} ${category} leaderboard:`, err);
          }
        }
      }

      setLeaderboards(leaderboardData);
    } catch (err) {
      console.error('Failed to fetch leaderboards:', err);
    }
  };

  const getRarityColor = (rarity) => {
    switch (rarity) {
      case 'common':
        return 'bg-gray-100 text-gray-800 border-gray-200';
      case 'rare':
        return 'bg-blue-100 text-blue-800 border-blue-200';
      case 'epic':
        return 'bg-purple-100 text-purple-800 border-purple-200';
      case 'legendary':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200';
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200';
    }
  };

  const getAchievementIcon = (iconName) => {
    const iconMap = {
      'graduation-cap': Trophy,
      'book-open': BookOpen,
      'crown': Crown,
      'brain': Brain,
      'trophy': Trophy,
      'star': Star,
      'calendar': Calendar,
      'flame': Flame,
      'search': Target,
      'file-text': FileText,
      'trending-up': TrendingUp,
      'gem': Gem
    };
    return iconMap[iconName] || Award;
  };

  const getBadgeIcon = (iconName) => {
    const iconMap = {
      'shield': Shield,
      'award': Award,
      'target': Target
    };
    return iconMap[iconName] || Medal;
  };

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  if (loading) {
    return <div className="flex items-center justify-center min-h-screen">Loading gamification data...</div>;
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
              <Button variant="default" className="w-full justify-start" onClick={() => navigate('/gamification')}>
                <Trophy className="mr-2 h-4 w-4" /> Achievements
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
        <h1 className="text-3xl font-bold mb-6 text-gray-900 dark:text-white flex items-center">
          <Trophy className="mr-3 h-8 w-8 text-yellow-500" />
          Achievements & Progress
        </h1>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="achievements">Achievements</TabsTrigger>
            <TabsTrigger value="badges">Badges</TabsTrigger>
            <TabsTrigger value="leaderboards">Leaderboards</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            {/* Level Progress */}
            {levelProgress && (
              <Card className="bg-gradient-to-r from-purple-500 to-pink-500 text-white">
                <CardHeader>
                  <CardTitle className="flex items-center text-white">
                    <Crown className="mr-2 h-6 w-6" />
                    Level {levelProgress.level_info.current_level}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm text-purple-100 mb-2">
                        <span>Progress to Level {levelProgress.level_info.current_level + 1}</span>
                        <span>{levelProgress.progress.progress_in_level} / {levelProgress.progress.points_needed_for_level} XP</span>
                      </div>
                      <Progress 
                        value={levelProgress.progress.progress_percentage} 
                        className="h-3 bg-purple-400"
                      />
                    </div>
                    <div className="grid grid-cols-2 gap-4 text-sm">
                      <div>
                        <span className="text-purple-100">Total Points:</span>
                        <div className="text-xl font-bold">{levelProgress.level_info.total_points}</div>
                      </div>
                      <div>
                        <span className="text-purple-100">Current Streak:</span>
                        <div className="text-xl font-bold flex items-center">
                          <Flame className="mr-1 h-5 w-5" />
                          {levelProgress.level_info.current_learning_streak} days
                        </div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Stats Overview */}
            {stats && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <Card className="bg-gradient-to-r from-blue-500 to-blue-600 text-white">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-blue-100">Achievements</CardTitle>
                    <Award className="h-4 w-4 text-blue-200" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{stats.achievements_earned}</div>
                    <div className="mt-2">
                      <Progress 
                        value={stats.achievement_completion_rate} 
                        className="h-2 bg-blue-400"
                      />
                      <p className="text-xs text-blue-100 mt-1">
                        {stats.achievement_completion_rate.toFixed(1)}% Complete
                      </p>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-gradient-to-r from-green-500 to-green-600 text-white">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-green-100">Badges</CardTitle>
                    <Shield className="h-4 w-4 text-green-200" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{stats.badges_earned}</div>
                    <div className="mt-2">
                      <Progress 
                        value={stats.badge_completion_rate} 
                        className="h-2 bg-green-400"
                      />
                      <p className="text-xs text-green-100 mt-1">
                        {stats.badge_completion_rate.toFixed(1)}% Complete
                      </p>
                    </div>
                  </CardContent>
                </Card>

                <Card className="bg-gradient-to-r from-orange-500 to-orange-600 text-white">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-orange-100">Current Streak</CardTitle>
                    <Flame className="h-4 w-4 text-orange-200" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{stats.current_streak}</div>
                    <p className="text-xs text-orange-100 mt-2">
                      Best: {stats.longest_streak} days
                    </p>
                  </CardContent>
                </Card>

                <Card className="bg-gradient-to-r from-purple-500 to-purple-600 text-white">
                  <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                    <CardTitle className="text-sm font-medium text-purple-100">Level</CardTitle>
                    <Crown className="h-4 w-4 text-purple-200" />
                  </CardHeader>
                  <CardContent>
                    <div className="text-2xl font-bold">{stats.level}</div>
                    <p className="text-xs text-purple-100 mt-2">
                      {stats.total_points} total points
                    </p>
                  </CardContent>
                </Card>
              </div>
            )}
          </TabsContent>

          {/* Achievements Tab */}
          <TabsContent value="achievements" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {achievements.map((achievement) => {
                const IconComponent = getAchievementIcon(achievement.icon);
                return (
                  <Card key={achievement.id} className={`transition-all duration-200 ${achievement.earned ? 'bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200' : 'hover:shadow-md'}`}>
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div className="flex items-center space-x-3">
                          <div className={`p-2 rounded-full ${achievement.earned ? 'bg-yellow-200' : 'bg-gray-200'}`}>
                            <IconComponent className={`h-6 w-6 ${achievement.earned ? 'text-yellow-700' : 'text-gray-500'}`} />
                          </div>
                          <div>
                            <CardTitle className="text-lg">{achievement.name}</CardTitle>
                            <Badge className={getRarityColor(achievement.rarity)}>
                              {achievement.rarity}
                            </Badge>
                          </div>
                        </div>
                        {achievement.earned && (
                          <div className="text-right">
                            <div className="text-sm text-yellow-600 font-medium">+{achievement.points} XP</div>
                          </div>
                        )}
                      </div>
                    </CardHeader>
                    <CardContent>
                      <p className="text-gray-600 text-sm mb-3">{achievement.description}</p>
                      {!achievement.earned && (
                        <div>
                          <div className="flex justify-between text-xs text-gray-500 mb-1">
                            <span>Progress</span>
                            <span>{achievement.progress} / {achievement.condition_target}</span>
                          </div>
                          <Progress value={achievement.progress_percentage} className="h-2" />
                        </div>
                      )}
                      {achievement.earned && (
                        <div className="flex items-center text-sm text-yellow-600">
                          <Trophy className="h-4 w-4 mr-1" />
                          Earned {new Date(achievement.earned_at).toLocaleDateString()}
                        </div>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </TabsContent>

          {/* Badges Tab */}
          <TabsContent value="badges" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {badges.map((badge) => {
                const IconComponent = getBadgeIcon(badge.icon);
                return (
                  <Card key={badge.id} className={`text-center transition-all duration-200 ${badge.earned ? 'bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200' : 'opacity-60 hover:opacity-80'}`}>
                    <CardContent className="p-6">
                      <div className="flex flex-col items-center space-y-3">
                        <div 
                          className="p-4 rounded-full"
                          style={{ backgroundColor: badge.earned ? badge.color : '#E5E7EB' }}
                        >
                          <IconComponent className={`h-8 w-8 ${badge.earned ? 'text-white' : 'text-gray-400'}`} />
                        </div>
                        <div>
                          <h3 className="font-semibold text-lg">{badge.name}</h3>
                          <p className="text-sm text-gray-600 mt-1">{badge.description}</p>
                        </div>
                        {badge.earned && (
                          <div className="text-xs text-blue-600 flex items-center">
                            <Gift className="h-3 w-3 mr-1" />
                            Earned {new Date(badge.earned_at).toLocaleDateString()}
                          </div>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </TabsContent>

          {/* Leaderboards Tab */}
          <TabsContent value="leaderboards" className="space-y-6">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {Object.entries(leaderboards).map(([key, leaderboard]) => {
                if (!leaderboard || !leaderboard.leaderboard) return null;
                
                const [type, category] = key.split('_');
                const title = `${type.charAt(0).toUpperCase() + type.slice(1)} ${category.charAt(0).toUpperCase() + category.slice(1)}`;
                
                return (
                  <Card key={key}>
                    <CardHeader>
                      <CardTitle className="flex items-center">
                        <BarChart3 className="mr-2 h-5 w-5" />
                        {title} Leaderboard
                      </CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-3">
                        {leaderboard.leaderboard.slice(0, 10).map((entry, index) => (
                          <div key={entry.id} className={`flex items-center justify-between p-2 rounded ${entry.user_id === user.id ? 'bg-blue-50 border border-blue-200' : 'hover:bg-gray-50'}`}>
                            <div className="flex items-center space-x-3">
                              <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                                index === 0 ? 'bg-yellow-100 text-yellow-800' :
                                index === 1 ? 'bg-gray-100 text-gray-800' :
                                index === 2 ? 'bg-orange-100 text-orange-800' :
                                'bg-gray-50 text-gray-600'
                              }`}>
                                {entry.rank}
                              </div>
                              <div>
                                <div className="font-medium">{entry.user.username}</div>
                                {entry.user_id === user.id && (
                                  <div className="text-xs text-blue-600">You</div>
                                )}
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="font-bold">{entry.score}</div>
                              <div className="text-xs text-gray-500">
                                {category === 'points' ? 'points' : category}
                              </div>
                            </div>
                          </div>
                        ))}
                      </div>
                      {leaderboard.user_position && leaderboard.user_position.rank > 10 && (
                        <div className="mt-4 pt-4 border-t">
                          <div className="flex items-center justify-between p-2 rounded bg-blue-50 border border-blue-200">
                            <div className="flex items-center space-x-3">
                              <div className="w-8 h-8 rounded-full bg-blue-100 text-blue-800 flex items-center justify-center text-sm font-bold">
                                {leaderboard.user_position.rank}
                              </div>
                              <div>
                                <div className="font-medium">{user.username}</div>
                                <div className="text-xs text-blue-600">Your Position</div>
                              </div>
                            </div>
                            <div className="text-right">
                              <div className="font-bold">{leaderboard.user_position.score}</div>
                              <div className="text-xs text-gray-500">
                                {category === 'points' ? 'points' : category}
                              </div>
                            </div>
                          </div>
                        </div>
                      )}
                    </CardContent>
                  </Card>
                );
              })}
            </div>
          </TabsContent>
        </Tabs>
      </main>
    </div>
  );
};

export default Gamification;

