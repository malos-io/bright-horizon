<template>
  <div class="page">
    <div class="page-header">
      <h2>TESDA Instructor Directory</h2>
      <div class="header-actions">
        <select v-model="courseFilter" class="filter-select">
          <option value="">All Courses</option>
          <option v-for="c in courses" :key="c" :value="c">{{ c }}</option>
        </select>
        <select v-model="activeFilter" class="filter-select">
          <option value="">All</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
        <select v-model="contactedFilter" class="filter-select">
          <option value="">Contacted?</option>
          <option value="yes">Contacted</option>
          <option value="no">Not Contacted</option>
        </select>
        <div class="search-box">
          <input v-model="search" type="text" placeholder="Search name..." class="search-input" />
        </div>
        <button class="btn-sync" @click="triggerSync" :disabled="syncing">
          {{ syncing ? 'Syncing...' : 'Sync Data' }}
        </button>
      </div>
    </div>

    <div v-if="lastSynced" class="sync-info">
      Last synced: {{ lastSynced }}
    </div>

    <div v-if="loading" class="loading-state">Loading instructors...</div>

    <div v-else-if="filtered.length" class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th class="sortable" @click="toggleSort('name')">Name {{ sortIcon('name') }}</th>
            <th class="sortable" @click="toggleSort('course')">Course {{ sortIcon('course') }}</th>
            <th class="sortable" @click="toggleSort('region')">Region {{ sortIcon('region') }}</th>
            <th>NTTC Cert</th>
            <th class="sortable" @click="toggleSort('valid_until_nttc')">Valid Until {{ sortIcon('valid_until_nttc') }}</th>
            <th class="sortable" @click="toggleSort('status')">Status {{ sortIcon('status') }}</th>
            <th class="sortable" @click="toggleSort('contacted')">Contacted {{ sortIcon('contacted') }}</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filtered" :key="item.id">
            <td class="cell-name">{{ item.name }}</td>
            <td class="cell-course">{{ shortCourse(item.course) }}</td>
            <td>{{ item.region || '--' }}</td>
            <td>{{ item.nttc_cert || item.cert_num || '--' }}</td>
            <td>
              <span :class="['validity-badge', isExpired(item.valid_until_nttc) ? 'expired' : 'valid']">
                {{ item.valid_until_nttc || '--' }}
              </span>
            </td>
            <td>
              <span :class="['status-badge', 'status-' + (item.status || 'new')]">
                {{ formatStatus(item.status) }}
              </span>
              <span v-if="!item.active" class="inactive-badge">Inactive</span>
            </td>
            <td>
              <span :class="['contacted-badge', item.contacted ? 'yes' : 'no']">
                {{ item.contacted ? 'Yes' : 'No' }}
              </span>
            </td>
            <td>
              <button class="btn-edit" @click="openEdit(item)">Edit</button>
              <a v-if="item.detail_link" :href="item.detail_link" target="_blank" class="btn-link">TESDA</a>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else class="empty-state">
      {{ search || courseFilter || activeFilter || contactedFilter ? 'No instructors matching filters' : 'No instructors found. Try syncing data.' }}
    </div>

    <!-- Edit Modal -->
    <div v-if="editing" class="modal-overlay" @click.self="editing = null">
      <div class="modal">
        <h3>{{ editing.name }}</h3>
        <p class="modal-course">{{ editing.course }}</p>

        <label class="field-label">Status</label>
        <select v-model="editForm.status" class="field-input">
          <option value="new">New</option>
          <option value="contacted">Contacted</option>
          <option value="interested">Interested</option>
          <option value="not_interested">Not Interested</option>
        </select>

        <label class="field-label">Contacted</label>
        <div class="toggle-row">
          <input type="checkbox" v-model="editForm.contacted" id="contacted-toggle" />
          <label for="contacted-toggle">{{ editForm.contacted ? 'Yes' : 'No' }}</label>
        </div>

        <label class="field-label">Notes</label>
        <textarea v-model="editForm.notes" class="field-textarea" rows="4" placeholder="Add notes..."></textarea>

        <div class="modal-actions">
          <button class="btn-cancel" @click="editing = null">Cancel</button>
          <button class="btn-save" @click="saveEdit" :disabled="saving">
            {{ saving ? 'Saving...' : 'Save' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import {
  getTesdaInstructors,
  updateTesdaInstructor,
  triggerTesdaSync,
  getTesdaSyncStatus,
} from '../services/api'

const instructors = ref([])
const loading = ref(false)
const syncing = ref(false)
const saving = ref(false)
const search = ref('')
const courseFilter = ref('')
const activeFilter = ref('active')
const contactedFilter = ref('')
const lastSynced = ref('')
const editing = ref(null)
const editForm = ref({ status: 'new', contacted: false, notes: '' })
const sortKey = ref('name')
const sortDir = ref('asc')

const courses = [
  'EVENTS MANAGEMENT SERVICES NC III',
  'BOOKKEEPING NC III',
  'HOUSEKEEPING NC III',
  'HILOT (WELLNESS MASSAGE) NC II',
]

const filtered = computed(() => {
  let list = instructors.value
  if (courseFilter.value) {
    list = list.filter((i) => i.course === courseFilter.value)
  }
  if (activeFilter.value === 'active') {
    list = list.filter((i) => i.active)
  } else if (activeFilter.value === 'inactive') {
    list = list.filter((i) => !i.active)
  }
  if (contactedFilter.value === 'yes') {
    list = list.filter((i) => i.contacted)
  } else if (contactedFilter.value === 'no') {
    list = list.filter((i) => !i.contacted)
  }
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter((i) => i.name?.toLowerCase().includes(q))
  }
  if (sortKey.value) {
    const key = sortKey.value
    const dir = sortDir.value === 'asc' ? 1 : -1
    list = [...list].sort((a, b) => {
      const va = (a[key] ?? '').toString().toLowerCase()
      const vb = (b[key] ?? '').toString().toLowerCase()
      return va < vb ? -dir : va > vb ? dir : 0
    })
  }
  return list
})

function toggleSort(key) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
}

