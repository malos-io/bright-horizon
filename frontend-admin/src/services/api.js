import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Attach Bearer token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// On each successful response, refresh the JWT (sliding window)
api.interceptors.response.use(
  async (response) => {
    const token = localStorage.getItem('admin_token')
    // Only refresh on non-auth endpoints to avoid infinite loop
    if (token && !response.config.url.includes('/zoho/')) {
      try {
        const refreshRes = await api.post('/zoho/refresh-token')
        const newToken = refreshRes.data.token
        localStorage.setItem('admin_token', newToken)
      } catch {
        // Refresh failed — token might be expired, let the 401 handler deal with it
      }
    }
    return response
  },
  (error) => {
    // If 401, clear auth and redirect to login
    if (error.response?.status === 401) {
      localStorage.removeItem('admin_token')
      localStorage.removeItem('admin_name')
      localStorage.removeItem('admin_email')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export const getCourses = async () => {
  const response = await api.get('/courses')
  return response.data
}

export const getCourse = async (slug) => {
  const response = await api.get(`/courses/${slug}`)
  return response.data
}

export const getCategories = async () => {
  const response = await api.get('/categories')
  return response.data
}

export const getEnrollments = async () => {
  const response = await api.get('/enrollments')
  return response.data
}

export const getInbox = async (limit = 20, start = 1) => {
  const response = await api.get('/email/inbox', { params: { limit, start } })
  return response.data
}

export const getMessage = async (folderId, messageId) => {
  const response = await api.get(`/email/messages/${folderId}/${messageId}`)
  return response.data
}

export const getStaff = async () => {
  const response = await api.get('/staff')
  return response.data
}

export const addStaff = async (email, role) => {
  const response = await api.post('/staff', { email, role })
  return response.data
}

export const updateStaffRole = async (email, role) => {
  const response = await api.put(`/staff/${encodeURIComponent(email)}`, { role })
  return response.data
}

export const removeStaff = async (email) => {
  const response = await api.delete(`/staff/${encodeURIComponent(email)}`)
  return response.data
}

export default api
