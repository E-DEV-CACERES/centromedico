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
    meta: { title: 'Inicio', requiresAuth: true, roles: ['Admin', 'Doctor', 'Recepcionista', 'User'] }
  },
  {
    path: '/pacientes',
    name: 'pacientes',
    component: () => import('@/views/PacientesView.vue'),
    meta: { title: 'Pacientes', requiresAuth: true, roles: ['Admin', 'Doctor', 'Recepcionista', 'User'] }
  },
  {
    path: '/doctores',
    name: 'doctores',
    component: () => import('@/views/DoctoresView.vue'),
    meta: { title: 'Doctores', requiresAuth: true, roles: ['Admin', 'Doctor', 'Recepcionista', 'User'] }
  },
  {
    path: '/citas',
    name: 'citas',
    component: () => import('@/views/CitasView.vue'),
    meta: { title: 'Citas', requiresAuth: true, roles: ['Admin', 'Doctor', 'Recepcionista', 'User'] }
  },
  {
    path: '/consultas',
    name: 'consultas',
    component: () => import('@/views/ConsultasView.vue'),
    meta: { title: 'Consultas', requiresAuth: true, roles: ['Admin', 'Doctor'] }
  },
  {
    path: '/recetas',
    name: 'recetas',
    component: () => import('@/views/RecetasView.vue'),
    meta: { title: 'Recetas', requiresAuth: true, roles: ['Admin', 'Doctor'] }
  },
  {
    path: '/historial',
    name: 'historial',
    component: () => import('@/views/HistorialView.vue'),
    meta: { title: 'Historial Médico', requiresAuth: true, roles: ['Admin', 'Doctor'] }
  },
  {
    path: '/examenes',
    name: 'examenes',
    component: () => import('@/views/ExamenesView.vue'),
    meta: { title: 'Exámenes', requiresAuth: true, roles: ['Admin', 'Doctor', 'Recepcionista', 'User'] }
  },
  {
    path: '/usuarios',
    name: 'usuarios',
    component: () => import('@/views/UsuariosView.vue'),
    meta: { title: 'Usuarios', requiresAuth: true, roles: ['Admin'] }
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
  
  // Verificar permisos por rol
  if (requiresAuth && authStore.isAuthenticated) {
    const allowedRoles = to.meta.roles as string[] | undefined
    const userRole = authStore.userRole
    
    if (allowedRoles && userRole) {
      // Normalizar el rol del usuario (puede ser "User" o "Recepcionista")
      const normalizedRole = userRole === 'User' || userRole === 'Recepcionista' ? 'User' : userRole
      const normalizedAllowedRoles = allowedRoles.map(role => 
        role === 'User' || role === 'Recepcionista' ? 'User' : role
      )
      
      if (!normalizedAllowedRoles.includes(normalizedRole)) {
        // Usuario no tiene permiso para acceder a esta ruta
        next({ name: 'home' })
        return
      }
    }
  }
  
  next()
})

export default router
