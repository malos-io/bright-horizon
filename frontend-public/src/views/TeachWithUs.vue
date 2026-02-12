<template>
  <div class="teach-page">
    <!-- Hero Banner -->
    <section class="teach-hero">
      <div class="teach-hero-content">
        <h1>Are you a <span class="highlight">TESDA-certified</span> instructor?</h1>
        <p>Join our team of expert trainers and help shape the future of skilled Filipino workers.</p>
      </div>
    </section>

    <!-- Form Section -->
    <section class="form-section">
      <div class="form-container" v-if="!submitted">
        <h2>Apply to Teach</h2>
        <p class="form-subtitle">Tell us about yourself and the courses you're interested in teaching.</p>

        <form @submit.prevent="handleSubmit">
          <div class="form-grid">
            <div class="form-group">
              <label>First Name <span class="required">*</span></label>
              <input type="text" v-model="form.firstName" required placeholder="Enter your first name" />
            </div>
            <div class="form-group">
              <label>Last Name <span class="required">*</span></label>
              <input type="text" v-model="form.lastName" required placeholder="Enter your last name" />
            </div>
          </div>

          <div class="form-grid">
            <div class="form-group">
              <label>Email Address <span class="required">*</span></label>
              <input type="email" v-model="form.email" required placeholder="your@email.com" />
            </div>
            <div class="form-group">
              <label>Contact Number <span class="required">*</span></label>
              <input type="tel" v-model="form.contactNo" required placeholder="09XX-XXX-XXXX" />
            </div>
          </div>

          <!-- Course Selection -->
          <div class="form-group">
            <label>Courses Interested to Teach <span class="required">*</span></label>
            <p class="field-hint">Select all courses you are qualified to teach.</p>
            <div class="checkbox-grid">
              <label class="checkbox-label" v-for="course in availableCourses" :key="course.id">
                <input type="checkbox" :value="course.title" v-model="form.coursesInterested" />
                <span class="checkbox-text">{{ course.title }}</span>
              </label>
              <label class="checkbox-label">
                <input type="checkbox" v-model="showOther" />
                <span class="checkbox-text">Other</span>
              </label>
            </div>
          </div>

          <!-- Other Courses -->
          <div class="form-group" v-if="showOther">
            <label>Other Courses</label>
            <p class="field-hint">List any additional courses you can teach (separate with commas).</p>
            <textarea v-model="form.otherCourses" rows="3" placeholder="e.g., Welding NC II, Automotive Servicing NC II"></textarea>
          </div>

          <button type="submit" class="btn btn-primary btn-submit" :disabled="submitting || !isValid">
            {{ submitting ? 'Submitting...' : 'Submit Application' }}
          </button>
        </form>
      </div>

      <!-- Success State -->
      <div class="success-container" v-else>
        <div class="success-icon">&#10003;</div>
        <h2>Application Submitted!</h2>
        <p>Thank you for your interest in teaching at Bright Horizon Institute. Our admissions team will review your application and get in touch with you soon.</p>
        <div class="success-actions">
          <router-link to="/" class="btn btn-primary">Back to Home</router-link>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { getCourses, submitInstructorApplication } from '../services/api'

const courses = ref([])
const submitted = ref(false)
const submitting = ref(false)
const showOther = ref(false)

const form = ref({
  firstName: '',
  lastName: '',
  email: '',
  contactNo: '',
  coursesInterested: [],
  otherCourses: '',
})

const availableCourses = computed(() => courses.value)

const isValid = computed(() => {
  return (
    form.value.firstName.trim() &&
    form.value.lastName.trim() &&
    form.value.email.trim() &&
    form.value.contactNo.trim() &&
    (form.value.coursesInterested.length > 0 || (showOther.value && form.value.otherCourses.trim()))
  )
})

onMounted(async () => {
  try {
    courses.value = await getCourses()
  } catch (error) {
    console.error('Error fetching courses:', error)
  }
})

async function handleSubmit() {
  if (!isValid.value) return
  submitting.value = true
  try {
    await submitInstructorApplication({
      firstName: form.value.firstName,
      lastName: form.value.lastName,
      email: form.value.email,
      contactNo: form.value.contactNo,
      coursesInterested: form.value.coursesInterested,
      otherCourses: showOther.value ? form.value.otherCourses : '',
    })
    submitted.value = true
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } catch (e) {
    alert('Failed to submit application. Please try again.')
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.teach-page {
  background: linear-gradient(180deg, #f8f9ff 0%, #ffffff 50%, #f0f4ff 100%);
  min-height: 100vh;
}

.teach-hero {
  background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 100%);
  padding: 80px 20px;
  text-align: center;
}

.teach-hero-content {
  max-width: 700px;
  margin: 0 auto;
}

.teach-hero h1 {
  font-size: 40px;
  font-weight: 800;
  color: #fff;
  line-height: 1.3;
  margin-bottom: 15px;
}

.teach-hero .highlight {
  background: linear-gradient(135deg, #ffd699 0%, #e88a1a 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.teach-hero p {
  font-size: 18px;
  color: rgba(255, 255, 255, 0.9);
  line-height: 1.6;
}

.form-section {
  max-width: 700px;
  margin: -40px auto 60px;
  padding: 0 20px;
  position: relative;
  z-index: 1;
}

.form-container {
  background: #fff;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}

.form-container h2 {
  font-size: 24px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 8px;
}

.form-subtitle {
  color: #666;
  font-size: 15px;
  margin: 0 0 30px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-weight: 600;
  font-size: 14px;
  color: #1a1a2e;
  margin-bottom: 6px;
}

.required {
  color: #e74c3c;
}

.field-hint {
  font-size: 13px;
  color: #888;
  margin: 0 0 10px;
}

.form-group input[type="text"],
.form-group input[type="email"],
.form-group input[type="tel"],
.form-group textarea {
  width: 100%;
  padding: 0.75rem 0.85rem;
  border: 1.5px solid #ddd;
  border-radius: 8px;
  font-size: 15px;
  font-family: inherit;
  transition: border-color 0.2s;
  box-sizing: border-box;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #1a5fa4;
  box-shadow: 0 0 0 3px rgba(26, 95, 164, 0.1);
}

.form-group textarea {
  resize: vertical;
}

.checkbox-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border: 1.5px solid #eee;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.checkbox-label:hover {
  border-color: #1a5fa4;
  background: #f8f9ff;
}

.checkbox-label input[type="checkbox"] {
  accent-color: #1a5fa4;
  width: 16px;
  height: 16px;
}

.checkbox-text {
  font-size: 14px;
  color: #333;
}

.btn {
  padding: 14px 28px;
  border-radius: 10px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  text-decoration: none;
  display: inline-block;
  font-size: 16px;
  border: none;
}

.btn-primary {
  background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 8px 25px rgba(26, 95, 164, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-submit {
  width: 100%;
  margin-top: 10px;
  padding: 16px;
}

/* Success State */
.success-container {
  background: #fff;
  border-radius: 16px;
  padding: 60px 40px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.success-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, #27ae60 0%, #2ecc71 100%);
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 36px;
  margin: 0 auto 20px;
}

.success-container h2 {
  font-size: 28px;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 15px;
}

.success-container p {
  color: #666;
  font-size: 16px;
  line-height: 1.6;
  max-width: 500px;
  margin: 0 auto 30px;
}

.success-actions {
  display: flex;
  justify-content: center;
}

@media (max-width: 768px) {
  .teach-hero h1 {
    font-size: 28px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .checkbox-grid {
    grid-template-columns: 1fr;
  }

  .form-container {
    padding: 25px;
  }
}
</style>
