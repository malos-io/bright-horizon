<template>
  <div id="app">
    <!-- Public pages (login) render without sidebar -->
    <router-view v-if="$route.meta.public" />

    <!-- Authenticated layout with sidebar -->
    <div v-else class="student-layout">
      <aside class="sidebar">
        <div class="sidebar-header">
          <img :src="logo" alt="Bright Horizon Institute" class="sidebar-logo" />
          <h2>Student Portal</h2>
        </div>
        <nav class="sidebar-nav">
          <router-link to="/" class="nav-item" exact>
            <span class="nav-icon">&#9632;</span>
            Dashboard
          </router-link>
          <router-link to="/my-classes" class="nav-item">
            <span class="nav-icon">&#128218;</span>
            My Classes
          </router-link>
        </nav>
        <div class="sidebar-footer">
          <div class="user-name">{{ auth.state.name || 'Student' }}</div>
          <div class="user-email">{{ auth.state.email }}</div>
          <button class="logout-btn" @click="handleLogout">Logout</button>
        </div>
      </aside>
      <main class="main-content">
        <header class="top-bar">
          <h1 class="page-title">{{ pageTitle }}</h1>
          <div class="user-info">
            <span>{{ auth.state.email }}</span>
          </div>
        </header>
        <div class="content-area">
          <router-view />
        </div>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuth } from './composables/useAuth'
import logo from './assets/logo.png'

const auth = useAuth()
const router = useRouter()
const route = useRoute()

const pageTitles = {
  Dashboard: 'Dashboard',
  MyClasses: 'My Classes',
  ApplicationDetail: 'Application Details',
}
const pageTitle = computed(() => pageTitles[route.name] || route.name)

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  background: #f0f2f5;
}

#app {
  min-height: 100vh;
}

.student-layout {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 260px;
  background: linear-gradient(180deg, #0d3b6e 0%, #1a5fa4 100%);
  color: white;
  padding: 2rem 0 0;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
}

.sidebar-header {
  padding: 1rem 1.5rem 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  text-align: center;
}

.sidebar-logo {
  width: 100px;
  height: 100px;
  object-fit: contain;
  margin-bottom: 0.75rem;
  background: white;
  border-radius: 50%;
  padding: 8px;
}

.sidebar-header h2 {
  font-size: 1.1rem;
  font-weight: 700;
}

.sidebar-nav {
  padding: 1rem 0;
  flex: 1;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1.5rem;
  color: rgba(255, 255, 255, 0.85);
  text-decoration: none;
  transition: all 0.2s;
  font-size: 0.95rem;
}

.nav-item:hover,
.nav-item.router-link-active {
  background: rgba(255, 255, 255, 0.15);
  color: white;
}

.nav-icon {
  font-size: 1.1rem;
}

.sidebar-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
}

.sidebar-footer .user-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: white;
}

.sidebar-footer .user-email {
  font-size: 0.75rem;
  color: rgba(255, 255, 255, 0.6);
  margin-bottom: 0.75rem;
  word-break: break-all;
}

.sidebar-footer .logout-btn {
  width: 100%;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.1);
  color: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.sidebar-footer .logout-btn:hover {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.top-bar {
  background: white;
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.page-title {
  font-size: 1.25rem;
  color: #1a1a2e;
}

.user-info {
  font-size: 0.9rem;
  color: #666;
}

.content-area {
  padding: 2rem;
  flex: 1;
}
</style>
