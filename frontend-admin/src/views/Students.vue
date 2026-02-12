<template>
  <div class="students-page">
    <div class="students-header">
      <h2>Students</h2>
      <div class="header-actions">
        <div class="search-box">
          <input
            v-model="search"
            type="text"
            placeholder="Search students..."
            class="search-input"
          />
        </div>
        <button class="btn-refresh" @click="loadStudents">Refresh</button>
      </div>
    </div>

    <div v-if="loading" class="loading-state">Loading students...</div>

    <div v-else-if="filteredStudents.length" class="students-list">
      <div
        class="student-card"
        v-for="student in filteredStudents"
        :key="student.id"
        @click="router.push('/students/' + student.id)"
      >
        <div class="student-avatar">
          {{ getInitials(student) }}
        </div>
        <div class="student-info">
          <div class="student-name">{{ student.lastName }}, {{ student.firstName }}</div>
          <div class="student-email">{{ student.email }}</div>
        </div>
        <div class="student-meta">
          <span class="meta-date">{{ formatDate(student.updated_at || student.created_at) }}</span>
          <span class="meta-label">Enrolled</span>
        </div>
        <span class="card-arrow">&#8594;</span>
      </div>
    </div>

    <div v-else-if="search && students.length" class="empty-state">No students matching "{{ search }}"</div>
    <div v-else class="empty-state">No students yet</div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getStudents } from '../services/api'

const router = useRouter()
const students = ref([])
const loading = ref(false)
const search = ref('')

const filteredStudents = computed(() => {
  if (!search.value.trim()) return students.value
  const q = search.value.toLowerCase()
  return students.value.filter(s =>
    `${s.firstName} ${s.lastName} ${s.email}`.toLowerCase().includes(q)
  )
})

function getInitials(student) {
  const first = (student.firstName || '')[0] || ''
  const last = (student.lastName || '')[0] || ''
  return (first + last).toUpperCase() || '?'
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

async function loadStudents() {
  loading.value = true
  try {
    students.value = await getStudents()
  } catch (err) {
    console.error('Failed to load students:', err)
  } finally {
    loading.value = false
  }
}

onMounted(loadStudents)
</script>

<style scoped>
.students-page {
  max-width: 900px;
}

.students-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  gap: 1rem;
}

.students-header h2 {
  font-size: 1.25rem;
  color: #1a1a2e;
  white-space: nowrap;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.search-input {
  padding: 0.4rem 0.75rem;
  font-size: 0.85rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  outline: none;
  width: 200px;
  transition: border-color 0.2s;
}

.search-input:focus {
  border-color: #1a5fa4;
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
  white-space: nowrap;
}

.btn-refresh:hover {
  background: #d0e2fc;
}

.students-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.student-card {
  display: flex;
  align-items: center;
  gap: 1rem;
  background: white;
  border-radius: 10px;
  padding: 1rem 1.25rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
  cursor: pointer;
  transition: box-shadow 0.2s, transform 0.15s;
}

.student-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  transform: translateY(-1px);
}

.student-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #e8f0fe;
  color: #1a5fa4;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.85rem;
  font-weight: 700;
  flex-shrink: 0;
}

.student-info {
  flex: 1;
  min-width: 0;
}

.student-name {
  font-size: 0.95rem;
  font-weight: 600;
  color: #1a1a2e;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.student-email {
  font-size: 0.8rem;
  color: #888;
  margin-top: 0.1rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.student-meta {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 0.1rem;
  flex-shrink: 0;
}

.meta-date {
  font-size: 0.85rem;
  font-weight: 600;
  color: #444;
}

.meta-label {
  font-size: 0.65rem;
  font-weight: 500;
  color: #999;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.card-arrow {
  color: #ccc;
  font-size: 1.1rem;
  flex-shrink: 0;
  transition: color 0.2s, transform 0.2s;
}

.student-card:hover .card-arrow {
  color: #1a5fa4;
  transform: translateX(2px);
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

@media (max-width: 600px) {
  .students-header {
    flex-direction: column;
    align-items: flex-start;
  }
  .header-actions {
    width: 100%;
  }
  .search-input {
    flex: 1;
  }
  .student-card {
    flex-wrap: wrap;
  }
  .student-meta {
    align-items: flex-start;
    margin-left: 56px;
  }
  .card-arrow {
    display: none;
  }
}
</style>
