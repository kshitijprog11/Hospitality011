import axios from 'axios'

// Create axios instance with base configuration
const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Request interceptor for adding auth tokens if needed
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('authToken')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Response interceptor for handling errors globally
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle unauthorized access
      localStorage.removeItem('authToken')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// Feedback API functions
export const feedbackAPI = {
  // Create new feedback
  create: (data) => api.post('/feedback/', data),
  
  // Get feedback list with filters
  getList: (params = {}) => api.get('/feedback/', { params }),
  
  // Get feedback by ID
  getById: (id) => api.get(`/feedback/${id}`),
  
  // Update feedback
  update: (id, data) => api.patch(`/feedback/${id}`, data),
  
  // Get analytics
  getAnalytics: (params = {}) => api.get('/feedback/analytics/summary', { params }),
  
  // Get flagged feedback for alerts
  getFlagged: (limit = 10) => api.get('/feedback/alerts/flagged', { params: { limit } }),
}

// Health check API
export const healthAPI = {
  check: () => api.get('/health'),
  feedbackHealth: () => api.get('/feedback/health'),
}

// Utility functions for handling API responses
export const handleApiError = (error) => {
  if (error.response) {
    // Server responded with error status
    const message = error.response.data?.detail || error.response.data?.message || 'An error occurred'
    return {
      message,
      status: error.response.status,
      data: error.response.data,
    }
  } else if (error.request) {
    // Request was made but no response received
    return {
      message: 'Network error - please check your connection',
      status: 0,
      data: null,
    }
  } else {
    // Something else happened
    return {
      message: error.message || 'An unexpected error occurred',
      status: 0,
      data: null,
    }
  }
}

// Format query parameters for API calls
export const formatQueryParams = (filters) => {
  const params = {}
  
  Object.keys(filters).forEach(key => {
    const value = filters[key]
    if (value !== null && value !== undefined && value !== '') {
      if (value instanceof Date) {
        params[key] = value.toISOString()
      } else {
        params[key] = value
      }
    }
  })
  
  return params
}

export default api