import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  { path: '/login', component: () => import('../views/Login.vue'), meta: { public: true } },
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', component: () => import('../views/Dashboard.vue'), meta: { requiresAuth: true } },
  { path: '/logbook', component: () => import('../views/Logbook.vue'), meta: { requiresAuth: true } },
  { path: '/failures/new', component: () => import('../views/FailureNew.vue'), meta: { requiresAuth: true } },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
  { path: '/settings', component: () => import('../views/Settings.vue'), meta: { requiresAuth: true } },
  { path: '/analytics', name: 'analytics', component: () => import('@/views/AnalyticsBoard.vue')},
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})

// simple guard using localStorage (store isn't guaranteed here yet)
router.beforeEach((to, from, next) => {
  const authed = !!localStorage.getItem('auth_token')
  if (to.meta.requiresAuth && !authed) return next({ path: '/login', query: { next: to.fullPath } })
  next()
})