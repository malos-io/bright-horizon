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

export const createBatch = async (slug, data) => {
  const response = await api.post(`/courses/${slug}/batches`, data)
  return response.data
}

export const editBatch = async (slug, batchId, data) => {
  const response = await api.patch(`/courses/${slug}/batches/${batchId}`, data)
  return response.data
}

export const closeBatchEnrollment = async (slug, batchId) => {
  const response = await api.post(`/courses/${slug}/batches/${batchId}/close-enrollment`)
  return response.data
}

export const closeBatch = async (slug, batchId) => {
  const response = await api.post(`/courses/${slug}/batches/${batchId}/close`)
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

export const sendInterviewSchedule = async (enrollmentId) => {
  const response = await api.post(`/enrollments/${enrollmentId}/send-interview-schedule`)
  return response.data
}

export const completeEnrollment = async (enrollmentId) => {
  const response = await api.post(`/enrollments/${enrollmentId}/complete`)
  return response.data
}

export const archiveEnrollment = async (enrollmentId) => {
  const response = await api.post(`/enrollments/${enrollmentId}/archive`)
  return response.data
}

export const unarchiveEnrollment = async (enrollmentId) => {
  const response = await api.post(`/enrollments/${enrollmentId}/unarchive`)
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

export const getCoursesSummary = async () => {
  const response = await api.get('/courses-summary')
  return response.data
}

export const getCourseBatches = async (slug) => {
  const response = await api.get(`/courses/${slug}/batches`)
  return response.data
}

export const getStudents = async () => {
  const response = await api.get('/students')
  return response.data
}

export const getStudentDetail = async (id) => {
  const response = await api.get(`/students/${id}`)
  return response.data
}

export const updateStudentEmail = async (id, newEmail) => {
  const response = await api.patch(`/students/${id}/email`, { new_email: newEmail })
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

export const getEnrollment = async (id) => {
  const response = await api.get(`/enrollments/${id}`)
  return response.data
}

export const updateEnrollment = async (id, fields) => {
  const response = await api.patch(`/enrollments/${id}`, fields)
  return response.data
}

export const getDocuments = async (enrollmentId) => {
  const response = await api.get(`/enrollments/${enrollmentId}/documents`)
  return response.data
}

export const uploadDocument = async (enrollmentId, docType, file, source = 'official') => {
  const formData = new FormData()
  formData.append('file', file)
  const response = await api.post(
    `/enrollments/${enrollmentId}/documents/${docType}?source=${source}`,
    formData,
    { headers: { 'Content-Type': 'multipart/form-data' } }
  )
  return response.data
}

export const deleteDocument = async (enrollmentId, docType, source = 'official') => {
  const response = await api.delete(`/enrollments/${enrollmentId}/documents/${docType}?source=${source}`)
  return response.data
}

export const reviewDocument = async (enrollmentId, docType, status, rejectReason = null) => {
  const body = { status }
  if (rejectReason) body.reject_reason = rejectReason
  const response = await api.post(`/enrollments/${enrollmentId}/documents/${docType}/review`, body)
  return response.data
}

export const exportEnrollmentPdf = async (id) => {
  const response = await api.get(`/enrollments/${id}/pdf`, { responseType: 'blob' })
  const disposition = response.headers['content-disposition'] || ''
  const match = disposition.match(/filename="?(.+?)"?$/)
  const filename = match ? match[1] : `Tesda Registration ${id}.pdf`
  const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }))
  const link = document.createElement('a')
  link.href = url
  link.setAttribute('download', filename)
  document.body.appendChild(link)
  link.click()
  link.remove()
  window.URL.revokeObjectURL(url)
}

export default api
