<template>
  <div class="dashboard">
    <div class="stats-grid">
      <div class="stat-card">
        <h3>Total Courses</h3>
        <p class="stat-value">{{ courses.length }}</p>
      </div>
      <div class="stat-card">
        <h3>Categories</h3>
        <p class="stat-value">{{ categories.length }}</p>
      </div>
      <div class="stat-card">
        <h3>Pending Enrollments</h3>
        <p class="stat-value">{{ pendingCount }}</p>
      </div>
      <div class="stat-card">
        <h3>Total Enrollments</h3>
        <p class="stat-value">{{ enrollments.length }}</p>
      </div>
    </div>

    <div class="section">
      <div class="section-header">
        <h2>{{ sectionTitle }}</h2>
        <div class="section-header-actions">
          <button class="btn-tab" :class="{ active: filterMode === 'active' }" @click="filterMode = 'active'">Active</button>
          <button class="btn-tab" :class="{ active: filterMode === 'all' }" @click="filterMode = 'all'">All</button>
          <select v-model="filterMode" class="status-filter">
            <option value="active">Active</option>
            <option value="all">All Statuses</option>
            <option value="pending">Pending</option>
            <option value="pending_upload">Pending Upload</option>
            <option value="pending_review">Pending Review</option>
            <option value="documents_rejected">Docs Rejected</option>
            <option value="in_waitlist">In Waitlist</option>
            <option value="physical_docs_required">Interview Required</option>
            <option value="completed">Completed</option>
            <option value="archived">Archived</option>
            <option value="withdrawn">Withdrawn</option>
            <option value="cancelled">Cancelled</option>
          </select>
          <select v-model="courseFilter" class="status-filter">
            <option value="all">All Courses</option>
            <option v-for="course in courses" :key="course.id || course.slug" :value="course.title">
              {{ course.title }}
            </option>
          </select>
          <button class="btn-export" @click="exportCSV">Export CSV</button>
          <button class="btn-refresh" @click="loadEnrollments">Refresh</button>
        </div>
      </div>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th></th>
              <th>Name</th>
              <th>Email</th>
              <th>Contact</th>
              <th>Course</th>
              <th>Status</th>
              <th>Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="enrollment in paginatedEnrollments" :key="enrollment.id">
              <td>
                <button class="btn-detail" @click="router.push('/application/' + enrollment.id)">View</button>
              </td>
              <td>{{ enrollment.lastName }}, {{ enrollment.firstName }} {{ enrollment.middleName }}</td>
              <td>{{ enrollment.email }}</td>
              <td>{{ enrollment.contactNo || enrollment.phone || '--' }}</td>
              <td>{{ enrollment.course }}</td>
              <td>
                <span class="status-badge" :class="'status-' + enrollment.status">
                  {{ formatStatus(enrollment.status) }}
                </span>
              </td>
              <td>{{ formatDate(enrollment.created_at) }}</td>
              <td>
                <button
                  v-if="enrollment.status === 'in_waitlist'"
                  class="btn-action"
                  @click="handleSendInterview(enrollment)"
                  :disabled="sendingInterview === enrollment.id"
                >
                  {{ sendingInterview === enrollment.id ? 'Sending...' : 'Send Interview Schedule' }}
                </button>
                <button
                  v-if="enrollment.status === 'physical_docs_required'"
                  class="btn-action btn-action-green"
                  @click="handleCompleteEnrollment(enrollment)"
                  :disabled="completingEnrollment === enrollment.id"
                >
                  {{ completingEnrollment === enrollment.id ? 'Completing...' : 'Complete' }}
                </button>
              </td>
            </tr>
            <tr v-if="displayedEnrollments.length === 0">
              <td colspan="8" class="empty-state">No enrollment applications found</td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="totalPages > 1" class="pagination">
        <button class="btn-page" :disabled="currentPage === 1" @click="currentPage--">&laquo; Prev</button>
        <span class="page-info">Page {{ currentPage }} of {{ totalPages }} ({{ displayedEnrollments.length }} results)</span>
        <button class="btn-page" :disabled="currentPage === totalPages" @click="currentPage++">Next &raquo;</button>
      </div>
    </div>

    <div class="section" style="margin-top: 1.5rem;">
      <h2>Courses</h2>
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>Title</th>
              <th>Category</th>
              <th>Next Start Date</th>
              <th>Instructor</th>
              <th>Class Size</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="course in courses" :key="course.id || course.slug">
              <td>{{ course.title }}</td>
              <td>{{ course.category }}</td>
              <td>{{ formatStartDate(course.start_dates) }}</td>
              <td>{{ course.instructor?.name || 'TBA' }}</td>
              <td>{{ course.class_size || '--' }} students</td>
            </tr>
            <tr v-if="courses.length === 0">
              <td colspan="5" class="empty-state">No courses found</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getCourses, getCategories, getEnrollments, sendInterviewSchedule, completeEnrollment } from '../services/api'

