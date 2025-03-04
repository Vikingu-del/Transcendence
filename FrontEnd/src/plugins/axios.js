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

                console.log('Attempting to refresh token...');
                
                // Change the endpoint to match your backend
                const response = await axios.post('/api/auth/token/refresh/', {
                    refresh: refreshToken
                });

                console.log('Refresh response:', response.status);
                
                // Check for both 'token' and 'access' fields since your backend returns 'access'
                if (response.data?.access || response.data?.token) {
                    const newToken = response.data.access || response.data.token;
                    console.log('Got new token successfully');
                    
                    localStorage.setItem('token', newToken);
                    axiosInstance.defaults.headers.common['Authorization'] = `Bearer ${newToken}`;
                    
                    // Process any queued requests
                    processQueue(null, newToken);
                    
                    // Retry the original request with the new token
                    return axiosInstance(originalRequest);
                } else {
                    console.error('Invalid token refresh response format:', response.data);
                    throw new Error('Invalid token refresh response');
                }
            } catch (refreshError) {
                console.error('Token refresh failed:', refreshError);
                processQueue(refreshError, null);
                
                // Only clear tokens if refresh actually failed
                if (refreshError.response?.status === 401) {
                    localStorage.removeItem('token');
                    localStorage.removeItem('refreshToken');
                    router.push('/login');
                }
                
                return Promise.reject(refreshError);
            } finally {
                isRefreshing = false;
            }
        }
        return Promise.reject(error);
    }
);

export default axiosInstance;