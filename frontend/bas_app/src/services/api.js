import axios from 'axios';

// Определяем API_URL
// Используем пустой baseURL, чтобы работали legacy роуты (/flights/...)
const API_URL = window.location.hostname === 'localhost' ? 
                'http://localhost:8000' : 
                '';

console.log('API URL:', API_URL);

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor для добавления токена
api.interceptors.request.use(
  (config) => {
    // Для FormData не устанавливаем Content-Type, браузер сделает это сам
    if (config.data instanceof FormData) {
      delete config.headers['Content-Type'];
    }
    
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Interceptor для обработки ошибок
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Перенаправление на страницу входа
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;