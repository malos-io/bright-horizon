import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '../services/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('admin_token') || '')
  const userName = ref(localStorage.getItem('admin_name') || '')
  const userEmail = ref(localStorage.getItem('admin_email') || '')

  const isAuthenticated = computed(() => !!token.value)

  function setAuth(authToken, name, email) {
    token.value = authToken
    userName.value = name
    userEmail.value = email
    localStorage.setItem('admin_token', authToken)
    localStorage.setItem('admin_name', name)
    localStorage.setItem('admin_email', email)
  }

  function logout() {
    token.value = ''
    userName.value = ''
    userEmail.value = ''
    localStorage.removeItem('admin_token')
    localStorage.removeItem('admin_name')
    localStorage.removeItem('admin_email')
  }

  function redirectToZoho() {
    const clientId = import.meta.env.VITE_ZOHO_CLIENT_ID
    const redirectUri = import.meta.env.VITE_ZOHO_REDIRECT_URI
    const scope = 'ZohoMail.messages.ALL,ZohoMail.accounts.READ,ZohoMail.folders.READ,AaaServer.profile.READ'
    const url = `https://accounts.zoho.com/oauth/v2/auth?scope=${scope}&client_id=${clientId}&response_type=code&redirect_uri=${encodeURIComponent(redirectUri)}&access_type=offline&prompt=consent`
    window.location.href = url
  }

  async function refreshToken() {
    try {
      const response = await api.post('/zoho/refresh-token')
      const newToken = response.data.token
      token.value = newToken
      localStorage.setItem('admin_token', newToken)
      return newToken
    } catch {
      logout()
      return null
    }
  }

  return {
    token,
    userName,
    userEmail,
    isAuthenticated,
    setAuth,
    logout,
    redirectToZoho,
    refreshToken,
  }
})
