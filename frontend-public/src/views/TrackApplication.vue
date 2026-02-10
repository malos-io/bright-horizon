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
          <div class="card-icon-wrap">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
          </div>
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
          <div class="card-icon-wrap">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/><circle cx="12" cy="16" r="1"/></svg>
          </div>
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
          <div class="card-icon-wrap" style="margin-left: auto; margin-right: auto;">
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="9" y1="15" x2="15" y2="15"/><line x1="9" y1="11" x2="13" y2="11"/></svg>
          </div>
          <h2>Your Application{{ applications.length > 1 ? 's' : '' }}</h2>

          <div v-for="app in applications" :key="app.id" class="application-item">
            <div class="app-header">
              <h3>{{ app.firstName }} {{ app.middleName ? app.middleName + ' ' : '' }}{{ app.lastName }}</h3>
              <span class="status-badge" :class="'status-' + app.status">{{ formatStatus(app.status) }}</span>
            </div>
            <p v-if="app.status === 'in_waitlist'" class="status-note status-note-success">All submitted documents have been accepted. Please wait for further instructions from our admissions team.</p>
            <p v-else-if="app.status === 'documents_rejected'" class="status-note status-note-warning">One or more documents require attention. Please click "See Application" below to review and re-upload.</p>
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
            <button class="btn btn-primary btn-full btn-see-app" @click="openApplicationDetail(app)">See Application</button>
          </div>

          <router-link to="/" class="btn btn-outline btn-full" style="margin-top: 20px;">Back to Home</router-link>
        </div>

        <!-- State 4: Application Detail -->
        <div v-else-if="step === 'detail'" class="track-card detail-card">
          <button class="btn-back" @click="editing = false; step = 'status'">&larr; Back to Applications</button>

          <div v-if="detailLoading" class="loading-state">Loading application details...</div>

          <template v-else-if="selectedEnrollment">
            <div class="detail-summary">
              <h2>{{ selectedEnrollment.lastName }}, {{ selectedEnrollment.firstName }} {{ selectedEnrollment.middleName }}</h2>
              <span class="status-badge" :class="'status-' + selectedEnrollment.status">{{ formatStatus(selectedEnrollment.status) }}</span>
            </div>

            <div v-if="selectedEnrollment.status === 'in_waitlist'" class="status-note status-note-success">All submitted documents have been reviewed and accepted. Your application is now on the waitlist. Please wait for further instructions from our admissions team.</div>
            <div v-else-if="selectedEnrollment.status === 'documents_rejected'" class="status-note status-note-warning">One or more documents need attention. Please check the Documents section below to review the feedback and re-upload as needed.</div>

            <!-- Application Form -->
            <div class="detail-section">
              <div class="section-header-row">
                <h3 class="section-toggle" @click="formExpanded = !formExpanded">
                  {{ formExpanded ? '&#9660;' : '&#9654;' }} Application Form
                </h3>
                <div v-if="canEdit" class="edit-controls">
                  <template v-if="!editing">
                    <button class="btn-edit" @click="startEditing">Edit</button>
                  </template>
                  <template v-else>
                    <button class="btn-save" @click="saveEditing" :disabled="saving">{{ saving ? 'Saving...' : 'Save' }}</button>
                    <button class="btn-cancel" @click="cancelEditing" :disabled="saving">Cancel</button>
                  </template>
                </div>
              </div>
              <p v-if="saveMessage" class="save-message" :class="saveMessageType">{{ saveMessage }}</p>
              <div v-show="formExpanded" class="detail-form-content">
                <!-- Section II: Manpower Profile -->
                <div class="detail-form-section">
                  <h4>II. Manpower Profile</h4>
                  <div class="detail-form-row three-col">
                    <div class="detail-form-group"><label>Last Name</label><input v-if="editing" v-model="formData.lastName" /><input v-else :value="selectedEnrollment.lastName" disabled /></div>
                    <div class="detail-form-group"><label>First Name</label><input v-if="editing" v-model="formData.firstName" /><input v-else :value="selectedEnrollment.firstName" disabled /></div>
                    <div class="detail-form-group"><label>Middle Name</label><input v-if="editing" v-model="formData.middleName" /><input v-else :value="selectedEnrollment.middleName" disabled /></div>
                  </div>
                  <h5 class="detail-sub-heading">Complete Mailing Address</h5>
                  <div class="detail-form-row three-col">
                    <div class="detail-form-group"><label>Region</label><input v-if="editing" v-model="formData.region" /><input v-else :value="selectedEnrollment.region" disabled /></div>
                    <div class="detail-form-group"><label>Province</label><input v-if="editing" v-model="formData.province" /><input v-else :value="selectedEnrollment.province" disabled /></div>
                    <div class="detail-form-group"><label>City / Municipality</label><input v-if="editing" v-model="formData.city" /><input v-else :value="selectedEnrollment.city" disabled /></div>
                  </div>
                  <div class="detail-form-row three-col">
                    <div class="detail-form-group"><label>Street No. / Street</label><input v-if="editing" v-model="formData.street" /><input v-else :value="selectedEnrollment.street" disabled /></div>
                    <div class="detail-form-group"><label>Barangay</label><input v-if="editing" v-model="formData.barangay" /><input v-else :value="selectedEnrollment.barangay" disabled /></div>
                    <div class="detail-form-group"><label>District</label><input v-if="editing" v-model="formData.district" /><input v-else :value="selectedEnrollment.district" disabled /></div>
                  </div>
                  <div class="detail-form-row three-col">
                    <div class="detail-form-group"><label>Email</label><input :value="selectedEnrollment.email" disabled class="field-locked" /></div>
                    <div class="detail-form-group"><label>Contact No.</label><input v-if="editing" v-model="formData.contactNo" /><input v-else :value="selectedEnrollment.contactNo" disabled /></div>
                    <div class="detail-form-group"><label>Nationality</label><input v-if="editing" v-model="formData.nationality" /><input v-else :value="selectedEnrollment.nationality" disabled /></div>
                  </div>
                </div>

                <!-- Section III: Personal Information -->
                <div class="detail-form-section">
                  <h4>III. Personal Information</h4>
                  <div class="detail-form-row three-col">
                    <div class="detail-form-group"><label>Sex</label><input v-if="editing" v-model="formData.sex" /><input v-else :value="selectedEnrollment.sex" disabled /></div>
                    <div class="detail-form-group"><label>Civil Status</label><input v-if="editing" v-model="formData.civilStatus" /><input v-else :value="selectedEnrollment.civilStatus" disabled /></div>
                    <div class="detail-form-group"><label>Employment Status</label><input v-if="editing" v-model="formData.employmentStatus" /><input v-else :value="selectedEnrollment.employmentStatus" disabled /></div>
                  </div>
                  <div class="detail-form-row three-col" v-if="!editing">
                    <div class="detail-form-group"><label>Date of Birth</label><input :value="`${selectedEnrollment.birthMonth} ${selectedEnrollment.birthDay}, ${selectedEnrollment.birthYear}`" disabled /></div>
                    <div class="detail-form-group"><label>Age</label><input :value="selectedEnrollment.age || '--'" disabled /></div>
                  </div>
                  <div class="detail-form-row three-col" v-if="editing">
                    <div class="detail-form-group"><label>Birth Month</label><input v-model="formData.birthMonth" /></div>
                    <div class="detail-form-group"><label>Birth Day</label><input v-model="formData.birthDay" /></div>
                    <div class="detail-form-group"><label>Birth Year</label><input v-model="formData.birthYear" /></div>
                  </div>
                  <h5 class="detail-sub-heading">Birthplace</h5>
                  <div class="detail-form-row three-col">
                    <div class="detail-form-group"><label>Region</label><input v-if="editing" v-model="formData.birthplaceRegion" /><input v-else :value="selectedEnrollment.birthplaceRegion" disabled /></div>
                    <div class="detail-form-group"><label>Province</label><input v-if="editing" v-model="formData.birthplaceProvince" /><input v-else :value="selectedEnrollment.birthplaceProvince" disabled /></div>
                    <div class="detail-form-group"><label>City / Municipality</label><input v-if="editing" v-model="formData.birthplaceCity" /><input v-else :value="selectedEnrollment.birthplaceCity" disabled /></div>
                  </div>
                </div>

                <!-- Educational Attainment -->
                <div class="detail-form-section">
                  <h4>Educational Attainment</h4>
                  <div class="detail-form-group"><input v-if="editing" v-model="formData.educationalAttainment" /><input v-else :value="selectedEnrollment.educationalAttainment" disabled /></div>
                </div>

                <!-- Section IV: Classification -->
                <div class="detail-form-section">
                  <h4>IV. Learner Classification</h4>
                  <div class="detail-form-group">
                    <input :value="(selectedEnrollment.learnerClassification || []).join(', ') || 'None'" disabled />
                  </div>
                  <div v-if="(selectedEnrollment.learnerClassification || []).includes('Others')" class="detail-form-group">
                    <label>Others (specify)</label>
                    <input v-if="editing" v-model="formData.classificationOther" /><input v-else :value="selectedEnrollment.classificationOther" disabled />
                  </div>
                </div>

                <!-- Section V: NCAE -->
                <div class="detail-form-section">
                  <h4>V. NCAE / YP4SC</h4>
                  <div class="detail-form-group"><input :value="selectedEnrollment.ncaeTaken ? 'Yes' : 'No'" disabled /></div>
                  <div v-if="selectedEnrollment.ncaeTaken" class="detail-form-row two-col">
                    <div class="detail-form-group"><label>Where?</label><input v-if="editing" v-model="formData.ncaeWhere" /><input v-else :value="selectedEnrollment.ncaeWhere" disabled /></div>
                    <div class="detail-form-group"><label>When?</label><input v-if="editing" v-model="formData.ncaeWhen" /><input v-else :value="selectedEnrollment.ncaeWhen" disabled /></div>
                  </div>
                </div>

                <!-- Section VI: Course (always locked) -->
                <div class="detail-form-section">
                  <h4>VI. Course / Qualification</h4>
                  <div class="detail-form-group"><input :value="selectedEnrollment.course" disabled class="field-locked" /></div>
                </div>

                <!-- Section VIII: Scholarship -->
                <div class="detail-form-section">
                  <h4>VIII. Scholarship</h4>
                  <div class="detail-form-group"><input :value="selectedEnrollment.applyScholarship ? 'Yes' : 'No'" disabled /></div>
                </div>
              </div>
            </div>

            <!-- Documents Section -->
            <div class="detail-section">
              <h3 class="section-toggle" @click="docsExpanded = !docsExpanded">
                {{ docsExpanded ? '&#9660;' : '&#9654;' }} Documents
              </h3>
              <div v-show="docsExpanded" class="detail-docs-content">
                <div class="detail-doc-card" v-for="(info, docType) in documentTypes" :key="docType">
                  <div class="detail-doc-header">
                    <span class="detail-doc-name">{{ info.label }}</span>
                    <span class="detail-doc-badge" :class="info.required ? 'badge-required' : 'badge-optional'">
                      {{ info.required ? 'Required' : 'Optional' }}
                    </span>
                  </div>

                  <!-- Review status bar -->
                  <div class="detail-review-bar" v-if="getDocReviewStatus(docType) !== 'pending'">
                    <span class="detail-doc-status" :class="'doc-status-' + getDocReviewStatus(docType)">
                      {{ formatDocStatus(getDocReviewStatus(docType)) }}
                    </span>
                    <span v-if="getDocRejectReason(docType)" class="detail-reject-reason">
                      {{ getDocRejectReason(docType) }}
                    </span>
                  </div>

                  <!-- Applicant Upload Slot -->
                  <div class="detail-doc-slot">
                    <span class="detail-slot-label">Your Upload</span>
                    <div v-if="applicantDocuments[docType]?.applicant_upload" class="detail-slot-file">
                      <a :href="applicantDocuments[docType].applicant_upload.file_url" target="_blank" class="detail-file-link">
                        {{ applicantDocuments[docType].applicant_upload.file_name }}
                      </a>
                      <span class="detail-file-meta">{{ formatDate(applicantDocuments[docType].applicant_upload.uploaded_at) }}</span>
                    </div>
                    <div v-if="!applicantDocuments[docType]?.applicant_upload || getDocReviewStatus(docType) === 'rejected'" class="detail-slot-upload">
                      <label class="detail-upload-label" :class="{ disabled: uploading[docType] }">
                        <input type="file" accept="image/*,application/pdf" class="detail-file-input" @change="handleApplicantUpload($event, docType)" :disabled="uploading[docType]" />
                        {{ uploading[docType] ? 'Uploading...' : (applicantDocuments[docType]?.applicant_upload ? 'Re-upload' : 'Upload Document') }}
                      </label>
                    </div>
                  </div>

                  <!-- Official Scan (read-only if exists) -->
                  <div v-if="applicantDocuments[docType]?.official_scan" class="detail-doc-slot">
                    <span class="detail-slot-label">Official Scan</span>
                    <div class="detail-slot-file">
                      <a :href="applicantDocuments[docType].official_scan.file_url" target="_blank" class="detail-file-link">
                        {{ applicantDocuments[docType].official_scan.file_name }}
                      </a>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </div>

      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { sendOtp, verifyOtp, getApplicantEnrollment, getApplicantDocuments, uploadApplicantDocument, updateApplicantEnrollment, clearApplicantToken } from '@/services/api'

