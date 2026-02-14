<template>
  <div class="detail-page">
    <button class="back-btn" @click="router.push('/')">&#8592; Back to Dashboard</button>

    <div v-if="loading" class="loading-state">Loading enrollment details...</div>
    <div v-else-if="errorMsg" class="error-state">{{ errorMsg }}</div>

    <template v-else>
      <!-- Summary Card -->
      <div class="summary-card">
        <div class="summary-left">
          <h1>{{ enrollment.course }}</h1>
          <p class="summary-name">{{ fullName }}</p>
          <p class="summary-date">Applied {{ formatDate(enrollment.created_at) }}</p>
        </div>
        <div class="summary-right">
          <span class="status-badge" :class="'status-' + enrollment.status">
            {{ formatStatus(enrollment.status) }}
          </span>
          <button v-if="canWithdraw" class="btn-withdraw-sm" @click="openWithdrawModal">Withdraw</button>
        </div>
      </div>

      <!-- Progress Steps -->
      <div class="progress-card">
        <h2>Enrollment Progress</h2>
        <div class="steps">
          <div
            v-for="(step, i) in steps"
            :key="step.key"
            class="step"
            :class="{ active: i <= currentStepIndex, current: i === currentStepIndex }"
          >
            <div class="step-circle">
              <span v-if="i < currentStepIndex">&#10003;</span>
              <span v-else>{{ i + 1 }}</span>
            </div>
            <span class="step-label">{{ step.label }}</span>
            <div v-if="i < steps.length - 1" class="step-line" :class="{ filled: i < currentStepIndex }"></div>
          </div>
        </div>
      </div>

      <!-- Action Banner -->
      <div v-if="actionBanner" class="action-banner" :class="'banner-' + actionBanner.type">
        <span class="banner-icon">{{ actionBanner.icon }}</span>
        <div>
          <strong>{{ actionBanner.title }}</strong>
          <p>{{ actionBanner.message }}</p>
        </div>
      </div>

      <!-- Documents Section -->
      <div class="section-card">
        <h2>Documents</h2>
        <div class="documents-grid">
          <div v-for="(meta, docType) in documentTypes" :key="docType" class="doc-card">
            <div class="doc-header">
              <span class="doc-name">{{ meta.label }}</span>
              <span class="doc-req" :class="meta.required ? 'required' : 'optional'">
                {{ meta.required ? 'Required' : 'Optional' }}
              </span>
            </div>

            <!-- Review status -->
            <div v-if="docReview(docType)" class="doc-review" :class="'review-' + docReview(docType).status">
              <template v-if="docReview(docType).status === 'accepted'">Accepted</template>
              <template v-else-if="docReview(docType).status === 'rejected'">
                <span>Rejected</span>
                <p v-if="docReview(docType).reject_reason" class="reject-reason">
                  {{ docReview(docType).reject_reason }}
                </p>
              </template>
              <template v-else-if="docReview(docType).status === 'uploaded'">Uploaded — Awaiting Review</template>
              <template v-else>Not uploaded yet</template>
            </div>
            <div v-else class="doc-review review-pending">Not uploaded yet</div>

            <!-- File link -->
            <a
              v-if="docFile(docType)"
              :href="docFile(docType).file_url"
              target="_blank"
              rel="noopener"
              class="doc-file-link"
            >
              View: {{ docFile(docType).file_name }}
            </a>

            <!-- Upload button -->
            <div v-if="canUpload(docType)" class="doc-upload">
              <label :for="'upload-' + docType" class="upload-btn">
                {{ uploading === docType ? 'Uploading...' : 'Upload File' }}
              </label>
              <input
                :id="'upload-' + docType"
                type="file"
                accept=".pdf,.jpg,.jpeg,.png"
                hidden
                :disabled="!!uploading"
                @change="handleUpload(docType, $event)"
              />
            </div>
          </div>
        </div>
      </div>

      <!-- Application Details (read-only) -->
      <div class="section-card">
        <h2>Application Details</h2>
        <div class="details-grid">
          <div class="detail-item">
            <span class="detail-label">Full Name</span>
            <span class="detail-value">{{ fullName }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Email</span>
            <span class="detail-value">{{ enrollment.email }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Contact No.</span>
            <span class="detail-value">{{ enrollment.contactNo || '--' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Course</span>
            <span class="detail-value">{{ enrollment.course }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Date of Birth</span>
            <span class="detail-value">{{ birthDate }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Sex</span>
            <span class="detail-value">{{ enrollment.sex || '--' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Civil Status</span>
            <span class="detail-value">{{ enrollment.civilStatus || '--' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Nationality</span>
            <span class="detail-value">{{ enrollment.nationality || '--' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Address</span>
            <span class="detail-value">{{ fullAddress }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Educational Attainment</span>
            <span class="detail-value">{{ enrollment.educationalAttainment || '--' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Employment Status</span>
            <span class="detail-value">{{ enrollment.employmentStatus || '--' }}</span>
          </div>
          <div class="detail-item">
            <span class="detail-label">Date Applied</span>
            <span class="detail-value">{{ formatDate(enrollment.created_at) }}</span>
          </div>
        </div>
      </div>
    </template>

    <!-- Withdraw Modal -->
    <div v-if="withdrawModal.show" class="modal-overlay" @click.self="withdrawModal.show = false">
      <div class="modal-card">
        <h3>Withdraw Application</h3>
        <p class="modal-subtitle">Are you sure you want to withdraw this application? This action cannot be undone.</p>

        <div class="modal-field">
          <label class="modal-label">Reason for withdrawal <span class="required-star">*</span></label>
          <div class="radio-list">
            <label v-for="r in withdrawReasons" :key="r" class="radio-option">
              <input type="radio" v-model="withdrawModal.reason" :value="r" />
              <span>{{ r }}</span>
            </label>
          </div>
        </div>

        <div class="modal-field">
          <label class="modal-label">
            Additional comments
            <span v-if="withdrawCommentsRequired" class="required-star">*</span>
          </label>
          <textarea
            v-model="withdrawModal.comments"
            rows="3"
            class="modal-textarea"
            placeholder="Please provide any additional details..."
          ></textarea>
        </div>

        <p v-if="withdrawModal.error" class="modal-error">{{ withdrawModal.error }}</p>

        <div class="modal-actions">
          <button class="modal-btn-cancel" @click="withdrawModal.show = false" :disabled="withdrawModal.submitting">Cancel</button>
          <button class="modal-btn-danger" @click="submitWithdraw" :disabled="withdrawModal.submitting || !withdrawModal.reason">
            {{ withdrawModal.submitting ? 'Withdrawing...' : 'Withdraw Application' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getEnrollment, getDocuments, uploadDocument, withdrawEnrollment } from '../services/api'

const route = useRoute()
const router = useRouter()

const loading = ref(true)
const errorMsg = ref('')
const enrollment = ref({})
const documentTypes = ref({})
const documents = ref({})
const uploading = ref(null)

const enrollmentId = route.params.id

// Withdraw modal state
const withdrawModal = ref({
  show: false,
  reason: '',
  comments: '',
  submitting: false,
  error: '',
})

const withdrawReasons = [
  'Schedule conflict',
  'Financial reasons',
  'Found another program',
  'Personal/family reasons',
  'Changed career plans',
  'Other',
]

const canWithdraw = computed(() => {
  const withdrawable = ['pending', 'pending_upload', 'pending_review', 'documents_rejected', 'in_waitlist', 'physical_docs_required']
  return withdrawable.includes(enrollment.value.status)
})

const withdrawCommentsRequired = computed(() => withdrawModal.value.reason === 'Other')

const openWithdrawModal = () => {
  withdrawModal.value = { show: true, reason: '', comments: '', submitting: false, error: '' }
}

const submitWithdraw = async () => {
  const modal = withdrawModal.value
  if (!modal.reason) {
    modal.error = 'Please select a reason.'
    return
  }
  if (modal.reason === 'Other' && !modal.comments.trim()) {
    modal.error = 'Please provide details for your reason.'
    return
  }
  modal.submitting = true
  modal.error = ''
  try {
    await withdrawEnrollment(enrollmentId, modal.reason, modal.comments)
    enrollment.value.status = 'withdrawn'
    modal.show = false
  } catch (e) {
    modal.error = e.response?.data?.detail || 'Failed to withdraw application.'
  } finally {
    modal.submitting = false
  }
}

onMounted(async () => {
  try {
    const [enrollData, docData] = await Promise.all([
      getEnrollment(enrollmentId),
      getDocuments(enrollmentId),
    ])
    enrollment.value = enrollData
    documentTypes.value = docData.document_types || {}
    documents.value = docData.documents || {}
  } catch (e) {
    errorMsg.value = e.response?.data?.detail || 'Failed to load enrollment details.'
  } finally {
    loading.value = false
  }
})

const fullName = computed(() => {
  const e = enrollment.value
  return [e.firstName, e.middleName, e.lastName].filter(Boolean).join(' ') || '--'
})

const birthDate = computed(() => {
  const e = enrollment.value
  if (!e.birthMonth || !e.birthDay || !e.birthYear) return '--'
  return `${e.birthMonth} ${e.birthDay}, ${e.birthYear}`
})

const fullAddress = computed(() => {
  const e = enrollment.value
  const parts = [e.street, e.barangay, e.district, e.city, e.province, e.region]
  return parts.filter(Boolean).join(', ') || '--'
})

// Progress steps
const steps = [
  { key: 'pending_upload', label: 'Upload Documents' },
  { key: 'pending_review', label: 'Under Review' },
  { key: 'in_waitlist', label: 'Waitlisted' },
  { key: 'physical_docs_required', label: 'Interview' },
  { key: 'completed', label: 'Enrolled' },
]

const currentStepIndex = computed(() => {
  const status = enrollment.value.status
  if (status === 'documents_rejected') return 0
  if (status === 'pending') return 0
  const idx = steps.findIndex(s => s.key === status)
  return idx >= 0 ? idx : 0
})

// Action banner
const actionBanner = computed(() => {
  const status = enrollment.value.status
  const banners = {
    pending: {
      type: 'info',
      icon: '\u{1F4C4}',
      title: 'Upload Your Documents',
      message: 'Please upload the required documents to proceed with your enrollment.',
    },
    pending_upload: {
      type: 'info',
      icon: '\u{1F4C4}',
      title: 'Upload Your Documents',
      message: 'Please upload the required documents to proceed with your enrollment.',
    },
    pending_review: {
      type: 'wait',
      icon: '\u{1F50D}',
      title: 'Documents Under Review',
      message: 'Your documents are being reviewed. You will be notified once the review is complete.',
    },
    documents_rejected: {
      type: 'warning',
      icon: '\u{26A0}\u{FE0F}',
      title: 'Some Documents Were Rejected',
      message: 'Please review the feedback below and re-upload the required documents.',
    },
    in_waitlist: {
      type: 'success',
      icon: '\u{2705}',
      title: 'You Are in the Waitlist',
      message: 'Your documents have been accepted. You will be contacted when a slot becomes available.',
    },
    physical_docs_required: {
      type: 'info',
      icon: '\u{1F4DE}',
      title: 'Interview Required',
      message: 'Please check your email for the interview schedule. Bring your physical documents.',
    },
    completed: {
      type: 'success',
      icon: '\u{1F389}',
      title: 'Enrollment Complete!',
      message: 'Congratulations! You are now enrolled. Check your email for further instructions.',
    },
    withdrawn: {
      type: 'withdrawn',
      icon: '\u{1F6AB}',
      title: 'Application Withdrawn',
      message: 'You have withdrawn this application. You may submit a new application at any time.',
    },
    cancelled: {
      type: 'cancelled',
      icon: '\u{26D4}',
      title: 'Application Cancelled',
      message: 'This application has been cancelled by the admissions team. You may submit a new application if you wish.',
    },
  }
  return banners[status] || null
})

// Document helpers
function docReview(docType) {
  return documents.value[docType]?.review || null
}

function docFile(docType) {
  const doc = documents.value[docType]
  return doc?.applicant_upload || doc?.official_scan || null
}

function canUpload(docType) {
  const status = enrollment.value.status
  if (status !== 'pending_upload' && status !== 'pending' && status !== 'documents_rejected') return false
  const review = docReview(docType)
  if (review && review.status === 'accepted') return false
  return true
}

async function handleUpload(docType, event) {
  const file = event.target.files?.[0]
  if (!file) return
  uploading.value = docType
  try {
    await uploadDocument(enrollmentId, docType, file)
    // Refresh documents
    const docData = await getDocuments(enrollmentId)
    documents.value = docData.documents || {}
    // Also refresh enrollment in case status changed
    const enrollData = await getEnrollment(enrollmentId)
    enrollment.value = enrollData
  } catch (e) {
    alert(e.response?.data?.detail || 'Upload failed. Please try again.')
  } finally {
    uploading.value = null
    event.target.value = ''
  }
}

function formatDate(dateStr) {
  if (!dateStr) return '--'
  const d = new Date(dateStr)
  if (isNaN(d)) return '--'
  return d.toLocaleDateString('en-PH', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function formatStatus(status) {
  const map = {
    pending: 'Pending',
    pending_upload: 'Upload Documents',
    pending_review: 'Under Review',
    documents_rejected: 'Documents Rejected',
    in_waitlist: 'In Waitlist',
    physical_docs_required: 'Interview Required',
    completed: 'Enrolled',
    withdrawn: 'Withdrawn',
    cancelled: 'Cancelled',
  }
  return map[status] || status
}
</script>

<style scoped>
.detail-page {
  max-width: 900px;
}

.back-btn {
  background: none;
  border: none;
  color: #1a5fa4;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0.4rem 0;
  margin-bottom: 1rem;
}

.back-btn:hover {
  text-decoration: underline;
}

.loading-state,
.error-state {
  text-align: center;
  padding: 3rem;
  color: #999;
  font-size: 0.95rem;
}

.error-state {
  color: #dc2626;
}

/* Summary Card */
.summary-card {
  background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 100%);
  color: white;
  border-radius: 12px;
  padding: 1.5rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.summary-card h1 {
  font-size: 1.35rem;
  margin-bottom: 0.3rem;
}

.summary-name {
  opacity: 0.9;
  font-size: 0.95rem;
  margin-bottom: 0.15rem;
}

.summary-date {
  opacity: 0.7;
  font-size: 0.8rem;
}

/* Progress Card */
.progress-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  margin-bottom: 1rem;
}

.progress-card h2,
.section-card h2 {
  font-size: 1.05rem;
  color: #1a1a2e;
  margin-bottom: 1.25rem;
}

.steps {
  display: flex;
  align-items: flex-start;
  position: relative;
}

.step {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
}

.step-circle {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e5e7eb;
  color: #999;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  z-index: 1;
  transition: all 0.3s;
}

.step.active .step-circle {
  background: #1a5fa4;
  color: white;
}

.step.current .step-circle {
  background: #1a5fa4;
  box-shadow: 0 0 0 4px rgba(26, 95, 164, 0.2);
}

.step-label {
  font-size: 0.7rem;
  color: #999;
  text-align: center;
  margin-top: 0.5rem;
  line-height: 1.2;
}

.step.active .step-label {
  color: #1a5fa4;
  font-weight: 600;
}

.step-line {
  position: absolute;
  top: 16px;
  left: 50%;
  width: 100%;
  height: 2px;
  background: #e5e7eb;
  z-index: 0;
}

.step-line.filled {
  background: #1a5fa4;
}

/* Action Banner */
.action-banner {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-radius: 10px;
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.action-banner strong {
  display: block;
  margin-bottom: 0.15rem;
}

.action-banner p {
  font-size: 0.82rem;
  opacity: 0.85;
  margin: 0;
}

.banner-icon {
  font-size: 1.3rem;
  flex-shrink: 0;
  margin-top: 0.1rem;
}

.banner-info { background: #e3f2fd; color: #1565c0; }
.banner-wait { background: #fff8e1; color: #f57f17; }
.banner-warning { background: #fef2f2; color: #dc2626; }
.banner-success { background: #e8f5e9; color: #2e7d32; }

/* Section Card */
.section-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  margin-bottom: 1rem;
}

/* Documents Grid */
.documents-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 0.75rem;
}

.doc-card {
  border: 1px solid #f0f0f0;
  border-radius: 10px;
  padding: 1rem;
}

.doc-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
}

.doc-name {
  font-weight: 600;
  font-size: 0.85rem;
  color: #1a1a2e;
}

.doc-req {
  font-size: 0.65rem;
  font-weight: 600;
  padding: 0.15rem 0.5rem;
  border-radius: 8px;
}

.doc-req.required {
  background: #fff3cd;
  color: #856404;
}

.doc-req.optional {
  background: #e8f0fe;
  color: #1a5fa4;
}

.doc-review {
  font-size: 0.78rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.review-accepted { color: #2e7d32; }
.review-rejected { color: #dc2626; }
.review-uploaded { color: #f57f17; }
.review-pending { color: #999; }

.reject-reason {
  font-weight: 400;
  font-size: 0.75rem;
  margin-top: 0.2rem;
  color: #b91c1c;
}

.doc-file-link {
  display: inline-block;
  font-size: 0.78rem;
  color: #1a5fa4;
  text-decoration: none;
  margin-bottom: 0.5rem;
  word-break: break-all;
}

.doc-file-link:hover {
  text-decoration: underline;
}

.doc-upload {
  margin-top: 0.25rem;
}

.upload-btn {
  display: inline-block;
  padding: 0.4rem 0.9rem;
  font-size: 0.78rem;
  font-weight: 600;
  color: white;
  background: #1a5fa4;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.upload-btn:hover {
  background: #0d3b6e;
}

/* Details Grid */
.details-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
}

.detail-label {
  font-size: 0.72rem;
  font-weight: 600;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.detail-value {
  font-size: 0.9rem;
  color: #1a1a2e;
}

/* Status badges (same as dashboard) */
.status-badge {
  display: inline-block;
  padding: 0.3rem 0.75rem;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
  flex-shrink: 0;
}

.status-pending,
.status-pending_upload { background: #fff3cd; color: #856404; }
.status-pending_review { background: #e3f2fd; color: #1565c0; }
.status-documents_rejected { background: #f8d7da; color: #721c24; }
.status-in_waitlist { background: #d4edda; color: #155724; }
.status-physical_docs_required { background: #e8f0fe; color: #1a5fa4; }
.status-completed { background: #c8e6c9; color: #1b5e20; }
.status-withdrawn { background: #fef2f2; color: #991b1b; }
.status-cancelled { background: #fefce8; color: #92400e; }

.summary-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 8px;
  flex-shrink: 0;
}

.btn-withdraw-sm {
  padding: 6px 14px;
  font-size: 12px;
  font-weight: 600;
  color: #dc2626;
  background: rgba(255, 255, 255, 0.15);
  border: 1px solid rgba(220, 38, 38, 0.5);
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-withdraw-sm:hover {
  background: rgba(254, 226, 226, 0.3);
}

.banner-withdrawn { background: #fef2f2; color: #991b1b; }
.banner-cancelled { background: #fefce8; color: #92400e; }

/* ── Withdraw Modal ── */

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 20px;
}

.modal-card {
  background: white;
  border-radius: 16px;
  padding: 28px;
  max-width: 480px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-card h3 {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a2e;
  margin: 0 0 6px;
}

.modal-subtitle {
  font-size: 13px;
  color: #666;
  margin: 0 0 18px;
  line-height: 1.5;
}

.modal-field {
  margin-bottom: 14px;
}

.modal-label {
  display: block;
  font-size: 12px;
  font-weight: 600;
  color: #444;
  margin-bottom: 8px;
}

.required-star {
  color: #dc2626;
}

.radio-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.radio-option {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: #333;
  cursor: pointer;
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  transition: background 0.15s;
}

.radio-option:hover {
  background: #f8fafc;
}

.radio-option input[type="radio"] {
  accent-color: #1a5fa4;
}

.modal-textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1.5px solid #ddd;
  border-radius: 8px;
  font-size: 13px;
  font-family: inherit;
  resize: vertical;
  box-sizing: border-box;
}

.modal-textarea:focus {
  outline: none;
  border-color: #1a5fa4;
}

.modal-error {
  color: #dc2626;
  font-size: 12px;
  margin: 0 0 10px;
}

.modal-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 18px;
}

.modal-btn-cancel {
  padding: 10px 20px;
  font-size: 13px;
  font-weight: 600;
  color: #666;
  background: #f0f0f0;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.modal-btn-cancel:hover:not(:disabled) { background: #e0e0e0; }
.modal-btn-cancel:disabled { opacity: 0.6; cursor: not-allowed; }

.modal-btn-danger {
  padding: 10px 20px;
  font-size: 13px;
  font-weight: 600;
  color: white;
  background: #dc2626;
  border: none;
  border-radius: 8px;
  cursor: pointer;
}

.modal-btn-danger:hover:not(:disabled) { background: #b91c1c; }
.modal-btn-danger:disabled { opacity: 0.6; cursor: not-allowed; }

@media (max-width: 600px) {
  .summary-card {
    flex-direction: column;
    gap: 0.75rem;
  }
  .steps {
    flex-direction: column;
    gap: 0.5rem;
  }
  .step {
    flex-direction: row;
    gap: 0.75rem;
  }
  .step-label {
    text-align: left;
    margin-top: 0;
  }
  .step-line {
    display: none;
  }
  .documents-grid {
    grid-template-columns: 1fr;
  }
  .details-grid {
    grid-template-columns: 1fr;
  }
}
</style>
