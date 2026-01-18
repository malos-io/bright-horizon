import axios from 'axios'

// Use relative URL for production (nginx reverse proxy) or localhost for development
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

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

export const getCoursesByCategory = async (category) => {
  const response = await api.get(`/courses/category/${category}`)
  return response.data
}

export default api
