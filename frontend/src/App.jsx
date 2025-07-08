import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/AnalyticsDashboard'; // Use AnalyticsDashboard
import LearningPaths from './pages/LearningPaths';
import LearningPathDetail from './pages/LearningPathDetail';
import Quizzes from './pages/Quizzes';
import QuizDetail from './pages/QuizDetail';
import Resources from './pages/Resources';
import ResourceDetail from './pages/ResourceDetail';
import Notes from './pages/Notes';
import NoteDetail from './pages/NoteDetail';
import Settings from './pages/Settings';
import Recommendations from './pages/Recommendations';
import Notifications from './pages/Notifications';
import Feedback from './pages/Feedback';
import './App.css';

const PrivateRoute = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();

  if (loading) {
    return <div>Loading...</div>; // Or a spinner component
  }

  return isAuthenticated ? children : <Navigate to="/login" />;
};

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route
            path="/dashboard"
            element={
              <PrivateRoute>
                <Dashboard />
              </PrivateRoute>
            }
          />
          <Route
            path="/learning-paths"
            element={
              <PrivateRoute>
                <LearningPaths />
              </PrivateRoute>
            }
          />
          <Route
            path="/learning-paths/:id"
            element={
              <PrivateRoute>
                <LearningPathDetail />
              </PrivateRoute>
            }
          />
          <Route
            path="/quizzes"
            element={
              <PrivateRoute>
                <Quizzes />
              </PrivateRoute>
            }
          />
          <Route
            path="/quizzes/:id"
            element={
              <PrivateRoute>
                <QuizDetail />
              </PrivateRoute>
            }
          />
          <Route
            path="/resources"
            element={
              <PrivateRoute>
                <Resources />
              </PrivateRoute>
            }
          />
          <Route
            path="/resources/:id"
            element={
              <PrivateRoute>
                <ResourceDetail />
              </PrivateRoute>
            }
          />
          <Route
            path="/notes"
            element={
              <PrivateRoute>
                <Notes />
              </PrivateRoute>
            }
          />
          <Route
            path="/notes/:id"
            element={
              <PrivateRoute>
                <NoteDetail />
              </PrivateRoute>
            }
          />
          <Route
            path="/settings"
            element={
              <PrivateRoute>
                <Settings />
              </PrivateRoute>
            }
          />
          <Route
            path="/recommendations"
            element={
              <PrivateRoute>
                <Recommendations />
              </PrivateRoute>
            }
          />
          <Route
            path="/notifications"
            element={
              <PrivateRoute>
                <Notifications />
              </PrivateRoute>
            }
          />
          <Route
            path="/feedback"
            element={
              <PrivateRoute>
                <Feedback />
              </PrivateRoute>
            }
          />
          <Route path="*" element={<Navigate to="/dashboard" />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;