const router = useRouter()
const courses = ref([])
const categories = ref([])
const enrollments = ref([])
const sendingInterview = ref(null)
const completingEnrollment = ref(null)
const filterMode = ref('active')
const courseFilter = ref('all')
const currentPage = ref(1)
const perPage = 10

function formatStartDate(startDates) {
  const val = (startDates && startDates.length) ? startDates[0] : ''
  if (!val || val === 'TBA') return 'TBA'
  const d = new Date(val + 'T00:00:00')
  if (isNaN(d)) return val
  return d.toLocaleDateString('en-PH', { year: 'numeric', month: 'long', day: 'numeric' })
}

const pendingCount = computed(() =>
  enrollments.value.filter(e =>
    e.status === 'pending' || e.status === 'pending_upload' || e.status === 'pending_review'
  ).length
)

const INACTIVE_STATUSES = ['archived', 'withdrawn', 'cancelled', 'completed']

const sectionTitle = computed(() => {
  if (filterMode.value === 'active') return 'Active Enrollment Applications'
  if (filterMode.value === 'all') return 'All Enrollment Applications'
  return `${formatStatus(filterMode.value)} Applications`
})

const displayedEnrollments = computed(() => {
  let result
  if (filterMode.value === 'active') {
    result = enrollments.value.filter(e => !INACTIVE_STATUSES.includes(e.status))
  } else if (filterMode.value === 'all') {
    result = enrollments.value
  } else {
    result = enrollments.value.filter(e => e.status === filterMode.value)
  }
  if (courseFilter.value !== 'all') {
    result = result.filter(e => e.course === courseFilter.value)
  }
  return result
})

const totalPages = computed(() => Math.max(1, Math.ceil(displayedEnrollments.value.length / perPage)))

const paginatedEnrollments = computed(() => {
  const start = (currentPage.value - 1) * perPage
  return displayedEnrollments.value.slice(start, start + perPage)
})

watch([filterMode, courseFilter], () => {
  currentPage.value = 1
})

function buildMailingAddress(e) {
  return [e.street, e.barangay, e.district, e.city, e.province, e.region]
    .filter(Boolean)
    .join(', ')
}

