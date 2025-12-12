<template>
  <AppLayout>
    <div class="p-6">
      <div class="mb-4">
        <h2 class="text-2xl font-bold text-gray-800">Gestión de Exámenes de Laboratorio</h2>
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
              style="width: 250px"
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
              style="width: 250px"
            >
              <el-option
                v-for="doctor in doctores"
                :key="doctor.Codigo"
                :label="`${doctor.Nombre} ${doctor.Apellidos}${doctor.Especialidad ? ' - ' + doctor.Especialidad : ''}`"
                :value="doctor.Codigo"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="Estado">
            <el-select
              v-model="filtros.estado"
              placeholder="Todos los estados"
              clearable
              style="width: 150px"
            >
              <el-option label="Pendiente" value="Pendiente" />
              <el-option label="Completado" value="Completado" />
              <el-option label="Cancelado" value="Cancelado" />
            </el-select>
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="aplicarFiltros">Buscar</el-button>
            <el-button @click="limpiarFiltros">Limpiar</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- Tabla de exámenes -->
      <el-card>
        <el-table :data="examenesFiltrados" v-loading="loading" stripe>
          <el-table-column prop="Codigo" label="Código" width="100" />
          <el-table-column label="Paciente" width="200">
            <template #default="{ row }">
              <span v-if="pacientes.length > 0 && row.Codigo_Paciente">
                {{ getPacienteNombre(row.Codigo_Paciente) }}
              </span>
              <span v-else-if="row.Codigo_Paciente">{{ row.Codigo_Paciente }}</span>
              <span v-else class="text-gray-400">N/A</span>
            </template>
          </el-table-column>
          <el-table-column label="Doctor" width="200">
            <template #default="{ row }">
              <span v-if="doctores.length > 0 && row.Codigo_Doctor">
                {{ getDoctorNombre(row.Codigo_Doctor) }}
              </span>
              <span v-else-if="row.Codigo_Doctor">{{ row.Codigo_Doctor }}</span>
              <span v-else class="text-gray-400">N/A</span>
            </template>
          </el-table-column>
          <el-table-column prop="Tipo_Examen" label="Tipo de Examen" min-width="200" show-overflow-tooltip />
          <el-table-column prop="Fecha_Solicitud" label="Fecha Solicitud" width="180">
            <template #default="{ row }">
              {{ formatearFecha(row.Fecha_Solicitud) }}
            </template>
          </el-table-column>
          <el-table-column prop="Estado" label="Estado" width="120">
            <template #default="{ row }">
              <el-tag
                :type="getEstadoTagType(row.Estado)"
                size="small"
              >
                {{ row.Estado || 'Pendiente' }}
              </el-tag>
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
                  @click="imprimirExamen(row)"
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

        <!-- Paginación -->
        <div class="mt-4 flex justify-end">
          <el-pagination
            v-model:current-page="paginacion.pagina"
            v-model:page-size="paginacion.tamano"
            :page-sizes="[10, 20, 50, 100]"
            :total="examenesFiltrados.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </el-card>

      <!-- Dialog para crear/editar examen -->
      <el-dialog
        v-model="dialogVisible"
        :title="isEdit ? 'Editar Examen de Laboratorio' : 'Nuevo Examen de Laboratorio'"
        width="700px"
      >
        <el-form :model="form" :rules="rules" ref="formRef" label-width="150px">
          <el-form-item label="Paciente" prop="Codigo_Paciente">
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
          <el-form-item label="Doctor" prop="Codigo_Doctor">
            <el-select
              v-model="form.Codigo_Doctor"
              placeholder="Seleccione un doctor"
              filterable
              style="width: 100%"
            >
              <el-option
                v-for="doctor in doctores"
                :key="doctor.Codigo"
                :label="`${doctor.Nombre} ${doctor.Apellidos}${doctor.Especialidad ? ' - ' + doctor.Especialidad : ''}`"
                :value="doctor.Codigo"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="Tipo de Examen" prop="Tipo_Examen">
            <el-input
              v-model="form.Tipo_Examen"
              placeholder="Ej: Hemograma completo, Radiografía de tórax..."
            />
          </el-form-item>
          <el-form-item label="Fecha de Solicitud" prop="Fecha_Solicitud">
            <el-date-picker
              v-model="form.Fecha_Solicitud"
              type="datetime"
              format="YYYY-MM-DD HH:mm"
              value-format="YYYY-MM-DDTHH:mm:ss"
              placeholder="Seleccione fecha y hora"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="Estado" prop="Estado">
            <el-select
              v-model="form.Estado"
              placeholder="Seleccione el estado"
              style="width: 100%"
            >
              <el-option label="Pendiente" value="Pendiente" />
              <el-option label="Completado" value="Completado" />
              <el-option label="Cancelado" value="Cancelado" />
            </el-select>
          </el-form-item>
          <el-form-item label="Fecha de Resultado" v-if="form.Estado === 'Completado'">
            <el-date-picker
              v-model="form.Fecha_Resultado"
              type="datetime"
              format="YYYY-MM-DD HH:mm"
              value-format="YYYY-MM-DDTHH:mm:ss"
              placeholder="Seleccione fecha y hora del resultado"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="Resultado" v-if="form.Estado === 'Completado'">
            <el-input
              v-model="form.Resultado"
              type="textarea"
              :rows="4"
              placeholder="Ingrese el resultado del examen"
            />
          </el-form-item>
          <el-form-item label="Observaciones">
            <el-input
              v-model="form.Observaciones"
              type="textarea"
              :rows="3"
              placeholder="Ingrese observaciones adicionales"
            />
          </el-form-item>
        </el-form>
        <template #footer>
          <el-button @click="dialogVisible = false">Cancelar</el-button>
          <el-button type="primary" @click="handleSubmit" :loading="submitting">
            {{ isEdit ? 'Actualizar' : 'Crear' }}
          </el-button>
        </template>
      </el-dialog>

      <!-- Dialog para ver detalles -->
      <el-dialog
        v-model="dialogDetallesVisible"
        title="Detalles del Examen de Laboratorio"
        width="800px"
      >
        <el-descriptions :column="2" border v-if="examenSeleccionado">
          <el-descriptions-item label="Código">
            {{ examenSeleccionado.Codigo }}
          </el-descriptions-item>
          <el-descriptions-item label="Estado">
            <el-tag :type="getEstadoTagType(examenSeleccionado.Estado)" size="small">
              {{ examenSeleccionado.Estado || 'Pendiente' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Paciente">
            {{ getPacienteNombre(examenSeleccionado.Codigo_Paciente) }}
          </el-descriptions-item>
          <el-descriptions-item label="Doctor">
            {{ getDoctorNombre(examenSeleccionado.Codigo_Doctor) }}
          </el-descriptions-item>
          <el-descriptions-item label="Tipo de Examen" :span="2">
            {{ examenSeleccionado.Tipo_Examen }}
          </el-descriptions-item>
          <el-descriptions-item label="Fecha de Solicitud">
            {{ formatearFecha(examenSeleccionado.Fecha_Solicitud) }}
          </el-descriptions-item>
          <el-descriptions-item label="Fecha de Resultado" v-if="examenSeleccionado.Fecha_Resultado">
            {{ formatearFecha(examenSeleccionado.Fecha_Resultado) }}
          </el-descriptions-item>
          <el-descriptions-item label="Resultado" :span="2" v-if="examenSeleccionado.Resultado">
            <div class="whitespace-pre-wrap">
              {{ examenSeleccionado.Resultado }}
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="Observaciones" :span="2" v-if="examenSeleccionado.Observaciones">
            <div class="whitespace-pre-wrap">
              {{ examenSeleccionado.Observaciones }}
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="Fecha de Creación" v-if="examenSeleccionado.Fecha_Creacion">
            {{ formatearFecha(examenSeleccionado.Fecha_Creacion) }}
          </el-descriptions-item>
          <el-descriptions-item label="Última Modificación" v-if="examenSeleccionado.Fecha_Modificacion">
            {{ formatearFecha(examenSeleccionado.Fecha_Modificacion) }}
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
import { ref, onMounted, computed, nextTick } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance, type FormRules } from 'element-plus'
import { View, Edit, Close, Printer } from '@element-plus/icons-vue'
import AppLayout from '@/components/AppLayout.vue'
import {
  getExamenes,
  createExamen,
  updateExamen,
  deleteExamen,
  type Examen,
  type ExamenCreate,
  type ExamenUpdate,
  type ExamenFilters
} from '@/services/examenes'
import { getPacientes, type Paciente } from '@/services/pacientes'
import { getDoctores, type Doctor } from '@/services/doctores'

const examenes = ref<Examen[]>([])
const pacientes = ref<Paciente[]>([])
const doctores = ref<Doctor[]>([])
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const dialogDetallesVisible = ref(false)
const isEdit = ref(false)
const examenSeleccionado = ref<Examen | null>(null)
const formRef = ref<FormInstance>()

const filtros = ref<ExamenFilters>({
  codigo_paciente: undefined,
  codigo_doctor: undefined,
  estado: undefined
})

const paginacion = ref({
  pagina: 1,
  tamano: 20
})

const form = ref<ExamenCreate & { Codigo?: number }>({
  Codigo_Paciente: 0,
  Codigo_Doctor: 0,
  Tipo_Examen: '',
  Fecha_Solicitud: undefined,
  Fecha_Resultado: undefined,
  Resultado: undefined,
  Observaciones: undefined,
  Estado: 'Pendiente'
})

const rules: FormRules = {
  Codigo_Paciente: [
    { required: true, message: 'Por favor seleccione un paciente', trigger: 'change' }
  ],
  Codigo_Doctor: [
    { required: true, message: 'Por favor seleccione un doctor', trigger: 'change' }
  ],
  Tipo_Examen: [
    { required: true, message: 'Por favor ingrese el tipo de examen', trigger: 'blur' }
  ],
  Fecha_Solicitud: [
    { required: true, message: 'Por favor seleccione la fecha de solicitud', trigger: 'change' }
  ],
  Estado: [
    { required: true, message: 'Por favor seleccione el estado', trigger: 'change' }
  ]
}

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

// Exámenes filtrados
const examenesFiltrados = computed(() => {
  let resultado = [...examenes.value]

  // Filtrar por paciente
  if (filtros.value.codigo_paciente) {
    resultado = resultado.filter(e => e.Codigo_Paciente === filtros.value.codigo_paciente)
  }

  // Filtrar por doctor
  if (filtros.value.codigo_doctor) {
    resultado = resultado.filter(e => e.Codigo_Doctor === filtros.value.codigo_doctor)
  }

  // Filtrar por estado
  if (filtros.value.estado) {
    resultado = resultado.filter(e => e.Estado === filtros.value.estado)
  }

  // Ordenar por fecha descendente (más recientes primero)
  resultado.sort((a, b) => {
    const fechaA = a.Fecha_Solicitud ? new Date(a.Fecha_Solicitud).getTime() : 0
    const fechaB = b.Fecha_Solicitud ? new Date(b.Fecha_Solicitud).getTime() : 0
    return fechaB - fechaA
  })

  // Aplicar paginación
  const inicio = (paginacion.value.pagina - 1) * paginacion.value.tamano
  const fin = inicio + paginacion.value.tamano
  return resultado.slice(inicio, fin)
})

async function loadExamenes() {
  loading.value = true
  try {
    const response = await getExamenes()
    examenes.value = response.data
  } catch (error) {
    ElMessage.error('Error al cargar exámenes de laboratorio')
    console.error('Error al cargar exámenes:', error)
  } finally {
    loading.value = false
  }
}

async function loadPacientes() {
  try {
    const response = await getPacientes()
    pacientes.value = response.data
  } catch (error) {
    ElMessage.error('Error al cargar pacientes')
    console.error('Error al cargar pacientes:', error)
  }
}

async function loadDoctores() {
  try {
    const response = await getDoctores()
    doctores.value = response.data
  } catch (error) {
    ElMessage.error('Error al cargar doctores')
    console.error('Error al cargar doctores:', error)
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
    case 'Completado':
      return 'success'
    case 'Pendiente':
      return 'warning'
    case 'Cancelado':
      return 'danger'
    default:
      return 'info'
  }
}

function aplicarFiltros() {
  paginacion.value.pagina = 1
  ElMessage.success('Filtros aplicados')
}

function limpiarFiltros() {
  filtros.value = {
    codigo_paciente: undefined,
    codigo_doctor: undefined,
    estado: undefined
  }
  paginacion.value.pagina = 1
  ElMessage.info('Filtros limpiados')
}

function handleEdit(row: Examen) {
  isEdit.value = true
  form.value = {
    Codigo: row.Codigo,
    Codigo_Paciente: row.Codigo_Paciente,
    Codigo_Doctor: row.Codigo_Doctor,
    Tipo_Examen: row.Tipo_Examen,
    Fecha_Solicitud: row.Fecha_Solicitud,
    Fecha_Resultado: row.Fecha_Resultado,
    Resultado: row.Resultado,
    Observaciones: row.Observaciones,
    Estado: row.Estado || 'Pendiente'
  }
  dialogVisible.value = true
  nextTick(() => {
    formRef.value?.clearValidate()
  })
}

async function handleSubmit() {
  if (!formRef.value) return

  await formRef.value.validate((valid) => {
    if (valid) {
      submitting.value = true
      
      if (isEdit.value) {
        // Actualizar
        const codigo = form.value.Codigo!
        const datosEnvio: ExamenUpdate = {
          Codigo_Paciente: form.value.Codigo_Paciente,
          Codigo_Doctor: form.value.Codigo_Doctor,
          Tipo_Examen: form.value.Tipo_Examen,
          Fecha_Solicitud: form.value.Fecha_Solicitud,
          Fecha_Resultado: form.value.Fecha_Resultado,
          Resultado: form.value.Resultado,
          Observaciones: form.value.Observaciones,
          Estado: form.value.Estado
        }

        updateExamen(codigo, datosEnvio)
          .then(() => {
            ElMessage.success('Examen actualizado exitosamente')
            dialogVisible.value = false
            loadExamenes()
          })
          .catch((error) => {
            ElMessage.error('Error al actualizar el examen')
            console.error('Error:', error)
          })
          .finally(() => {
            submitting.value = false
          })
      } else {
        // Crear
        const datosEnvio: ExamenCreate = {
          Codigo_Paciente: form.value.Codigo_Paciente,
          Codigo_Doctor: form.value.Codigo_Doctor,
          Tipo_Examen: form.value.Tipo_Examen,
          Fecha_Solicitud: form.value.Fecha_Solicitud,
          Fecha_Resultado: form.value.Fecha_Resultado,
          Resultado: form.value.Resultado,
          Observaciones: form.value.Observaciones,
          Estado: form.value.Estado
        }

        createExamen(datosEnvio)
          .then(() => {
            ElMessage.success('Examen creado exitosamente')
            dialogVisible.value = false
            loadExamenes()
          })
          .catch((error) => {
            ElMessage.error('Error al crear el examen')
            console.error('Error:', error)
          })
          .finally(() => {
            submitting.value = false
          })
      }
    }
  })
}

function handleDelete(codigo: number) {
  ElMessageBox.confirm(
    '¿Está seguro de que desea eliminar este examen? Esta acción no se puede deshacer.',
    'Confirmar eliminación',
    {
      confirmButtonText: 'Eliminar',
      cancelButtonText: 'Cancelar',
      type: 'warning'
    }
  )
    .then(() => {
      deleteExamen(codigo)
        .then(() => {
          ElMessage.success('Examen eliminado exitosamente')
          loadExamenes()
        })
        .catch((error) => {
          ElMessage.error('Error al eliminar el examen')
          console.error('Error:', error)
        })
    })
    .catch(() => {
      // Usuario canceló
    })
}

function verDetalles(examen: Examen) {
  examenSeleccionado.value = examen
  dialogDetallesVisible.value = true
}

function handleSizeChange(val: number) {
  paginacion.value.tamano = val
  paginacion.value.pagina = 1
}

function handlePageChange(val: number) {
  paginacion.value.pagina = val
}

function imprimirExamen(examen: Examen) {
  // Crear ventana de impresión
  const ventanaImpresion = window.open('', '_blank', 'width=800,height=600')
  if (!ventanaImpresion) {
    ElMessage.error('Por favor, permite ventanas emergentes para imprimir')
    return
  }

  // Obtener información del paciente y doctor
  const pacienteInfo = pacientesMap.value.get(examen.Codigo_Paciente || 0)
  const doctorInfo = doctoresMap.value.get(examen.Codigo_Doctor || 0)
  
  const nombrePaciente = pacienteInfo 
    ? `${pacienteInfo.Nombre} ${pacienteInfo.Apellidos}` 
    : 'N/A'
  const telefonoPaciente = pacienteInfo?.Numero_Celular || ''
  const fechaNacPaciente = pacienteInfo?.Fecha_Nacimiento 
    ? formatearFecha(pacienteInfo.Fecha_Nacimiento) 
    : ''
  const direccionPaciente = pacienteInfo?.Direccion || ''
  
  const nombreDoctor = doctorInfo 
    ? `Dr. ${doctorInfo.Nombre} ${doctorInfo.Apellidos}` 
    : 'N/A'
  const especialidadDoctor = doctorInfo?.Especialidad || ''

  // Formatear fechas y datos
  const fechaSolicitud = examen.Fecha_Solicitud
    ? formatearFecha(examen.Fecha_Solicitud)
    : 'N/A'
  const fechaResultado = examen.Fecha_Resultado
    ? formatearFecha(examen.Fecha_Resultado)
    : 'N/A'
  const tipoExamen = examen.Tipo_Examen || 'N/A'
  const estado = examen.Estado || 'Pendiente'
  const resultado = examen.Resultado 
    ? examen.Resultado.replace(/\n/g, '<br>') 
    : 'Sin resultado disponible'
  const observaciones = examen.Observaciones 
    ? examen.Observaciones.replace(/\n/g, '<br>') 
    : 'Sin observaciones'

  // Construir sección de paciente
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

  if (direccionPaciente) {
    seccionPaciente += `
      <div class="info-row">
        <span class="info-label">Dirección:</span>
        <span class="info-value">${direccionPaciente}</span>
      </div>`
  }
  
  seccionPaciente += `</div>`

  // Construir sección de doctor
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

  // Construir sección de estado con color
  const estadoColor = estado === 'Completado' ? '#67C23A' : estado === 'Pendiente' ? '#E6A23C' : '#F56C6C'
  const estadoBg = estado === 'Completado' ? '#F0F9FF' : estado === 'Pendiente' ? '#FFF7E6' : '#FEF0F0'

  // Generar HTML del baucher
  const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Examen de Laboratorio - ${examen.Codigo}</title>
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
    .examen-section {
      margin-top: 30px;
      border: 1px solid #000;
      padding: 20px;
    }
    .examen-section h3 {
      font-size: 18px;
      margin-bottom: 15px;
      text-align: center;
      text-transform: uppercase;
    }
    .examen-content {
      font-size: 14px;
      line-height: 1.8;
    }
    .tipo-examen {
      font-size: 18px;
      font-weight: bold;
      margin-bottom: 15px;
      text-align: center;
      padding: 15px;
      background: #f5f5f5;
      border-left: 4px solid #409EFF;
    }
    .estado-section {
      margin-top: 20px;
      padding: 15px;
      background: ${estadoBg};
      border-left: 4px solid ${estadoColor};
      border-radius: 4px;
    }
    .resultado-section {
      margin-top: 20px;
      padding: 15px;
      background: #f0f8ff;
      border-left: 4px solid #409EFF;
    }
    .observaciones-section {
      margin-top: 20px;
      padding: 15px;
      background: #fffacd;
      border-left: 4px solid #E6A23C;
    }
    .footer {
      margin-top: 40px;
      padding-top: 20px;
      border-top: 2px solid #000;
      text-align: center;
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
    <button onclick="window.print()"> Imprimir Examen</button>
    <button onclick="window.close()"> Cerrar</button>
  </div>
  
  <div class="baucher">
    <div class="codigo-badge">EXAMEN #${examen.Codigo}</div>
    
    <div class="header">
      <h1>Centro Médico</h1>
      <h2>EXAMEN DE LABORATORIO</h2>
    </div>

    ${seccionPaciente}

    ${seccionDoctor}

    <div class="examen-section">
      <h3>INFORMACIÓN DEL EXAMEN</h3>
      <div class="examen-content">
        <div class="tipo-examen">${tipoExamen}</div>
        <div class="info-row">
          <span class="info-label">Código:</span>
          <span class="info-value">${examen.Codigo}</span>
        </div>
        <div class="info-row">
          <span class="info-label">Fecha de Solicitud:</span>
          <span class="info-value"><strong>${fechaSolicitud}</strong></span>
        </div>
        ${examen.Fecha_Resultado ? `
        <div class="info-row">
          <span class="info-label">Fecha de Resultado:</span>
          <span class="info-value"><strong>${fechaResultado}</strong></span>
        </div>
        ` : ''}
      </div>
    </div>

    <div class="estado-section">
      <strong>ESTADO:</strong><br>
      <div style="margin-top: 10px; font-size: 16px; font-weight: bold; color: ${estadoColor};">
        ${estado}
      </div>
    </div>

    ${examen.Resultado ? `
    <div class="resultado-section">
      <strong>RESULTADO:</strong><br>
      <div style="margin-top: 10px; line-height: 1.8;">
        ${resultado}
      </div>
    </div>
    ` : ''}

    ${examen.Observaciones ? `
    <div class="observaciones-section">
      <strong>OBSERVACIONES:</strong><br>
      <div style="margin-top: 10px; line-height: 1.8;">
        ${observaciones}
      </div>
    </div>
    ` : ''}

    <div class="footer">
      <div style="margin-top: 30px; font-size: 12px; color: #666;">
        <p>Este documento es parte del expediente médico del paciente.</p>
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
  loadExamenes()
  loadPacientes()
  loadDoctores()
})
</script>

<style scoped>
.whitespace-pre-wrap {
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
