import api from './api';

export const uploadResume = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await api.post('/api/v1/resume/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getResumes = async () => {
  const response = await api.get('/api/v1/resume');
  return response.data;
};

export const downloadResume = async (id) => {
  const response = await api.get(`/api/v1/resume/${id}/download`, {
    responseType: 'blob',
  });
  return response.data;
};

export const deleteResume = async (id) => {
  const response = await api.delete(`/api/v1/resume/${id}`);
  return response.data;
};

export default {
  uploadResume,
  getResumes,
  downloadResume,
  deleteResume,
};
