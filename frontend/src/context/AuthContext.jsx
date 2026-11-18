import React, { createContext, useContext, useState, useEffect } from 'react';
import { login as apiLogin, logout as apiLogout, getMe } from '../services/auth';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(() => {
    try {
      const savedUser = localStorage.getItem('user');
      return savedUser ? JSON.parse(savedUser) : null;
    } catch {
      return null;
    }
  });
  const [token, setToken] = useState(() => localStorage.getItem('token') || null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const savedToken = localStorage.getItem('token');
      if (savedToken) {
        try {
          const userData = await getMe();
          // Fallback if userData is nested in data or direct
          const userObj = userData.data || userData;
          setUser(userObj);
          localStorage.setItem('user', JSON.stringify(userObj));
        } catch (error) {
          console.error('Failed to restore auth session:', error);
          localStorage.removeItem('token');
          localStorage.removeItem('user');
          setToken(null);
          setUser(null);
        }
      }
      setIsLoading(false);
    };

    initAuth();
  }, []);

  const login = async (email, password) => {
    const data = await apiLogin(email, password);
    const receivedToken = data.access_token || data.token || (data.data && data.data.access_token);
    let userData = data.user || (data.data && data.data.user);

    if (receivedToken) {
      localStorage.setItem('token', receivedToken);
      setToken(receivedToken);

      if (!userData) {
        try {
          const meRes = await getMe();
          userData = meRes.data || meRes;
        } catch {
          userData = { email, role: 'student', username: email.split('@')[0] };
        }
      }

      localStorage.setItem('user', JSON.stringify(userData));
      setUser(userData);
    }
    return data;
  };

  const logout = async () => {
    await apiLogout();
    setUser(null);
    setToken(null);
  };

  const isAdmin = user?.role === 'admin' || user?.is_superuser === true;

  const value = {
    user,
    token,
    login,
    logout,
    isLoading,
    isAdmin,
    setUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export default AuthContext;
