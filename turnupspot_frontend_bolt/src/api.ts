import axios, { AxiosRequestConfig, AxiosResponse } from "axios";
import type { InternalAxiosRequestConfig } from "axios";
import { toast } from "react-toastify";

// Loading state management for API calls
let loadingCallbacks: {
  startLoading: () => void;
  stopLoading: () => void;
} | null = null;

export const setLoadingCallbacks = (callbacks: {
  startLoading: () => void;
  stopLoading: () => void;
}) => {
  loadingCallbacks = callbacks;
};

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers = config.headers || {};
    config.headers.Authorization = `Bearer ${token}`;
  }

  // Start loading for API requests
  if (loadingCallbacks) {
    loadingCallbacks.startLoading();
  }

  return config;
});

// Add response interceptor to handle errors
api.interceptors.response.use(
  (response) => {
    // Stop loading for successful responses
    if (loadingCallbacks) {
      loadingCallbacks.stopLoading();
    }
    return response;
  },
  (error) => {
    // Stop loading for error responses
    if (loadingCallbacks) {
      loadingCallbacks.stopLoading();
    }
    // Extract error message from response
    let errorMessage = "An unexpected error occurred";
    
    if (error.response?.data?.detail) {
      errorMessage = error.response.data.detail;
    } else if (error.response?.data?.message) {
      errorMessage = error.response.data.message;
    } else if (error.message) {
      errorMessage = error.message;
    }

    // Show toast for specific error codes
    if (error.response?.status === 401) {
      toast.error("Authentication required. Please log in again.");
    } else if (error.response?.status === 403) {
      toast.error("Permission denied.");
    } else if (error.response?.status === 404) {
      toast.error("Resource not found.");
    } else if (error.response?.status >= 500) {
      toast.error("Server error occurred. Please try again later.");
    }

    // Re-throw with the extracted message
    const enhancedError = new Error(errorMessage);
    (enhancedError as Error & { response?: unknown }).response = error.response;
    return Promise.reject(enhancedError);
  }
);

export const get = <T = unknown>(
  url: string,
  config?: AxiosRequestConfig
): Promise<AxiosResponse<T>> => api.get<T>(url, config);

export const post = <T = unknown>(
  url: string,
  data?: unknown,
  config?: AxiosRequestConfig
): Promise<AxiosResponse<T>> => api.post<T>(url, data, config);

export const put = <T = unknown>(
  url: string,
  data?: unknown,
  config?: AxiosRequestConfig
): Promise<AxiosResponse<T>> => api.put<T>(url, data, config);

export const del = <T = unknown>(
  url: string,
  config?: AxiosRequestConfig
): Promise<AxiosResponse<T>> => api.delete<T>(url, config);

export default api;
