import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import Courses from '../views/Courses.vue'
import CourseDetail from '../views/CourseDetail.vue'
import Email from '../views/Email.vue'
import Staff from '../views/Staff.vue'
import Students from '../views/Students.vue'
import StudentDetail from '../views/StudentDetail.vue'
import Login from '../views/Login.vue'
import AuthCallback from '../views/AuthCallback.vue'
import ApplicationDetail from '../views/ApplicationDetail.vue'
import Sponsors from '../views/Sponsors.vue'
import SponsorScholars from '../views/SponsorScholars.vue'
import StudentApplications from '../views/StudentApplications.vue'
import InstructorApplications from '../views/InstructorApplications.vue'
import InstructorApplicationDetail from '../views/InstructorApplicationDetail.vue'
import TesdaInstructors from '../views/TesdaInstructors.vue'
import TesdaTvis from '../views/TesdaTvis.vue'

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
    path: '/courses',
    name: 'Courses',
    component: Courses,
  },
  {
    path: '/courses/:slug',
    name: 'CourseDetail',
    component: CourseDetail,
  },
  {
    path: '/student-applications',
    name: 'StudentApplications',
    component: StudentApplications,
  },
  {
    path: '/application/:id',
    name: 'ApplicationDetail',
    component: ApplicationDetail,
  },
  {
    path: '/email',
    name: 'Email',
    component: Email,
  },
  {
    path: '/students',
    name: 'Students',
    component: Students,
  },
  {
    path: '/students/:id',
    name: 'StudentDetail',
    component: StudentDetail,
  },
  {
    path: '/staff',
    name: 'Staff',
    component: Staff,
  },
  {
    path: '/instructor-applications',
    name: 'InstructorApplications',
    component: InstructorApplications,
  },
  {
    path: '/instructor-applications/:id',
    name: 'InstructorApplicationDetail',
    component: InstructorApplicationDetail,
  },
  {
    path: '/sponsors',
    name: 'Sponsors',
    component: Sponsors,
  },
  {
    path: '/sponsors/:id/scholars',
    name: 'SponsorScholars',
    component: SponsorScholars,
  },
  {
    path: '/tesda-instructors',
    name: 'TesdaInstructors',
    component: TesdaInstructors,
  },
  {
    path: '/tesda-tvis',
    name: 'TesdaTvis',
    component: TesdaTvis,
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
