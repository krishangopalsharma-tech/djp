import { createRouter, createWebHistory } from 'vue-router'
import SettingsLayout from '@/views/settings/SettingsLayout.vue'
const FailureIdSettings = () => import('@/views/settings/FailureIdSettings.vue')
const TelegramSettings = () => import('@/views/settings/TelegramSettings.vue')
const UsersRolesSettings = () => import('@/views/settings/UsersRolesSettings.vue')
const CircuitManagement = () => import('@/views/settings/CircuitManagement.vue')
const SupervisorManagement = () => import('@/views/settings/SupervisorManagement.vue')
const StationSectionManagement = () => import('@/views/settings/StationSectionManagement.vue')
const DepotManagement = () => import('@/views/settings/DepotManagement.vue')

const routes = [
  { path: '/login', component: () => import('../views/Login.vue'), meta: { public: true } },
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', component: () => import('../views/Dashboard.vue'), meta: { requiresAuth: true, title: 'Dashboard' } },
  { path: '/logbook', component: () => import('../views/Logbook.vue'), meta: { requiresAuth: true, title: 'Logbook' } },
  { path: '/failures/new', name: 'LogbookEntry', alias: ['/logbook/new'], component: () => import('../views/FailureNew.vue'), meta: { requiresAuth: true, title: 'Logbook Entry' } },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
  {
    path: '/settings',
    component: SettingsLayout,
    meta: { requiresAuth: true, title: 'Settings' },
    children: [
      { path: '', redirect: '/settings/failure-id' },
      { path: 'failure-id', name: 'SettingsFailureId', component: FailureIdSettings, meta: { title: 'Failure ID Configuration' } },
      { path: 'telegram', name: 'SettingsTelegram', component: TelegramSettings, meta: { title: 'Telegram Integration Settings' } },
      { path: 'users-roles', name: 'SettingsUsersRoles', component: UsersRolesSettings, meta: { title: 'User and Role Management' } },
      { path: 'circuits', name: 'SettingsCircuits', component: CircuitManagement, meta: { title: 'Circuit Management' } },
      { path: 'supervisors', name: 'SettingsSupervisors', component: SupervisorManagement, meta: { title: 'Supervisor Management' } },
      { path: 'stations-sections', name: 'SettingsStationsSections', component: StationSectionManagement, meta: { title: 'Station and Section Management' } },
      { path: 'depots', name: 'SettingsDepots', component: DepotManagement, meta: { title: 'Depot Management' } },
    ],
  },
  { path: '/analytics', name: 'analytics', component: () => import('@/views/AnalyticsBoard.vue'), meta: { title: 'Analytics Board' } },
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
