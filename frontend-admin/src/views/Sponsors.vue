<template>
  <div class="sponsors-admin">
    <div class="page-header">
      <h2>Sponsors</h2>
      <button class="btn-primary" @click="openAddForm">+ Add Sponsor</button>
    </div>

    <!-- Add / Edit Form -->
    <div v-if="showForm" class="form-card">
      <h3>{{ editing ? 'Edit Sponsor' : 'Add Sponsor' }}</h3>
      <div class="form-grid">
        <div class="form-group">
          <label>Name *</label>
          <input v-model="form.name" class="form-input" placeholder="e.g. Hon. Juan Dela Cruz" />
        </div>
        <div class="form-group">
          <label>Title *</label>
          <input v-model="form.title" class="form-input" placeholder="e.g. City Councilor" />
        </div>
        <div class="form-group">
          <label>Position / Location</label>
          <input v-model="form.position" class="form-input" placeholder="e.g. District 1, Siayan" />
        </div>
        <div class="form-group full-width">
          <label>Message / Quote</label>
          <textarea v-model="form.message" class="form-input" rows="2" placeholder="Optional quote from the sponsor"></textarea>
        </div>
        <div class="form-group full-width">
          <label>Photo</label>
          <div class="image-upload-row">
            <img v-if="editing && editingImage && !form.imageFile" :src="editingImage" class="preview-thumb" />
            <img v-if="imagePreview" :src="imagePreview" class="preview-thumb" />
            <input type="file" accept="image/*" @change="onImageChange" ref="fileInput" />
          </div>
        </div>
      </div>
      <div v-if="formError" class="form-error">{{ formError }}</div>
      <div class="form-actions">
        <button class="btn-cancel" @click="closeForm">Cancel</button>
        <button class="btn-primary" @click="handleSave" :disabled="saving">
          {{ saving ? 'Saving...' : editing ? 'Update' : 'Create' }}
        </button>
      </div>
    </div>

    <!-- Sponsors Table -->
    <div class="table-card">
      <div v-if="loading" class="loading-state">Loading sponsors...</div>
      <div v-else-if="sponsors.length === 0" class="empty-state">No sponsors yet. Click "Add Sponsor" to get started.</div>
      <table v-else class="data-table">
        <thead>
          <tr>
            <th>Order</th>
            <th>Photo</th>
            <th>Name</th>
            <th>Title</th>
            <th>Scholars</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(sponsor, index) in sponsors" :key="sponsor.id">
            <td class="order-cell">
              <button class="btn-order" @click="moveUp(index)" :disabled="index === 0 || reordering">&uarr;</button>
              <button class="btn-order" @click="moveDown(index)" :disabled="index === sponsors.length - 1 || reordering">&darr;</button>
            </td>
            <td>
              <img v-if="sponsor.image" :src="sponsor.image" :alt="sponsor.name" class="thumb-img" />
              <svg v-else class="thumb-placeholder" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
                <rect width="80" height="80" fill="#e0e0e0" rx="8"/>
                <circle cx="40" cy="30" r="12" fill="#bbb"/>
                <ellipse cx="40" cy="62" rx="20" ry="14" fill="#bbb"/>
              </svg>
            </td>
            <td>
              <strong>{{ sponsor.name }}</strong>
              <div v-if="sponsor.position" class="sub-text">{{ sponsor.position }}</div>
            </td>
            <td>{{ sponsor.title }}</td>
            <td class="scholars-cell">
              <span class="scholars-count">{{ sponsor.scholars_sponsored }}</span>
              <button v-if="sponsor.scholars_sponsored > 0" class="btn-scholars" @click="$router.push('/sponsors/' + sponsor.id + '/scholars')">
                View
              </button>
            </td>
            <td class="actions-cell">
              <button class="btn-edit" @click="startEdit(sponsor)">Edit</button>
              <button class="btn-delete" @click="handleDelete(sponsor)">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getSponsors, createSponsor, updateSponsor, deleteSponsor, reorderSponsors } from '../services/api'

const sponsors = ref([])
const loading = ref(false)
const showForm = ref(false)
const editing = ref(null)
const editingImage = ref(null)
const saving = ref(false)
const reordering = ref(false)
const formError = ref('')
const fileInput = ref(null)
const imagePreview = ref(null)

const form = ref({
  name: '',
  title: '',
  position: '',
  message: '',
  imageFile: null,
})

