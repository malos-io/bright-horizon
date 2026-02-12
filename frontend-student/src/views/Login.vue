<template>
  <div class="login-page">
    <div class="login-card">
      <img :src="logo" alt="Bright Horizon Institute" class="login-logo" />
      <h1>Student Portal</h1>
      <p class="login-tagline">Bright Horizon Institute Inc.</p>

      <!-- Step 1: Email -->
      <template v-if="step === 'email'">
        <p class="login-subtitle">Enter your email address to sign in.</p>
        <form @submit.prevent="handleSendOtp">
          <div class="form-group">
            <label for="email">Email Address</label>
            <input
              id="email"
              v-model="email"
              type="email"
              placeholder="your.email@example.com"
              required
              :disabled="sending"
              autocomplete="email"
            />
          </div>
          <div v-if="error" class="error-msg">{{ error }}</div>
          <button type="submit" class="login-btn" :disabled="sending || !email.trim()">
            {{ sending ? 'Sending...' : 'Send Verification Code' }}
          </button>
        </form>
      </template>

      <!-- Step 2: OTP Verification -->
      <template v-else>
        <p class="login-subtitle">
          We sent a 6-digit code to <strong>{{ email }}</strong>
        </p>
        <form @submit.prevent="handleVerifyOtp">
          <div class="form-group">
            <label for="otp">Verification Code</label>
            <input
              id="otp"
              ref="otpInput"
              v-model="otpCode"
              type="text"
              inputmode="numeric"
              pattern="[0-9]*"
              maxlength="6"
              placeholder="000000"
              required
              :disabled="verifying"
              autocomplete="one-time-code"
              class="otp-input"
            />
          </div>
          <div v-if="error" class="error-msg">{{ error }}</div>
          <button type="submit" class="login-btn" :disabled="verifying || otpCode.length !== 6">
            {{ verifying ? 'Verifying...' : 'Verify & Sign In' }}
          </button>
        </form>
        <div class="link-row">
          <button class="link-btn" @click="resetToEmail" :disabled="verifying">
            Use a different email
          </button>
          <button class="link-btn" @click="handleResendOtp" :disabled="sending || resendCooldown > 0">
            {{ resendCooldown > 0 ? `Resend code in ${resendCooldown}s` : 'Resend code' }}
          </button>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '../composables/useAuth'
import { sendOtp, verifyOtp } from '../services/api'
import logo from '../assets/logo.png'

const router = useRouter()
const auth = useAuth()

const step = ref('email')
const email = ref('')
const otpCode = ref('')
const otpInput = ref(null)
const error = ref('')
const sending = ref(false)
const verifying = ref(false)
const resendCooldown = ref(0)
let cooldownInterval = null

function startCooldown() {
  resendCooldown.value = 60
  if (cooldownInterval) clearInterval(cooldownInterval)
  cooldownInterval = setInterval(() => {
    resendCooldown.value--
    if (resendCooldown.value <= 0) clearInterval(cooldownInterval)
  }, 1000)
}

async function handleSendOtp() {
  error.value = ''
  sending.value = true
  try {
    await sendOtp(email.value.trim().toLowerCase())
    step.value = 'verify'
    startCooldown()
    await nextTick()
    otpInput.value?.focus()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to send verification code. Please try again.'
  } finally {
    sending.value = false
  }
}

async function handleResendOtp() {
  error.value = ''
  sending.value = true
  try {
    await sendOtp(email.value.trim().toLowerCase())
    startCooldown()
    error.value = ''
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to resend code.'
  } finally {
    sending.value = false
  }
}

async function handleVerifyOtp() {
  error.value = ''
  verifying.value = true
  try {
    const data = await verifyOtp(email.value.trim().toLowerCase(), otpCode.value.trim())
    if (data.role !== 'student') {
      error.value = 'Your account has not been activated yet. Please wait for your enrollment to be completed.'
      return
    }
    const name = data.applications?.[0]?.firstName || ''
    const apps = (data.applications || []).map(a => ({
      id: a.id,
      course: a.course,
      status: a.status,
      firstName: a.firstName,
      lastName: a.lastName,
      created_at: a.created_at,
    }))
    auth.setAuth(data.token, name, email.value.trim().toLowerCase(), apps)
    router.push('/')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Verification failed. Please check your code and try again.'
  } finally {
    verifying.value = false
  }
}

function resetToEmail() {
  step.value = 'email'
  otpCode.value = ''
  error.value = ''
}

onUnmounted(() => {
  if (cooldownInterval) clearInterval(cooldownInterval)
})
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 50%, #2d7da8 100%);
  padding: 2rem;
}

.login-card {
  background: white;
  border-radius: 16px;
  padding: 2.5rem;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  text-align: center;
}

.login-logo {
  width: 80px;
  height: 80px;
  object-fit: contain;
  margin-bottom: 1rem;
}

.login-card h1 {
  font-size: 1.5rem;
  color: #1a1a2e;
  margin-bottom: 0.25rem;
}

.login-tagline {
  font-size: 0.8rem;
  color: #999;
  margin-bottom: 1.5rem;
}

.login-subtitle {
  font-size: 0.9rem;
  color: #666;
  margin-bottom: 1.5rem;
  line-height: 1.4;
}

.login-subtitle strong {
  color: #1a5fa4;
}

.form-group {
  text-align: left;
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.8rem;
  font-weight: 600;
  color: #444;
  margin-bottom: 0.4rem;
}

.form-group input {
  width: 100%;
  padding: 0.75rem;
  font-size: 0.95rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  outline: none;
  transition: border-color 0.2s;
}

.form-group input:focus {
  border-color: #1a5fa4;
}

.otp-input {
  text-align: center;
  font-size: 1.75rem !important;
  font-weight: 700;
  letter-spacing: 0.5rem;
  font-family: 'Courier New', monospace;
}

.error-msg {
  background: #fef2f2;
  color: #dc2626;
  font-size: 0.82rem;
  padding: 0.6rem 0.75rem;
  border-radius: 6px;
  margin-bottom: 1rem;
  text-align: left;
}

.login-btn {
  width: 100%;
  padding: 0.75rem;
  font-size: 0.95rem;
  font-weight: 700;
  color: white;
  background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 100%);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.2s;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 15px rgba(26, 95, 164, 0.4);
}

.login-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.link-row {
  display: flex;
  justify-content: space-between;
  margin-top: 1rem;
}

.link-btn {
  background: none;
  border: none;
  color: #1a5fa4;
  font-size: 0.82rem;
  cursor: pointer;
  padding: 0.4rem;
}

.link-btn:hover:not(:disabled) {
  text-decoration: underline;
}

.link-btn:disabled {
  color: #999;
  cursor: not-allowed;
}

@media (max-width: 480px) {
  .login-card {
    padding: 1.5rem;
  }
  .link-row {
    flex-direction: column;
    gap: 0.25rem;
  }
}
</style>
