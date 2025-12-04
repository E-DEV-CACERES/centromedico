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
            <li>Control de facturación</li>
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
import { ref, onMounted, markRaw } from 'vue'
import { useRouter } from 'vue-router'
import AppLayout from '@/components/AppLayout.vue'
import {
  User,
  Avatar,
  Calendar,
  Document,
  Money,
  Notebook,
  Files,
  Search,
  UserFilled
} from '@element-plus/icons-vue'
import { getPacientes } from '@/services/pacientes'
import { getDoctores } from '@/services/doctores'

const router = useRouter()

const cards = ref([
  { title: 'Pacientes', count: 0, icon: markRaw(User), color: '#409EFF', route: '/pacientes' },
  { title: 'Doctores', count: 0, icon: markRaw(Avatar), color: '#67C23A', route: '/doctores' },
  { title: 'Citas', count: 0, icon: markRaw(Calendar), color: '#E6A23C', route: '/citas' },
  { title: 'Consultas', count: 0, icon: markRaw(Document), color: '#F56C6C', route: '/consultas' },
  { title: 'Facturación', count: 0, icon: markRaw(Money), color: '#909399', route: '/facturacion' },
  { title: 'Recetas', count: 0, icon: markRaw(Notebook), color: '#409EFF', route: '/recetas' },
  { title: 'Historial', count: 0, icon: markRaw(Files), color: '#67C23A', route: '/historial' },
  { title: 'Exámenes', count: 0, icon: markRaw(Search), color: '#E6A23C', route: '/examenes' },
  { title: 'Usuarios', count: 0, icon: markRaw(UserFilled), color: '#F56C6C', route: '/usuarios' }
])

function navigateTo(route: string) {
  router.push(route)
}

onMounted(async () => {
  try {
    const pacientesRes = await getPacientes()
    cards.value[0].count = pacientesRes.data.length

    const doctoresRes = await getDoctores()
    cards.value[1].count = doctoresRes.data.length
  } catch (error) {
    console.error('Error al cargar datos:', error)
  }
})
</script>
