<template>
  <div class="login-page">
    <div class="login-card">
      <img :src="logo" alt="Bright Horizons Institute" class="login-logo" />
      <h1>Admin Portal</h1>
      <p>Sign in with your organization account to continue.</p>
      <button class="login-btn" @click="authStore.redirectToZoho()">
        Sign in with Zoho
      </button>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
import logo from '../assets/logo.png'

const authStore = useAuthStore()
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1a5fa4 0%, #e8872a 100%);
}

.login-card {
  background: white;
  border-radius: 12px;
  padding: 3rem 2.5rem;
  text-align: center;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.15);
  max-width: 400px;
  width: 100%;
}

.login-logo {
  width: 80px;
  height: 80px;
  object-fit: contain;
  margin-bottom: 1.5rem;
}

.login-card h1 {
  font-size: 1.5rem;
  color: #1a1a2e;
  margin-bottom: 0.5rem;
}

.login-card p {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 2rem;
}

.login-btn {
  width: 100%;
  padding: 0.85rem 1.5rem;
  background: #1a5fa4;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.login-btn:hover {
  background: #154d87;
}
</style>
