import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/views/HomeView.vue'),
    meta: { title: 'Inicio' }
  },
  {
    path: '/pacientes',
    name: 'pacientes',
    component: () => import('@/views/PacientesView.vue'),
    meta: { title: 'Pacientes' }
  },
  {
    path: '/doctores',
    name: 'doctores',
    component: () => import('@/views/DoctoresView.vue'),
    meta: { title: 'Doctores' }
  },
  {
    path: '/citas',
    name: 'citas',
    component: () => import('@/views/CitasView.vue'),
    meta: { title: 'Citas' }
  },
  {
    path: '/consultas',
    name: 'consultas',
    component: () => import('@/views/ConsultasView.vue'),
    meta: { title: 'Consultas' }
  },
  {
    path: '/facturacion',
    name: 'facturacion',
    component: () => import('@/views/FacturacionView.vue'),
    meta: { title: 'Facturación' }
  },
  {
    path: '/recetas',
    name: 'recetas',
    component: () => import('@/views/RecetasView.vue'),
    meta: { title: 'Recetas' }
  },
  {
    path: '/historial',
    name: 'historial',
    component: () => import('@/views/HistorialView.vue'),
    meta: { title: 'Historial Médico' }
  },
  {
    path: '/examenes',
    name: 'examenes',
    component: () => import('@/views/ExamenesView.vue'),
    meta: { title: 'Exámenes' }
  },
  {
    path: '/usuarios',
    name: 'usuarios',
    component: () => import('@/views/UsuariosView.vue'),
    meta: { title: 'Usuarios' }
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, _from, next) => {
  document.title = `${to.meta.title || 'Sistema'} - Centro Médico`
  next()
})

export default router
