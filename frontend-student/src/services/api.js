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
  const token = localStorage.getItem('student_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// On 401, clear auth and redirect to login
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('student_token')
      localStorage.removeItem('student_name')
      localStorage.removeItem('student_email')
      localStorage.removeItem('student_applications')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// ── OTP Auth ──

export const sendOtp = async (email) => {
  const response = await api.post('/otp/send', { email })
  return response.data
}

export const verifyOtp = async (email, code) => {
  const response = await api.post('/otp/verify', { email, code })
  return response.data
}

// ── Applicant Enrollment ──

export const getEnrollment = async (enrollmentId) => {
  const response = await api.get(`/applicant/enrollments/${enrollmentId}`)
  return response.data
}

export const updateEnrollment = async (enrollmentId, fields) => {
  const response = await api.patch(`/applicant/enrollments/${enrollmentId}`, fields)
  return response.data
}

// ── Applicant Documents ──

export const getDocuments = async (enrollmentId) => {
  const response = await api.get(`/applicant/enrollments/${enrollmentId}/documents`)
  return response.data
}

export const uploadDocument = async (enrollmentId, docType, file) => {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post(
    `/applicant/enrollments/${enrollmentId}/documents/${docType}`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  )
  return response.data
}

// ── My Classes ──

export const getMyClasses = async () => {
  const response = await api.get('/applicant/my-classes')
  return response.data
}

// ── Courses (public) ──

export const getCourses = async () => {
  const response = await api.get('/courses')
  return response.data
}

export default api
