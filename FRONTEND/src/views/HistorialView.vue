<template>
  <AppLayout>
    <div class="p-6">
      <div class="mb-4 flex justify-between items-center">
        <h2 class="text-2xl font-bold text-gray-800">Historial Médico</h2>
        <el-button type="primary" @click="handleCreate">
          <el-icon class="mr-1"><Plus /></el-icon>
          Nuevo Historial
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
          <el-form-item label="Fecha Desde">
            <el-date-picker
              v-model="filtros.fechaDesde"
              type="date"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              placeholder="Fecha desde"
              style="width: 180px"
            />
          </el-form-item>
          <el-form-item label="Fecha Hasta">
            <el-date-picker
              v-model="filtros.fechaHasta"
              type="date"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
              placeholder="Fecha hasta"
              style="width: 180px"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="aplicarFiltros">Buscar</el-button>
            <el-button @click="limpiarFiltros">Limpiar</el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <!-- Tabla de historiales -->
      <el-card>
        <el-table :data="historialesFiltrados" v-loading="loading" stripe>
          <el-table-column prop="Codigo_Historial" label="Código" width="100" />
          <el-table-column label="Paciente" width="200">
            <template #default="{ row }">
              <span v-if="pacientes.length > 0 && row.Codigo_Paciente">
                {{ getPacienteNombre(row.Codigo_Paciente) }}
              </span>
              <span v-else-if="row.Codigo_Paciente">{{ row.Codigo_Paciente }}</span>
              <span v-else class="text-gray-400">N/A</span>
            </template>
          </el-table-column>
          <el-table-column prop="Fecha_Ingreso" label="Fecha de Ingreso" width="180">
            <template #default="{ row }">
              {{ formatearFecha(row.Fecha_Ingreso) }}
            </template>
          </el-table-column>
          <el-table-column prop="Diagnostico" label="Diagnóstico" show-overflow-tooltip min-width="200" />
          <el-table-column prop="Tratamiento" label="Tratamiento" show-overflow-tooltip min-width="200" />
          <el-table-column label="Exámenes Solicitados" min-width="250">
            <template #default="{ row }">
              <div v-if="row.Examenes_Solicitados && row.Examenes_Solicitados.length > 0" class="flex flex-col gap-1">
                <el-tag
                  v-for="(examen, index) in row.Examenes_Solicitados"
                  :key="index"
                  type="warning"
                  size="small"
                  class="mb-1"
                >
                  {{ examen.Descripcion }}
                </el-tag>
              </div>
              <span v-else class="text-gray-400 text-xs">Sin exámenes solicitados</span>
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
                  @click="imprimirHistorial(row)"
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
                  @click="handleDelete(row.Codigo_Historial)"
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
            :total="historialesFiltrados.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </el-card>

      <!-- Dialog para crear/editar historial -->
      <el-dialog
        v-model="dialogVisible"
        :title="isEdit ? 'Editar Historial Médico' : 'Nuevo Historial Médico'"
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
          <el-form-item label="Fecha de Ingreso" prop="Fecha_Ingreso">
            <el-date-picker
              v-model="form.Fecha_Ingreso"
              type="datetime"
              format="YYYY-MM-DD HH:mm"
              value-format="YYYY-MM-DDTHH:mm:ss"
              placeholder="Seleccione fecha y hora"
              style="width: 100%"
            />
          </el-form-item>
          <el-form-item label="Diagnóstico" prop="Diagnostico">
            <el-input
              v-model="form.Diagnostico"
              type="textarea"
              :rows="3"
              placeholder="Ingrese el diagnóstico"
            />
          </el-form-item>
          <el-form-item label="Tratamiento" prop="Tratamiento">
            <el-input
              v-model="form.Tratamiento"
              type="textarea"
              :rows="4"
              placeholder="Ingrese el tratamiento prescrito"
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
        title="Detalles del Historial Médico"
        width="800px"
      >
        <el-descriptions :column="2" border v-if="historialSeleccionado">
          <el-descriptions-item label="Código">
            {{ historialSeleccionado.Codigo_Historial }}
          </el-descriptions-item>
          <el-descriptions-item label="Paciente">
            {{ getPacienteNombre(historialSeleccionado.Codigo_Paciente) }}
          </el-descriptions-item>
          <el-descriptions-item label="Fecha de Ingreso">
            {{ formatearFecha(historialSeleccionado.Fecha_Ingreso) }}
          </el-descriptions-item>
          <el-descriptions-item label="Diagnóstico" :span="2">
            <div class="whitespace-pre-wrap">
              {{ historialSeleccionado.Diagnostico || 'Sin diagnóstico registrado' }}
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="Tratamiento" :span="2">
            <div class="whitespace-pre-wrap">
              {{ historialSeleccionado.Tratamiento || 'Sin tratamiento registrado' }}
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="Observaciones" :span="2">
            <div class="whitespace-pre-wrap">
              {{ historialSeleccionado.Observaciones || 'Sin observaciones' }}
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="Exámenes Solicitados" :span="2" v-if="historialSeleccionado.Examenes_Solicitados && historialSeleccionado.Examenes_Solicitados.length > 0">
            <div class="flex flex-col gap-2">
              <div
                v-for="(examen, index) in historialSeleccionado.Examenes_Solicitados"
                :key="index"
                class="border-l-4 border-yellow-400 pl-3 py-2 bg-yellow-50 rounded"
              >
                <div class="text-sm font-semibold text-gray-700">
                  {{ formatearFecha(examen.Fecha_Consulta) }}
                </div>
                <div class="text-sm text-gray-600 mt-1">
                  {{ examen.Descripcion }}
                </div>
              </div>
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="Exámenes Solicitados" :span="2" v-else>
            <span class="text-gray-400">Sin exámenes solicitados</span>
          </el-descriptions-item>
          <el-descriptions-item label="Fecha de Creación" v-if="historialSeleccionado.Fecha_Creacion">
            {{ formatearFecha(historialSeleccionado.Fecha_Creacion) }}
          </el-descriptions-item>
          <el-descriptions-item label="Última Modificación" v-if="historialSeleccionado.Fecha_Modificacion">
            {{ formatearFecha(historialSeleccionado.Fecha_Modificacion) }}
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
import { Plus, View, Edit, Close, Printer } from '@element-plus/icons-vue'
import AppLayout from '@/components/AppLayout.vue'
import {
  getHistoriales,
  createHistorial,
  updateHistorial,
  deleteHistorial,
  type Historial,
  type HistorialCreate,
  type HistorialUpdate,
  type HistorialFilters
} from '@/services/historial'
import { getPacientes, type Paciente } from '@/services/pacientes'

