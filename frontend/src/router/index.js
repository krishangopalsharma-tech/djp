// Path: frontend/src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import SettingsLayout from '@/views/settings/SettingsLayout.vue'
import EmailSettings from '@/views/settings/EmailSettings.vue'
import SectionManagement from '@/views/settings/SectionManagement.vue'
import ReportsManagement from '@/views/settings/ReportsManagement.vue'
import TelegramSettings from '@/views/settings/TelegramSettings.vue'
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
  
  // This is the line that needs to be present and correct
  { path: '/failures/edit/:id', name: 'FailureEdit', component: () => import('@/views/FailureEdit.vue'), meta: { requiresAuth: true, title: 'Edit Failure' } },

  { path: '/reports-now', name: 'ReportsNow', component: ReportsNow, meta: { requiresAuth: true, title: 'Reports Now' } },
  { path: '/supervisor-movements', name: 'SupervisorMovements', component: SupervisorMovements, meta: { requiresAuth: true, title: 'Supervisor Movements' } },
  {
    path: '/settings',
    component: SettingsLayout,
    meta: { requiresAuth: true, title: 'Settings' },
    children: [
      { path: '', redirect: '/settings/reports' },
      { path: 'email', name: 'SettingsEmail', component: EmailSettings, meta: { title: 'Email Settings' } },
      { path: 'reports', name: 'SettingsReports', component: ReportsManagement, meta: { title: 'Reports Management' } },
      { path: 'failure-id', name: 'SettingsFailureId', component: FailureIdSettings, meta: { title: 'Failure ID Configuration' } },
      { path: 'telegram', name: 'SettingsTelegram', component: TelegramSettings, meta: { title: 'Telegram Integration Settings' } },
      { path: 'users-roles', name: 'SettingsUsersRoles', component: UsersRolesSettings, meta: { title: 'User and Role Management' } },
      { path: 'circuits', name: 'SettingsCircuits', component: CircuitManagement, meta: { title: 'Circuit Management' } },
      { path: 'depots', name: 'SettingsDepots', component: DepotManagement, meta: { title: 'Depot Management' } },
      { path: 'supervisors', name: 'SettingsSupervisors', component: SupervisorManagement, meta: { title: 'Supervisor Management' } },
      { path: 'stations', name: 'SettingsStations', component: StationManagement, meta: { title: 'Station Management' } },
      { path: 'sections', name: 'SettingsSections', component: SectionManagement, meta: { title: 'Section Management' } },
    ],
  },
  { path: '/analytics', name: 'analytics', component: () => import('@/views/AnalyticsBoard.vue'), meta: { title: 'Analytics Board' } },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach((to, from, next) => {
  const authed = !!localStorage.getItem('auth_token')
  if (to.meta.requiresAuth && !authed) return next({ path: '/login', query: { next: to.fullPath } })
  next()
})
