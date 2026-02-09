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

export const getSponsors = async () => {
  const response = await api.get('/sponsors')
  return response.data
}

export const submitEnrollment = async (data) => {
  const response = await api.post('/enrollments', data)
  return response.data
}

export const sendOtp = async (email) => {
  const response = await api.post('/otp/send', { email })
  return response.data
}

export const verifyOtp = async (email, code) => {
  const response = await api.post('/otp/verify', { email, code })
  if (response.data.token) {
    setApplicantToken(response.data.token)
  }
  return response.data
}

// ── Applicant token management ──

let applicantToken = null

export const setApplicantToken = (token) => {
  applicantToken = token
}

export const clearApplicantToken = () => {
  applicantToken = null
}

const authHeaders = () =>
  applicantToken ? { Authorization: `Bearer ${applicantToken}` } : {}

// ── Applicant authenticated endpoints ──

export const getApplicantEnrollment = async (enrollmentId) => {
  const response = await api.get(`/applicant/enrollments/${enrollmentId}`, {
    headers: authHeaders(),
  })
  return response.data
}

export const getApplicantDocuments = async (enrollmentId) => {
  const response = await api.get(`/applicant/enrollments/${enrollmentId}/documents`, {
    headers: authHeaders(),
  })
  return response.data
}

export const updateApplicantEnrollment = async (enrollmentId, fields) => {
  const response = await api.patch(`/applicant/enrollments/${enrollmentId}`, fields, {
    headers: authHeaders(),
  })
  return response.data
}

export const uploadApplicantDocument = async (enrollmentId, docType, file) => {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post(
    `/applicant/enrollments/${enrollmentId}/documents/${docType}`,
    formData,
    {
      headers: {
        ...authHeaders(),
        'Content-Type': 'multipart/form-data',
      },
    }
  )
  return response.data
}

export default api
