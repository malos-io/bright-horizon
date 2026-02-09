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
        <h2>Enrollment Applications</h2>
        <button class="btn-refresh" @click="loadEnrollments">Refresh</button>
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
            <tr v-for="enrollment in enrollments" :key="enrollment.id">
              <td>
                <button
                  class="btn-view"
                  @click="router.push('/application/' + enrollment.id)"
                  title="View Application"
                >
                  &#128065;
                </button>
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
              <td class="actions-cell">
                <button
                  class="btn-pdf"
                  @click="downloadPdf(enrollment.id)"
                  :disabled="pdfLoading === enrollment.id"
                >
                  {{ pdfLoading === enrollment.id ? 'Exporting...' : 'Export Application to PDF' }}
                </button>
              </td>
            </tr>
            <tr v-if="enrollments.length === 0">
              <td colspan="8" class="empty-state">No enrollment applications yet</td>
            </tr>
          </tbody>
        </table>
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
              <th>Price</th>
              <th>Duration</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="course in courses" :key="course.id || course.slug">
              <td>{{ course.title }}</td>
              <td>{{ course.category }}</td>
              <td>{{ course.price || '--' }}</td>
              <td>{{ course.duration || '--' }}</td>
            </tr>
            <tr v-if="courses.length === 0">
              <td colspan="4" class="empty-state">No courses found</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getCourses, getCategories, getEnrollments, exportEnrollmentPdf } from '../services/api'

const router = useRouter()
const courses = ref([])
const categories = ref([])
const enrollments = ref([])
const pdfLoading = ref(null)

const pendingCount = computed(() =>
  enrollments.value.filter(e =>
    e.status === 'pending' || e.status === 'pending_upload' || e.status === 'pending_review'
  ).length
)

function formatStatus(status) {
  const map = {
    pending: 'Pending',
    pending_upload: 'Pending Upload of Required Documents',
    pending_review: 'Pending Review',
    documents_rejected: 'Docs Rejected',
    documents_accepted: 'Docs Accepted',
    physical_docs_required: 'Physical Docs Required',
    completed: 'Completed',
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

async function downloadPdf(id) {
  pdfLoading.value = id
  try {
    await exportEnrollmentPdf(id)
  } catch (e) {
    console.error('Failed to export PDF:', e)
    alert('Failed to export PDF. Please try again.')
  } finally {
    pdfLoading.value = null
  }
}

async function loadEnrollments() {
  try {
    enrollments.value = await getEnrollments()
  } catch (e) {
    console.error('Failed to load enrollments:', e)
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

.section h2 {
  font-size: 1.1rem;
  color: #1a1a2e;
  margin-bottom: 1rem;
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
.status-documents_accepted { background: #d4edda; color: #155724; }
.status-physical_docs_required { background: #e8f0fe; color: #1a5fa4; }
.status-completed { background: #c8e6c9; color: #1b5e20; }

.actions-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-view {
  padding: 0.3rem 0.5rem;
  font-size: 1rem;
  background: none;
  border: 1px solid #ddd;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
  line-height: 1;
}

.btn-view:hover {
  background: #f0f5ff;
  border-color: #1a5fa4;
}

.btn-pdf {
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

.btn-pdf:hover:not(:disabled) {
  background: #d0e2fc;
}

.btn-pdf:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.empty-state {
  text-align: center;
  color: #999;
  padding: 2rem !important;
}

@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
