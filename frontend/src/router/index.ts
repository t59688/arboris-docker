import { createRouter, createWebHistory } from 'vue-router'
import WorkspaceEntry from '../views/WorkspaceEntry.vue'
import NovelWorkspace from '../views/NovelWorkspace.vue'
import InspirationMode from '../views/InspirationMode.vue'
import WritingDesk from '../views/WritingDesk.vue'
import NovelDetail from '../views/NovelDetail.vue'
import PoemDetail from '../views/PoemDetail.vue'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'workspace-entry',
      component: WorkspaceEntry,
      meta: { requiresAuth: true },
    },
    {
      path: '/workspace',
      name: 'novel-workspace',
      component: NovelWorkspace,
      meta: { requiresAuth: true },
    },
    {
      path: '/inspiration',
      name: 'inspiration-mode',
      component: InspirationMode,
      meta: { requiresAuth: true },
    },
    {
      path: '/detail/:id',
      name: 'novel-detail',
      component: NovelDetail,
      props: true,
      meta: { requiresAuth: true },
    },
    {
      path: '/poem/:id',
      name: 'poem-detail',
      component: PoemDetail,
      props: true,
      meta: { requiresAuth: true },
    },
    {
      path: '/novel/:id',
      name: 'writing-desk',
      component: WritingDesk,
      props: true,
      meta: { requiresAuth: true },
    },
    {
      path: '/login',
      name: 'login',
      component: Login,
    },
    {
      path: '/register',
      name: 'register',
      component: Register,
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('../views/AdminView.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: '/admin/novel/:id',
      name: 'admin-novel-detail',
      component: () => import('../views/AdminNovelDetail.vue'),
      props: true,
      meta: { requiresAuth: true, requiresAdmin: true },
    },
    {
      path: '/settings',
      name: 'settings',
      component: () => import('../views/SettingsView.vue'),
      meta: { requiresAuth: true },
    },
  ],
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()
  
  // Attempt to fetch user info if token exists but user info is not loaded
  if (authStore.token && !authStore.user) {
    await authStore.fetchUser()
  }

  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresAdmin = to.matched.some(record => record.meta.requiresAdmin)
  const isAuthenticated = authStore.isAuthenticated
  const isAdmin = authStore.user?.is_admin

  const mustChangePassword = authStore.user?.is_admin && authStore.mustChangePassword

  if (requiresAuth && !isAuthenticated) {
    next('/login')
  } else if (requiresAdmin && !isAdmin) {
    next('/') // Redirect to a non-admin page if not an admin
  } else if (isAuthenticated && mustChangePassword) {
    if (to.name !== 'admin' || to.query.tab !== 'password') {
      next({ name: 'admin', query: { tab: 'password' } })
    } else {
      next()
    }
  }
  else {
    next()
  }
})

export default router
