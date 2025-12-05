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
        <div v-if="!loading && !hasPacientes" class="text-center py-8 text-gray-500">
          <p>No hay pacientes registrados</p>
        </div>
        <el-table 
          v-else
          :data="pacientes" 
          v-loading="loading" 
          stripe
          empty-text="No hay datos"
        >
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
        :title="dialogTitle"
        width="600px"
        :close-on-click-modal="false"
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
import { ref, computed, onMounted } from 'vue'
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

// Estado reactivo
const pacientes = ref<Paciente[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const form = ref<PacienteCreate & { Codigo?: number }>(createEmptyForm())

// Computed properties
const hasPacientes = computed(() => pacientes.value.length > 0)
const dialogTitle = computed(() => isEdit.value ? 'Editar Paciente' : 'Nuevo Paciente')

// Constantes
const MESSAGES = {
  LOAD_ERROR: 'Error al cargar pacientes',
  SAVE_ERROR: 'Error al guardar paciente',
  DELETE_ERROR: 'Error al eliminar paciente',
  DELETE_SUCCESS: 'Paciente eliminado correctamente',
  UPDATE_SUCCESS: 'Paciente actualizado correctamente',
  CREATE_SUCCESS: 'Paciente creado correctamente',
  VALIDATION_REQUIRED: 'Nombre y Apellidos son requeridos',
  DELETE_CONFIRM: '¿Está seguro de eliminar este paciente?',
  NO_PATIENTS: 'No hay pacientes registrados'
} as const

/**
 * Crea un formulario vacío con valores por defecto
 */
function createEmptyForm(): PacienteCreate & { Codigo?: number } {
  return {
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
}

/**
 * Carga la lista de pacientes desde el servidor
 */
async function loadPacientes(): Promise<void> {
  loading.value = true
  try {
    const response = await getPacientes()
    
    if (Array.isArray(response.data)) {
      pacientes.value = response.data
    } else {
      ElMessage.error('Error: Los datos recibidos no tienen el formato esperado')
      pacientes.value = []
    }
  } catch (error: unknown) {
    handleError(error, MESSAGES.LOAD_ERROR)
    pacientes.value = []
  } finally {
    loading.value = false
  }
}

/**
 * Maneja errores de forma centralizada
 */
function handleError(error: unknown, defaultMessage: string): void {
  if (error && typeof error === 'object' && 'response' in error) {
    const axiosError = error as { response?: { data?: { detail?: string; message?: string } } }
    const errorMessage = axiosError.response?.data?.detail || 
                        axiosError.response?.data?.message || 
                        defaultMessage
    ElMessage.error(errorMessage)
  } else {
    ElMessage.error(defaultMessage)
  }
}

/**
 * Abre el diálogo para crear un nuevo paciente
 */
function handleCreate(): void {
  isEdit.value = false
  form.value = createEmptyForm()
  dialogVisible.value = true
}

/**
 * Abre el diálogo para editar un paciente existente
 */
function handleEdit(row: Paciente): void {
  isEdit.value = true
  form.value = { ...row }
  dialogVisible.value = true
}

/**
 * Valida el formulario antes de enviar
 */
function validateForm(): boolean {
  if (!form.value.Nombre?.trim() || !form.value.Apellidos?.trim()) {
    ElMessage.warning(MESSAGES.VALIDATION_REQUIRED)
    return false
  }
  return true
}

/**
 * Guarda o actualiza un paciente
 */
async function handleSubmit(): Promise<void> {
  if (!validateForm()) {
    return
  }

  try {
    if (isEdit.value && form.value.Codigo) {
      await updatePaciente(form.value.Codigo, form.value)
      ElMessage.success(MESSAGES.UPDATE_SUCCESS)
    } else {
      await createPaciente(form.value)
      ElMessage.success(MESSAGES.CREATE_SUCCESS)
    }
    dialogVisible.value = false
    await loadPacientes()
  } catch (error: unknown) {
    handleError(error, MESSAGES.SAVE_ERROR)
  }
}

/**
 * Elimina un paciente después de confirmación
 */
async function handleDelete(codigo: number): Promise<void> {
  try {
    await ElMessageBox.confirm(MESSAGES.DELETE_CONFIRM, 'Confirmar', {
      type: 'warning',
      confirmButtonText: 'Eliminar',
      cancelButtonText: 'Cancelar'
    })
    
    await deletePaciente(codigo)
    ElMessage.success(MESSAGES.DELETE_SUCCESS)
    await loadPacientes()
  } catch (error: unknown) {
    // El usuario canceló la acción
    if (error === 'cancel') {
      return
    }
    handleError(error, MESSAGES.DELETE_ERROR)
  }
}

// Lifecycle hooks
onMounted(() => {
  loadPacientes()
})
</script>
