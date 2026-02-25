<template>
  <div class="course-detail">
    <div class="detail-header">
      <button class="btn-back" @click="router.push('/courses')">&#8592; Back to Courses</button>
    </div>

    <div v-if="loading" class="loading-state">Loading course...</div>
    <div v-else-if="!course" class="empty-state">Course not found</div>

    <template v-else>
      <!-- Course summary -->
      <div class="summary-card">
        <div class="summary-info">
          <h2>{{ course.title }}</h2>
          <p class="summary-meta">{{ course.category }} &middot; {{ course.instructor?.name || 'TBA' }}</p>
        </div>
        <div class="summary-stats">
          <span class="stat-badge">{{ totalBatches }} {{ totalBatches === 1 ? 'batch' : 'batches' }}</span>
          <span class="stat-badge stat-students">{{ totalStudents }} {{ totalStudents === 1 ? 'student' : 'students' }}</span>
        </div>
      </div>

      <!-- Course Pricing -->
      <div class="section">
        <div class="section-header">
          <h3 class="section-title">Course Pricing</h3>
          <div v-if="!editingPrice" class="section-actions">
            <button class="btn-action" @click="startEditingPrice">Edit</button>
          </div>
        </div>
        <div v-if="!editingPrice" class="info-grid">
          <div class="info-item">
            <span class="info-label">Price</span>
            <span class="info-value">{{ course.price > 0 ? '₱' + Number(course.price).toLocaleString() : 'Free / TBA' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Discounted Price</span>
            <span class="info-value">{{ course.discounted_price != null ? '₱' + Number(course.discounted_price).toLocaleString() : '--' }}</span>
          </div>
        </div>
        <div v-else class="edit-form">
          <div class="form-row">
            <label>Price (₱)</label>
            <input type="number" min="0" step="0.01" v-model="priceForm.price" />
          </div>
          <div class="form-row">
            <label>Discounted Price (₱)</label>
            <input type="number" min="0" step="0.01" v-model="priceForm.discountedPrice" placeholder="Leave empty for no discount" />
          </div>
          <div class="form-actions">
            <button class="btn-action btn-action-green" :disabled="savingPrice" @click="savePrice">{{ savingPrice ? 'Saving...' : 'Save' }}</button>
            <button class="btn-action" @click="editingPrice = false">Cancel</button>
          </div>
        </div>
      </div>

      <!-- Active Batch -->
      <div class="section">
        <div class="section-header">
          <h3 class="section-title">
            {{ activeBatch ? 'Active Class Batch' : 'No Active Class' }}
            <span v-if="activeBatch" class="status-indicator" :class="'status-' + activeBatch.status">
              {{ activeBatch.status === 'active' ? 'Active' : 'Enrollment Closed' }}
            </span>
          </h3>
          <div v-if="activeBatch && !editing" class="section-actions">
            <button class="btn-action" @click="startEditing">Edit</button>
            <button
              v-if="activeBatch.status === 'active'"
              class="btn-action btn-action-yellow"
              @click="handleCloseEnrollment"
              :disabled="saving"
            >Close Enrollment</button>
            <button
              class="btn-action btn-action-red"
              @click="handleCloseBatch"
              :disabled="saving"
            >Close Class Batch</button>
          </div>
        </div>

        <!-- No active batch — show Start button -->
        <div v-if="!activeBatch && !showNewBatch" class="no-batch">
          <p>No active class batch for this course. Start one to set the start date, instructor, and open enrollment.</p>
          <button class="btn-action btn-action-green" @click="showNewBatch = true">Start A New Class Batch</button>
        </div>

        <!-- Active batch — view mode -->
        <div v-if="activeBatch && !editing" class="info-grid">
          <div class="info-item">
            <span class="info-label">Start Date</span>
            <span class="info-value">{{ formatStartDate(activeBatch.start_date) }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Enrollment Deadline</span>
            <span class="info-value">{{ formatStartDate(activeBatch.enrollment_deadline) || '--' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Instructor</span>
            <span class="info-value">{{ activeBatch.instructor?.name || 'TBA' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Instructor Title</span>
            <span class="info-value">{{ activeBatch.instructor?.title || '--' }}</span>
          </div>
          <div class="info-item">
            <span class="info-label">Enrolled Students</span>
            <span class="info-value">{{ activeBatch.student_count }}</span>
          </div>
        </div>

        <!-- Active batch students list -->
        <div v-if="activeBatch && !editing && activeBatch.students?.length" class="batch-students" style="margin-top: 1rem;">
          <table class="data-table">
            <thead>
              <tr>
                <th></th>
                <th>Name</th>
                <th>Email</th>
                <th>Enrollment Date</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in activeBatch.students" :key="s.enrollment_id">
                <td>
                  <button class="btn-detail" @click="router.push('/application/' + s.enrollment_id)">View</button>
                </td>
                <td>{{ s.lastName }}, {{ s.firstName }}</td>
                <td>{{ s.email }}</td>
                <td>{{ formatDate(s.created_at) }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Edit active batch mode -->
        <div v-if="editing" class="edit-form">
          <div class="form-row">
            <label>Start Date</label>
            <input type="date" v-model="editForm.startDate" />
          </div>
          <div class="form-row">
            <label>Enrollment Deadline</label>
            <input type="date" v-model="editForm.deadline" />
          </div>
          <div class="form-row">
            <label>Instructor Name</label>
            <input type="text" v-model="editForm.instructorName" />
          </div>
          <div class="form-row">
            <label>Instructor Title</label>
            <input type="text" v-model="editForm.instructorTitle" />
          </div>
          <div class="form-actions">
            <button class="btn-action btn-action-green" :disabled="saving" @click="saveEdit">{{ saving ? 'Saving...' : 'Save' }}</button>
            <button class="btn-action" @click="editing = false">Cancel</button>
          </div>
        </div>

        <!-- New Batch form -->
        <div v-if="showNewBatch" class="edit-form">
          <p class="form-note">Starting a new batch will make this the active class. The start date, instructor, and deadline will be shown on the public page and Dashboard.</p>
          <div class="form-row">
            <label>Start Date *</label>
            <input type="date" v-model="newBatchForm.startDate" />
          </div>
          <div class="form-row">
            <label>Enrollment Deadline</label>
            <input type="date" v-model="newBatchForm.deadline" />
          </div>
          <div class="form-row">
            <label>Instructor Name</label>
            <input type="text" v-model="newBatchForm.instructorName" placeholder="TBA" />
          </div>
          <div class="form-row">
            <label>Instructor Title</label>
            <input type="text" v-model="newBatchForm.instructorTitle" placeholder="Certified TESDA Trainer" />
          </div>
          <div class="form-actions">
            <button class="btn-action btn-action-green" :disabled="saving || !newBatchForm.startDate" @click="handleCreateBatch">{{ saving ? 'Creating...' : 'Start Batch' }}</button>
            <button class="btn-action" @click="showNewBatch = false">Cancel</button>
          </div>
        </div>
      </div>

      <!-- Batch History -->
      <div class="section">
        <h3 class="section-title">Batch History</h3>
        <div v-if="batches.length" class="batches-list">
          <div class="batch-card" v-for="batch in batches" :key="batch.batch_id || batch.batch_number">
            <div class="batch-header" @click="toggleBatch(batch.batch_id || batch.batch_number)">
              <div class="batch-info">
                <span class="batch-label">{{ batch.batch_label }}</span>
                <span v-if="batch.start_date" class="batch-date">{{ formatStartDate(batch.start_date) }}</span>
                <span v-else class="batch-date batch-date-muted">(Pre-tracking)</span>
              </div>
              <div class="batch-right">
                <span class="batch-count">{{ batch.student_count }} {{ batch.student_count === 1 ? 'student' : 'students' }}</span>
                <span class="batch-toggle">{{ expandedBatch === (batch.batch_id || batch.batch_number) ? '&#9650;' : '&#9660;' }}</span>
              </div>
            </div>
            <div v-if="expandedBatch === (batch.batch_id || batch.batch_number)" class="batch-students">
              <table v-if="batch.students.length" class="data-table">
                <thead>
                  <tr>
                    <th></th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Enrollment Date</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="s in batch.students" :key="s.enrollment_id">
                    <td>
                      <button class="btn-detail" @click="router.push('/application/' + s.enrollment_id)">View</button>
                    </td>
                    <td>{{ s.lastName }}, {{ s.firstName }}</td>
                    <td>{{ s.email }}</td>
                    <td>{{ formatDate(s.created_at) }}</td>
                  </tr>
                </tbody>
              </table>
              <div v-else class="empty-batch">No students in this batch</div>
            </div>
          </div>
        </div>
        <div v-else class="empty">No completed batches yet</div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getCourseBatches, createBatch, editBatch, closeBatchEnrollment, closeBatch, updateCoursePrice } from '../services/api'

const route = useRoute()
const router = useRouter()

const course = ref(null)
const activeBatch = ref(null)
const batches = ref([])
const totalStudents = ref(0)
const totalBatches = ref(0)
const loading = ref(true)
const expandedBatch = ref(null)

const editing = ref(false)
const saving = ref(false)
const editForm = ref({ startDate: '', deadline: '', instructorName: '', instructorTitle: '' })
const showNewBatch = ref(false)
const newBatchForm = ref({ startDate: '', deadline: '', instructorName: '', instructorTitle: '' })

const editingPrice = ref(false)
const savingPrice = ref(false)
const priceForm = ref({ price: 0, discountedPrice: '' })

function toggleBatch(key) {
  expandedBatch.value = expandedBatch.value === key ? null : key
}

function startEditing() {
  if (!activeBatch.value) return
  editForm.value = {
    startDate: activeBatch.value.start_date || '',
    deadline: activeBatch.value.enrollment_deadline || '',
    instructorName: activeBatch.value.instructor?.name || '',
    instructorTitle: activeBatch.value.instructor?.title || '',
  }
  editing.value = true
}

function startEditingPrice() {
  if (!course.value) return
  priceForm.value = {
    price: course.value.price || 0,
    discountedPrice: course.value.discounted_price != null ? course.value.discounted_price : '',
  }
  editingPrice.value = true
}

async function savePrice() {
  savingPrice.value = true
  try {
    const payload = { price: Number(priceForm.value.price) || 0 }
    const dp = priceForm.value.discountedPrice
    payload.discounted_price = dp !== '' && dp !== null ? Number(dp) : null
    await updateCoursePrice(route.params.slug, payload)
    editingPrice.value = false
    await reload()
  } catch (err) {
    console.error('Failed to save price:', err)
    alert(err.response?.data?.detail || 'Failed to save price')
  } finally {
    savingPrice.value = false
  }
}

async function saveEdit() {
  if (!activeBatch.value) return
  saving.value = true
  try {
    const payload = {}
    if (editForm.value.startDate) {
      payload.start_date = editForm.value.startDate
    }
    payload.enrollment_deadline = editForm.value.deadline || null
    payload.instructor = {
      name: editForm.value.instructorName || 'TBA',
      title: editForm.value.instructorTitle || '',
      bio: activeBatch.value.instructor?.bio || '',
      image: activeBatch.value.instructor?.image || '',
    }
    await editBatch(route.params.slug, activeBatch.value.batch_id, payload)
    editing.value = false
    await reload()
  } catch (err) {
    console.error('Failed to save:', err)
    alert(err.response?.data?.detail || 'Failed to save changes')
  } finally {
    saving.value = false
  }
}

async function handleCreateBatch() {
  if (!newBatchForm.value.startDate) return
  saving.value = true
  try {
    const payload = {
      start_date: newBatchForm.value.startDate,
      enrollment_deadline: newBatchForm.value.deadline || null,
      instructor: {
        name: newBatchForm.value.instructorName || '',
        title: newBatchForm.value.instructorTitle || '',
      },
    }
    await createBatch(route.params.slug, payload)
    showNewBatch.value = false
    newBatchForm.value = { startDate: '', deadline: '', instructorName: '', instructorTitle: '' }
    await reload()
  } catch (err) {
    console.error('Failed to create batch:', err)
    alert(err.response?.data?.detail || 'Failed to create batch')
  } finally {
    saving.value = false
  }
}

async function handleCloseEnrollment() {
  if (!activeBatch.value) return
  if (!confirm('Close enrollment for this batch? Students at "Physical Documents Required" status will be moved back to waitlist.')) return
  saving.value = true
  try {
    const result = await closeBatchEnrollment(route.params.slug, activeBatch.value.batch_id)
    alert(`Enrollment closed. ${result.reverted_to_waitlist} student(s) moved back to waitlist.`)
    await reload()
  } catch (err) {
    console.error('Failed to close enrollment:', err)
    alert(err.response?.data?.detail || 'Failed to close enrollment')
  } finally {
    saving.value = false
  }
}

async function handleCloseBatch() {
  if (!activeBatch.value) return
  if (!confirm('Close this class batch? The course will revert to TBA on the public page and Dashboard.')) return
  saving.value = true
  try {
    await closeBatch(route.params.slug, activeBatch.value.batch_id)
    await reload()
  } catch (err) {
    console.error('Failed to close batch:', err)
    alert(err.response?.data?.detail || 'Failed to close batch')
  } finally {
    saving.value = false
  }
}

async function reload() {
  const data = await getCourseBatches(route.params.slug)
  course.value = data.course
  activeBatch.value = data.active_batch || null
  batches.value = data.batches || []
  totalStudents.value = data.total_students || 0
  totalBatches.value = data.total_batches || 0
}

function formatStartDate(dateStr) {
  if (!dateStr || dateStr === 'TBA') return 'TBA'
  try {
    const d = new Date(dateStr + 'T00:00:00')
    if (isNaN(d)) return dateStr
    return d.toLocaleDateString('en-PH', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  } catch {
    return dateStr
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

onMounted(async () => {
  try {
    await reload()
    if (batches.value.length === 1) {
      expandedBatch.value = batches.value[0].batch_id || batches.value[0].batch_number
    }
  } catch (e) {
    console.error('Failed to load course:', e)
    course.value = null
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.course-detail {
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

.summary-stats {
  display: flex;
  gap: 0.5rem;
}

.stat-badge {
  display: inline-block;
  padding: 0.3rem 0.8rem;
  border-radius: 12px;
  font-size: 0.8rem;
  font-weight: 600;
  background: #e8f0fe;
  color: #1a5fa4;
}

.stat-students {
  background: #c8e6c9;
  color: #1b5e20;
}

.section {
  background: white;
  border-radius: 12px;
  padding: 1.5rem 2rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  margin-bottom: 1.5rem;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-header .section-title {
  margin-bottom: 0;
}

.section-title {
  font-size: 1rem;
  font-weight: 700;
  color: #1a1a2e;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-indicator {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 8px;
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}

.status-active {
  background: #c8e6c9;
  color: #1b5e20;
}

.status-enrollment_closed {
  background: #fff3cd;
  color: #856404;
}

.section-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-action {
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

.btn-action:hover {
  background: #d0e2fc;
}

.btn-action:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-action-green {
  color: #1b5e20;
  background: #c8e6c9;
}

.btn-action-green:hover {
  background: #a5d6a7;
}

.btn-action-yellow {
  color: #856404;
  background: #fff3cd;
}

.btn-action-yellow:hover {
  background: #ffe69c;
}

.btn-action-red {
  color: #721c24;
  background: #f8d7da;
}

.btn-action-red:hover {
  background: #f1aeb5;
}

.no-batch {
  text-align: center;
  padding: 1rem 0;
}

.no-batch p {
  font-size: 0.85rem;
  color: #888;
  margin-bottom: 1rem;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: #888;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.info-value {
  font-size: 0.9rem;
  color: #333;
}

.edit-form {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.form-row {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.form-row label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #666;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.form-row input {
  padding: 0.5rem 0.75rem;
  font-size: 0.85rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  outline: none;
  transition: border-color 0.2s;
  max-width: 300px;
}

.form-row input:focus {
  border-color: #1a5fa4;
}

.form-note {
  font-size: 0.82rem;
  color: #666;
  background: #fff8e1;
  padding: 0.6rem 0.8rem;
  border-radius: 6px;
  border-left: 3px solid #ffc107;
}

.form-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.batches-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.batch-card {
  border: 1px solid #e8f0fe;
  border-radius: 10px;
  overflow: hidden;
}

.batch-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.85rem 1.25rem;
  background: #f0f5ff;
  cursor: pointer;
  transition: background 0.2s;
}

.batch-header:hover {
  background: #e4ecfa;
}

.batch-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.batch-label {
  font-size: 0.9rem;
  font-weight: 700;
  color: #1a1a2e;
}

.batch-date {
  font-size: 0.8rem;
  color: #555;
}

.batch-date-muted {
  color: #999;
  font-style: italic;
}

.batch-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.batch-count {
  font-size: 0.8rem;
  font-weight: 600;
  color: #666;
}

.batch-toggle {
  font-size: 0.7rem;
  color: #999;
}

.batch-students {
  border-top: 1px solid #e8f0fe;
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

.empty,
.empty-batch {
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
  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
  .batch-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
</style>