function escapeCsvField(val, forceText = false) {
  const str = String(val ?? '')
  if (forceText && str) {
    return '="' + str.replace(/"/g, '""') + '"'
  }
  if (str.includes(',') || str.includes('"') || str.includes('\n')) {
    return '"' + str.replace(/"/g, '""') + '"'
  }
  return str
}

function exportCSV() {
  const rows = displayedEnrollments.value
  if (rows.length === 0) {
    alert('No data to export.')
    return
  }
  const headers = ['Name', 'Course', 'Email', 'Contact', 'Mailing Address', 'Status']
  const csvRows = [headers.join(',')]
  for (const e of rows) {
    const name = `${e.lastName}, ${e.firstName} ${e.middleName || ''}`.trim()
    const contact = e.contactNo || e.phone || ''
    const line = [
      escapeCsvField(name),
      escapeCsvField(e.course),
      escapeCsvField(e.email),
      escapeCsvField(contact, true),
      escapeCsvField(buildMailingAddress(e)),
      escapeCsvField(formatStatus(e.status)),
    ]
    csvRows.push(line.join(','))
  }
  const blob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8;' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  const courseSuffix = courseFilter.value !== 'all' ? `-${courseFilter.value.replace(/\s+/g, '_')}` : ''
  a.download = `enrollments-${filterMode.value}${courseSuffix}-${new Date().toISOString().slice(0, 10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

function formatStatus(status) {
  const map = {
    pending: 'Pending',
    pending_upload: 'Pending Upload of Required Documents',
    pending_review: 'Pending Review',
    documents_rejected: 'Docs Rejected',
    in_waitlist: 'In Waitlist',
    physical_docs_required: 'Physical Documents and Interview Required',
    completed: 'Completed',
    archived: 'Archived',
    withdrawn: 'Withdrawn',
    cancelled: 'Cancelled',
  }
  return map[status] || status
}

function formatDate(dateStr) {
  if (!dateStr) return '--'
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-PH', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

async function loadEnrollments() {
  try {
    enrollments.value = await getEnrollments()
  } catch (e) {
    console.error('Failed to load enrollments:', e)
  }
}

async function handleSendInterview(enrollment) {
  const course = courses.value.find(c => c.title === enrollment.course)
  const hasStartDate = course?.start_dates?.[0] && course.start_dates[0] !== 'TBA'

  if (!hasStartDate) {
    alert('This course has no start date set. Please set up an active batch in the Courses page first.')
    return
  }

  if (!confirm(`Send interview schedule email to ${enrollment.firstName} ${enrollment.lastName} (${enrollment.email})?`)) {
    return
  }

  sendingInterview.value = enrollment.id
  try {
    await sendInterviewSchedule(enrollment.id)
    alert('Interview schedule email sent successfully.')
    await loadEnrollments()
  } catch (e) {
    const msg = e.response?.data?.detail || 'Failed to send interview schedule.'
    alert(msg)
  } finally {
    sendingInterview.value = null
  }
}

async function handleCompleteEnrollment(enrollment) {
  if (!confirm(`Complete enrollment for ${enrollment.firstName} ${enrollment.lastName} (${enrollment.email})?\n\nThis will finalize their enrollment and activate their student account.`)) {
    return
  }

  completingEnrollment.value = enrollment.id
  try {
    await completeEnrollment(enrollment.id)
    alert('Enrollment completed successfully. Student account has been activated.')
    await loadEnrollments()
  } catch (e) {
    const msg = e.response?.data?.detail || 'Failed to complete enrollment.'
    alert(msg)
  } finally {
    completingEnrollment.value = null
  }
}

onMounted(async () => {
  try {
    courses.value = await getCourses()
  } catch (e) {
    console.error('Failed to load courses:', e)
  }
  try {
    categories.value = await getCategories()
  } catch (e) {
    console.error('Failed to load categories:', e)
  }
  loadEnrollments()
})
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.stat-card h3 {
  font-size: 0.85rem;
  color: #666;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.stat-value {
  font-size: 2rem;
  font-weight: 700;
  color: #1a5fa4;
}

.section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-header h2 {
  font-size: 1.1rem;
  color: #1a1a2e;
}

.section-header-actions {
  display: flex;
  gap: 0.5rem;
}

.section h2 {
  font-size: 1.1rem;
  color: #1a1a2e;
  margin-bottom: 1rem;
}

.btn-export {
  padding: 0.4rem 1rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: #fff;
  background: #166534;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-export:hover {
  background: #14532d;
}

.btn-refresh {
  padding: 0.4rem 1rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: #1a5fa4;
  background: #e8f0fe;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-refresh:hover {
  background: #d0e2fc;
}

.btn-tab {
  padding: 0.4rem 1rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: #666;
  background: #f0f0f0;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s, color 0.2s;
}

.btn-tab:hover {
  background: #e0e0e0;
}

.btn-tab.active {
  color: #1a5fa4;
  background: #e8f0fe;
}

.status-filter {
  padding: 0.4rem 0.6rem;
  font-size: 0.8rem;
  font-weight: 500;
  border: 1px solid #ddd;
  border-radius: 6px;
  color: #333;
  background: white;
  cursor: pointer;
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
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.data-table th {
  font-size: 0.8rem;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.data-table td {
  font-size: 0.9rem;
  color: #333;
}

.data-table tbody tr:hover {
  background: #f8f9ff;
}

.status-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-pending {
  background: #fff3cd;
  color: #856404;
}

.status-approved {
  background: #d4edda;
  color: #155724;
}

.status-rejected, .status-documents_rejected {
  background: #f8d7da;
  color: #721c24;
}

.status-pending_upload { background: #fff3cd; color: #856404; }
.status-pending_review { background: #e3f2fd; color: #1565c0; }
.status-in_waitlist { background: #d4edda; color: #155724; }
.status-physical_docs_required { background: #e8f0fe; color: #1a5fa4; }
.status-completed { background: #c8e6c9; color: #1b5e20; }
.status-archived { background: #e0e0e0; color: #616161; }
.status-withdrawn { background: #fef2f2; color: #991b1b; }
.status-cancelled { background: #fefce8; color: #92400e; }

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

.btn-action {
  padding: 0.3rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #fff;
  background: #1a5fa4;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
  white-space: nowrap;
}

.btn-action:hover:not(:disabled) {
  background: #15508a;
}

.btn-action:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-action-green {
  background: #166534;
}

.btn-action-green:hover:not(:disabled) {
  background: #14532d;
}

.empty-state {
  text-align: center;
  color: #999;
  padding: 2rem !important;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #eee;
}

.btn-page {
  padding: 0.4rem 1rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: #1a5fa4;
  background: #e8f0fe;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-page:hover:not(:disabled) {
  background: #d0e2fc;
}

.btn-page:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-info {
  font-size: 0.8rem;
  color: #666;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
