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

// Game and Match API functions
export const gameAPI = {
  // Get game state
  getGameState: (gameId: string) =>
    get(`/games/${gameId}/state`),

  // Get game day info
  getGameDayInfo: (sportGroupId: string) =>
    get(`/games/game-day/${sportGroupId}`),

  // Start match
  startMatch: (gameId: string, data: { team_a_id: string; team_b_id: string }) =>
    post(`/games/${gameId}/start-match`, data),

  // End match
  endMatch: (gameId: string) =>
    post(`/games/${gameId}/match/end`),

  // Update match score
  updateScore: (gameId: string, data: { team_id: string; action: "increment" | "decrement" | "set"; value?: number }) =>
    post(`/games/${gameId}/match/score`, data),

  // Start scheduled match
  startScheduledMatch: (gameId: string) =>
    post(`/games/${gameId}/match/start-scheduled`),

  // Timer controls
  startTimer: (gameId: string) =>
    post(`/games/${gameId}/timer/start`),

  updateTimer: (gameId: string, data: { action: string; time?: number }) =>
    post(`/games/${gameId}/timer`, data),

  getTimerStatus: (gameId: string) =>
    get(`/games/${gameId}/timer`),

  // Coin toss functions
  performCoinToss: (gameId: string, data: {
    team_a_id: string;
    team_b_id: string;
    team_a_choice: string;
    team_b_choice: string;
    coin_toss_type?: string;
  }) =>
    post(`/games/${gameId}/coin-toss`, data),

  // Get suggested teams
  getSuggestedTeams: (gameId: string) =>
    get(`/games/${gameId}/suggested-teams`),

  // Get teams for game
  getGameTeams: (gameId: string) =>
    get<{ teams: unknown[] }>(`/games/${gameId}/teams`),
};

export default api;