const step = ref('email')
const email = ref('')
const otpDigits = ref(['', '', '', '', '', ''])
const otpRefs = ref([])
const loading = ref(false)
const error = ref('')
const applications = ref([])
const resendCooldown = ref(0)

// Detail view state
const selectedEnrollment = ref(null)
const detailLoading = ref(false)
const formExpanded = ref(false)
const docsExpanded = ref(true)
const documentTypes = ref({})
const applicantDocuments = ref({})
const uploading = ref({})

// Editing state
const editing = ref(false)
const saving = ref(false)
const saveMessage = ref('')
const saveMessageType = ref('success')
const formData = reactive({
  lastName: '', firstName: '', middleName: '',
  street: '', barangay: '', district: '', city: '', province: '', region: '',
  contactNo: '', nationality: '',
  sex: '', civilStatus: '', employmentStatus: '',
  birthMonth: '', birthDay: '', birthYear: '',
  birthplaceCity: '', birthplaceProvince: '', birthplaceRegion: '',
  educationalAttainment: '',
  learnerClassification: [], classificationOther: '',
  ncaeTaken: false, ncaeWhere: '', ncaeWhen: '',
  applyScholarship: false,
})
const editSnapshot = ref({})

const canEdit = computed(() => {
  const s = selectedEnrollment.value?.status
  return s === 'pending_upload' || s === 'pending'
})

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
    pending_upload: 'Pending Upload of Required Documents',
    pending_review: 'Under Review',
    documents_rejected: 'Documents Need Attention',
    in_waitlist: 'In Waitlist',
    physical_docs_required: 'Physical Documents and Interview Required',
    completed: 'Completed',
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

