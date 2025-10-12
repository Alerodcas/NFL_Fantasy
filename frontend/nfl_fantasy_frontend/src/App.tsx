import React, { ReactNode } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import RegisterForm from './components/RegisterForm';
import LoginForm from './components/LoginForm';
import ProfilePage from './components/ProfilePage';
import TeamForm from './components/TeamForm';
import { AuthProvider } from './context/AuthContext';
import { useAuth } from './hooks/useAuth';

// Componente para proteger rutas que requieren autenticación
const PrivateRoute = ({ children }: { children: ReactNode }) => {
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
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;