<template>
  <AppLayout>
    <div class="p-6">
      <el-row :gutter="20">
        <el-col :xs="24" :sm="12" :md="8" :lg="6" v-for="card in cards" :key="card.title">
          <el-card class="mb-4 cursor-pointer hover:shadow-lg transition-shadow" @click="navigateTo(card.route)">
            <div class="flex items-center">
              <el-icon :size="40" :color="card.color" class="mr-4">
                <component :is="card.icon" />
              </el-icon>
              <div>
                <div class="text-2xl font-bold text-gray-800">{{ card.count }}</div>
                <div class="text-sm text-gray-600">{{ card.title }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- Gráficas -->
      <el-row :gutter="16" class="mt-6">
        <!-- Gráfica de Barras - Resumen General -->
        <el-col :xs="24" :sm="12" :md="12" :lg="6">
          <el-card class="chart-card">
            <template #header>
              <div class="flex items-center justify-between">
                <span class="text-sm font-semibold">Resumen General</span>
              </div>
            </template>
            <div v-loading="loadingCharts" class="chart-container-small">
              <BarChart :data="barChartData" />
            </div>
          </el-card>
        </el-col>

        <!-- Gráfica de Dona - Distribución de Exámenes por Estado -->
        <el-col :xs="24" :sm="12" :md="12" :lg="6">
          <el-card class="chart-card">
            <template #header>
              <div class="flex items-center justify-between">
                <span class="text-sm font-semibold">Estado de Exámenes</span>
              </div>
            </template>
            <div v-loading="loadingCharts" class="chart-container-small">
              <DonutChart :data="examenesPorEstado" />
            </div>
          </el-card>
        </el-col>

        <!-- Gráfica de Líneas - Citas por Mes -->
        <el-col :xs="24" :sm="12" :md="12" :lg="6">
          <el-card class="chart-card">
            <template #header>
              <div class="flex items-center justify-between">
                <span class="text-sm font-semibold">Citas por Mes</span>
              </div>
            </template>
            <div v-loading="loadingCharts" class="chart-container-small">
              <LineChart :data="citasPorMes" />
            </div>
          </el-card>
        </el-col>

        <!-- Gráfica de Barras Horizontales - Usuarios por Rol -->
        <el-col :xs="24" :sm="12" :md="12" :lg="6">
          <el-card class="chart-card">
            <template #header>
              <div class="flex items-center justify-between">
                <span class="text-sm font-semibold">Usuarios por Rol</span>
              </div>
            </template>
            <div v-loading="loadingCharts" class="chart-container-small">
              <HorizontalBarChart :data="usuariosPorRol" />
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-card class="mt-6">
        <template #header>
          <div class="flex items-center justify-between">
            <span class="text-lg font-semibold">Bienvenido al Sistema de Centro Médico</span>
          </div>
        </template>
        <div class="text-gray-700">
          <p class="mb-4">
            Sistema integral para la gestión de un centro médico que incluye:
          </p>
          <ul class="list-disc list-inside space-y-2">
            <li>Gestión de pacientes y doctores</li>
            <li>Programación y seguimiento de citas</li>
            <li>Registro de consultas médicas</li>
            <li>Emisión de recetas médicas</li>
            <li>Historial médico completo</li>
            <li>Gestión de exámenes de laboratorio</li>
            <li>Administración de usuarios del sistema</li>
          </ul>
        </div>
      </el-card>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, markRaw, computed } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import {
  User,
  Avatar,
  Calendar,
  Document,
  Notebook,
  Files,
  Search,
  UserFilled
} from '@element-plus/icons-vue'
import { getPacientes } from '@/services/pacientes'
import { getDoctores } from '@/services/doctores'
import { getCitas } from '@/services/citas'
import { getExamenes } from '@/services/examenes'
import { getUsuarios } from '@/services/usuarios'
import { getConsultas } from '@/services/consultas'
import { getRecetas } from '@/services/recetas'
import BarChart from '@/components/charts/BarChart.vue'
import DonutChart from '@/components/charts/DonutChart.vue'
import LineChart from '@/components/charts/LineChart.vue'
import HorizontalBarChart from '@/components/charts/HorizontalBarChart.vue'

const router = useRouter()
const loadingCharts = ref(false)

const cards = ref([
  { title: 'Pacientes', count: 0, icon: markRaw(User), color: '#409EFF', route: '/pacientes' },
  { title: 'Doctores', count: 0, icon: markRaw(Avatar), color: '#67C23A', route: '/doctores' },
  { title: 'Citas', count: 0, icon: markRaw(Calendar), color: '#E6A23C', route: '/citas' },
  { title: 'Consultas', count: 0, icon: markRaw(Document), color: '#F56C6C', route: '/consultas' },
  { title: 'Recetas', count: 0, icon: markRaw(Notebook), color: '#409EFF', route: '/recetas' },
  { title: 'Historial', count: 0, icon: markRaw(Files), color: '#67C23A', route: '/historial' },
  { title: 'Exámenes', count: 0, icon: markRaw(Search), color: '#E6A23C', route: '/examenes' },
  { title: 'Usuarios', count: 0, icon: markRaw(UserFilled), color: '#F56C6C', route: '/usuarios' }
])