// ── Editing functions ──

const populateFormData = (enrollment) => {
  for (const key of Object.keys(formData)) {
    if (key === 'learnerClassification') {
      formData[key] = [...(enrollment[key] || [])]
    } else {
      formData[key] = enrollment[key] ?? ''
    }
  }
}

const startEditing = () => {
  populateFormData(selectedEnrollment.value)
  editSnapshot.value = JSON.parse(JSON.stringify(formData))
  editing.value = true
  formExpanded.value = true
  saveMessage.value = ''
}

const cancelEditing = () => {
  // Restore snapshot
  for (const key of Object.keys(formData)) {
    formData[key] = editSnapshot.value[key]
  }
  editing.value = false
  saveMessage.value = ''
}

const saveEditing = async () => {
  saving.value = true
  saveMessage.value = ''
  try {
    // Build diff: only send changed fields
    const changes = {}
    for (const key of Object.keys(formData)) {
      if (JSON.stringify(formData[key]) !== JSON.stringify(editSnapshot.value[key])) {
        changes[key] = formData[key]
      }
    }
    if (Object.keys(changes).length === 0) {
      editing.value = false
      return
    }
    await updateApplicantEnrollment(selectedEnrollment.value.id, changes)
    // Refresh enrollment data
    const enrollment = await getApplicantEnrollment(selectedEnrollment.value.id)
    selectedEnrollment.value = enrollment
    populateFormData(enrollment)
    editing.value = false
    saveMessage.value = 'Changes saved successfully.'
    saveMessageType.value = 'success'
    setTimeout(() => { saveMessage.value = '' }, 3000)
  } catch (e) {
    if (e.response?.status === 401) {
      clearApplicantToken()
      step.value = 'email'
      error.value = 'Session expired. Please verify your email again.'
    } else {
      saveMessage.value = e.response?.data?.detail || 'Failed to save changes.'
      saveMessageType.value = 'error'
    }
  } finally {
    saving.value = false
  }
}

