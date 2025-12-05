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

      <!-- Alerta de notificación de cita creada -->
      <el-alert
        v-if="showCitaCreatedAlert"
        title="¡Cita creada exitosamente!"
        type="success"
        :closable="true"
        @close="showCitaCreatedAlert = false"
        class="mb-4"
        show-icon
      >
        <template #default>
          <div class="mt-2">
            <p><strong>Paciente:</strong> {{ alertData.paciente }}</p>
            <p><strong>Doctor:</strong> {{ alertData.doctor }}</p>
            <p><strong>Fecha y Hora:</strong> {{ alertData.fechaHora }}</p>
            <p><strong>Estado:</strong> {{ alertData.estado }}</p>
          </div>
        </template>
      </el-alert>

      <el-card>
        <el-table :data="citas" v-loading="loading" stripe>
          <el-table-column prop="Codigo" label="Código" width="100" />
          <el-table-column label="Paciente" width="180">
            <template #default="{ row }">
              <span v-if="pacientes.length > 0">{{ getPacienteNombre(row.Codigo_Paciente) }}</span>
              <span v-else>{{ row.Codigo_Paciente }}</span>
            </template>
          </el-table-column>
          <el-table-column label="Doctor" width="180">
            <template #default="{ row }">
              <span v-if="doctores.length > 0">{{ getDoctorNombre(row.Codigo_Doctor) }}</span>
              <span v-else>{{ row.Codigo_Doctor }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="Fecha_Hora" label="Fecha y Hora" />
          <el-table-column prop="Estado" label="Estado" width="120" />
          <el-table-column prop="Motivo" label="Motivo" />
          <el-table-column label="Acciones" width="200" fixed="right" align="center">
            <template #default="{ row }">
              <div class="flex gap-2 justify-center">
                <el-button 
                  size="small" 
                  type="warning" 
                  @click="handleEdit(row)"
                  :icon="Edit"
                  circle
                  title="Editar"
                />
                <el-button 
                  size="small" 
                  type="success" 
                  @click="handleCargarAConsulta(row)"
                  :icon="ArrowRight"
                  circle
                  title="Cargar a Consulta"
                />
                <el-button 
                  size="small" 
                  type="danger" 
                  @click="handleDelete(row.Codigo)"
                  circle
                  title="Eliminar"
                >
                  <el-icon><Close /></el-icon>
                </el-button>
              </div>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- Dialog para crear/editar -->
      <el-dialog
        v-model="dialogVisible"
        :title="isEdit ? 'Editar Cita' : 'Nueva Cita'"
        width="600px"
      >
        <el-form :model="form" label-width="150px">
          <el-form-item label="Paciente" required>
            <el-select
              v-model="form.Codigo_Paciente"
              placeholder="Seleccione un paciente"
              filterable
              style="width: 100%"
            >
              <el-option
                v-for="paciente in pacientes"
                :key="paciente.Codigo"
                :label="`${paciente.Nombre} ${paciente.Apellidos}`"
                :value="paciente.Codigo"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="Doctor" required>
            <el-select
              v-model="form.Codigo_Doctor"
              placeholder="Seleccione un doctor"
              filterable
              style="width: 100%"
            >
              <el-option
                v-for="doctor in doctoresActivos"
                :key="doctor.Codigo"
                :label="`${doctor.Nombre} ${doctor.Apellidos}${doctor.Especialidad ? ' - ' + doctor.Especialidad : ''}`"
                :value="doctor.Codigo"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="Fecha y Hora" required>
            <el-date-picker
              v-model="form.Fecha_Hora"
              type="datetime"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DDTHH:mm:ss"
              placeholder="Seleccione fecha y hora"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="Estado">
            <el-select v-model="form.Estado" placeholder="Seleccionar" style="width: 100%">
              <el-option label="Programada" value="Programada" />
              <el-option label="Confirmada" value="Confirmada" />
              <el-option label="Cancelada" value="Cancelada" />
              <el-option label="Completada" value="Completada" />
            </el-select>
          </el-form-item>
          <el-form-item label="Motivo">
            <el-input v-model="form.Motivo" type="textarea" :rows="3" />
          </el-form-item>
          <el-form-item label="Observaciones">
            <el-input v-model="form.Observaciones" type="textarea" :rows="3" />
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
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import { Plus, Edit, ArrowRight, Close } from '@element-plus/icons-vue'
import AppLayout from '@/components/AppLayout.vue'
import {
  getCitas,
  createCita,
  updateCita,
  deleteCita,
  type Cita,
  type CitaCreate
} from '@/services/citas'
import { createConsulta, type ConsultaCreate } from '@/services/consultas'
import { getDoctores, type Doctor } from '@/services/doctores'
import { getPacientes, type Paciente } from '@/services/pacientes'
import { useRouter } from 'vue-router'

const citas = ref<Cita[]>([])
const doctores = ref<Doctor[]>([])
const pacientes = ref<Paciente[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const showCitaCreatedAlert = ref(false)
const alertData = ref({
  paciente: '',
  doctor: '',
  fechaHora: '',
  estado: ''
})
const form = ref<CitaCreate & { Codigo?: number }>({
  Codigo_Paciente: 0,
  Codigo_Doctor: 0,
  Fecha_Hora: '',
  Estado: 'Programada',
  Motivo: '',
  Observaciones: ''
})

// Computed para filtrar solo doctores activos
const doctoresActivos = computed(() => {
  return doctores.value.filter(d => d.Estado === 'Activo')
})

// Mapeos para búsqueda rápida
const pacientesMap = computed(() => {
  const map = new Map<number, Paciente>()
  pacientes.value.forEach(p => map.set(p.Codigo, p))
  return map
})

const doctoresMap = computed(() => {
  const map = new Map<number, Doctor>()
  doctores.value.forEach(d => map.set(d.Codigo, d))
  return map
})

const router = useRouter()

async function loadCitas() {
  loading.value = true
  try {
    const response = await getCitas()
    citas.value = response.data
  } catch (error) {
    ElMessage.error('Error al cargar citas')
  } finally {
    loading.value = false
  }
}

async function loadDoctores() {
  try {
    const response = await getDoctores()
    doctores.value = response.data
  } catch (error) {
    ElMessage.error('Error al cargar doctores')
  }
}

async function loadPacientes() {
  try {
    const response = await getPacientes()
    pacientes.value = response.data
  } catch (error) {
    ElMessage.error('Error al cargar pacientes')
  }
}

function getPacienteNombre(codigo: number | undefined): string {
  if (!codigo) return 'N/A'
  const paciente = pacientesMap.value.get(codigo)
  return paciente ? `${paciente.Nombre} ${paciente.Apellidos}` : `Paciente ${codigo}`
}

function getDoctorNombre(codigo: number | undefined): string {
  if (!codigo) return 'N/A'
  const doctor = doctoresMap.value.get(codigo)
  return doctor ? `${doctor.Nombre} ${doctor.Apellidos}${doctor.Especialidad ? ' - ' + doctor.Especialidad : ''}` : `Doctor ${codigo}`
}

function formatearFechaHora(fechaHora: string | undefined): string {
  if (!fechaHora) return 'N/A'
  try {
    const fecha = new Date(fechaHora)
    return fecha.toLocaleString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return fechaHora
  }
}

function handleCreate() {
  isEdit.value = false
  form.value = {
    Codigo_Paciente: 0,
    Codigo_Doctor: 0,
    Fecha_Hora: '',
    Estado: 'Programada',
    Motivo: '',
    Observaciones: ''
  }
  // Cargar doctores y pacientes si no están cargados
  if (doctores.value.length === 0) {
    loadDoctores()
  }
  if (pacientes.value.length === 0) {
    loadPacientes()
  }
  dialogVisible.value = true
}

function handleEdit(row: Cita) {
  isEdit.value = true
  form.value = { ...row }
  dialogVisible.value = true
}

async function handleSubmit() {
  // Validar campos requeridos
  if (!form.value.Codigo_Paciente || form.value.Codigo_Paciente === 0) {
    ElMessage.warning('Debe seleccionar un paciente')
    return
  }
  
  if (!form.value.Codigo_Doctor || form.value.Codigo_Doctor === 0) {
    ElMessage.warning('Debe seleccionar un doctor')
    return
  }
  
  if (!form.value.Fecha_Hora) {
    ElMessage.warning('Debe seleccionar una fecha y hora')
    return
  }

  try {
    // Asegurar que la fecha tenga el formato ISO 8601 correcto para Pydantic
    let fechaHora = form.value.Fecha_Hora
    
    // Si es un string, normalizarlo al formato ISO 8601
    if (typeof fechaHora === 'string') {
      // Reemplazar espacio por T si no tiene T
      if (!fechaHora.includes('T')) {
        fechaHora = fechaHora.replace(' ', 'T')
      }
      // Asegurar que tenga segundos (formato: YYYY-MM-DDTHH:mm:ss)
      const timePart = fechaHora.split('T')[1]
      if (timePart) {
        const timeParts = timePart.split(':')
        if (timeParts.length === 2) {
          // Si solo tiene horas y minutos, agregar segundos
          fechaHora = fechaHora.replace(timePart, `${timePart}:00`)
        }
      }
    }
    
    // Validar que la fecha sea futura (con margen de 5 minutos)
    const fechaSeleccionada = new Date(fechaHora)
    const ahora = new Date()
    ahora.setMinutes(ahora.getMinutes() - 5) // Margen de 5 minutos
    
    if (fechaSeleccionada < ahora) {
      ElMessage.warning('La fecha y hora de la cita debe ser en el futuro')
      return
    }
    
    // Preparar datos para enviar
    const datosEnvio: CitaCreate = {
      Codigo_Paciente: form.value.Codigo_Paciente,
      Codigo_Doctor: form.value.Codigo_Doctor,
      Fecha_Hora: fechaHora,
      Estado: form.value.Estado || 'Programada',
      Motivo: form.value.Motivo && form.value.Motivo.trim() ? form.value.Motivo.trim() : undefined,
      Observaciones: form.value.Observaciones && form.value.Observaciones.trim() ? form.value.Observaciones.trim() : undefined
    }
    
    console.log('Datos a enviar:', datosEnvio)
    console.log('Tipo de Fecha_Hora:', typeof datosEnvio.Fecha_Hora)

    if (isEdit.value && form.value.Codigo) {
      await updateCita(form.value.Codigo, datosEnvio)
      ElMessage.success('Cita actualizada correctamente')
    } else {
      // Crear la cita
      await createCita(datosEnvio)
      
      // Obtener información del paciente y doctor para la notificación
      const pacienteNombre = getPacienteNombre(form.value.Codigo_Paciente)
      const doctorNombre = getDoctorNombre(form.value.Codigo_Doctor)
      const fechaFormateada = formatearFechaHora(form.value.Fecha_Hora)
      
      // Mostrar notificación
      ElNotification({
        title: '¡Cita Creada Exitosamente!',
        message: `Cita programada para ${pacienteNombre} con ${doctorNombre} el ${fechaFormateada}`,
        type: 'success',
        duration: 5000,
        position: 'top-right',
        showClose: true
      })
      
      // Mostrar alerta en la página
      alertData.value = {
        paciente: pacienteNombre,
        doctor: doctorNombre,
        fechaHora: fechaFormateada,
        estado: datosEnvio.Estado || 'Programada'
      }
      showCitaCreatedAlert.value = true
      
      // Ocultar la alerta después de 8 segundos
      setTimeout(() => {
        showCitaCreatedAlert.value = false
      }, 8000)
      
      ElMessage.success('Cita creada correctamente')
    }
    dialogVisible.value = false
    loadCitas()
  } catch (error: any) {
    console.error('Error completo al guardar cita:', error)
    console.error('Response:', error?.response)
    
    let errorMessage = 'Error al guardar cita'
    
    if (error?.response?.data) {
      const errorData = error.response.data
      // Pydantic validation errors
      if (errorData.detail && Array.isArray(errorData.detail)) {
        const validationErrors = errorData.detail.map((err: any) => {
          const field = err.loc ? err.loc.join('.') : 'campo'
          return `${field}: ${err.msg}`
        }).join(', ')
        errorMessage = `Error de validación: ${validationErrors}`
      } else if (errorData.detail) {
        errorMessage = errorData.detail
      } else if (errorData.message) {
        errorMessage = errorData.message
      }
    }
    
    ElMessage.error(errorMessage)
  }
}

async function handleCargarAConsulta(cita: Cita) {
  try {
    await ElMessageBox.confirm(
      '¿Desea crear una consulta médica a partir de esta cita?',
      'Cargar a Consulta',
      {
        type: 'info',
        confirmButtonText: 'Sí, crear consulta',
        cancelButtonText: 'Cancelar'
      }
    )

    // Normalizar fecha de la cita
    let fechaConsulta = cita.Fecha_Hora
    if (fechaConsulta && typeof fechaConsulta === 'string') {
      if (!fechaConsulta.includes('T')) {
        fechaConsulta = fechaConsulta.replace(' ', 'T')
      }
      const timePart = fechaConsulta.split('T')[1]
      if (timePart) {
        const timeParts = timePart.split(':')
        if (timeParts.length === 2) {
          fechaConsulta = fechaConsulta.replace(timePart, `${timePart}:00`)
        }
      }
    }

    // Preparar datos de la consulta basados en la cita
    const consultaData: ConsultaCreate = {
      Codigo_Paciente: cita.Codigo_Paciente || undefined,
      Codigo_Doctor: cita.Codigo_Doctor || undefined,
      Tipo_de_Consulta: cita.Motivo || 'Consulta General',
      Fecha_de_Consulta: fechaConsulta || undefined,
      Diagnostico: cita.Observaciones || undefined,
      Estado: 'Programada'
    }

    console.log('Creando consulta desde cita:', consultaData)

    // Crear la consulta
    const response = await createConsulta(consultaData)
    
    // Eliminar la cita después de crear la consulta exitosamente
    if (cita.Codigo) {
      try {
        await deleteCita(cita.Codigo)
        ElMessage.success('Consulta creada y cita eliminada correctamente')
      } catch (deleteError) {
        console.error('Error al eliminar la cita:', deleteError)
        ElMessage.warning('Consulta creada, pero hubo un error al eliminar la cita')
      }
    } else {
      ElMessage.success('Consulta creada correctamente desde la cita')
    }
    
    // Recargar las citas para actualizar la lista
    await loadCitas()
    
    // Redirigir a la vista de consultas con el código para abrir el diálogo de edición
    if (response.data?.Codigo) {
      router.push({
        path: '/consultas',
        query: { editar: response.data.Codigo.toString() }
      })
    } else {
      router.push('/consultas')
    }
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('Error al crear consulta desde cita:', error)
      
      let errorMessage = 'Error al crear la consulta'
      if (error?.response?.data) {
        const errorData = error.response.data
        if (errorData.detail && Array.isArray(errorData.detail)) {
          const validationErrors = errorData.detail
            .map((err: any) => {
              const field = err.loc ? err.loc.join('.') : 'campo'
              return `${field}: ${err.msg}`
            })
            .join(', ')
          errorMessage = `Error de validación: ${validationErrors}`
        } else if (errorData.detail) {
          errorMessage = errorData.detail
        } else if (errorData.message) {
          errorMessage = errorData.message
        }
      }
      
      ElMessage.error(errorMessage)
    }
  }
}

async function handleDelete(codigo: number) {
  try {
    await ElMessageBox.confirm('¿Está seguro de eliminar esta cita?', 'Confirmar', {
      type: 'warning'
    })
    await deleteCita(codigo)
    ElMessage.success('Cita eliminada correctamente')
    loadCitas()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Error al eliminar cita')
    }
  }
}

onMounted(() => {
  loadCitas()
  loadDoctores()
  loadPacientes()
})
</script>