const datos = ref({
  pacientes: [] as any[],
  doctores: [] as any[],
  citas: [] as any[],
  consultas: [] as any[],
  recetas: [] as any[],
  examenes: [] as any[],
  usuarios: [] as any[]
})

// Gráfica de Barras - Resumen General
const barChartData = computed(() => ({
  labels: ['Pacientes', 'Doctores', 'Citas', 'Consultas', 'Recetas', 'Exámenes', 'Usuarios'],
  values: [
    datos.value.pacientes.length,
    datos.value.doctores.length,
    datos.value.citas.length,
    datos.value.consultas.length,
    datos.value.recetas.length,
    datos.value.examenes.length,
    datos.value.usuarios.length
  ],
  colors: ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#409EFF', '#E6A23C', '#F56C6C']
}))

// Gráfica de Dona - Exámenes por Estado
const examenesPorEstado = computed(() => {
  const estados: Record<string, number> = {}
  datos.value.examenes.forEach(examen => {
    const estado = examen.Estado || 'Pendiente'
    estados[estado] = (estados[estado] || 0) + 1
  })
  
  const labels = Object.keys(estados)
  const values = Object.values(estados)
  const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399']
  
  return {
    labels,
    values,
    colors: colors.slice(0, labels.length)
  }
})

// Gráfica de Líneas - Citas por Mes
const citasPorMes = computed(() => {
  const meses: Record<string, number> = {}
  
  datos.value.citas.forEach(cita => {
    if (cita.Fecha_Hora) {
      const fecha = new Date(cita.Fecha_Hora)
      const mes = fecha.toLocaleString('es-ES', { month: 'short', year: 'numeric' })
      meses[mes] = (meses[mes] || 0) + 1
    }
  })
  
  const labels = Object.keys(meses).sort()
  const values = labels.map(label => meses[label])
  
  return {
    labels,
    values,
    color: '#409EFF'
  }
})

// Gráfica de Barras Horizontales - Usuarios por Rol
const usuariosPorRol = computed(() => {
  const roles: Record<string, number> = {}
  
  datos.value.usuarios.forEach(usuario => {
    const rol = usuario.Rol || 'Recepcionista'
    roles[rol] = (roles[rol] || 0) + 1
  })
  
  const labels = Object.keys(roles)
  const values = Object.values(roles)
  const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C']
  
  return {
    labels,
    values,
    colors: colors.slice(0, labels.length)
  }
})

function navigateTo(route: string) {
  router.push(route)
}

async function loadAllData() {
  loadingCharts.value = true
  try {
    // Cargar todos los datos
    const [pacientesRes, doctoresRes, citasRes, consultasRes, recetasRes, examenesRes, usuariosRes] = await Promise.all([
      getPacientes().catch(() => ({ data: [] })),
      getDoctores().catch(() => ({ data: [] })),
      getCitas().catch(() => ({ data: [] })),
      getConsultas().catch(() => ({ data: [] })),
      getRecetas().catch(() => ({ data: [] })),
      getExamenes().catch(() => ({ data: [] })),
      getUsuarios().catch(() => ({ data: [] }))
    ])

    datos.value = {
      pacientes: pacientesRes.data,
      doctores: doctoresRes.data,
      citas: citasRes.data,
      consultas: consultasRes.data,
      recetas: recetasRes.data,
      examenes: examenesRes.data,
      usuarios: usuariosRes.data
    }

    // Actualizar contadores en las cards
    cards.value[0].count = datos.value.pacientes.length
    cards.value[1].count = datos.value.doctores.length
    cards.value[2].count = datos.value.citas.length
    cards.value[3].count = datos.value.consultas.length
    cards.value[4].count = datos.value.recetas.length
    cards.value[5].count = 0 // Historial - no hay endpoint directo
    cards.value[6].count = datos.value.examenes.length
    cards.value[7].count = datos.value.usuarios.length
  } catch (error) {
    console.error('Error al cargar datos:', error)
  } finally {
    loadingCharts.value = false
  }
}

onMounted(() => {
  loadAllData()
})
</script>

<style scoped>
.chart-container {
  height: 300px;
  width: 100%;
  position: relative;
}

.chart-container-small {
  height: 220px;
  width: 100%;
  position: relative;
}

.chart-card {
  margin-bottom: 16px;
}

.chart-card :deep(.el-card__body) {
  padding: 12px;
}

.chart-card :deep(.el-card__header) {
  padding: 12px 16px;
}
</style>
