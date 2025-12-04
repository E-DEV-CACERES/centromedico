<template>
  <AppLayout>
    <div class="p-6">
      <div class="mb-4 flex justify-between items-center">
        <h2 class="text-2xl font-bold text-gray-800">Gestión de Citas</h2>
        <el-button type="primary" @click="handleCreate">
          <el-icon class="mr-2"><Plus /></el-icon>
          Nueva Cita
        </el-button>
      </div>

      <el-card>
        <el-table :data="citas" v-loading="loading" stripe>
          <el-table-column prop="Codigo" label="Código" width="100" />
          <el-table-column prop="Codigo_Paciente" label="Paciente" width="120" />
          <el-table-column prop="Codigo_Doctor" label="Doctor" width="120" />
          <el-table-column prop="Fecha_Hora" label="Fecha y Hora" />
          <el-table-column prop="Estado" label="Estado" width="120" />
          <el-table-column prop="Motivo" label="Motivo" />
          <el-table-column label="Acciones" width="200" fixed="right">
            <template #default="{ row }">
              <el-button size="small" @click="handleEdit(row)">Editar</el-button>
              <el-button size="small" type="danger" @click="handleDelete(row.Codigo)">
                Eliminar
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import AppLayout from '@/components/AppLayout.vue'

const citas = ref([])
const loading = ref(false)

function handleCreate() {
  ElMessage.info('Funcionalidad en desarrollo')
}

function handleEdit(row: any) {
  ElMessage.info('Funcionalidad en desarrollo')
}

function handleDelete(codigo: number) {
  ElMessage.info('Funcionalidad en desarrollo')
}

onMounted(() => {
  // Cargar citas
})
</script>
