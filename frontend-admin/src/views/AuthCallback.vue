<template>
  <div class="callback-page">
    <div class="callback-card">
      <p v-if="error">{{ error }}</p>
      <p v-else>Signing you in...</p>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const error = ref('')

onMounted(() => {
  const params = new URLSearchParams(window.location.search)
  const token = params.get('token')
  const name = params.get('name')
  const email = params.get('email')

  if (token) {
    authStore.setAuth(token, name || '', email || '')
    router.replace('/')
  } else {
    error.value = 'Authentication failed. Please try again.'
    setTimeout(() => router.replace('/login'), 3000)
  }
})
</script>

<style scoped>
.callback-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f2f5;
}

.callback-card {
  background: white;
  border-radius: 12px;
  padding: 2rem 3rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  font-size: 1.1rem;
  color: #333;
}
</style>
