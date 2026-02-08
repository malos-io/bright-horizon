<template>
  <div class="email-page">
    <!-- Email Layout -->
    <div class="email-header">
      <h2>Email</h2>
      <div class="email-actions">
        <a href="https://mail.zoho.com/" target="_blank" rel="noopener noreferrer" class="btn btn-primary">
          Open Mailbox &#8599;
        </a>
        <button class="btn btn-secondary" @click="loadInbox">Refresh</button>
      </div>
    </div>

    <div class="email-layout">
      <!-- Inbox List -->
      <div class="inbox-panel">
        <div v-if="loading" class="loading">Loading emails...</div>
        <div v-else-if="emails.length === 0" class="empty">No emails found</div>
        <div
          v-for="email in emails"
          :key="email.messageId"
          class="email-item"
          :class="{ active: selectedEmail?.messageId === email.messageId, unread: email.status === '0' }"
          @click="selectEmail(email)"
        >
          <div class="email-from">{{ email.sender || email.fromAddress || 'Unknown' }}</div>
          <div class="email-subject">{{ email.subject || '(No Subject)' }}</div>
          <div class="email-summary">{{ email.summary || '' }}</div>
          <div class="email-date">{{ formatDate(email.receivedTime || email.sentDateInGMT) }}</div>
        </div>
      </div>

      <!-- Email Detail -->
      <div class="detail-panel">
        <div v-if="loadingMessage" class="loading">Loading message...</div>
        <div v-else-if="!selectedEmail" class="empty">Select an email to read</div>
        <div v-else class="email-detail">
          <div class="detail-header">
            <h3>{{ selectedEmail.subject || '(No Subject)' }}</h3>
            <div class="detail-meta">
              <span><strong>From:</strong> {{ selectedEmail.sender || selectedEmail.fromAddress }}</span>
              <span><strong>To:</strong> {{ selectedEmail.toAddress || '' }}</span>
              <span><strong>Date:</strong> {{ formatDate(selectedEmail.receivedTime || selectedEmail.sentDateInGMT) }}</span>
            </div>
          </div>
          <div class="detail-body" v-html="messageContent"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getInbox, getMessage } from '../services/api'

const emails = ref([])
const selectedEmail = ref(null)
const messageContent = ref('')
const loading = ref(false)
const loadingMessage = ref(false)

async function loadInbox() {
  loading.value = true
  try {
    emails.value = await getInbox()
  } catch (err) {
    console.error('Failed to load inbox:', err)
  } finally {
    loading.value = false
  }
}

async function selectEmail(email) {
  selectedEmail.value = email
  loadingMessage.value = true
  messageContent.value = ''
  try {
    const data = await getMessage(email.folderId, email.messageId)
    messageContent.value = data.content || '(No content)'
  } catch (err) {
    messageContent.value = '<p>Failed to load message content.</p>'
    console.error('Failed to load message:', err)
  } finally {
    loadingMessage.value = false
  }
}

function formatDate(timestamp) {
  if (!timestamp) return ''
  const date = new Date(Number(timestamp))
  if (isNaN(date.getTime())) return timestamp
  const now = new Date()
  if (date.toDateString() === now.toDateString()) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }
  return date.toLocaleDateString([], { month: 'short', day: 'numeric' })
}

onMounted(loadInbox)
</script>

<style scoped>
.email-page {
  height: calc(100vh - 80px);
  display: flex;
  flex-direction: column;
}

.email-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.email-header h2 {
  font-size: 1.25rem;
  color: #1a1a2e;
}

.email-actions {
  display: flex;
  gap: 0.5rem;
}

.email-layout {
  display: flex;
  flex: 1;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  background: white;
  min-height: 0;
}

.inbox-panel {
  width: 360px;
  border-right: 1px solid #e0e0e0;
  overflow-y: auto;
  flex-shrink: 0;
}

.detail-panel {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.email-item {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #f0f0f0;
  cursor: pointer;
  transition: background 0.15s;
}

.email-item:hover {
  background: #f8f9fa;
}

.email-item.active {
  background: #e8f0fe;
}

.email-item.unread .email-from,
.email-item.unread .email-subject {
  font-weight: 600;
}

.email-from {
  font-size: 0.85rem;
  color: #333;
  margin-bottom: 2px;
}

.email-subject {
  font-size: 0.9rem;
  color: #1a1a2e;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.email-summary {
  font-size: 0.8rem;
  color: #888;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-top: 2px;
}

.email-date {
  font-size: 0.75rem;
  color: #999;
  margin-top: 4px;
}

.detail-header {
  border-bottom: 1px solid #e0e0e0;
  padding-bottom: 1rem;
  margin-bottom: 1rem;
}

.detail-header h3 {
  font-size: 1.1rem;
  color: #1a1a2e;
  margin-bottom: 0.5rem;
}

.detail-meta {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.85rem;
  color: #666;
}

.detail-body {
  font-size: 0.9rem;
  line-height: 1.6;
  color: #333;
}

.loading,
.empty {
  padding: 2rem;
  text-align: center;
  color: #999;
  font-size: 0.9rem;
}

/* Buttons */
.btn {
  padding: 0.5rem 1.25rem;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background 0.2s;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.btn-primary {
  background: #1a5fa4;
  color: white;
}

.btn-primary:hover {
  background: #154d87;
}

.btn-secondary {
  background: #f0f0f0;
  color: #333;
}

.btn-secondary:hover {
  background: #e0e0e0;
}
</style>
