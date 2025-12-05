<template>
  <AppLayout>
    <div class="p-6">
      <div class="mb-4 flex justify-between items-center">
        <h2 class="text-2xl font-bold text-gray-800">Gestión de Recetas Médicas</h2>
        <el-button type="primary" @click="handleCreate">
          <el-icon class="mr-2"><Plus /></el-icon>
          Nueva Receta
        </el-button>
      </div>

      <!-- Filtros -->
      <el-card class="mb-4">
        <el-form :inline="true" :model="filtros" class="demo-form-inline">
          <el-form-item label="Paciente">
            <el-select
              v-model="filtros.codigo_paciente"
              placeholder="Todos los pacientes"
              filterable
              clearable
              style="width: 200px"
            >
              <el-option
                v-for="paciente in pacientes"
                :key="paciente.Codigo"
                :label="`${paciente.Nombre} ${paciente.Apellidos}`"
                :value="paciente.Codigo"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="Doctor">
            <el-select
              v-model="filtros.codigo_doctor"
              placeholder="Todos los doctores"
              filterable
              clearable
              style="width: 200px"
            >
              <el-option
                v-for="doctor in doctores"
                :key="doctor.Codigo"
                :label="`${doctor.Nombre} ${doctor.Apellidos}${doctor.Especialidad ? ' - ' + doctor.Especialidad : ''}`"
                :value="doctor.Codigo"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="Fecha Desde">
            <el-date-picker
              v-model="filtros.fechaDesde"
              type="date"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              placeholder="Fecha desde"
              style="width: 150px"
            />
          </el-form-item>
          <el-form-item label="Fecha Hasta">
            <el-date-picker
              v-model="filtros.fechaHasta"
              type="date"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              placeholder="Fecha hasta"
              style="width: 150px"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="aplicarFiltros">Buscar</el-button>
            <el-button @click="limpiarFiltros">Limpiar</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- Tabla de recetas -->
      <el-card>
        <el-table :data="recetasFiltradas" v-loading="loading" stripe>
          <el-table-column prop="receta.Codigo" label="Código" width="100" />
          <el-table-column label="Paciente" width="180">
            <template #default="{ row }">
              <span v-if="row.paciente">
                {{ `${row.paciente.Nombre} ${row.paciente.Apellidos}` }}
              </span>
              <span v-else-if="row.receta.Nombre_Paciente">{{ row.receta.Nombre_Paciente }}</span>
              <span v-else class="text-gray-400">N/A</span>
            </template>
          </el-table-column>
          <el-table-column label="Doctor" width="200">
            <template #default="{ row }">
              <span v-if="row.doctor">
                {{ `${row.doctor.Nombre} ${row.doctor.Apellidos}${row.doctor.Especialidad ? ' - ' + row.doctor.Especialidad : ''}` }}
              </span>
              <span v-else class="text-gray-400">N/A</span>
            </template>
          </el-table-column>
          <el-table-column prop="receta.Fecha_Receta" label="Fecha de Receta" width="180">
            <template #default="{ row }">
              {{ formatearFecha(row.receta.Fecha_Receta) }}
            </template>
          </el-table-column>
          <el-table-column prop="receta.Medicamento" label="Medicamento" show-overflow-tooltip />
          <el-table-column label="Consulta" width="120">
            <template #default="{ row }">
              <el-tag v-if="row.consulta" type="info" size="small">
                {{ row.consulta.Codigo }}
              </el-tag>
              <span v-else class="text-gray-400">N/A</span>
            </template>
          </el-table-column>
          <el-table-column label="Acciones" width="240" fixed="right" align="center">
            <template #default="{ row }">
              <div class="flex gap-2 justify-center">
                <el-button 
                  size="small" 
                  type="primary" 
                  @click="verDetalles(row)"
                  :icon="View"
                  circle
                  title="Ver Detalles"
                />
                <el-button 
                  size="small" 
                  type="success" 
                  @click="imprimirReceta(row)"
                  :icon="Printer"
                  circle
                  title="Imprimir"
                />
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
                  type="danger" 
                  @click="handleDelete(row.receta.Codigo)"
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
        :title="isEdit ? 'Editar Receta' : 'Nueva Receta'"
        width="700px"
      >
        <el-form :model="form" label-width="150px">
          <el-form-item label="Paciente" required>
            <el-select
              v-model="form.Codigo_Paciente"
              placeholder="Seleccione un paciente"
              filterable
              clearable
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
              clearable
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
          <el-form-item label="Consulta (Opcional)">
            <el-select
              v-model="form.Codigo_Consulta"
              placeholder="Seleccione una consulta"
              filterable
              clearable
              style="width: 100%"
            >
              <el-option
                v-for="consulta in consultas"
                :key="consulta.Codigo"
                :label="`Consulta #${consulta.Codigo} - ${formatearFecha(consulta.Fecha_de_Consulta)}`"
                :value="consulta.Codigo"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="Fecha de Receta">
            <el-date-picker
              v-model="form.Fecha_Receta"
              type="datetime"
              format="YYYY-MM-DD HH:mm:ss"
              value-format="YYYY-MM-DDTHH:mm:ss"
              placeholder="Seleccione fecha y hora"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="Medicamento" required>
            <el-input
              v-model="form.Medicamento"
              type="textarea"
              :rows="3"
              placeholder="Ingrese el nombre del medicamento"
            />
          </el-form-item>
          <el-form-item label="Instrucciones" required>
            <el-input
              v-model="form.Instrucciones"
              type="textarea"
              :rows="4"
              placeholder="Ingrese las instrucciones de uso del medicamento"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="dialogVisible = false">Cancelar</el-button>
          <el-button type="primary" @click="handleSubmit">Guardar</el-button>
        </template>
      </el-dialog>

      <!-- Dialog para ver detalles -->
      <el-dialog
        v-model="dialogDetallesVisible"
        title="Detalles de la Receta"
        width="800px"
      >
        <el-descriptions :column="2" border v-if="recetaSeleccionada">
          <el-descriptions-item label="Código">
            {{ recetaSeleccionada.receta.Codigo }}
          </el-descriptions-item>
          <el-descriptions-item label="Fecha de Receta">
            {{ formatearFecha(recetaSeleccionada.receta.Fecha_Receta) }}
          </el-descriptions-item>
          <el-descriptions-item label="Paciente" :span="2">
            <div v-if="recetaSeleccionada.paciente">
              <strong>{{ `${recetaSeleccionada.paciente.Nombre} ${recetaSeleccionada.paciente.Apellidos}` }}</strong>
              <div class="text-sm text-gray-500 mt-1">
                <span v-if="recetaSeleccionada.paciente.Telefono">Tel: {{ recetaSeleccionada.paciente.Telefono }}</span>
                <span v-if="recetaSeleccionada.paciente.Email" class="ml-2">Email: {{ recetaSeleccionada.paciente.Email }}</span>
              </div>
            </div>
            <span v-else class="text-gray-400">N/A</span>
          </el-descriptions-item>
          <el-descriptions-item label="Doctor" :span="2">
            <div v-if="recetaSeleccionada.doctor">
              <strong>{{ `${recetaSeleccionada.doctor.Nombre} ${recetaSeleccionada.doctor.Apellidos}` }}</strong>
              <div class="text-sm text-gray-500 mt-1">
                <span v-if="recetaSeleccionada.doctor.Especialidad">Especialidad: {{ recetaSeleccionada.doctor.Especialidad }}</span>
                <el-tag :type="recetaSeleccionada.doctor.Estado === 'Activo' ? 'success' : 'danger'" size="small" class="ml-2">
                  {{ recetaSeleccionada.doctor.Estado }}
                </el-tag>
              </div>
            </div>
            <span v-else class="text-gray-400">N/A</span>
          </el-descriptions-item>
          <el-descriptions-item label="Consulta" :span="2" v-if="recetaSeleccionada.consulta">
            <div>
              <strong>Consulta #{{ recetaSeleccionada.consulta.Codigo }}</strong>
              <div class="text-sm text-gray-500 mt-1">
                <div>Tipo: {{ recetaSeleccionada.consulta.Tipo_de_Consulta || 'N/A' }}</div>
                <div>Fecha: {{ formatearFecha(recetaSeleccionada.consulta.Fecha_de_Consulta) }}</div>
                <div>Estado: 
                  <el-tag 
                    :type="getEstadoTagType(recetaSeleccionada.consulta.Estado)" 
                    size="small"
                  >
                    {{ recetaSeleccionada.consulta.Estado }}
                  </el-tag>
                </div>
                <div v-if="recetaSeleccionada.consulta.Diagnostico" class="mt-2">
                  <strong>Diagnóstico:</strong>
                  <p class="text-sm whitespace-pre-wrap">{{ recetaSeleccionada.consulta.Diagnostico }}</p>
                </div>
              </div>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="Medicamento" :span="2">
            <div class="whitespace-pre-wrap">
              {{ recetaSeleccionada.receta.Medicamento || 'N/A' }}
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="Instrucciones" :span="2">
            <div class="whitespace-pre-wrap">
              {{ recetaSeleccionada.receta.Instrucciones || 'N/A' }}
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="Fecha de Creación" v-if="recetaSeleccionada.receta.Fecha_Creacion">
            {{ formatearFecha(recetaSeleccionada.receta.Fecha_Creacion) }}
          </el-descriptions-item>
          <el-descriptions-item label="Última Modificación" v-if="recetaSeleccionada.receta.Fecha_Modificacion">
            {{ formatearFecha(recetaSeleccionada.receta.Fecha_Modificacion) }}
          </el-descriptions-item>
        </el-descriptions>
        <template #footer>
          <el-button @click="dialogDetallesVisible = false">Cerrar</el-button>
        </template>
      </el-dialog>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Printer, View, Edit, Close } from '@element-plus/icons-vue'
