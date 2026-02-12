import { reactive, computed } from 'vue'

const STORAGE_KEYS = {
  token: 'student_token',
  name: 'student_name',
  email: 'student_email',
  applications: 'student_applications',
}

const state = reactive({
  token: localStorage.getItem(STORAGE_KEYS.token) || '',
  name: localStorage.getItem(STORAGE_KEYS.name) || '',
  email: localStorage.getItem(STORAGE_KEYS.email) || '',
  applications: JSON.parse(localStorage.getItem(STORAGE_KEYS.applications) || '[]'),
})

export function useAuth() {
  const isAuthenticated = computed(() => !!state.token)

  function setAuth(token, name, email, applications) {
    state.token = token
    state.name = name
    state.email = email
    state.applications = applications || []
    localStorage.setItem(STORAGE_KEYS.token, token)
    localStorage.setItem(STORAGE_KEYS.name, name)
    localStorage.setItem(STORAGE_KEYS.email, email)
    localStorage.setItem(STORAGE_KEYS.applications, JSON.stringify(state.applications))
  }

  function logout() {
    state.token = ''
    state.name = ''
    state.email = ''
    state.applications = []
    Object.values(STORAGE_KEYS).forEach(k => localStorage.removeItem(k))
  }

  return { state, isAuthenticated, setAuth, logout }
}
