<template>
  <AppLayout>
    <div class="p-6">
      <div class="mb-4 flex justify-between items-center">
        <h2 class="text-2xl font-bold text-gray-800">Historial de Consultas Médicas</h2>
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
          <el-form-item label="Estado">
            <el-select
              v-model="filtros.estado"
              placeholder="Todos los estados"
              clearable
              style="width: 150px"
            >
              <el-option label="Programada" value="Programada" />
              <el-option label="En Proceso" value="En Proceso" />
              <el-option label="Completada" value="Completada" />
              <el-option label="Cancelada" value="Cancelada" />
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

      <!-- Tabla de consultas -->
      <el-card>
        <el-table :data="consultasFiltradas" v-loading="loading" stripe>
          <el-table-column prop="Codigo" label="Código" width="100" />
          <el-table-column label="Paciente" width="180">
            <template #default="{ row }">
              <span v-if="pacientes.length > 0 && row.Codigo_Paciente">
                {{ getPacienteNombre(row.Codigo_Paciente) }}
              </span>
              <span v-else-if="row.Codigo_Paciente">{{ row.Codigo_Paciente }}</span>
              <span v-else class="text-gray-400">N/A</span>
            </template>
          </el-table-column>
          <el-table-column label="Doctor" width="180">
            <template #default="{ row }">
              <span v-if="doctores.length > 0 && row.Codigo_Doctor">
                {{ getDoctorNombre(row.Codigo_Doctor) }}
              </span>
              <span v-else-if="row.Codigo_Doctor">{{ row.Codigo_Doctor }}</span>
              <span v-else class="text-gray-400">N/A</span>
            </template>
          </el-table-column>
          <el-table-column prop="Tipo_de_Consulta" label="Tipo" width="150" />
          <el-table-column prop="Fecha_de_Consulta" label="Fecha de Consulta" width="180">
            <template #default="{ row }">
              {{ formatearFecha(row.Fecha_de_Consulta) }}
            </template>
          </el-table-column>
          <el-table-column prop="Estado" label="Estado" width="120">
            <template #default="{ row }">
              <el-tag
                :type="getEstadoTagType(row.Estado)"
                size="small"
              >
                {{ row.Estado }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="Diagnostico" label="Diagnóstico" show-overflow-tooltip />
          <el-table-column label="Acciones" width="120" fixed="right" align="center">
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
            :total="consultasFiltradas.length"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handlePageChange"
          />
        </div>
      </el-card>

      <!-- Dialog para ver detalles -->
      <el-dialog
        v-model="dialogDetallesVisible"
        title="Detalles de la Consulta"
        width="800px"
      >
        <el-descriptions :column="2" border v-if="consultaSeleccionada">
          <el-descriptions-item label="Código">
            {{ consultaSeleccionada.Codigo }}
          </el-descriptions-item>
          <el-descriptions-item label="Estado">
            <el-tag :type="getEstadoTagType(consultaSeleccionada.Estado)" size="small">
              {{ consultaSeleccionada.Estado }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Paciente">
            {{ getPacienteNombre(consultaSeleccionada.Codigo_Paciente) }}
          </el-descriptions-item>
          <el-descriptions-item label="Doctor">
            {{ getDoctorNombre(consultaSeleccionada.Codigo_Doctor) }}
          </el-descriptions-item>
          <el-descriptions-item label="Tipo de Consulta">
            {{ consultaSeleccionada.Tipo_de_Consulta || 'N/A' }}
          </el-descriptions-item>
          <el-descriptions-item label="Fecha de Consulta">
            {{ formatearFecha(consultaSeleccionada.Fecha_de_Consulta) }}
          </el-descriptions-item>
          <el-descriptions-item label="Diagnóstico" :span="2">
            <div class="whitespace-pre-wrap">
              {{ consultaSeleccionada.Diagnostico || 'Sin diagnóstico registrado' }}
            </div>
          </el-descriptions-item>
          <el-descriptions-item label="Fecha de Creación" v-if="consultaSeleccionada.Fecha_Creacion">
            {{ formatearFecha(consultaSeleccionada.Fecha_Creacion) }}
          </el-descriptions-item>
          <el-descriptions-item label="Última Modificación" v-if="consultaSeleccionada.Fecha_Modificacion">
            {{ formatearFecha(consultaSeleccionada.Fecha_Modificacion) }}
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
import { ElMessage } from 'element-plus'
import { View } from '@element-plus/icons-vue'
import AppLayout from '@/components/AppLayout.vue'
import {
  getConsultas,
  type Consulta,
  type ConsultaFilters
} from '@/services/consultas'
import { getDoctores, type Doctor } from '@/services/doctores'
import { getPacientes, type Paciente } from '@/services/pacientes'

const consultas = ref<Consulta[]>([])
const doctores = ref<Doctor[]>([])
const pacientes = ref<Paciente[]>([])
const loading = ref(false)
const dialogDetallesVisible = ref(false)
const consultaSeleccionada = ref<Consulta | null>(null)

const filtros = ref<ConsultaFilters & { fechaDesde?: string; fechaHasta?: string }>({
  codigo_paciente: undefined,
  codigo_doctor: undefined,
  estado: undefined,
  fechaDesde: undefined,
  fechaHasta: undefined
})

const paginacion = ref({
  pagina: 1,
  tamano: 20
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

// Consultas filtradas
const consultasFiltradas = computed(() => {
  let resultado = [...consultas.value]

  // Filtrar por paciente
  if (filtros.value.codigo_paciente) {
    resultado = resultado.filter(c => c.Codigo_Paciente === filtros.value.codigo_paciente)
  }

  // Filtrar por doctor
  if (filtros.value.codigo_doctor) {
    resultado = resultado.filter(c => c.Codigo_Doctor === filtros.value.codigo_doctor)
  }

  // Filtrar por estado
  if (filtros.value.estado) {
    resultado = resultado.filter(c => c.Estado === filtros.value.estado)
  }

  // Filtrar por fecha desde
  if (filtros.value.fechaDesde) {
    resultado = resultado.filter(c => {
      if (!c.Fecha_de_Consulta) return false
      const fechaConsulta = new Date(c.Fecha_de_Consulta)
      const fechaDesde = new Date(filtros.value.fechaDesde!)
      fechaDesde.setHours(0, 0, 0, 0)
      return fechaConsulta >= fechaDesde
    })
  }

  // Filtrar por fecha hasta
  if (filtros.value.fechaHasta) {
    resultado = resultado.filter(c => {
      if (!c.Fecha_de_Consulta) return false
      const fechaConsulta = new Date(c.Fecha_de_Consulta)
      const fechaHasta = new Date(filtros.value.fechaHasta!)
      fechaHasta.setHours(23, 59, 59, 999)
      return fechaConsulta <= fechaHasta
    })
  }

  // Ordenar por fecha descendente (más recientes primero)
  resultado.sort((a, b) => {
    const fechaA = a.Fecha_de_Consulta ? new Date(a.Fecha_de_Consulta).getTime() : 0
    const fechaB = b.Fecha_de_Consulta ? new Date(b.Fecha_de_Consulta).getTime() : 0
    return fechaB - fechaA
  })

  // Aplicar paginación
  const inicio = (paginacion.value.pagina - 1) * paginacion.value.tamano
  const fin = inicio + paginacion.value.tamano
  return resultado.slice(inicio, fin)
})

async function loadConsultas() {
  loading.value = true
  try {
    const response = await getConsultas()
    consultas.value = response.data
  } catch (error) {
    ElMessage.error('Error al cargar consultas')
    console.error('Error al cargar consultas:', error)
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
  paginacion.value.pagina = 1 // Resetear a la primera página
  ElMessage.success('Filtros aplicados')
}

function limpiarFiltros() {
  filtros.value = {
    codigo_paciente: undefined,
    codigo_doctor: undefined,
    estado: undefined,
    fechaDesde: undefined,
    fechaHasta: undefined
  }
  paginacion.value.pagina = 1
  ElMessage.info('Filtros limpiados')
}

function verDetalles(consulta: Consulta) {
  consultaSeleccionada.value = consulta
  dialogDetallesVisible.value = true
}

function handleSizeChange(val: number) {
  paginacion.value.tamano = val
  paginacion.value.pagina = 1
}

function handlePageChange(val: number) {
  paginacion.value.pagina = val
}

onMounted(() => {
  loadConsultas()
  loadDoctores()
  loadPacientes()
})
</script>

<style scoped>
.whitespace-pre-wrap {
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
