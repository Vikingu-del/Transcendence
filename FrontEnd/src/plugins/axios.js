import axios from 'axios';
// import store from '@/store';
import router from '@/router';
// import { config } from '@/config/environment';

const axiosInstance = axios.create({
    baseURL: 'http://localhost',
    headers: {
        'Content-Type': 'application/json',
    },
    timeout: 10000
});

let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
    failedQueue.forEach(prom => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token);
        }
    });
    failedQueue = [];
};

// Request interceptor
axiosInstance.interceptors.request.use(
    config => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers['Authorization'] = `Bearer ${token}`;
        }
        return config;
    },
    error => Promise.reject(error)
);

// Response interceptor
axiosInstance.interceptors.response.use(
    response => response,
    async error => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._retry) {
            if (isRefreshing) {
                return new Promise((resolve, reject) => {
                    failedQueue.push({ resolve, reject });
                }).then(token => {
                    originalRequest.headers['Authorization'] = `Bearer ${token}`;
                    return axiosInstance(originalRequest);
                }).catch(err => Promise.reject(err));
            }

            originalRequest._retry = true;
            isRefreshing = true;

            try {
                const refreshToken = localStorage.getItem('refreshToken');
                if (!refreshToken) {
                    throw new Error('No refresh token available');
                }

                const response = await axiosInstance.post('/api/user/sync-token/', {
                    refresh: refreshToken
                });

                if (response.data?.token) {
                    const newToken = response.data.token;
                    localStorage.setItem('token', newToken);
                    axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
                    processQueue(null, newToken);
                    return axiosInstance(originalRequest);
                }
            } catch (refreshError) {
                processQueue(refreshError, null);
                localStorage.removeItem('token');
                localStorage.removeItem('refreshToken');
                router.push('/login');
                return Promise.reject(refreshError);
            } finally {
                isRefreshing = false;
            }
        }
        return Promise.reject(error);
    }
);

export default axiosInstance;