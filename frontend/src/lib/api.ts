import axios from 'axios';

// Use environment variable for API URL, default to relative path for same-origin deployment
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export const authApi = {
  register: (data: { email: string; password: string; full_name?: string }) =>
    api.post('/auth/register', data),
  
  login: (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);
    return api.post('/auth/login', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    });
  },
  
  getMe: () => api.get('/auth/me'),
};

export const analysisApi = {
  discoverGaps: (data: {
    field_of_study: string;
    area_of_interest: string;
    research_type: string;
    year_range_start: number;
    year_range_end: number;
    min_citations: number;
    data_source: string;
  }) => api.post('/analysis/discover', data),
  
  createProject: (data: {
    title: string;
    description?: string;
    field_of_study?: string;
    research_type?: string;
    year_range_start?: number;
    year_range_end?: number;
    min_citations?: number;
    data_source?: string;
  }) => api.post('/analysis/projects', data),
  
  getProjects: () => api.get('/analysis/projects'),
  
  getProject: (id: number) => api.get(`/analysis/projects/${id}`),
};
