import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { title: 'Iniciar Sesión', requiresAuth: false }
  },
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
    meta: { title: 'Inicio', requiresAuth: true }
  },
  {
    path: '/pacientes',
    name: 'pacientes',
    component: () => import('@/views/PacientesView.vue'),
    meta: { title: 'Pacientes', requiresAuth: true }
  },
  {
    path: '/doctores',
    name: 'doctores',
    component: () => import('@/views/DoctoresView.vue'),
    meta: { title: 'Doctores', requiresAuth: true }
  },
  {
    path: '/citas',
    name: 'citas',
    component: () => import('@/views/CitasView.vue'),
    meta: { title: 'Citas', requiresAuth: true }
  },
  {
    path: '/consultas',
    name: 'consultas',
    component: () => import('@/views/ConsultasView.vue'),
    meta: { title: 'Consultas', requiresAuth: true }
  },
  {
    path: '/facturacion',
    name: 'facturacion',
    component: () => import('@/views/FacturacionView.vue'),
    meta: { title: 'Facturación', requiresAuth: true }
  },
  {
    path: '/recetas',
    name: 'recetas',
    component: () => import('@/views/RecetasView.vue'),
    meta: { title: 'Recetas', requiresAuth: true }
  },
  {
    path: '/historial',
    name: 'historial',
    component: () => import('@/views/HistorialView.vue'),
    meta: { title: 'Historial Médico', requiresAuth: true }
  },
  {
    path: '/examenes',
    name: 'examenes',
    component: () => import('@/views/ExamenesView.vue'),
    meta: { title: 'Exámenes', requiresAuth: true }
  },
  {
    path: '/usuarios',
    name: 'usuarios',
    component: () => import('@/views/UsuariosView.vue'),
    meta: { title: 'Usuarios', requiresAuth: true }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach(async (to, from, next) => {
  document.title = `${to.meta.title || 'Sistema'} - Centro Médico`
  
  const authStore = useAuthStore()
  
  // Inicializar auth si no está inicializado
  if (!authStore.usuario) {
    authStore.initAuth()
  }
  
  const requiresAuth = to.meta.requiresAuth !== false
  
  if (requiresAuth && !authStore.isAuthenticated) {
    // Intentar verificar autenticación
    const isAuth = await authStore.checkAuth()
    
    if (!isAuth) {
      next({ name: 'login', query: { redirect: to.fullPath } })
      return
    }
  }
  
  // Si está autenticado y va a login, redirigir a home
  if (to.name === 'login' && authStore.isAuthenticated) {
    next({ name: 'home' })
    return
  }
  
  next()
})

export default router
