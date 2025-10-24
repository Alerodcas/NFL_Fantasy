import React, { ReactNode } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import RegisterForm from './features/auth/components/RegisterForm';
import LoginForm from './features/auth/components/LoginForm';
import ProfilePage from './features/profile/components/ProfilePage';
import TeamForm from './features/teams/components/TeamForm';
import LeagueForm from "./features/leagues/components/LeagueForm";
import { AuthProvider } from './shared/context/AuthContext';
import { useAuth } from './shared/hooks/useAuth';
import SeasonForm from './features/seasons/Seasonsform';

// Componente para proteger rutas que requieren autenticación
const PrivateRoute = ({ children }: { children: JSX.Element }): JSX.Element | null => {
  const { token } = useAuth();
  // use the same localStorage key used by AuthContext/login ("token")
  const stored = typeof window !== 'undefined' ? localStorage.getItem('token') : null;
  const effectiveToken = token || stored;
  return effectiveToken ? children : <Navigate to="/login" />;
};


function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/register" element={<RegisterForm />} />
          <Route path="/login" element={<LoginForm />} />
          <Route
            path="/profile"
            element={
              <PrivateRoute>
                <ProfilePage />
              </PrivateRoute>
            }
          />
        
          <Route
            path="/teams/new"
            element={
              <PrivateRoute>
                <TeamForm />
              </PrivateRoute>
            }
          />
          <Route path="/create-league" element={<LeagueForm />} />
          <Route path="/create-season" element={<SeasonForm />} />
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;