function sortIcon(key) {
  if (sortKey.value !== key) return ''
  return sortDir.value === 'asc' ? '\u25B2' : '\u25BC'
}

function shortCourse(course) {
  if (!course) return '--'
  return course.replace(' NC III', '').replace(' NC II', '')
}

function isExpired(dateStr) {
  if (!dateStr) return false
  const parts = dateStr.split('/')
  if (parts.length !== 3) return false
  const d = new Date(parts[2], parts[0] - 1, parts[1])
  return d < new Date()
}

function formatStatus(status) {
  const map = {
    new: 'New',
    contacted: 'Contacted',
    interested: 'Interested',
    not_interested: 'Not Interested',
  }
  return map[status] || 'New'
}

function openEdit(item) {
  editing.value = item
  editForm.value = {
    status: item.status || 'new',
    contacted: !!item.contacted,
    notes: item.notes || '',
  }
}

async function saveEdit() {
  saving.value = true
  try {
    await updateTesdaInstructor(editing.value.id, editForm.value)
    Object.assign(editing.value, editForm.value)
    editing.value = null
  } catch (err) {
    console.error('Failed to update instructor:', err)
  } finally {
    saving.value = false
  }
}

async function loadData() {
  loading.value = true
  try {
    const [data, syncStatus] = await Promise.all([
      getTesdaInstructors(),
      getTesdaSyncStatus(),
    ])
    instructors.value = data
    if (syncStatus.synced_at) {
      lastSynced.value = new Date(syncStatus.synced_at).toLocaleString('en-PH')
    }
  } catch (err) {
    console.error('Failed to load instructors:', err)
  } finally {
    loading.value = false
  }
}

