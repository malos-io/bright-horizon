<template>
  <div class="track-page">
    <!-- Hero Section -->
    <section class="track-hero">
      <div class="hero-content">
        <h1>Track Your <span class="highlight">Application</span></h1>
        <p>Enter the email address you used when applying to check your application status.</p>
      </div>
    </section>

    <!-- Main Content -->
    <section class="track-section">
      <div class="track-container">

        <!-- State 1: Email Entry -->
        <div v-if="step === 'email'" class="track-card">
          <div class="card-icon">&#128233;</div>
          <h2>Enter Your Email</h2>
          <p class="card-subtitle">We'll send a verification code to confirm your identity.</p>
          <form @submit.prevent="handleSendOtp">
            <div class="form-group">
              <input
                v-model="email"
                type="email"
                placeholder="your.email@example.com"
                required
                class="form-input"
                :disabled="loading"
              />
            </div>
            <p v-if="error" class="error-message">{{ error }}</p>
            <button type="submit" class="btn btn-primary btn-full" :disabled="loading">
              {{ loading ? 'Sending...' : 'Send Verification Code' }}
            </button>
          </form>
        </div>

        <!-- State 2: OTP Entry -->
        <div v-else-if="step === 'otp'" class="track-card">
          <div class="card-icon">&#128274;</div>
          <h2>Enter Verification Code</h2>
          <p class="card-subtitle">We sent a 6-digit code to <strong>{{ maskedEmail }}</strong></p>
          <form @submit.prevent="handleVerifyOtp">
            <div class="otp-inputs">
              <input
                v-for="(digit, index) in otpDigits"
                :key="index"
                :ref="el => otpRefs[index] = el"
                v-model="otpDigits[index]"
                type="text"
                maxlength="1"
                inputmode="numeric"
                class="otp-input"
                :disabled="loading"
                @input="handleOtpInput(index)"
                @keydown.backspace="handleOtpBackspace(index, $event)"
                @paste="handleOtpPaste($event)"
              />
            </div>
            <p v-if="error" class="error-message">{{ error }}</p>
            <button type="submit" class="btn btn-primary btn-full" :disabled="loading || otpCode.length < 6">
              {{ loading ? 'Verifying...' : 'Verify Code' }}
            </button>
          </form>
          <div class="otp-footer">
            <button
              class="btn-link"
              :disabled="resendCooldown > 0"
              @click="handleSendOtp"
            >
              {{ resendCooldown > 0 ? `Resend code in ${resendCooldown}s` : 'Resend Code' }}
            </button>
            <button class="btn-link" @click="step = 'email'">Change Email</button>
          </div>
        </div>

        <!-- State 3: Application Status -->
        <div v-else-if="step === 'status'" class="track-card status-card">
          <div class="card-icon">&#9989;</div>
          <h2>Your Application{{ applications.length > 1 ? 's' : '' }}</h2>

          <div v-for="app in applications" :key="app.id" class="application-item">
            <div class="app-header">
              <h3>{{ app.firstName }} {{ app.middleName ? app.middleName + ' ' : '' }}{{ app.lastName }}</h3>
              <span class="status-badge" :class="'status-' + app.status">{{ formatStatus(app.status) }}</span>
            </div>
            <div class="app-details">
              <div class="detail-row">
                <span class="detail-label">Reference ID</span>
                <span class="detail-value">{{ app.id }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Course</span>
                <span class="detail-value">{{ app.course }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Date Applied</span>
                <span class="detail-value">{{ formatDate(app.created_at) }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Email</span>
                <span class="detail-value">{{ app.email }}</span>
              </div>
            </div>
          </div>

          <router-link to="/" class="btn btn-outline btn-full" style="margin-top: 20px;">Back to Home</router-link>
        </div>

      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { sendOtp, verifyOtp } from '@/services/api'

const step = ref('email')
const email = ref('')
const otpDigits = ref(['', '', '', '', '', ''])
const otpRefs = ref([])
const loading = ref(false)
const error = ref('')
const applications = ref([])
const resendCooldown = ref(0)

const otpCode = computed(() => otpDigits.value.join(''))

const maskedEmail = computed(() => {
  if (!email.value) return ''
  const [local, domain] = email.value.split('@')
  if (local.length <= 2) return email.value
  return local[0] + '***' + local[local.length - 1] + '@' + domain
})

const handleOtpInput = (index) => {
  const val = otpDigits.value[index]
  if (val && !/^\d$/.test(val)) {
    otpDigits.value[index] = ''
    return
  }
  if (val && index < 5) {
    otpRefs.value[index + 1]?.focus()
  }
}

const handleOtpBackspace = (index, event) => {
  if (!otpDigits.value[index] && index > 0) {
    event.preventDefault()
    otpDigits.value[index - 1] = ''
    otpRefs.value[index - 1]?.focus()
  }
}

const handleOtpPaste = (event) => {
  event.preventDefault()
  const pasted = event.clipboardData.getData('text').replace(/\D/g, '').slice(0, 6)
  for (let i = 0; i < 6; i++) {
    otpDigits.value[i] = pasted[i] || ''
  }
  const focusIndex = Math.min(pasted.length, 5)
  otpRefs.value[focusIndex]?.focus()
}

const startCooldown = () => {
  resendCooldown.value = 60
  const interval = setInterval(() => {
    resendCooldown.value--
    if (resendCooldown.value <= 0) clearInterval(interval)
  }, 1000)
}

const handleSendOtp = async () => {
  error.value = ''
  loading.value = true
  try {
    await sendOtp(email.value)
    step.value = 'otp'
    otpDigits.value = ['', '', '', '', '', '']
    startCooldown()
  } catch (e) {
    error.value = e.response?.data?.detail || 'Failed to send verification code.'
  } finally {
    loading.value = false
  }
}

const handleVerifyOtp = async () => {
  error.value = ''
  loading.value = true
  try {
    const data = await verifyOtp(email.value, otpCode.value)
    applications.value = data.applications
    step.value = 'status'
  } catch (e) {
    error.value = e.response?.data?.detail || 'Verification failed.'
  } finally {
    loading.value = false
  }
}

const formatStatus = (status) => {
  const map = {
    pending: 'Pending',
    under_review: 'Under Review',
    approved: 'Approved',
    rejected: 'Rejected',
    enrolled: 'Enrolled',
  }
  return map[status] || status
}

const formatDate = (dateStr) => {
  if (!dateStr) return 'N/A'
  const date = new Date(dateStr)
  return date.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' })
}
</script>

<style scoped>
.track-page {
  min-height: 100vh;
  background: #f4f6f9;
}

.track-hero {
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  padding: 80px 20px;
  text-align: center;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
  color: white;
}

.track-hero h1 {
  font-size: 48px;
  font-weight: 800;
  margin-bottom: 20px;
}

.highlight {
  background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.track-hero p {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.8);
  line-height: 1.7;
}

.track-section {
  padding: 0 20px;
  margin-top: -40px;
  position: relative;
  z-index: 1;
  padding-bottom: 60px;
}

.track-container {
  max-width: 500px;
  margin: 0 auto;
}

.track-card {
  background: #fff;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.card-icon {
  font-size: 48px;
  margin-bottom: 15px;
}

.track-card h2 {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 8px;
}

.card-subtitle {
  color: #666;
  font-size: 15px;
  margin: 0 0 25px;
  line-height: 1.5;
}

.form-group {
  margin-bottom: 16px;
}

.form-input {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  font-size: 16px;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #1a5fa4;
}

.otp-inputs {
  display: flex;
  gap: 10px;
  justify-content: center;
  margin-bottom: 20px;
}

.otp-input {
  width: 50px;
  height: 58px;
  border: 2px solid #e0e0e0;
  border-radius: 10px;
  text-align: center;
  font-size: 24px;
  font-weight: 700;
  color: #0d3b6e;
  transition: border-color 0.3s;
}

.otp-input:focus {
  outline: none;
  border-color: #1a5fa4;
  box-shadow: 0 0 0 3px rgba(26, 95, 164, 0.1);
}

.error-message {
  color: #e74c3c;
  font-size: 14px;
  margin: 0 0 16px;
}

.btn {
  padding: 14px 24px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
  font-size: 16px;
  text-decoration: none;
  display: inline-block;
  text-align: center;
}

.btn-primary {
  background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(26, 95, 164, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-outline {
  background: transparent;
  border: 2px solid #1a5fa4;
  color: #1a5fa4;
}

.btn-outline:hover {
  background: #1a5fa4;
  color: white;
}

.btn-full {
  width: 100%;
}

.btn-link {
  background: none;
  border: none;
  color: #1a5fa4;
  font-size: 14px;
  cursor: pointer;
  text-decoration: underline;
  padding: 0;
}

.btn-link:disabled {
  color: #999;
  cursor: not-allowed;
  text-decoration: none;
}

.otp-footer {
  display: flex;
  justify-content: space-between;
  margin-top: 20px;
}

/* Status Card */
.status-card {
  text-align: left;
  max-width: 600px;
}

.status-card .card-icon {
  text-align: center;
}

.status-card h2 {
  text-align: center;
  margin-bottom: 25px;
}

.application-item {
  background: #f8f9fb;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 16px;
  border: 1px solid #eee;
}

.app-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.app-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0;
}

.status-badge {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  white-space: nowrap;
}

.status-pending {
  background: #fff3e0;
  color: #e65100;
}

.status-under_review {
  background: #e3f2fd;
  color: #1565c0;
}

.status-approved {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-rejected {
  background: #ffebee;
  color: #c62828;
}

.status-enrolled {
  background: #e8f5e9;
  color: #1b5e20;
}

.app-details {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.detail-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.detail-label {
  font-size: 14px;
  color: #888;
  font-weight: 500;
}

.detail-value {
  font-size: 14px;
  color: #1a1a2e;
  font-weight: 500;
  text-align: right;
  max-width: 60%;
  word-break: break-all;
}

@media (max-width: 768px) {
  .track-hero h1 {
    font-size: 36px;
  }

  .track-card {
    padding: 30px 20px;
  }

  .otp-input {
    width: 42px;
    height: 50px;
    font-size: 20px;
  }

  .otp-inputs {
    gap: 6px;
  }

  .app-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .detail-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 2px;
  }

  .detail-value {
    text-align: left;
    max-width: 100%;
  }
}
</style>
