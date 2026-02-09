<template>
  <div id="app">
    <div class="student-layout">
      <aside class="sidebar">
        <div class="sidebar-header">
          <img :src="logo" alt="Bright Horizons Institute" class="sidebar-logo" />
          <h2>Student Portal</h2>
        </div>
        <nav class="sidebar-nav">
          <router-link to="/" class="nav-item">
            <span class="nav-icon">&#9632;</span>
            Dashboard
          </router-link>
        </nav>
      </aside>
      <main class="main-content">
        <header class="top-bar">
          <h1 class="page-title">My Learning</h1>
          <div class="user-info">
            <span>Student</span>
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
import logo from './assets/logo.png'
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
  padding: 2rem 0;
  flex-shrink: 0;
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