async function triggerSync() {
  syncing.value = true
  try {
    await triggerTesdaSync()
    alert('Sync job triggered. Data will update in a few minutes.')
  } catch (err) {
    console.error('Failed to trigger sync:', err)
    alert('Failed to trigger sync job.')
  } finally {
    syncing.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.page {
  max-width: 1200px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
  gap: 1rem;
  flex-wrap: wrap;
}

.page-header h2 {
  font-size: 1.25rem;
  color: #1a1a2e;
  white-space: nowrap;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.filter-select {
  padding: 0.4rem 0.6rem;
  font-size: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  outline: none;
  background: #fff;
  cursor: pointer;
}

.filter-select:focus {
  border-color: #1a5fa4;
}

.search-input {
  padding: 0.4rem 0.6rem;
  font-size: 0.8rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  outline: none;
  width: 160px;
}

.search-input:focus {
  border-color: #1a5fa4;
}

.btn-sync {
  padding: 0.4rem 1rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: white;
  background: #1a5fa4;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  white-space: nowrap;
}

.btn-sync:hover {
  background: #0d3b6e;
}

.btn-sync:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.sync-info {
  font-size: 0.75rem;
  color: #999;
  margin-bottom: 1rem;
}

.table-wrap {
  background: white;
  border-radius: 10px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.data-table th {
  background: #f8f9fa;
  padding: 0.75rem 0.75rem;
  text-align: left;
  font-weight: 600;
  color: #555;
  border-bottom: 2px solid #e9ecef;
  white-space: nowrap;
}

.data-table th.sortable {
  cursor: pointer;
  user-select: none;
}

.data-table th.sortable:hover {
  background: #eef1f4;
}

.data-table td {
  padding: 0.6rem 0.75rem;
  border-bottom: 1px solid #f0f0f0;
  vertical-align: middle;
}

.data-table tbody tr:hover {
  background: #f8f9fb;
}

.cell-name {
  font-weight: 600;
  color: #1a1a2e;
}

.cell-course {
  white-space: nowrap;
}

.validity-badge {
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: 4px;
  white-space: nowrap;
}

.validity-badge.valid {
  background: #c8e6c9;
  color: #1b5e20;
}

.validity-badge.expired {
  background: #ffcdd2;
  color: #b71c1c;
}

.status-badge {
  font-size: 0.7rem;
  font-weight: 600;
  padding: 2px 8px;
  border-radius: 12px;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  white-space: nowrap;
}

.status-new {
  background: #e3f2fd;
  color: #1565c0;
}

.status-contacted {
  background: #fff3cd;
  color: #856404;
}

.status-interested {
  background: #c8e6c9;
  color: #1b5e20;
}

.status-not_interested {
  background: #f0f0f0;
  color: #777;
}

.inactive-badge {
  font-size: 0.65rem;
  padding: 1px 6px;
  border-radius: 4px;
  background: #ffcdd2;
  color: #b71c1c;
  margin-left: 4px;
}

.contacted-badge {
  font-size: 0.75rem;
  padding: 2px 8px;
  border-radius: 4px;
}

.contacted-badge.yes {
  background: #c8e6c9;
  color: #1b5e20;
}

.contacted-badge.no {
  background: #f0f0f0;
  color: #999;
}

.btn-edit {
  padding: 3px 10px;
  font-size: 0.75rem;
  color: #1a5fa4;
  background: #e8f0fe;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin-right: 4px;
}

.btn-edit:hover {
  background: #d0e2fc;
}

.btn-link {
  padding: 3px 10px;
  font-size: 0.75rem;
  color: #666;
  background: #f0f0f0;
  border-radius: 4px;
  text-decoration: none;
}

.btn-link:hover {
  background: #e0e0e0;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  width: 100%;
  max-width: 420px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
}

.modal h3 {
  font-size: 1.1rem;
  color: #1a1a2e;
  margin-bottom: 0.25rem;
}

.modal-course {
  font-size: 0.8rem;
  color: #888;
  margin-bottom: 1rem;
}

.field-label {
  display: block;
  font-size: 0.8rem;
  font-weight: 600;
  color: #555;
  margin-bottom: 0.25rem;
  margin-top: 0.75rem;
}

.field-input {
  width: 100%;
  padding: 0.4rem 0.6rem;
  font-size: 0.85rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  outline: none;
}

.field-input:focus {
  border-color: #1a5fa4;
}

.field-textarea {
  width: 100%;
  padding: 0.5rem;
  font-size: 0.85rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  outline: none;
  resize: vertical;
  font-family: inherit;
}

.field-textarea:focus {
  border-color: #1a5fa4;
}

.toggle-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1.25rem;
}

.btn-cancel {
  padding: 0.4rem 1rem;
  font-size: 0.85rem;
  background: #f0f0f0;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  color: #666;
}

.btn-cancel:hover {
  background: #e0e0e0;
}

.btn-save {
  padding: 0.4rem 1rem;
  font-size: 0.85rem;
  background: #1a5fa4;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.btn-save:hover {
  background: #0d3b6e;
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.loading-state,
.empty-state {
  text-align: center;
  color: #999;
  padding: 3rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  font-size: 0.9rem;
}
</style>
