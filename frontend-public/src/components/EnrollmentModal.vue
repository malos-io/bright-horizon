<template>
  <Teleport to="body">
    <div v-if="isOpen" class="modal-overlay" @click.self="handleClose">
      <div class="modal-content">
        <div class="modal-header">
          <h2>Apply for Class Now</h2>
          <button class="close-btn" @click="handleClose">&times;</button>
        </div>

        <div v-if="submitted" class="success-state">
          <div class="success-icon">&#10003;</div>
          <h3>Enrollment Submitted!</h3>
          <p>We'll get back to you shortly.</p>
        </div>

        <form v-else @submit.prevent="handleSubmit">
          <div class="form-group">
            <label for="fullName">Full Name <span class="required">*</span></label>
            <input
              id="fullName"
              v-model="form.fullName"
              type="text"
              placeholder="Juan Dela Cruz"
            />
            <span v-if="errors.fullName" class="error">{{ errors.fullName }}</span>
          </div>

          <div class="form-group">
            <label for="email">Email <span class="required">*</span></label>
            <input
              id="email"
              v-model="form.email"
              type="email"
              placeholder="juan@email.com"
            />
            <span v-if="errors.email" class="error">{{ errors.email }}</span>
          </div>

          <div class="form-group">
            <label for="phone">Phone Number <span class="required">*</span></label>
            <input
              id="phone"
              v-model="form.phone"
              type="tel"
              placeholder="09XX XXX XXXX"
            />
            <span v-if="errors.phone" class="error">{{ errors.phone }}</span>
          </div>

          <div class="form-group">
            <label for="course">Course of Interest <span class="required">*</span></label>
            <select id="course" v-model="form.course">
              <option value="" disabled>Select a course</option>
              <option v-for="c in courses" :key="c.id" :value="c.title">
                {{ c.title }}
              </option>
            </select>
            <span v-if="errors.course" class="error">{{ errors.course }}</span>
          </div>

          <div class="form-group">
            <label for="message">Message (optional)</label>
            <textarea
              id="message"
              v-model="form.message"
              rows="3"
              placeholder="Any questions or special requests..."
            ></textarea>
          </div>

          <p v-if="submitError" class="error submit-error">{{ submitError }}</p>

          <button type="submit" class="btn-submit" :disabled="submitting">
            {{ submitting ? 'Submitting...' : 'Submit Enrollment' }}
          </button>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { ref, reactive, watch, onMounted, onUnmounted } from 'vue'
import { useEnrollmentModal } from '../composables/useEnrollmentModal'
import { getCourses, submitEnrollment } from '../services/api'

const { isOpen, prefilledCourse, close } = useEnrollmentModal()

const courses = ref([])
const submitted = ref(false)
const submitting = ref(false)
const submitError = ref('')

const form = reactive({
  fullName: '',
  email: '',
  phone: '',
  course: '',
  message: ''
})

const errors = reactive({
  fullName: '',
  email: '',
  phone: '',
  course: ''
})

onMounted(async () => {
  try {
    courses.value = await getCourses()
  } catch (e) {
    console.error('Failed to load courses:', e)
  }
})

watch(prefilledCourse, (val) => {
  if (val) form.course = val
})

watch(isOpen, (val) => {
  document.body.style.overflow = val ? 'hidden' : ''
  if (val) submitted.value = false
})

function onKeydown(e) {
  if (e.key === 'Escape' && isOpen.value) handleClose()
}
onMounted(() => document.addEventListener('keydown', onKeydown))
onUnmounted(() => document.removeEventListener('keydown', onKeydown))

function resetForm() {
  Object.assign(form, { fullName: '', email: '', phone: '', course: '', message: '' })
  Object.keys(errors).forEach(k => errors[k] = '')
}

function validate() {
  let valid = true
  Object.keys(errors).forEach(k => errors[k] = '')

  if (!form.fullName.trim()) { errors.fullName = 'Full name is required'; valid = false }
  if (!form.email.trim()) {
    errors.email = 'Email is required'; valid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(form.email)) {
    errors.email = 'Enter a valid email'; valid = false
  }
  if (!form.phone.trim()) { errors.phone = 'Phone number is required'; valid = false }
  if (!form.course) { errors.course = 'Please select a course'; valid = false }

  return valid
}

async function handleSubmit() {
  if (!validate()) return

  submitting.value = true
  submitError.value = ''

  try {
    await submitEnrollment({ ...form })
    submitted.value = true
    resetForm()

    setTimeout(() => {
      close()
      submitted.value = false
    }, 2000)
  } catch (e) {
    submitError.value = 'Failed to submit. Please try again.'
    console.error('Enrollment submission error:', e)
  } finally {
    submitting.value = false
  }
}

function handleClose() {
  close()
  submitted.value = false
  resetForm()
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
}

.modal-content {
  background: white;
  border-radius: 16px;
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 30px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 25px;
}

.modal-header h2 {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  font-size: 28px;
  color: #999;
  cursor: pointer;
  padding: 0;
  line-height: 1;
  transition: color 0.3s;
}

.close-btn:hover {
  color: #333;
}

.success-state {
  text-align: center;
  padding: 40px 20px;
}

.success-icon {
  width: 60px;
  height: 60px;
  background: linear-gradient(135deg, #1a5fa4 0%, #e8872a 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 28px;
  margin: 0 auto 20px;
}

.success-state h3 {
  font-size: 22px;
  color: #1a1a2e;
  margin-bottom: 8px;
}

.success-state p {
  color: #666;
  font-size: 16px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-size: 14px;
  font-weight: 600;
  color: #1a1a2e;
  margin-bottom: 6px;
}

.required {
  color: #ff6b6b;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 15px;
  color: #333;
  transition: border-color 0.3s;
  font-family: inherit;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #1a5fa4;
  box-shadow: 0 0 0 3px rgba(26, 95, 164, 0.1);
}

.form-group select {
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23666' d='M6 8L1 3h10z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 14px center;
  padding-right: 36px;
}

.form-group textarea {
  resize: vertical;
}

.error {
  display: block;
  color: #ff6b6b;
  font-size: 12px;
  margin-top: 4px;
}

.btn-submit {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #1a5fa4 0%, #e8872a 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-submit:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(26, 95, 164, 0.4);
}

.btn-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.submit-error {
  text-align: center;
  font-size: 14px;
  margin-bottom: 12px;
}

@media (max-width: 480px) {
  .modal-content {
    padding: 20px;
  }

  .modal-header h2 {
    font-size: 20px;
  }
}
</style>