import AppLayout from '@/components/AppLayout.vue'
import {
  getRecetasCompletas,
  createReceta,
  updateReceta,
  deleteReceta,
  type RecetaCompleta,
  type RecetaCreate
} from '@/services/recetas'
import { getConsultas, type Consulta } from '@/services/consultas'
import { getDoctores, type Doctor } from '@/services/doctores'
import { getPacientes, type Paciente } from '@/services/pacientes'

const recetas = ref<RecetaCompleta[]>([])
const doctores = ref<Doctor[]>([])
const pacientes = ref<Paciente[]>([])
const consultas = ref<Consulta[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogDetallesVisible = ref(false)
const isEdit = ref(false)
const recetaSeleccionada = ref<RecetaCompleta | null>(null)

const form = ref<RecetaCreate & { Codigo?: number }>({
  Codigo_Paciente: undefined,
  Codigo_Doctor: undefined,
  Codigo_Consulta: undefined,
  Nombre_Paciente: undefined,
  Fecha_Receta: undefined,
  Medicamento: undefined,
  Instrucciones: undefined
})

const filtros = ref({
  codigo_paciente: undefined as number | undefined,
  codigo_doctor: undefined as number | undefined,
  fechaDesde: undefined as string | undefined,
  fechaHasta: undefined as string | undefined
})

// Computed para filtrar solo doctores activos
const doctoresActivos = computed(() => {
  return doctores.value.filter(d => d.Estado === 'Activo')
})

// Recetas filtradas
const recetasFiltradas = computed(() => {
  let resultado = [...recetas.value]

  // Filtrar por paciente
  if (filtros.value.codigo_paciente) {
    resultado = resultado.filter(r => r.receta.Codigo_Paciente === filtros.value.codigo_paciente)
  }

  // Filtrar por doctor
  if (filtros.value.codigo_doctor) {
    resultado = resultado.filter(r => r.receta.Codigo_Doctor === filtros.value.codigo_doctor)
  }

  // Filtrar por fecha desde
  if (filtros.value.fechaDesde) {
    resultado = resultado.filter(r => {
      if (!r.receta.Fecha_Receta) return false
      const fechaReceta = new Date(r.receta.Fecha_Receta)
      const fechaDesde = new Date(filtros.value.fechaDesde!)
      fechaDesde.setHours(0, 0, 0, 0)
      return fechaReceta >= fechaDesde
    })
  }

  // Filtrar por fecha hasta
  if (filtros.value.fechaHasta) {
    resultado = resultado.filter(r => {
      if (!r.receta.Fecha_Receta) return false
      const fechaReceta = new Date(r.receta.Fecha_Receta)
      const fechaHasta = new Date(filtros.value.fechaHasta!)
      fechaHasta.setHours(23, 59, 59, 999)
      return fechaReceta <= fechaHasta
    })
  }

  // Ordenar por fecha descendente (más recientes primero)
  resultado.sort((a, b) => {
    const fechaA = a.receta.Fecha_Receta ? new Date(a.receta.Fecha_Receta).getTime() : 0
    const fechaB = b.receta.Fecha_Receta ? new Date(b.receta.Fecha_Receta).getTime() : 0
    return fechaB - fechaA
  })

  return resultado
})

async function loadRecetas() {
  loading.value = true
  try {
    const response = await getRecetasCompletas()
    recetas.value = response.data
  } catch (error) {
    ElMessage.error('Error al cargar recetas')
    console.error('Error al cargar recetas:', error)
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

async function loadConsultas() {
  try {
    const response = await getConsultas()
    consultas.value = response.data
  } catch (error) {
    console.error('Error al cargar consultas:', error)
  }
}

function formatearFecha(fecha: string | undefined): string {
  if (!fecha) return 'N/A'
  try {
    const date = new Date(fecha)
    return date.toLocaleString('es-ES', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return fecha
  }
}

function getEstadoTagType(estado: string | undefined): string {
  switch (estado) {
    case 'Completada':
      return 'success'
    case 'En Proceso':
      return 'warning'
    case 'Cancelada':
      return 'danger'
    case 'Programada':
      return 'info'
    default:
      return ''
  }
}

function aplicarFiltros() {
  ElMessage.success('Filtros aplicados')
}

function limpiarFiltros() {
  filtros.value = {
    codigo_paciente: undefined,
    codigo_doctor: undefined,
    fechaDesde: undefined,
    fechaHasta: undefined
  }
  ElMessage.info('Filtros limpiados')
}

function handleCreate() {
  isEdit.value = false
  form.value = {
    Codigo_Paciente: undefined,
    Codigo_Doctor: undefined,
    Codigo_Consulta: undefined,
    Nombre_Paciente: undefined,
    Fecha_Receta: new Date().toISOString().split('T')[0] + 'T' + new Date().toTimeString().split(' ')[0],
    Medicamento: undefined,
    Instrucciones: undefined
  }
  // Cargar datos si no están cargados
  if (doctores.value.length === 0) {
    loadDoctores()
  }
  if (pacientes.value.length === 0) {
    loadPacientes()
  }
  if (consultas.value.length === 0) {
    loadConsultas()
  }
  dialogVisible.value = true
}

function handleEdit(row: RecetaCompleta) {
  isEdit.value = true
  form.value = {
    Codigo: row.receta.Codigo,
    Codigo_Paciente: row.receta.Codigo_Paciente,
    Codigo_Doctor: row.receta.Codigo_Doctor,
    Codigo_Consulta: row.receta.Codigo_Consulta,
    Nombre_Paciente: row.receta.Nombre_Paciente,
    Fecha_Receta: row.receta.Fecha_Receta,
    Medicamento: row.receta.Medicamento,
    Instrucciones: row.receta.Instrucciones
  }
  dialogVisible.value = true
}

function verDetalles(row: RecetaCompleta) {
  recetaSeleccionada.value = row
  dialogDetallesVisible.value = true
}

async function handleSubmit() {
  // Validar campos requeridos
  if (!form.value.Codigo_Paciente) {
    ElMessage.warning('Debe seleccionar un paciente')
    return
  }
  
  if (!form.value.Codigo_Doctor) {
    ElMessage.warning('Debe seleccionar un doctor')
    return
  }
  
  if (!form.value.Medicamento || !form.value.Medicamento.trim()) {
    ElMessage.warning('Debe ingresar el medicamento')
    return
  }
  
  if (!form.value.Instrucciones || !form.value.Instrucciones.trim()) {
    ElMessage.warning('Debe ingresar las instrucciones')
    return
  }

  try {
    // Normalizar fecha si existe
    let fechaReceta = form.value.Fecha_Receta
    if (fechaReceta && typeof fechaReceta === 'string') {
      if (!fechaReceta.includes('T')) {
        fechaReceta = fechaReceta.replace(' ', 'T')
      }
      const timePart = fechaReceta.split('T')[1]
      if (timePart) {
        const timeParts = timePart.split(':')
        if (timeParts.length === 2) {
          fechaReceta = fechaReceta.replace(timePart, `${timePart}:00`)
        }
      }
    }

    // Obtener nombre del paciente
    const paciente = pacientes.value.find(p => p.Codigo === form.value.Codigo_Paciente)
    const nombrePaciente = paciente ? `${paciente.Nombre} ${paciente.Apellidos}` : undefined

    // Preparar datos para enviar
    const datosEnvio: RecetaCreate = {
      Codigo_Paciente: form.value.Codigo_Paciente,
      Codigo_Doctor: form.value.Codigo_Doctor,
      Codigo_Consulta: form.value.Codigo_Consulta || undefined,
      Nombre_Paciente: nombrePaciente,
      Fecha_Receta: fechaReceta || undefined,
      Medicamento: form.value.Medicamento.trim(),
      Instrucciones: form.value.Instrucciones.trim()
    }

    console.log('Datos a enviar:', datosEnvio)

    if (isEdit.value && form.value.Codigo) {
      await updateReceta(form.value.Codigo, datosEnvio)
      ElMessage.success('Receta actualizada correctamente')
    } else {
      await createReceta(datosEnvio)
      ElMessage.success('Receta creada correctamente')
    }
    dialogVisible.value = false
    await loadRecetas()
  } catch (error: any) {
    console.error('Error completo al guardar receta:', error)
    console.error('Response:', error?.response)

    let errorMessage = 'Error al guardar receta'

    if (error?.response?.data) {
      const errorData = error.response.data
      // Pydantic validation errors
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

async function handleDelete(codigo: number) {
  try {
    await ElMessageBox.confirm('¿Está seguro de eliminar esta receta?', 'Confirmar', {
      type: 'warning'
    })
    await deleteReceta(codigo)
    ElMessage.success('Receta eliminada correctamente')
    await loadRecetas()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Error al eliminar receta')
    }
  }
}

function imprimirReceta(receta: RecetaCompleta) {
  // Crear ventana de impresión
  const ventanaImpresion = window.open('', '_blank', 'width=800,height=600')
  if (!ventanaImpresion) {
    ElMessage.error('Por favor, permite ventanas emergentes para imprimir')
    return
  }

  // Obtener información
  const pacienteInfo = receta.paciente
  const doctorInfo = receta.doctor
  const consultaInfo = receta.consulta
  const datosReceta = receta.receta

  // Formatear fecha
  const fechaReceta = datosReceta.Fecha_Receta
    ? formatearFecha(datosReceta.Fecha_Receta)
    : 'N/A'

  // Preparar datos para el HTML
  const nombrePaciente = pacienteInfo 
    ? `${pacienteInfo.Nombre} ${pacienteInfo.Apellidos}` 
    : datosReceta.Nombre_Paciente || 'N/A'
  const telefonoPaciente = pacienteInfo?.Telefono || ''
  const fechaNacPaciente = pacienteInfo?.Fecha_Nacimiento 
    ? formatearFecha(pacienteInfo.Fecha_Nacimiento) 
    : ''
  const nombreDoctor = doctorInfo 
    ? `Dr. ${doctorInfo.Nombre} ${doctorInfo.Apellidos}` 
    : 'N/A'
  const especialidadDoctor = doctorInfo?.Especialidad || ''
  const codigoConsulta = consultaInfo?.Codigo || ''
  const tipoConsulta = consultaInfo?.Tipo_de_Consulta || ''
  const fechaConsulta = consultaInfo?.Fecha_de_Consulta 
    ? formatearFecha(consultaInfo.Fecha_de_Consulta) 
    : ''
  const examenesSolicitados = consultaInfo?.Examenes_Solicitados || false
  const examenesDescripcion = consultaInfo?.Examenes_Descripcion || ''
  const examenesSugeridos = consultaInfo?.Examenes_Sugeridos || false
  const examenesSugeridosDescripcion = consultaInfo?.Examenes_Sugeridos_Descripcion || ''
  const medicamento = datosReceta.Medicamento || 'N/A'
  const instrucciones = datosReceta.Instrucciones 
    ? datosReceta.Instrucciones.replace(/\n/g, '<br>') 
    : ''

  // Construir secciones HTML
  let seccionPaciente = `
    <div class="info-section">
      <h3>INFORMACIÓN DEL PACIENTE</h3>
      <div class="info-row">
        <span class="info-label">Nombre:</span>
        <span class="info-value">${nombrePaciente}</span>
      </div>`
  
  if (telefonoPaciente) {
    seccionPaciente += `
      <div class="info-row">
        <span class="info-label">Teléfono:</span>
        <span class="info-value">${telefonoPaciente}</span>
      </div>`
  }
  
  if (fechaNacPaciente) {
    seccionPaciente += `
      <div class="info-row">
        <span class="info-label">Fecha de Nacimiento:</span>
        <span class="info-value">${fechaNacPaciente}</span>
      </div>`
  }
  
  seccionPaciente += `</div>`

  let seccionDoctor = `
    <div class="info-section">
      <h3>INFORMACIÓN DEL MÉDICO</h3>
      <div class="info-row">
        <span class="info-label">Doctor:</span>
        <span class="info-value">${nombreDoctor}</span>
      </div>`
  
  if (especialidadDoctor) {
    seccionDoctor += `
      <div class="info-row">
        <span class="info-label">Especialidad:</span>
        <span class="info-value">${especialidadDoctor}</span>
      </div>`
  }
  
  seccionDoctor += `</div>`

  let seccionConsulta = ''
  if (consultaInfo) {
    seccionConsulta = `
      <div class="info-section">
        <h3>INFORMACIÓN DE LA CONSULTA</h3>
        <div class="info-row">
          <span class="info-label">Consulta #:</span>
          <span class="info-value">${codigoConsulta}</span>
        </div>`
    
    if (tipoConsulta) {
      seccionConsulta += `
        <div class="info-row">
          <span class="info-label">Tipo:</span>
          <span class="info-value">${tipoConsulta}</span>
        </div>`
    }
    
    if (fechaConsulta) {
      seccionConsulta += `
        <div class="info-row">
          <span class="info-label">Fecha de Consulta:</span>
          <span class="info-value">${fechaConsulta}</span>
        </div>`
    }
    
    seccionConsulta += `</div>`
  }

  // Sección de exámenes solicitados y sugeridos
  let seccionExamenes = ''
  if (consultaInfo && ((examenesSolicitados && examenesDescripcion) || (examenesSugeridos && examenesSugeridosDescripcion))) {
    seccionExamenes = `
      <div class="medicamento-section" style="margin-top: 20px; border-color: #409EFF;">
        <h3>EXÁMENES MÉDICOS</h3>
        <div class="medicamento-content">`
    
    if (examenesSolicitados && examenesDescripcion) {
      seccionExamenes += `
          <div style="margin-bottom: 20px; padding: 15px; background: #FFF7E6; border-left: 4px solid #E6A23C; border-radius: 4px;">
            <div style="font-weight: bold; margin-bottom: 8px; color: #E6A23C; font-size: 15px;"> EXÁMENES SOLICITADOS (Obligatorios)</div>
            <div style="padding-left: 10px; line-height: 1.8; color: #333;">${examenesDescripcion.replace(/\n/g, '<br>')}</div>
          </div>`
    }
    
    if (examenesSugeridos && examenesSugeridosDescripcion) {
      seccionExamenes += `
          <div style="padding: 15px; background: #ECF5FF; border-left: 4px solid #409EFF; border-radius: 4px;">
            <div style="font-weight: bold; margin-bottom: 8px; color: #409EFF; font-size: 15px;">💡 EXÁMENES SUGERIDOS (Opcionales)</div>
            <div style="padding-left: 10px; line-height: 1.8; color: #333;">${examenesSugeridosDescripcion.replace(/\n/g, '<br>')}</div>
          </div>`
    }
    
    seccionExamenes += `
        </div>
      </div>`
  }

  let seccionInstrucciones = ''
  if (instrucciones) {
    seccionInstrucciones = `
      <div class="instrucciones">
        <strong>Instrucciones:</strong><br>
        ${instrucciones}
      </div>`
  }

  // Generar HTML del baucher
  const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Receta Médica - ${datosReceta.Codigo}</title>
  <style>
    @media print {
      @page {
        size: A4;
        margin: 1cm;
      }
      body {
        margin: 0;
        padding: 0;
      }
      .no-print {
        display: none;
      }
    }
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    body {
      font-family: Arial, sans-serif;
      padding: 20px;
      max-width: 800px;
      margin: 0 auto;
      background: white;
    }
    .baucher {
      border: 2px solid #000;
      padding: 30px;
      background: white;
      position: relative;
    }
    .header {
      text-align: center;
      border-bottom: 3px solid #000;
      padding-bottom: 20px;
      margin-bottom: 30px;
    }
    .header h1 {
      font-size: 28px;
      font-weight: bold;
      margin-bottom: 10px;
      text-transform: uppercase;
    }
    .header h2 {
      font-size: 20px;
      font-weight: normal;
      color: #333;
    }
    .info-section {
      margin-bottom: 25px;
    }
    .info-section h3 {
      font-size: 16px;
      font-weight: bold;
      margin-bottom: 10px;
      border-bottom: 1px solid #ccc;
      padding-bottom: 5px;
    }
    .info-row {
      display: flex;
      margin-bottom: 8px;
      font-size: 14px;
    }
    .info-label {
      font-weight: bold;
      width: 150px;
      min-width: 150px;
    }
    .info-value {
      flex: 1;
    }
    .medicamento-section {
      margin-top: 30px;
      border: 1px solid #000;
      padding: 20px;
    }
    .medicamento-section h3 {
      font-size: 18px;
      margin-bottom: 15px;
      text-align: center;
      text-transform: uppercase;
    }
    .medicamento-content {
      font-size: 14px;
      line-height: 1.8;
    }
    .medicamento-name {
      font-size: 16px;
      font-weight: bold;
      margin-bottom: 10px;
      text-decoration: underline;
    }
    .instrucciones {
      margin-top: 15px;
      padding: 15px;
      background: #f5f5f5;
      border-left: 4px solid #000;
    }
    .footer {
      margin-top: 40px;
      padding-top: 20px;
      border-top: 2px solid #000;
      text-align: center;
    }
    .firma-section {
      margin-top: 50px;
      display: flex;
      justify-content: space-between;
    }
    .firma-box {
      text-align: center;
      width: 45%;
    }
    .firma-line {
      border-top: 1px solid #000;
      margin-top: 60px;
      padding-top: 5px;
    }
    .codigo-badge {
      position: absolute;
      top: 20px;
      right: 20px;
      background: #000;
      color: white;
      padding: 8px 15px;
      font-weight: bold;
      font-size: 14px;
    }
    .no-print {
      text-align: center;
      padding: 20px;
      background: #f0f0f0;
      margin-bottom: 20px;
    }
    .no-print button {
      padding: 10px 30px;
      font-size: 16px;
      background: #409EFF;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      margin: 0 10px;
    }
    .no-print button:hover {
      background: #66b1ff;
    }
  </style>
</head>
<body>
  <div class="no-print">
    <button onclick="window.print()"> Imprimir Receta</button>
    <button onclick="window.close()"> Cerrar</button>
  </div>
  
  <div class="baucher">
    <div class="codigo-badge">RECETA #${datosReceta.Codigo}</div>
    
    <div class="header">
      <h1>Centro Médico</h1>
      <h2>RECETA MÉDICA</h2>
    </div>

    ${seccionPaciente}

    ${seccionDoctor}

    ${seccionConsulta}

    ${seccionExamenes}

    <div class="medicamento-section">
      <h3>PRESCRIPCIÓN MÉDICA</h3>
      <div class="medicamento-content">
        <div class="medicamento-name">${medicamento}</div>
        ${seccionInstrucciones}
      </div>
    </div>

    <div class="info-section">
      <div class="info-row">
        <span class="info-label">Fecha de Receta:</span>
        <span class="info-value"><strong>${fechaReceta}</strong></span>
      </div>
    </div>

    <div class="footer">
      <div class="firma-section">
        <div class="firma-box">
          <div class="firma-line">
            <strong>Firma del Médico</strong>
          </div>
        </div>
        <div class="firma-box">
          <div class="firma-line">
            <strong>Firma del Paciente</strong>
          </div>
        </div>
      </div>
      <div style="margin-top: 30px; font-size: 12px; color: #666;">
        <p>Esta receta es válida por 30 días desde la fecha de emisión.</p>
        <p>Conserve este documento para su control médico.</p>
      </div>
    </div>
  </div>
</body>
</html>`

  // Escribir el HTML y abrir diálogo de impresión
  ventanaImpresion.document.write(html)
  ventanaImpresion.document.close()
}

onMounted(() => {
  loadRecetas()
  loadDoctores()
  loadPacientes()
  loadConsultas()
})
</script>

<style scoped>
.whitespace-pre-wrap {
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