// ── Detail view functions ──

const openApplicationDetail = async (app) => {
  step.value = 'detail'
  detailLoading.value = true
  error.value = ''
  try {
    const [enrollment, docs] = await Promise.all([
      getApplicantEnrollment(app.id),
      getApplicantDocuments(app.id),
    ])
    selectedEnrollment.value = enrollment
    documentTypes.value = docs.document_types || {}
    applicantDocuments.value = docs.documents || {}
  } catch (e) {
    if (e.response?.status === 401) {
      clearApplicantToken()
      step.value = 'email'
      error.value = 'Session expired. Please verify your email again.'
    } else {
      error.value = e.response?.data?.detail || 'Failed to load application details.'
      step.value = 'status'
    }
  } finally {
    detailLoading.value = false
  }
}

const getDocReviewStatus = (docType) => {
  return applicantDocuments.value[docType]?.review?.status || 'pending'
}

const getDocRejectReason = (docType) => {
  return applicantDocuments.value[docType]?.review?.reject_reason || ''
}

const formatDocStatus = (status) => {
  const map = { pending: 'Pending', uploaded: 'Uploaded - Needs Admin Review', accepted: 'Accepted', rejected: 'Rejected' }
  return map[status] || status
}

const handleApplicantUpload = async (event, docType) => {
  const file = event.target.files?.[0]
  if (!file) return
  uploading.value[docType] = true
  try {
    await uploadApplicantDocument(selectedEnrollment.value.id, docType, file)
    const docs = await getApplicantDocuments(selectedEnrollment.value.id)
    applicantDocuments.value = docs.documents || {}
    // Refresh enrollment to get updated status
    const enrollment = await getApplicantEnrollment(selectedEnrollment.value.id)
    selectedEnrollment.value = enrollment
  } catch (e) {
    if (e.response?.status === 401) {
      clearApplicantToken()
      step.value = 'email'
      error.value = 'Session expired. Please verify your email again.'
    } else {
      alert(e.response?.data?.detail || 'Failed to upload document. Please try again.')
    }
  } finally {
    uploading.value[docType] = false
    event.target.value = ''
  }
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
  color: inherit;
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
  transition: max-width 0.3s ease;
}

