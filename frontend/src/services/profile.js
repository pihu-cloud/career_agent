import api from './api';

export const getProfile = async () => {
  const response = await api.get('/api/v1/profile');
  return response.data;
};

export const updateProfile = async (data) => {
  const response = await api.put('/api/v1/profile', data);
  return response.data;
};

export const getSkills = async () => {
  const response = await api.get('/api/v1/profile/skills');
  return response.data;
};

export const addSkills = async (skills) => {
  const response = await api.post('/api/v1/profile/skills', skills);
  return response.data;
};

export const updateSkill = async (id, data) => {
  const response = await api.put(`/api/v1/profile/skills/${id}`, data);
  return response.data;
};

export const deleteSkill = async (id) => {
  const response = await api.delete(`/api/v1/profile/skills/${id}`);
  return response.data;
};

export const getInterests = async () => {
  const response = await api.get('/api/v1/profile/interests');
  return response.data;
};

export const addInterests = async (interests) => {
  const response = await api.post('/api/v1/profile/interests', interests);
  return response.data;
};

export const deleteInterest = async (id) => {
  const response = await api.delete(`/api/v1/profile/interests/${id}`);
  return response.data;
};

export const getPersonality = async () => {
  const response = await api.get('/api/v1/profile/personality');
  return response.data;
};

export const addPersonality = async (traits) => {
  const response = await api.post('/api/v1/profile/personality', traits);
  return response.data;
};

export const getAcademics = async () => {
  const response = await api.get('/api/v1/profile/academics');
  return response.data;
};

export const addAcademic = async (data) => {
  const response = await api.post('/api/v1/profile/academics', data);
  return response.data;
};

export const updateAcademic = async (id, data) => {
  const response = await api.put(`/api/v1/profile/academics/${id}`, data);
  return response.data;
};

export const deleteAcademic = async (id) => {
  const response = await api.delete(`/api/v1/profile/academics/${id}`);
  return response.data;
};

export const getProfileCompletion = async () => {
  const response = await api.get('/api/v1/profile/completion');
  return response.data;
};

export default {
  getProfile,
  updateProfile,
  getSkills,
  addSkills,
  updateSkill,
  deleteSkill,
  getInterests,
  addInterests,
  deleteInterest,
  getPersonality,
  addPersonality,
  getAcademics,
  addAcademic,
  updateAcademic,
  deleteAcademic,
  getProfileCompletion,
};
