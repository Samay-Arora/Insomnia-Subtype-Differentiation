/**
 * Main Application Component
 * React Router configuration for Sleep Research Platform
 * 
 * Routes:
 * - / : Landing page (public)
 * - /login : Login page (public)
 * - /signup : Signup page (public)
 * - /dashboard : Main dashboard (protected)
 * - /analysis : Analysis view (protected)
 * 
 * Auth State:
 * Uses simple boolean state for navigation testing
 * Replace with real auth context when integrating backend
 */

import React, { useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import {
  LandingPage,
  LoginPage,
  SignupPage,
  DashboardPage,
  AnalysisPage
} from './pages';

// Simple auth state for testing navigation
// TODO: Replace with real auth context when integrating backend
import { supabase } from './services/api';

const useAuth = () => {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loading, setLoading] = useState(true);

  React.useEffect(() => {
    // Check active session
    supabase.auth.getSession().then(({ data: { session } }) => {
      setIsLoggedIn(!!session);
      setLoading(false);
    });

    // Listen for auth changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setIsLoggedIn(!!session);
      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  const logout = async () => {
    await supabase.auth.signOut();
  };

  return { isLoggedIn, loading, logout };
};

// Protected route wrapper
interface ProtectedRouteProps {
  isLoggedIn: boolean;
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ isLoggedIn, children }) => {
  if (!isLoggedIn) {
    return <Navigate to="/login" replace />;
  }
  return <>{children}</>;
};

const App: React.FC = () => {
  const { isLoggedIn, loading, logout } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-zinc-900 text-white font-pixel">
        LOADING DREAMSCAPE...
      </div>
    );
  }

  return (
    <BrowserRouter>
      <Routes>
        {/* Public Routes */}
        <Route path="/" element={<LandingPage />} />
        <Route
          path="/login"
          element={
            isLoggedIn
              ? <Navigate to="/dashboard" replace />
              : <LoginPage />
          }
        />
        <Route
          path="/signup"
          element={
            isLoggedIn
              ? <Navigate to="/dashboard" replace />
              : <SignupPage />
          }
        />

        {/* Protected Routes */}
        <Route
          path="/dashboard"
          element={
            <ProtectedRoute isLoggedIn={isLoggedIn}>
              <DashboardPage onLogout={logout} />
            </ProtectedRoute>
          }
        />
        <Route
          path="/analysis/:sessionId?"
          element={
            <ProtectedRoute isLoggedIn={isLoggedIn}>
              <AnalysisPage onLogout={logout} />
            </ProtectedRoute>
          }
        />

        {/* Catch-all redirect */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