.track-container:has(.detail-card) {
  max-width: 800px;
}

.track-card {
  background: #fff;
  border-radius: 16px;
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  text-align: center;
}

.card-icon-wrap {
  width: 64px;
  height: 64px;
  margin: 0 auto 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #eef3fa;
  border-radius: 16px;
  color: #1a5fa4;
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

.status-card .card-icon-wrap {
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

.status-pending_upload {
  background: #fff3e0;
  color: #e65100;
}

.status-pending_review {
  background: #e3f2fd;
  color: #1565c0;
}

.status-documents_rejected {
  background: #fff3e0;
  color: #e65100;
}

.status-in_waitlist {
  background: #e8f5e9;
  color: #2e7d32;
}

.status-note {
  font-size: 13px;
  line-height: 1.5;
  padding: 10px 14px;
  border-radius: 8px;
  margin: 10px 0 0;
  text-align: left;
}

.status-note-success {
  background: #f0fdf4;
  color: #166534;
  border: 1px solid #bbf7d0;
}

.status-note-warning {
  background: #fffbeb;
  color: #92400e;
  border: 1px solid #fde68a;
}

.status-physical_docs_required {
  background: #e3f2fd;
  color: #1565c0;
}

.status-completed {
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

/* ── See Application button ── */

.btn-see-app {
  margin-top: 12px;
  font-size: 14px;
  padding: 10px 20px;
}

/* ── Detail View ── */

.detail-card {
  text-align: left;
}

.btn-back {
  background: none;
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 14px;
  color: #666;
  cursor: pointer;
  margin-bottom: 20px;
  transition: background 0.2s;
}

.btn-back:hover {
  background: #f5f5f5;
}

.loading-state {
  text-align: center;
  color: #888;
  padding: 40px 0;
  font-size: 15px;
}

.detail-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.detail-summary h2 {
  font-size: 20px;
  margin: 0;
  text-align: left;
}

.detail-section {
  margin-bottom: 20px;
  background: #fafbff;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid #e8f0fe;
}

.section-toggle {
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  color: #1a1a2e;
  margin: 0;
  user-select: none;
}

.section-toggle:hover {
  color: #1a5fa4;
}

.section-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.edit-controls {
  display: flex;
  gap: 8px;
}

.btn-edit {
  padding: 6px 16px;
  font-size: 13px;
  font-weight: 600;
  color: #1a5fa4;
  background: #e8f0fe;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-edit:hover { background: #d0e2fc; }

.btn-save {
  padding: 6px 16px;
  font-size: 13px;
  font-weight: 600;
  color: white;
  background: #27ae60;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-save:hover:not(:disabled) { background: #219a52; }
.btn-save:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-cancel {
  padding: 6px 16px;
  font-size: 13px;
  font-weight: 600;
  color: #666;
  background: #f0f0f0;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-cancel:hover:not(:disabled) { background: #e0e0e0; }
.btn-cancel:disabled { opacity: 0.6; cursor: not-allowed; }

.save-message {
  font-size: 13px;
  margin: 8px 0 0;
  padding: 8px 12px;
  border-radius: 6px;
}

.save-message.success { background: #d4edda; color: #155724; }
.save-message.error { background: #f8d7da; color: #721c24; }

.field-locked {
  background: #f0f0f0 !important;
  color: #999 !important;
}

/* ── Detail Form ── */

.detail-form-content {
  margin-top: 16px;
}

.detail-form-section {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #eee;
}

.detail-form-section:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.detail-form-section h4 {
  font-size: 14px;
  font-weight: 700;
  color: #0d3b6e;
  margin: 0 0 12px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.detail-sub-heading {
  font-size: 13px;
  font-weight: 600;
  color: #555;
  margin: 12px 0 8px;
}

.detail-form-row {
  display: grid;
  gap: 12px;
  margin-bottom: 10px;
}

.detail-form-row.three-col {
  grid-template-columns: repeat(3, 1fr);
}

.detail-form-row.two-col {
  grid-template-columns: repeat(2, 1fr);
}

.detail-form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.detail-form-group label {
  font-size: 11px;
  font-weight: 600;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.detail-form-group input {
  padding: 8px 10px;
  border: 1px solid #e0e0e0;
  border-radius: 6px;
  font-size: 13px;
  color: #333;
  background: #f9f9f9;
  width: 100%;
  box-sizing: border-box;
}

.detail-form-group input:not(:disabled) {
  background: #fff;
  border-color: #1a5fa4;
  box-shadow: 0 0 0 2px rgba(26, 95, 164, 0.08);
}

.detail-form-group input:not(:disabled):focus {
  outline: none;
  border-color: #0d3b6e;
  box-shadow: 0 0 0 3px rgba(26, 95, 164, 0.15);
}

/* ── Detail Documents ── */

.detail-docs-content {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.detail-doc-card {
  background: white;
  border: 1px solid #e8f0fe;
  border-radius: 10px;
  overflow: hidden;
}

.detail-doc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 16px;
  background: #f0f5ff;
  border-bottom: 1px solid #e8f0fe;
}

.detail-doc-name {
  font-size: 14px;
  font-weight: 600;
  color: #1a1a2e;
}

.detail-doc-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.badge-required { background: #fff3cd; color: #856404; }
.badge-optional { background: #e8f0fe; color: #1a5fa4; }

.detail-review-bar {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 16px;
  background: #fafbff;
  border-bottom: 1px solid #e8f0fe;
}

.detail-doc-status {
  font-size: 11px;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 10px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.doc-status-uploaded { background: #fff3cd; color: #856404; }
.doc-status-accepted { background: #d4edda; color: #155724; }
.doc-status-rejected { background: #f8d7da; color: #721c24; }

.detail-reject-reason {
  font-size: 13px;
  color: #721c24;
  font-style: italic;
}

.detail-doc-slot {
  padding: 10px 16px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  border-bottom: 1px solid #f0f0f0;
}

.detail-doc-slot:last-child {
  border-bottom: none;
}

.detail-slot-label {
  font-size: 11px;
  font-weight: 600;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.detail-slot-file {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.detail-file-link {
  font-size: 13px;
  color: #1a5fa4;
  text-decoration: none;
  word-break: break-all;
}

.detail-file-link:hover {
  text-decoration: underline;
}

.detail-file-meta {
  font-size: 11px;
  color: #999;
}

.detail-slot-upload {
  margin-top: 4px;
}

.detail-upload-label {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 14px;
  font-size: 13px;
  font-weight: 600;
  color: #1a5fa4;
  background: #e8f0fe;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.detail-upload-label:hover:not(.disabled) {
  background: #d0e2fc;
}

.detail-upload-label.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.detail-file-input {
  display: none;
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

  .detail-summary {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .detail-form-row.three-col,
  .detail-form-row.two-col {
    grid-template-columns: 1fr;
  }
}
</style>
