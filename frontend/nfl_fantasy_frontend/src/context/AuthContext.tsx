import React, { createContext, useState, useEffect, ReactNode } from 'react';
import api from '../api/apiService';

interface User {
  id: number;
  name: string;
  email: string;
  alias: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (token: string) => void;
  logout: () => void;
  loading: boolean;
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchUser = async () => {
      if (token) {
        try {
          const response = await api.get('/users/me/');
          setUser(response.data);
        } catch (error) {
          console.error('Failed to fetch user', error);
          logout();
        }
      }
      setLoading(false);
    };

    fetchUser();
  }, [token]);


  useEffect(() => {
    const saved = localStorage.getItem('token');
    if (saved) setToken(saved);
  }, []);

  const login = (newToken: string) => {
    setToken(newToken);
    localStorage.setItem('token', newToken); 
  };


  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, loading }}>
      {!loading && children}
    </AuthContext.Provider>
  );
};