const historiales = ref<Historial[]>([])
const pacientes = ref<Paciente[]>([])
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const dialogDetallesVisible = ref(false)
const isEdit = ref(false)
const historialSeleccionado = ref<Historial | null>(null)
const formRef = ref<FormInstance>()

const filtros = ref<HistorialFilters & { fechaDesde?: string; fechaHasta?: string }>({
  codigo_paciente: undefined,
  fechaDesde: undefined,
  fechaHasta: undefined
})

const paginacion = ref({
  pagina: 1,
  tamano: 20
})

const form = ref<HistorialCreate & { Codigo_Historial?: number }>({
  Codigo_Paciente: undefined,
  Fecha_Ingreso: undefined,
  Diagnostico: undefined,
  Tratamiento: undefined,
  Observaciones: undefined
})

const rules: FormRules = {
  Codigo_Paciente: [
    { required: true, message: 'Por favor seleccione un paciente', trigger: 'change' }
  ],
  Fecha_Ingreso: [
    { required: true, message: 'Por favor seleccione la fecha de ingreso', trigger: 'change' }
  ],
  Diagnostico: [
    { required: true, message: 'Por favor ingrese el diagnóstico', trigger: 'blur' }
  ],
  Tratamiento: [
    { required: true, message: 'Por favor ingrese el tratamiento', trigger: 'blur' }
  ]
}

// Mapeos para búsqueda rápida
const pacientesMap = computed(() => {
  const map = new Map<number, Paciente>()
  pacientes.value.forEach(p => map.set(p.Codigo, p))
  return map
})

// Historiales filtrados
const historialesFiltrados = computed(() => {
  let resultado = [...historiales.value]

  // Filtrar por paciente
  if (filtros.value.codigo_paciente) {
    resultado = resultado.filter(h => h.Codigo_Paciente === filtros.value.codigo_paciente)
  }

  // Filtrar por fecha desde
  if (filtros.value.fechaDesde) {
    resultado = resultado.filter(h => {
      if (!h.Fecha_Ingreso) return false
      const fechaIngreso = new Date(h.Fecha_Ingreso)
      const fechaDesde = new Date(filtros.value.fechaDesde!)
      fechaDesde.setHours(0, 0, 0, 0)
      return fechaIngreso >= fechaDesde
    })
  }

  // Filtrar por fecha hasta
  if (filtros.value.fechaHasta) {
    resultado = resultado.filter(h => {
      if (!h.Fecha_Ingreso) return false
      const fechaIngreso = new Date(h.Fecha_Ingreso)
      const fechaHasta = new Date(filtros.value.fechaHasta!)
      fechaHasta.setHours(23, 59, 59, 999)
      return fechaIngreso <= fechaHasta
    })
  }

  // Ordenar por fecha descendente (más recientes primero)
  resultado.sort((a, b) => {
    const fechaA = a.Fecha_Ingreso ? new Date(a.Fecha_Ingreso).getTime() : 0
    const fechaB = b.Fecha_Ingreso ? new Date(b.Fecha_Ingreso).getTime() : 0
    return fechaB - fechaA
  })

  // Aplicar paginación
  const inicio = (paginacion.value.pagina - 1) * paginacion.value.tamano
  const fin = inicio + paginacion.value.tamano
  return resultado.slice(inicio, fin)
})

