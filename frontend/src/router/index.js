import { createRouter, createWebHistory } from 'vue-router'
import SettingsLayout from '@/views/settings/SettingsLayout.vue'
import EmailSettings from '@/views/settings/EmailSettings.vue'
import SectionManagement from '@/views/settings/SectionManagement.vue'
import ReportsManagement from '@/views/settings/ReportsManagement.vue'
import TelegramSettings2 from '@/views/settings/TelegramSettings2.vue'
import ReportsNow from '@/views/ReportsNow.vue'
import SupervisorMovements from '@/views/SupervisorMovements.vue'
const FailureIdSettings = () => import('@/views/settings/FailureIdSettings.vue')
const UsersRolesSettings = () => import('@/views/settings/UsersRolesSettings.vue')
const CircuitManagement = () => import('@/views/settings/CircuitManagement.vue')
const SupervisorManagement = () => import('@/views/settings/SupervisorManagement.vue')
const StationManagement = () => import('@/views/settings/StationManagement.vue')
const DepotManagement = () => import('@/views/settings/DepotManagement.vue')

const routes = [
  { path: '/login', component: () => import('../views/Login.vue'), meta: { public: true } },
  { path: '/', redirect: '/dashboard' },
  { path: '/dashboard', component: () => import('../views/Dashboard.vue'), meta: { requiresAuth: true, title: 'Dashboard' } },
  { path: '/logbook', component: () => import('../views/Logbook.vue'), meta: { requiresAuth: true, title: 'Logbook' } },
  { path: '/failures/new', name: 'LogbookEntry', alias: ['/logbook/new'], component: () => import('../views/FailureNew.vue'), meta: { requiresAuth: true, title: 'Logbook Entry' } },
  { path: '/reports-now', name: 'ReportsNow', component: ReportsNow, meta: { requiresAuth: true, title: 'Reports Now' } },
  { path: '/supervisor-movements', name: 'SupervisorMovements', component: SupervisorMovements, meta: { requiresAuth: true, title: 'Supervisor Movements' } },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
  {
    path: '/settings',
    component: SettingsLayout,
    meta: { requiresAuth: true, title: 'Settings' },
    children: [
      // Default → Reports
      { path: '', redirect: '/settings/reports' },
      { path: 'email', name: 'SettingsEmail', component: EmailSettings, meta: { title: 'Email Settings' } },
      // 1) Reports Management
      { path: 'reports', name: 'SettingsReports', component: ReportsManagement, meta: { title: 'Reports Management' } },
      // 2) Failure ID Configuration
      { path: 'failure-id', name: 'SettingsFailureId', component: FailureIdSettings, meta: { title: 'Failure ID Configuration' } },
      // 3) Telegram Integration Settings
      { path: 'telegram', name: 'SettingsTelegram', component: TelegramSettings2, meta: { title: 'Telegram Integration Settings' } },
      // 4) User and Role Management
      { path: 'users-roles', name: 'SettingsUsersRoles', component: UsersRolesSettings, meta: { title: 'User and Role Management' } },
      // 5) Circuit Management
      { path: 'circuits', name: 'SettingsCircuits', component: CircuitManagement, meta: { title: 'Circuit Management' } },
      // 6) Depot Management
      { path: 'depots', name: 'SettingsDepots', component: DepotManagement, meta: { title: 'Depot Management' } },
      // 7) Supervisor Management
      { path: 'supervisors', name: 'SettingsSupervisors', component: SupervisorManagement, meta: { title: 'Supervisor Management' } },
      // 8) Station Management
      { path: 'stations', name: 'SettingsStations', component: StationManagement, meta: { title: 'Station Management' } },
      // 9) Section Management
      { path: 'sections', name: 'SettingsSections', component: SectionManagement, meta: { title: 'Section Management' } },
      { path: 'stations-sections', redirect: '/settings/stations' },
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
