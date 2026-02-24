<template>
  <div class="student-detail">
    <div class="detail-header">
      <button class="btn-back" @click="router.push('/students')">&#8592; Back to Students</button>
    </div>

    <div v-if="loading" class="loading-state">Loading student...</div>
    <div v-else-if="!student" class="empty-state">Student not found</div>

    <template v-else>
      <!-- Student summary -->
      <div class="summary-card">
        <div class="summary-info">
          <h2>{{ student.lastName }}, {{ student.firstName }}</h2>
          <p class="summary-meta">{{ student.email }}</p>
        </div>
        <div class="summary-actions">
          <span class="role-badge">Student</span>
          <button class="btn-change-email" @click="showEmailPanel = !showEmailPanel">
            {{ showEmailPanel ? 'Cancel' : 'Change Student Email' }}
          </button>
        </div>
      </div>

      <!-- Change Email Panel -->
      <div v-if="showEmailPanel" class="email-change-panel">
        <div class="verify-warning">
          <div class="verify-warning-icon">!</div>
          <div class="verify-warning-content">
            <strong>Identity Verification Required</strong>
            <p>Before changing a student's email, you <strong>must verify</strong> that the person requesting the change is the actual student. This protects the student's account and personal data.</p>
            <ul>
              <li>Ask the student to present a valid government-issued ID</li>
              <li>Verify <strong>in person</strong>, via <strong>video call</strong>, or via <strong>phone call</strong></li>
              <li>Confirm that the name and photo on the ID match the student on record</li>
            </ul>
            <p class="verify-reminder">Do NOT proceed if you have not personally verified the requestor's identity.</p>
          </div>
        </div>
        <div class="email-form">
          <label class="email-label">New Email Address</label>
          <div class="email-input-row">
            <input
              v-model="newEmail"
              type="email"
              placeholder="Enter new email address"
              class="email-input"
              :disabled="savingEmail"
            />
            <button
              class="btn-save-email"
              :disabled="!newEmail.trim() || savingEmail"
              @click="handleChangeEmail"
            >
              {{ savingEmail ? 'Updating...' : 'Update Email' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Enrollment History -->
      <div class="section">
        <h3 class="section-title">Enrollment History</h3>
        <div class="table-container">
          <table v-if="enrollments.length" class="data-table">
            <thead>
              <tr>
                <th></th>
                <th>Course</th>
                <th>Status</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="e in enrollments" :key="e.id">
                <td>
                  <button class="btn-detail" @click="router.push('/application/' + e.id)">View</button>
                </td>
                <td>{{ e.course }}</td>
                <td>
                  <span class="status-badge" :class="'status-' + e.status">
                    {{ formatStatus(e.status) }}
                  </span>
                </td>
                <td>{{ formatDate(e.created_at) }}</td>
              </tr>
            </tbody>
          </table>
          <div v-else class="empty">No enrollment history</div>
        </div>
      </div>

      <!-- Documents on File -->
      <div class="section">
        <h3 class="section-title">Documents on File</h3>
        <div v-if="Object.keys(documents).length" class="docs-grid">
          <div class="doc-card" v-for="(info, docType) in documents" :key="docType">
            <div class="doc-card-header">
              <span class="doc-name">{{ docLabels[docType] || docType }}</span>
              <span v-if="info.review" class="doc-status-badge" :class="'doc-status-' + (info.review.status || 'pending')">
                {{ info.review.status || 'pending' }}
              </span>
            </div>
            <div class="doc-file-row">
              <div v-if="info.official_scan" class="slot-file">
                <a :href="info.official_scan.file_url" target="_blank" class="file-link">
                  {{ info.official_scan.file_name }}
                </a>
                <span class="file-meta">{{ formatDate(info.official_scan.uploaded_at) }}</span>
              </div>
              <div v-else class="slot-empty-text">No official scan</div>
            </div>
          </div>
        </div>
        <div v-else class="empty">No documents on file</div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getStudentDetail, updateStudentEmail } from '../services/api'

const route = useRoute()
const router = useRouter()

const student = ref(null)
const enrollments = ref([])
const documents = ref({})
const loading = ref(true)
const showEmailPanel = ref(false)
const newEmail = ref('')
const savingEmail = ref(false)

const docLabels = {
  birth_certificate: 'Birth Certificate',
  educational_credentials: 'Educational Credentials',
  id_pictures: 'ID Pictures',
  government_id: 'Government Issued ID',
  proof_of_name_change: 'Proof of Name Change',
}

function formatStatus(status) {
  const map = {
    pending: 'Pending',
    pending_upload: 'Pending Upload',
    pending_review: 'Pending Review',
    documents_rejected: 'Docs Rejected',
    in_waitlist: 'In Waitlist',
    physical_docs_required: 'Physical Docs Required',
    waiting_for_class_start: 'Waiting for Class',
    completed: 'Completed',
  }
  return map[status] || status
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

async function handleChangeEmail() {
  if (!newEmail.value.trim()) return
  if (!confirm(`Are you sure you want to change this student's email?\n\nFrom: ${student.value.email}\nTo: ${newEmail.value.trim()}\n\nHave you verified the requestor's identity?`)) {
    return
  }
  savingEmail.value = true
  try {
    const result = await updateStudentEmail(route.params.id, newEmail.value.trim())
    alert(result.message)
    student.value.email = newEmail.value.trim().toLowerCase()
    newEmail.value = ''
    showEmailPanel.value = false
  } catch (e) {
    const msg = e.response?.data?.detail || 'Failed to update email.'
    alert(msg)
  } finally {
    savingEmail.value = false
  }
}

onMounted(async () => {
  try {
    const data = await getStudentDetail(route.params.id)
    student.value = data.student
    enrollments.value = data.enrollments || []
    documents.value = data.documents || {}
  } catch (e) {
    console.error('Failed to load student:', e)
    student.value = null
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.student-detail {
  max-width: 1000px;
}

.detail-header {
  margin-bottom: 1.5rem;
}

.btn-back {
  padding: 0.4rem 1rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: #666;
  background: white;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-back:hover {
  background: #f5f5f5;
  border-color: #ccc;
}

.loading-state,
.empty-state {
  text-align: center;
  color: #999;
  padding: 3rem;
  background: white;
  border-radius: 12px;
}

.summary-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.summary-info h2 {
  font-size: 1.25rem;
  color: #1a1a2e;
  margin-bottom: 0.25rem;
}

.summary-meta {
  font-size: 0.85rem;
  color: #666;
}

.summary-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-shrink: 0;
}

.role-badge {
  display: inline-block;
  padding: 0.3rem 0.8rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  background: #c8e6c9;
  color: #1b5e20;
}

.btn-change-email {
  padding: 0.4rem 0.9rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: #856404;
  background: #fff3cd;
  border: 1px solid #ffc107;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
}

.btn-change-email:hover {
  background: #ffe69c;
}

/* Change Email Panel */
.email-change-panel {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  margin-bottom: 1.5rem;
  overflow: hidden;
}

.verify-warning {
  display: flex;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  background: #fff8e1;
  border-bottom: 1px solid #ffe082;
}

.verify-warning-icon {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #f57f17;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.1rem;
  font-weight: 800;
  flex-shrink: 0;
  margin-top: 0.1rem;
}

.verify-warning-content {
  font-size: 0.85rem;
  color: #5d4037;
  line-height: 1.5;
}

.verify-warning-content strong {
  color: #e65100;
}

.verify-warning-content p {
  margin: 0.4rem 0;
}

.verify-warning-content ul {
  margin: 0.5rem 0;
  padding-left: 1.2rem;
}

.verify-warning-content li {
  margin-bottom: 0.3rem;
}

.verify-reminder {
  font-weight: 700;
  color: #c62828 !important;
  margin-top: 0.6rem !important;
}

.email-form {
  padding: 1.25rem 1.5rem;
}

.email-label {
  display: block;
  font-size: 0.8rem;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 0.5rem;
}

.email-input-row {
  display: flex;
  gap: 0.75rem;
}

.email-input {
  flex: 1;
  padding: 0.5rem 0.75rem;
  font-size: 0.9rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  outline: none;
  transition: border-color 0.2s;
}

.email-input:focus {
  border-color: #1a5fa4;
}

.btn-save-email {
  padding: 0.5rem 1.25rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: white;
  background: #e65100;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
}

.btn-save-email:hover:not(:disabled) {
  background: #bf360c;
}

.btn-save-email:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 1rem;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 1rem;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 0.6rem 0.75rem;
  text-align: left;
  border-bottom: 1px solid #eee;
  font-size: 0.85rem;
}

.data-table th {
  font-size: 0.75rem;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.data-table tbody tr:hover {
  background: #f8f9ff;
}

.btn-detail {
  padding: 0.3rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #1a5fa4;
  background: #e8f0fe;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
}

.btn-detail:hover {
  background: #d0e2fc;
}

.status-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-pending, .status-pending_upload { background: #fff3cd; color: #856404; }
.status-pending_review { background: #e3f2fd; color: #1565c0; }
.status-documents_rejected { background: #f8d7da; color: #721c24; }
.status-in_waitlist { background: #d4edda; color: #155724; }
.status-physical_docs_required { background: #e8f0fe; color: #1a5fa4; }
.status-waiting_for_class_start { background: #fef3c7; color: #92400e; }
.status-completed { background: #c8e6c9; color: #1b5e20; }

/* Documents */
.docs-grid {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.doc-card {
  background: #fafbff;
  border: 1px solid #e8f0fe;
  border-radius: 10px;
  overflow: hidden;
}

.doc-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1.25rem;
  background: #f0f5ff;
  border-bottom: 1px solid #e8f0fe;
}

.doc-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1a1a2e;
}

.doc-status-badge {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 0.2rem 0.6rem;
  border-radius: 10px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.doc-status-accepted { background: #d4edda; color: #155724; }
.doc-status-uploaded { background: #fff3cd; color: #856404; }
.doc-status-rejected { background: #f8d7da; color: #721c24; }
.doc-status-pending { background: #e8e8e8; color: #666; }

.doc-file-row {
  padding: 0.75rem 1.25rem;
}

.slot-file {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.file-link {
  font-size: 0.82rem;
  color: #1a5fa4;
  text-decoration: none;
  word-break: break-all;
}

.file-link:hover {
  text-decoration: underline;
}

.file-meta {
  font-size: 0.7rem;
  color: #999;
}

.slot-empty-text {
  font-size: 0.82rem;
  color: #999;
  font-style: italic;
}

.empty {
  padding: 1.5rem;
  text-align: center;
  color: #999;
  font-size: 0.9rem;
}

@media (max-width: 768px) {
  .summary-card {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }
}
</style>
