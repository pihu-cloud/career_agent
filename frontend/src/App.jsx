import React from 'react';
import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import Layout from './components/layout/Layout';
import LoadingSpinner from './components/ui/LoadingSpinner';

// Pages
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import ProfilePage from './pages/ProfilePage';
import SkillsPage from './pages/SkillsPage';
import InterestsPage from './pages/InterestsPage';
import PersonalityPage from './pages/PersonalityPage';
import AcademicsPage from './pages/AcademicsPage';
import ProfileCompletePage from './pages/ProfileCompletePage';
import ResumePage from './pages/ResumePage';
import ProgressPage from './pages/ProgressPage';
import OnboardingPage from './pages/OnboardingPage';
import AdminDashboard from './pages/AdminDashboard';
import RecommendationsPage from './pages/RecommendationsPage';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { user, token, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <LoadingSpinner fullScreen text="Authenticating session..." />;
  }

  if (!token && !user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return children;
};

// Admin Route Component
const AdminRoute = ({ children }) => {
  const { user, token, isLoading, isAdmin } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return <LoadingSpinner fullScreen text="Verifying permissions..." />;
  }

  if (!token && !user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (!isAdmin) {
    return <Navigate to="/dashboard" replace />;
  }

  return children;
};

// Root Redirect Component
const RootRedirect = () => {
  const { user, token, isLoading } = useAuth();

  if (isLoading) {
    return <LoadingSpinner fullScreen text="Initializing CareerPilot AI..." />;
  }

  if (token || user) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Navigate to="/login" replace />;
};

export const App = () => {
  return (
    <Routes>
      {/* Root redirect */}
      <Route path="/" element={<RootRedirect />} />

      {/* Public Auth Routes */}
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />

      {/* Onboarding Flow (Minimal Layout) */}
      <Route
        path="/onboarding"
        element={
          <ProtectedRoute>
            <OnboardingPage />
          </ProtectedRoute>
        }
      />

      {/* Protected Student / Dashboard Routes with Full Layout */}
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <Layout>
              <DashboardPage />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/profile"
        element={
          <ProtectedRoute>
            <Layout>
              <ProfilePage />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/profile/skills"
        element={
          <ProtectedRoute>
            <Layout>
              <SkillsPage />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/profile/interests"
        element={
          <ProtectedRoute>
            <Layout>
              <InterestsPage />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/profile/personality"
        element={
          <ProtectedRoute>
            <Layout>
              <PersonalityPage />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/profile/academics"
        element={
          <ProtectedRoute>
            <Layout>
              <AcademicsPage />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/profile/complete"
        element={
          <ProtectedRoute>
            <Layout>
              <ProfileCompletePage />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/resume"
        element={
          <ProtectedRoute>
            <Layout>
              <ResumePage />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/progress"
        element={
          <ProtectedRoute>
            <Layout>
              <ProgressPage />
            </Layout>
          </ProtectedRoute>
        }
      />

      <Route
        path="/recommendations"
        element={
          <ProtectedRoute>
            <Layout>
              <RecommendationsPage />
            </Layout>
          </ProtectedRoute>
        }
      />

      {/* Admin Route */}
      <Route
        path="/admin"
        element={
          <AdminRoute>
            <Layout>
              <AdminDashboard />
            </Layout>
          </AdminRoute>
        }
      />

      {/* Fallback */}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
};

export default App;