async function loadSponsors() {
  loading.value = true
  try {
    sponsors.value = await getSponsors()
  } catch (e) {
    console.error('Failed to load sponsors:', e)
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.value = { name: '', title: '', position: '', message: '', imageFile: null }
  editing.value = null
  editingImage.value = null
  formError.value = ''
  imagePreview.value = null
  if (fileInput.value) fileInput.value.value = ''
}

function openAddForm() {
  resetForm()
  showForm.value = true
}

function closeForm() {
  resetForm()
  showForm.value = false
}

function startEdit(sponsor) {
  editing.value = sponsor.id
  editingImage.value = sponsor.image
  imagePreview.value = null
  form.value = {
    name: sponsor.name,
    title: sponsor.title,
    position: sponsor.position || '',
    message: sponsor.message || '',
    imageFile: null,
  }
  showForm.value = true
}

function onImageChange(event) {
  const file = event.target.files[0]
  if (file) {
    form.value.imageFile = file
    imagePreview.value = URL.createObjectURL(file)
  }
}

async function handleSave() {
  if (!form.value.name.trim() || !form.value.title.trim()) {
    formError.value = 'Name and Title are required.'
    return
  }

  saving.value = true
  formError.value = ''
  try {
    const fd = new FormData()
    fd.append('name', form.value.name)
    fd.append('title', form.value.title)
    if (form.value.position) fd.append('position', form.value.position)
    if (form.value.message) fd.append('message', form.value.message)
    if (form.value.imageFile) fd.append('image', form.value.imageFile)

    if (editing.value) {
      await updateSponsor(editing.value, fd)
    } else {
      await createSponsor(fd)
    }
    closeForm()
    await loadSponsors()
  } catch (e) {
    formError.value = e.response?.data?.detail || 'Failed to save sponsor.'
  } finally {
    saving.value = false
  }
}

async function handleDelete(sponsor) {
  if (!confirm(`Delete sponsor "${sponsor.name}"? This cannot be undone.`)) return
  try {
    await deleteSponsor(sponsor.id)
    await loadSponsors()
  } catch (e) {
    alert(e.response?.data?.detail || 'Failed to delete sponsor.')
  }
}

async function moveUp(index) {
  if (index === 0) return
  reordering.value = true
  const ids = sponsors.value.map(s => s.id)
  ;[ids[index - 1], ids[index]] = [ids[index], ids[index - 1]]
  try {
    await reorderSponsors(ids)
    await loadSponsors()
  } catch (e) {
    alert('Failed to reorder sponsors.')
  } finally {
    reordering.value = false
  }
}

async function moveDown(index) {
  if (index >= sponsors.value.length - 1) return
  reordering.value = true
  const ids = sponsors.value.map(s => s.id)
  ;[ids[index], ids[index + 1]] = [ids[index + 1], ids[index]]
  try {
    await reorderSponsors(ids)
    await loadSponsors()
  } catch (e) {
    alert('Failed to reorder sponsors.')
  } finally {
    reordering.value = false
  }
}

onMounted(loadSponsors)
</script>

<style scoped>
.sponsors-admin {
  max-width: 1000px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.page-header h2 {
  font-size: 1.25rem;
  color: #1a1a2e;
}

.btn-primary {
  padding: 0.5rem 1.25rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #0d3b6e 0%, #1a5fa4 100%);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(26, 95, 164, 0.3);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Form Card */
.form-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  margin-bottom: 1.5rem;
}

.form-card h3 {
  font-size: 1rem;
  color: #1a1a2e;
  margin-bottom: 1rem;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  font-size: 0.8rem;
  font-weight: 600;
  color: #555;
}

.form-input {
  padding: 0.5rem 0.75rem;
  border: 1px solid #ddd;
  border-radius: 8px;
  font-size: 0.85rem;
  transition: border-color 0.2s;
}

.form-input:focus {
  outline: none;
  border-color: #1a5fa4;
}

.image-upload-row {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.preview-thumb {
  width: 48px;
  height: 48px;
  object-fit: cover;
  border-radius: 6px;
  border: 1px solid #eee;
}

.form-error {
  color: #c0392b;
  font-size: 0.8rem;
  margin-top: 0.5rem;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 1rem;
}

.btn-cancel {
  padding: 0.5rem 1.25rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: #666;
  background: #f0f0f0;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-cancel:hover {
  background: #e0e0e0;
}

/* Table Card */
.table-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
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

.thumb-img {
  width: 48px;
  height: 48px;
  object-fit: cover;
  border-radius: 6px;
}

.thumb-placeholder {
  width: 48px;
  height: 48px;
}

.sub-text {
  font-size: 0.75rem;
  color: #888;
  margin-top: 2px;
}

.order-cell {
  display: flex;
  gap: 4px;
  align-items: center;
}

.btn-order {
  padding: 0.2rem 0.5rem;
  font-size: 0.85rem;
  background: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-order:hover:not(:disabled) {
  background: #e0e0e0;
}

.btn-order:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

.actions-cell {
  display: flex;
  gap: 0.5rem;
}

.btn-edit {
  padding: 0.3rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #1a5fa4;
  background: #e8f0fe;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-edit:hover {
  background: #d0e2fc;
}

.btn-delete {
  padding: 0.3rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #c0392b;
  background: #fde8e8;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-delete:hover {
  background: #f8d7da;
}

.scholars-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.scholars-count {
  font-weight: 600;
  font-size: 0.9rem;
  color: #333;
}

.btn-scholars {
  padding: 0.25rem 0.6rem;
  font-size: 0.7rem;
  font-weight: 600;
  color: #1a5fa4;
  background: #e8f0fe;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-scholars:hover {
  background: #d0e2fc;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 2rem;
  color: #999;
}

@media (max-width: 768px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
