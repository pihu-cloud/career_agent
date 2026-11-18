import api from './api';

export const login = async (email, password) => {
  // Try JSON login endpoint or OAuth2 form data
  const response = await api.post('/api/v1/auth/login', { email, password });
  return response.data;
};

export const register = async (userData) => {
  const response = await api.post('/api/v1/auth/register', userData);
  return response.data;
};

export const logout = async () => {
  try {
    await api.post('/api/v1/auth/logout');
  } catch (error) {
    console.error('Logout error:', error);
  } finally {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }
};

export const getMe = async () => {
  const response = await api.get('/api/v1/auth/me');
  return response.data;
};

export const changePassword = async (data) => {
  const response = await api.post('/api/v1/auth/change-password', data);
  return response.data;
};

export const forgotPassword = async (email) => {
  const response = await api.post('/api/v1/auth/forgot-password', { email });
  return response.data;
};

export const resetPassword = async (data) => {
  const response = await api.post('/api/v1/auth/reset-password', data);
  return response.data;
};

export default {
  login,
  register,
  logout,
  getMe,
  changePassword,
  forgotPassword,
  resetPassword,
};