async function loadHistoriales() {
  loading.value = true
  try {
    const response = await getHistoriales()
    historiales.value = response.data
  } catch (error) {
    ElMessage.error('Error al cargar historiales médicos')
    console.error('Error al cargar historiales:', error)
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

function getPacienteNombre(codigo: number | undefined): string {
  if (!codigo) return 'N/A'
  const paciente = pacientesMap.value.get(codigo)
  return paciente ? `${paciente.Nombre} ${paciente.Apellidos}` : `Paciente ${codigo}`
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

function aplicarFiltros() {
  paginacion.value.pagina = 1
  ElMessage.success('Filtros aplicados')
}

function limpiarFiltros() {
  filtros.value = {
    codigo_paciente: undefined,
    fechaDesde: undefined,
    fechaHasta: undefined
  }
  paginacion.value.pagina = 1
  ElMessage.info('Filtros limpiados')
}

function handleCreate() {
  isEdit.value = false
  form.value = {
    Codigo_Paciente: undefined,
    Fecha_Ingreso: undefined,
    Diagnostico: undefined,
    Tratamiento: undefined,
    Observaciones: undefined
  }
  dialogVisible.value = true
  nextTick(() => {
    formRef.value?.clearValidate()
  })
}

function handleEdit(row: Historial) {
  isEdit.value = true
  form.value = {
    Codigo_Historial: row.Codigo_Historial,
    Codigo_Paciente: row.Codigo_Paciente,
    Fecha_Ingreso: row.Fecha_Ingreso,
    Diagnostico: row.Diagnostico,
    Tratamiento: row.Tratamiento,
    Observaciones: row.Observaciones
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
        const codigo = form.value.Codigo_Historial!
        const datosEnvio: HistorialUpdate = {
          Codigo_Paciente: form.value.Codigo_Paciente,
          Fecha_Ingreso: form.value.Fecha_Ingreso,
          Diagnostico: form.value.Diagnostico,
          Tratamiento: form.value.Tratamiento,
          Observaciones: form.value.Observaciones
        }

        updateHistorial(codigo, datosEnvio)
          .then(() => {
            ElMessage.success('Historial actualizado exitosamente')
            dialogVisible.value = false
            loadHistoriales()
          })
          .catch((error) => {
            ElMessage.error('Error al actualizar el historial')
            console.error('Error:', error)
          })
          .finally(() => {
            submitting.value = false
          })
      } else {
        // Crear
        const datosEnvio: HistorialCreate = {
          Codigo_Paciente: form.value.Codigo_Paciente,
          Fecha_Ingreso: form.value.Fecha_Ingreso,
          Diagnostico: form.value.Diagnostico,
          Tratamiento: form.value.Tratamiento,
          Observaciones: form.value.Observaciones
        }

        createHistorial(datosEnvio)
          .then(() => {
            ElMessage.success('Historial creado exitosamente')
            dialogVisible.value = false
            loadHistoriales()
          })
          .catch((error) => {
            ElMessage.error('Error al crear el historial')
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
    '¿Está seguro de que desea eliminar este historial médico? Esta acción no se puede deshacer.',
    'Confirmar eliminación',
    {
      confirmButtonText: 'Eliminar',
      cancelButtonText: 'Cancelar',
      type: 'warning'
    }
  )
    .then(() => {
      deleteHistorial(codigo)
        .then(() => {
          ElMessage.success('Historial eliminado exitosamente')
          loadHistoriales()
        })
        .catch((error) => {
          ElMessage.error('Error al eliminar el historial')
          console.error('Error:', error)
        })
    })
    .catch(() => {
      // Usuario canceló
    })
}

function verDetalles(historial: Historial) {
  historialSeleccionado.value = historial
  dialogDetallesVisible.value = true
}

function handleSizeChange(val: number) {
  paginacion.value.tamano = val
  paginacion.value.pagina = 1
}

function handlePageChange(val: number) {
  paginacion.value.pagina = val
}

function imprimirHistorial(historial: Historial) {
  // Crear ventana de impresión
  const ventanaImpresion = window.open('', '_blank', 'width=800,height=600')
  if (!ventanaImpresion) {
    ElMessage.error('Por favor, permite ventanas emergentes para imprimir')
    return
  }

  // Obtener información del paciente
  const pacienteInfo = pacientesMap.value.get(historial.Codigo_Paciente || 0)
  const nombrePaciente = pacienteInfo 
    ? `${pacienteInfo.Nombre} ${pacienteInfo.Apellidos}` 
    : 'N/A'
  const telefonoPaciente = pacienteInfo?.Numero_Celular || ''
  const fechaNacPaciente = pacienteInfo?.Fecha_Nacimiento 
    ? formatearFecha(pacienteInfo.Fecha_Nacimiento) 
    : ''
  const direccionPaciente = pacienteInfo?.Direccion || ''

  // Formatear fechas
  const fechaIngreso = historial.Fecha_Ingreso
    ? formatearFecha(historial.Fecha_Ingreso)
    : 'N/A'
  const diagnostico = historial.Diagnostico 
    ? historial.Diagnostico.replace(/\n/g, '<br>') 
    : 'Sin diagnóstico registrado'
  const tratamiento = historial.Tratamiento 
    ? historial.Tratamiento.replace(/\n/g, '<br>') 
    : 'Sin tratamiento registrado'
  const observaciones = historial.Observaciones 
    ? historial.Observaciones.replace(/\n/g, '<br>') 
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

  // Construir sección de exámenes solicitados
  let seccionExamenes = ''
  if (historial.Examenes_Solicitados && historial.Examenes_Solicitados.length > 0) {
    seccionExamenes = `
      <div class="medicamento-section" style="margin-top: 20px; border-color: #E6A23C;">
        <h3>EXÁMENES SOLICITADOS</h3>
        <div class="medicamento-content">`
    
    historial.Examenes_Solicitados.forEach((examen) => {
      const fechaExamen = examen.Fecha_Consulta 
        ? formatearFecha(examen.Fecha_Consulta) 
        : 'N/A'
      const descripcionExamen = examen.Descripcion 
        ? examen.Descripcion.replace(/\n/g, '<br>') 
        : ''
      
      seccionExamenes += `
          <div style="margin-bottom: 20px; padding: 15px; background: #FFF7E6; border-left: 4px solid #E6A23C; border-radius: 4px;">
            <div style="font-weight: bold; margin-bottom: 8px; color: #E6A23C; font-size: 15px;">📋 Fecha de Consulta: ${fechaExamen}</div>
            <div style="padding-left: 10px; line-height: 1.8; color: #333;">${descripcionExamen}</div>
          </div>`
    })
    
    seccionExamenes += `
        </div>
      </div>`
  }

  // Generar HTML del baucher
  const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Historial Médico - ${historial.Codigo_Historial}</title>
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
    .diagnostico-section {
      margin-top: 20px;
      padding: 15px;
      background: #f5f5f5;
      border-left: 4px solid #000;
    }
    .tratamiento-section {
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
    <button onclick="window.print()">Imprimir Historial</button>
    <button onclick="window.close()"> Cerrar</button>
  </div>
  
  <div class="baucher">
    <div class="codigo-badge">HISTORIAL #${historial.Codigo_Historial}</div>
    
    <div class="header">
      <h1>Centro Médico</h1>
      <h2>HISTORIAL MÉDICO</h2>
    </div>

    ${seccionPaciente}

    <div class="info-section">
      <h3>INFORMACIÓN DEL HISTORIAL</h3>
      <div class="info-row">
        <span class="info-label">Código:</span>
        <span class="info-value">${historial.Codigo_Historial}</span>
      </div>
      <div class="info-row">
        <span class="info-label">Fecha de Ingreso:</span>
        <span class="info-value"><strong>${fechaIngreso}</strong></span>
      </div>
    </div>

    <div class="diagnostico-section">
      <strong>DIAGNÓSTICO:</strong><br>
      <div style="margin-top: 10px; line-height: 1.8;">
        ${diagnostico}
      </div>
    </div>

    <div class="tratamiento-section">
      <strong>TRATAMIENTO:</strong><br>
      <div style="margin-top: 10px; line-height: 1.8;">
        ${tratamiento}
      </div>
    </div>

    ${seccionExamenes}

    <div class="observaciones-section">
      <strong>OBSERVACIONES:</strong><br>
      <div style="margin-top: 10px; line-height: 1.8;">
        ${observaciones}
      </div>
    </div>

    <div class="footer">
      <div style="margin-top: 30px; font-size: 12px; color: #666;">
        <p>Este documento es parte del historial médico del paciente.</p>
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
  loadHistoriales()
  loadPacientes()
})
</script>

<style scoped>
.whitespace-pre-wrap {
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
