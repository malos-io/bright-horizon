import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Email from '../views/Email.vue'
import Staff from '../views/Staff.vue'
import Login from '../views/Login.vue'
import AuthCallback from '../views/AuthCallback.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: Login,
    meta: { public: true },
  },
  {
    path: '/auth/callback',
    name: 'AuthCallback',
    component: AuthCallback,
    meta: { public: true },
  },
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
  },
  {
    path: '/email',
    name: 'Email',
    component: Email,
  },
  {
    path: '/staff',
    name: 'Staff',
    component: Staff,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior() {
    return { top: 0 }
  },
})

// Navigation guard — redirect to login if not authenticated
router.beforeEach((to) => {
  const token = localStorage.getItem('admin_token')
  if (!to.meta.public && !token) {
    return { name: 'Login' }
  }
})

export default router
