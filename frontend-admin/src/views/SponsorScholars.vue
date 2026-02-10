<template>
  <div class="sponsor-scholars">
    <div class="detail-header">
      <button class="btn-back" @click="router.push('/sponsors')">&larr; Back to Sponsors</button>
    </div>

    <div v-if="loading" class="loading-state">Loading...</div>
    <div v-else-if="!sponsor" class="empty-state">Sponsor not found</div>

    <template v-else>
      <div class="summary-card">
        <div class="summary-left">
          <img v-if="sponsor.image" :src="sponsor.image" :alt="sponsor.name" class="sponsor-thumb" />
          <svg v-else class="sponsor-thumb-placeholder" viewBox="0 0 80 80" xmlns="http://www.w3.org/2000/svg">
            <rect width="80" height="80" fill="#e0e0e0" rx="8"/>
            <circle cx="40" cy="30" r="12" fill="#bbb"/>
            <ellipse cx="40" cy="62" rx="20" ry="14" fill="#bbb"/>
          </svg>
          <div class="summary-info">
            <h2>{{ sponsor.name }}</h2>
            <p class="summary-meta">{{ sponsor.title }}</p>
            <p v-if="sponsor.position" class="summary-meta">{{ sponsor.position }}</p>
          </div>
        </div>
        <div class="summary-right">
          <span class="scholars-badge">{{ scholarsList.length }} Scholar{{ scholarsList.length !== 1 ? 's' : '' }}</span>
        </div>
      </div>

      <div class="table-card">
        <div v-if="scholarsLoading" class="loading-state">Loading scholars...</div>
        <div v-else-if="scholarsList.length === 0" class="empty-state">No scholars linked to this sponsor yet.</div>
        <table v-else class="data-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Course</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in scholarsList" :key="s.id">
              <td><strong>{{ s.lastName }}, {{ s.firstName }}</strong></td>
              <td>{{ s.course }}</td>
              <td><span class="status-badge" :class="'status-' + s.status">{{ s.status }}</span></td>
              <td>
                <button class="btn-view" @click="router.push('/application/' + s.id)">View Application</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { getSponsors, getSponsorScholars } from '../services/api'

const route = useRoute()
const router = useRouter()

const sponsor = ref(null)
const scholarsList = ref([])
const loading = ref(true)
const scholarsLoading = ref(false)

async function loadData() {
  loading.value = true
  try {
    const sponsors = await getSponsors()
    sponsor.value = sponsors.find(s => s.id === route.params.id) || null
    if (sponsor.value) {
      scholarsLoading.value = true
      scholarsList.value = await getSponsorScholars(route.params.id)
      scholarsLoading.value = false
    }
  } catch (e) {
    console.error('Failed to load sponsor data:', e)
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.sponsor-scholars {
  max-width: 1000px;
}

.detail-header {
  margin-bottom: 1.5rem;
}

.btn-back {
  padding: 0.4rem 1rem;
  font-size: 0.85rem;
  color: #666;
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-back:hover {
  background: #f5f5f5;
  border-color: #ccc;
}

.summary-card {
  background: white;
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08);
  margin-bottom: 1.5rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.sponsor-thumb {
  width: 56px;
  height: 56px;
  object-fit: cover;
  border-radius: 8px;
}

.sponsor-thumb-placeholder {
  width: 56px;
  height: 56px;
}

.summary-info h2 {
  font-size: 1.15rem;
  color: #1a1a2e;
  margin-bottom: 2px;
}

.summary-meta {
  font-size: 0.85rem;
  color: #888;
}

.scholars-badge {
  padding: 0.4rem 1rem;
  font-size: 0.85rem;
  font-weight: 600;
  color: #1a5fa4;
  background: #e8f0fe;
  border-radius: 8px;
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

.status-badge {
  display: inline-block;
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: capitalize;
}

.status-pending { background: #fff3cd; color: #856404; }
.status-enrolled { background: #d4edda; color: #155724; }
.status-completed { background: #cce5ff; color: #004085; }
.status-archived { background: #e2e3e5; color: #383d41; }
.status-interview { background: #e8d5f5; color: #6f42c1; }

.btn-view {
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

.btn-view:hover {
  background: #d0e2fc;
}

.loading-state,
.empty-state {
  text-align: center;
  padding: 2rem;
  color: #999;
}
</style>
