<template>
  <AppLayout>
    <div class="p-6">
      <div class="mb-4 flex justify-between items-center">
        <h2 class="text-2xl font-bold text-gray-800">Gestión de Pacientes</h2>
        <el-button type="primary" @click="handleCreate">
          <el-icon class="mr-2"><Plus /></el-icon>
          Nuevo Paciente
        </el-button>
      </div>

      <el-card>
        <el-table :data="pacientes" v-loading="loading" stripe>
          <el-table-column prop="Codigo" label="Código" width="100" />
          <el-table-column prop="Nombre" label="Nombre" />
          <el-table-column prop="Apellidos" label="Apellidos" />
          <el-table-column prop="Edad" label="Edad" width="100" />
          <el-table-column prop="Numero_Celular" label="Teléfono" />
          <el-table-column prop="Tipo_Sangre" label="Tipo Sangre" width="120" />
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

      <!-- Dialog para crear/editar -->
      <el-dialog
        v-model="dialogVisible"
        :title="isEdit ? 'Editar Paciente' : 'Nuevo Paciente'"
        width="600px"
      >
        <el-form :model="form" label-width="150px">
          <el-form-item label="Nombre" required>
            <el-input v-model="form.Nombre" />
          </el-form-item>
          <el-form-item label="Apellidos" required>
            <el-input v-model="form.Apellidos" />
          </el-form-item>
          <el-form-item label="Edad">
            <el-input v-model="form.Edad" />
          </el-form-item>
          <el-form-item label="Dirección">
            <el-input v-model="form.Direccion" type="textarea" />
          </el-form-item>
          <el-form-item label="Número Celular">
            <el-input v-model.number="form.Numero_Celular" type="number" />
          </el-form-item>
          <el-form-item label="Fecha Nacimiento">
            <el-date-picker
              v-model="form.Fecha_Nacimiento"
              type="datetime"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DDTHH:mm:ss"
            />
          </el-form-item>
          <el-form-item label="Tipo Sangre">
            <el-input v-model="form.Tipo_Sangre" />
          </el-form-item>
          <el-form-item label="Alergias">
            <el-input v-model="form.Alergias" type="textarea" />
          </el-form-item>
          <el-form-item label="Contacto Emergencia">
            <el-input v-model="form.Contacto_Emergencia" />
          </el-form-item>
          <el-form-item label="Teléfono Emergencia">
            <el-input v-model.number="form.Telefono_Emergencia" type="number" />
          </el-form-item>
          <el-form-item label="Código Seguro">
            <el-input v-model.number="form.Codigo_Seguro" type="number" />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="dialogVisible = false">Cancelar</el-button>
          <el-button type="primary" @click="handleSubmit">Guardar</el-button>
        </template>
      </el-dialog>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import AppLayout from '@/components/AppLayout.vue'
import {
  getPacientes,
  createPaciente,
  updatePaciente,
  deletePaciente,
  type Paciente,
  type PacienteCreate
} from '@/services/pacientes'

const pacientes = ref<Paciente[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const form = ref<PacienteCreate & { Codigo?: number }>({
  Nombre: '',
  Apellidos: '',
  Edad: '',
  Direccion: '',
  Numero_Celular: undefined,
  Fecha_Nacimiento: undefined,
  Tipo_Sangre: '',
  Alergias: '',
  Contacto_Emergencia: '',
  Telefono_Emergencia: undefined,
  Codigo_Seguro: undefined
})

async function loadPacientes() {
  loading.value = true
  try {
    const response = await getPacientes()
    pacientes.value = response.data
  } catch (error) {
    ElMessage.error('Error al cargar pacientes')
  } finally {
    loading.value = false
  }
}

function handleCreate() {
  isEdit.value = false
  form.value = {
    Nombre: '',
    Apellidos: '',
    Edad: '',
    Direccion: '',
    Numero_Celular: undefined,
    Fecha_Nacimiento: undefined,
    Tipo_Sangre: '',
    Alergias: '',
    Contacto_Emergencia: '',
    Telefono_Emergencia: undefined,
    Codigo_Seguro: undefined
  }
  dialogVisible.value = true
}

function handleEdit(row: Paciente) {
  isEdit.value = true
  form.value = { ...row }
  dialogVisible.value = true
}

async function handleSubmit() {
  if (!form.value.Nombre || !form.value.Apellidos) {
    ElMessage.warning('Nombre y Apellidos son requeridos')
    return
  }

  try {
    if (isEdit.value && form.value.Codigo) {
      await updatePaciente(form.value.Codigo, form.value)
      ElMessage.success('Paciente actualizado correctamente')
    } else {
      await createPaciente(form.value)
      ElMessage.success('Paciente creado correctamente')
    }
    dialogVisible.value = false
    loadPacientes()
  } catch (error) {
    ElMessage.error('Error al guardar paciente')
  }
}

async function handleDelete(codigo: number) {
  try {
    await ElMessageBox.confirm('¿Está seguro de eliminar este paciente?', 'Confirmar', {
      type: 'warning'
    })
    await deletePaciente(codigo)
    ElMessage.success('Paciente eliminado correctamente')
    loadPacientes()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Error al eliminar paciente')
    }
  }
}

onMounted(() => {
  loadPacientes()
})
</script>
