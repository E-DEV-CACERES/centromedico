<template>
  <AppLayout>
    <div class="p-6">
      <div class="mb-4 flex justify-between items-center">
        <h2 class="text-2xl font-bold text-gray-800">Gestión de Consultas Médicas</h2>
        <el-button type="primary" @click="handleCreate">
          <el-icon class="mr-2"><Plus /></el-icon>
          Nueva Consulta
        </el-button>
      </div>

      <el-card>
        <el-table :data="consultas" v-loading="loading" stripe>
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
          <el-table-column prop="Fecha_de_Consulta" label="Fecha de Consulta" width="180" />
          <el-table-column prop="Estado" label="Estado" width="120" />
          <el-table-column label="Exámenes" width="180">
            <template #default="{ row }">
              <div class="flex flex-col gap-1">
                <el-tag v-if="row.Examenes_Solicitados" type="warning" size="small">
                  Solicitados
                </el-tag>
                <el-tag v-if="row.Examenes_Sugeridos" type="info" size="small">
                  Sugeridos
                </el-tag>
                <span v-if="!row.Examenes_Solicitados && !row.Examenes_Sugeridos" class="text-gray-400 text-xs">No</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="Diagnostico" label="Diagnóstico" />
          <el-table-column label="Acciones" width="160" fixed="right" align="center">
            <template #default="{ row }">
              <div class="flex gap-2 justify-center">
                <el-button 
                  size="small" 
                  type="primary" 
                  @click="handleEdit(row)"
                  :icon="Check"
                  circle
                  title="Aplicar Consulta"
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
        :title="isEdit ? 'Editar Consulta' : 'Nueva Consulta'"
        width="900px"
      >
        <el-tabs v-model="activeTab" v-if="isEdit">
          <el-tab-pane label="Datos de Consulta" name="consulta">
            <el-form :model="form" label-width="150px">
          <el-form-item label="Paciente">
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
          <el-form-item label="Doctor">
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
          <el-form-item label="Tipo de Consulta">
            <el-input
              v-model="form.Tipo_de_Consulta"
              placeholder="Ej: General, Especializada, Urgencia"
            />
          </el-form-item>
          <el-form-item label="Fecha de Consulta">
            <el-date-picker
              v-model="form.Fecha_de_Consulta"
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
              <el-option label="En Proceso" value="En Proceso" />
              <el-option label="Completada" value="Completada" />
              <el-option label="Cancelada" value="Cancelada" />
            </el-select>
          </el-form-item>
          <el-form-item label="Diagnóstico">
            <el-input
              v-model="form.Diagnostico"
              type="textarea"
              :rows="4"
              placeholder="Ingrese el diagnóstico de la consulta"
            />
          </el-form-item>
          <el-form-item label="Exámenes Solicitados">
            <el-switch
              v-model="form.Examenes_Solicitados"
              active-text="Sí"
              inactive-text="No"
            />
          </el-form-item>
          <el-form-item 
            label="Descripción de Exámenes Solicitados" 
            v-if="form.Examenes_Solicitados"
          >
            <el-input
              v-model="form.Examenes_Descripcion"
              type="textarea"
              :rows="3"
              placeholder="Ej: Hemograma completo, Radiografía de tórax, Análisis de sangre..."
            />
          </el-form-item>
          <el-form-item label="Exámenes Sugeridos">
            <el-switch
              v-model="form.Examenes_Sugeridos"
              active-text="Sí"
              inactive-text="No"
            />
            <span class="ml-2 text-sm text-gray-500">(Opcionales para el paciente)</span>
          </el-form-item>
          <el-form-item 
            label="Descripción de Exámenes Sugeridos" 
            v-if="form.Examenes_Sugeridos"
          >
            <el-input
              v-model="form.Examenes_Sugeridos_Descripcion"
              type="textarea"
              :rows="3"
              placeholder="Ej: Ecografía abdominal, Tomografía, Análisis de orina completo..."
            />
          </el-form-item>
        </el-form>
          </el-tab-pane>
          
          <el-tab-pane label="Recetas Médicas" name="recetas">
            <div class="mb-4 flex justify-between items-center">
              <h3 class="text-lg font-semibold">Recetas asociadas a esta consulta</h3>
              <el-button type="primary" size="small" @click="handleCrearReceta">
                <el-icon class="mr-1"><Plus /></el-icon>
                Nueva Receta
              </el-button>
            </div>
            
            <el-table :data="recetasConsulta" v-loading="loadingRecetas" stripe>
              <el-table-column prop="Codigo" label="Código" width="100" />
              <el-table-column prop="Fecha_Receta" label="Fecha" width="150">
                <template #default="{ row }">
                  {{ formatearFecha(row.Fecha_Receta) }}
                </template>
              </el-table-column>
              <el-table-column prop="Medicamento" label="Medicamento" />
              <el-table-column prop="Instrucciones" label="Instrucciones" show-overflow-tooltip />
              <el-table-column label="Acciones" width="160" fixed="right" align="center">
                <template #default="{ row }">
                  <div class="flex gap-2 justify-center">
                    <el-button 
                      size="small" 
                      type="warning" 
                      @click="handleEditarReceta(row)"
                      :icon="Edit"
                      circle
                      title="Editar"
                    />
                    <el-button 
                      size="small" 
                      type="danger" 
                      @click="handleEliminarReceta(row.Codigo)"
                      circle
                      title="Eliminar"
                    >
                      <el-icon><Close /></el-icon>
                    </el-button>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>
        </el-tabs>
        
        <el-form v-else :model="form" label-width="150px">
          <el-form-item label="Paciente">
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
          <el-form-item label="Doctor">
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
          <el-form-item label="Tipo de Consulta">
            <el-input
              v-model="form.Tipo_de_Consulta"
              placeholder="Ej: General, Especializada, Urgencia"
            />
          </el-form-item>
          <el-form-item label="Fecha de Consulta">
            <el-date-picker
              v-model="form.Fecha_de_Consulta"
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
              <el-option label="En Proceso" value="En Proceso" />
              <el-option label="Completada" value="Completada" />
              <el-option label="Cancelada" value="Cancelada" />
            </el-select>
          </el-form-item>
          <el-form-item label="Diagnóstico">
            <el-input
              v-model="form.Diagnostico"
              type="textarea"
              :rows="4"
              placeholder="Ingrese el diagnóstico de la consulta"
            />
          </el-form-item>
          <el-form-item label="Exámenes Solicitados">
            <el-switch
              v-model="form.Examenes_Solicitados"
              active-text="Sí"
              inactive-text="No"
            />
          </el-form-item>
          <el-form-item 
            label="Descripción de Exámenes Solicitados" 
            v-if="form.Examenes_Solicitados"
          >
            <el-input
              v-model="form.Examenes_Descripcion"
              type="textarea"
              :rows="3"
              placeholder="Ej: Hemograma completo, Radiografía de tórax, Análisis de sangre..."
            />
          </el-form-item>
          <el-form-item label="Exámenes Sugeridos">
            <el-switch
              v-model="form.Examenes_Sugeridos"
              active-text="Sí"
              inactive-text="No"
            />
            <span class="ml-2 text-sm text-gray-500">(Opcionales para el paciente)</span>
          </el-form-item>
          <el-form-item 
            label="Descripción de Exámenes Sugeridos" 
            v-if="form.Examenes_Sugeridos"
          >
            <el-input
              v-model="form.Examenes_Sugeridos_Descripcion"
              type="textarea"
              :rows="3"
              placeholder="Ej: Ecografía abdominal, Tomografía, Análisis de orina completo..."
            />
          </el-form-item>
        </el-form>
        
        <!-- Dialog para crear/editar receta -->
        <el-dialog
          v-model="dialogRecetaVisible"
          :title="isEditReceta ? 'Editar Receta' : 'Nueva Receta'"
          width="600px"
          append-to-body
        >
          <el-form :model="formReceta" label-width="150px">
            <el-form-item label="Medicamento" required>
              <el-input
                v-model="formReceta.Medicamento"
                type="textarea"
                :rows="3"
                placeholder="Ingrese el nombre del medicamento"
              />
            </el-form-item>
            <el-form-item label="Instrucciones" required>
              <el-input
                v-model="formReceta.Instrucciones"
                type="textarea"
                :rows="4"
                placeholder="Ingrese las instrucciones de uso del medicamento"
              />
            </el-form-item>
            <el-form-item label="Fecha de Receta">
              <el-date-picker
                v-model="formReceta.Fecha_Receta"
                type="datetime"
                format="YYYY-MM-DD HH:mm:ss"
                value-format="YYYY-MM-DDTHH:mm:ss"
                placeholder="Seleccione fecha y hora"
                style="width: 100%"
              />
            </el-form-item>
          </el-form>
          <template #footer>
            <el-button @click="dialogRecetaVisible = false">Cancelar</el-button>
            <el-button type="primary" @click="handleSubmitReceta">Guardar</el-button>
          </template>
        </el-dialog>
        
        <template #footer>
          <el-button @click="dialogVisible = false">Cancelar</el-button>
          <el-button type="primary" @click="handleSubmit">Guardar</el-button>
        </template>
      </el-dialog>
    </div>
  </AppLayout>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Check, Close, Edit } from '@element-plus/icons-vue'
import AppLayout from '@/components/AppLayout.vue'
import { useRoute } from 'vue-router'
import {
  getConsultas,
  createConsulta,
  updateConsulta,
  deleteConsulta,
  getConsulta,
  type Consulta,
  type ConsultaCreate
} from '@/services/consultas'
import {
  getRecetas,
  createReceta,
  updateReceta,
  deleteReceta,
  type Receta,
  type RecetaCreate
} from '@/services/recetas'
import { getDoctores, type Doctor } from '@/services/doctores'
import { getPacientes, type Paciente } from '@/services/pacientes'

const consultas = ref<Consulta[]>([])
const doctores = ref<Doctor[]>([])
const pacientes = ref<Paciente[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const activeTab = ref('consulta')
const form = ref<ConsultaCreate & { Codigo?: number }>({
  Codigo_Paciente: undefined,
  Codigo_Doctor: undefined,
  Tipo_de_Consulta: undefined,
  Fecha_de_Consulta: undefined,
  Diagnostico: undefined,
  Estado: 'Programada',
  Examenes_Solicitados: false,
  Examenes_Descripcion: undefined,
  Examenes_Sugeridos: false,
  Examenes_Sugeridos_Descripcion: undefined
})

// Estados para recetas
const recetasConsulta = ref<Receta[]>([])
const loadingRecetas = ref(false)
const dialogRecetaVisible = ref(false)
const isEditReceta = ref(false)
const formReceta = ref<RecetaCreate & { Codigo?: number }>({
  Codigo_Paciente: undefined,
  Codigo_Doctor: undefined,
  Codigo_Consulta: undefined,
  Nombre_Paciente: undefined,
  Fecha_Receta: undefined,
  Medicamento: undefined,
  Instrucciones: undefined
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

const route = useRoute()

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

function handleCreate() {
  isEdit.value = false
  form.value = {
    Codigo_Paciente: undefined,
    Codigo_Doctor: undefined,
    Tipo_de_Consulta: undefined,
    Fecha_de_Consulta: undefined,
    Diagnostico: undefined,
    Estado: 'Programada',
    Examenes_Solicitados: false,
    Examenes_Descripcion: undefined,
    Examenes_Sugeridos: false,
    Examenes_Sugeridos_Descripcion: undefined
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

async function handleEdit(row: Consulta) {
  isEdit.value = true
  form.value = { ...row }
  activeTab.value = 'consulta'
  dialogVisible.value = true
  // Cargar recetas asociadas a esta consulta
  if (row.Codigo) {
    await loadRecetasConsulta(row.Codigo)
  }
}

async function handleSubmit() {
  try {
    // Normalizar fecha si existe
    let fechaConsulta = form.value.Fecha_de_Consulta
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

    // Preparar datos para enviar
    const datosEnvio: ConsultaCreate = {
      Codigo_Paciente: form.value.Codigo_Paciente || undefined,
      Codigo_Doctor: form.value.Codigo_Doctor || undefined,
      Tipo_de_Consulta: form.value.Tipo_de_Consulta && form.value.Tipo_de_Consulta.trim()
        ? form.value.Tipo_de_Consulta.trim()
        : undefined,
      Fecha_de_Consulta: fechaConsulta || undefined,
      Diagnostico: form.value.Diagnostico && form.value.Diagnostico.trim()
        ? form.value.Diagnostico.trim()
        : undefined,
      Estado: form.value.Estado || 'Programada',
      Examenes_Solicitados: form.value.Examenes_Solicitados ?? false,
      Examenes_Descripcion: form.value.Examenes_Descripcion && form.value.Examenes_Descripcion.trim()
        ? form.value.Examenes_Descripcion.trim()
        : undefined,
      Examenes_Sugeridos: form.value.Examenes_Sugeridos ?? false,
      Examenes_Sugeridos_Descripcion: form.value.Examenes_Sugeridos_Descripcion && form.value.Examenes_Sugeridos_Descripcion.trim()
        ? form.value.Examenes_Sugeridos_Descripcion.trim()
        : undefined
    }

    console.log('Datos a enviar:', datosEnvio)

    if (isEdit.value && form.value.Codigo) {
      await updateConsulta(form.value.Codigo, datosEnvio)
      ElMessage.success('Consulta actualizada correctamente')
      // Eliminar la consulta de la tabla después de guardarla
      consultas.value = consultas.value.filter(c => c.Codigo !== form.value.Codigo)
    } else {
      await createConsulta(datosEnvio)
      ElMessage.success('Consulta creada correctamente')
      // Recargar todas las consultas para mostrar la nueva
      loadConsultas()
    }
    dialogVisible.value = false
  } catch (error: any) {
    console.error('Error completo al guardar consulta:', error)
    console.error('Response:', error?.response)

    let errorMessage = 'Error al guardar consulta'

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
    await ElMessageBox.confirm('¿Está seguro de eliminar esta consulta?', 'Confirmar', {
      type: 'warning'
    })
    await deleteConsulta(codigo)
    ElMessage.success('Consulta eliminada correctamente')
    loadConsultas()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Error al eliminar consulta')
    }
  }
}

// Función para abrir el diálogo de edición con una consulta específica
async function abrirEdicionConsulta(codigo: number) {
  try {
    // Cargar la consulta completa
    const response = await getConsulta(codigo)
    if (response.data) {
      isEdit.value = true
      form.value = { ...response.data }
      activeTab.value = 'consulta'
      dialogVisible.value = true
      // Cargar recetas asociadas
      await loadRecetasConsulta(codigo)
    }
  } catch (error) {
    console.error('Error al cargar la consulta:', error)
    ElMessage.error('Error al cargar la consulta para editar')
  }
}

// Funciones para gestionar recetas
async function loadRecetasConsulta(codigoConsulta: number) {
  loadingRecetas.value = true
  try {
    // Obtener todas las recetas y filtrar por consulta
    const response = await getRecetas()
    // Filtrar solo las recetas de esta consulta
    recetasConsulta.value = response.data.filter(
      (r: Receta) => r.Codigo_Consulta === codigoConsulta
    )
  } catch (error) {
    console.error('Error al cargar recetas:', error)
    recetasConsulta.value = []
  } finally {
    loadingRecetas.value = false
  }
}

function handleCrearReceta() {
  if (!form.value.Codigo) {
    ElMessage.warning('Debe guardar la consulta primero antes de agregar recetas')
    return
  }
  isEditReceta.value = false
  formReceta.value = {
    Codigo_Paciente: form.value.Codigo_Paciente,
    Codigo_Doctor: form.value.Codigo_Doctor,
    Codigo_Consulta: form.value.Codigo,
    Nombre_Paciente: getPacienteNombre(form.value.Codigo_Paciente),
    Fecha_Receta: new Date().toISOString().split('T')[0] + 'T' + new Date().toTimeString().split(' ')[0],
    Medicamento: undefined,
    Instrucciones: undefined
  }
  dialogRecetaVisible.value = true
}

function handleEditarReceta(receta: Receta) {
  isEditReceta.value = true
  formReceta.value = { ...receta }
  dialogRecetaVisible.value = true
}

async function handleSubmitReceta() {
  if (!formReceta.value.Medicamento || !formReceta.value.Medicamento.trim()) {
    ElMessage.warning('Debe ingresar el medicamento')
    return
  }
  if (!formReceta.value.Instrucciones || !formReceta.value.Instrucciones.trim()) {
    ElMessage.warning('Debe ingresar las instrucciones')
    return
  }

  try {
    const datosEnvio: RecetaCreate = {
      Codigo_Paciente: formReceta.value.Codigo_Paciente,
      Codigo_Doctor: formReceta.value.Codigo_Doctor,
      Codigo_Consulta: formReceta.value.Codigo_Consulta,
      Nombre_Paciente: formReceta.value.Nombre_Paciente,
      Fecha_Receta: formReceta.value.Fecha_Receta || undefined,
      Medicamento: formReceta.value.Medicamento.trim(),
      Instrucciones: formReceta.value.Instrucciones.trim()
    }

    if (isEditReceta.value && formReceta.value.Codigo) {
      await updateReceta(formReceta.value.Codigo, datosEnvio)
      ElMessage.success('Receta actualizada correctamente')
    } else {
      await createReceta(datosEnvio)
      ElMessage.success('Receta creada correctamente')
    }
    dialogRecetaVisible.value = false
    if (form.value.Codigo) {
      await loadRecetasConsulta(form.value.Codigo)
    }
  } catch (error: any) {
    console.error('Error al guardar receta:', error)
    let errorMessage = 'Error al guardar receta'
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
      }
    }
    ElMessage.error(errorMessage)
  }
}

async function handleEliminarReceta(codigo: number) {
  try {
    await ElMessageBox.confirm('¿Está seguro de eliminar esta receta?', 'Confirmar', {
      type: 'warning'
    })
    await deleteReceta(codigo)
    ElMessage.success('Receta eliminada correctamente')
    if (form.value.Codigo) {
      await loadRecetasConsulta(form.value.Codigo)
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Error al eliminar receta')
    }
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

// Detectar si hay un query parameter para editar automáticamente
watch(
  () => route.query.editar,
  async (codigoConsulta) => {
    if (codigoConsulta && typeof codigoConsulta === 'string') {
      const codigo = parseInt(codigoConsulta, 10)
      if (!isNaN(codigo)) {
        // Esperar a que las consultas se carguen
        await loadConsultas()
        // Esperar un momento para asegurar que todo esté listo
        setTimeout(() => {
          abrirEdicionConsulta(codigo)
        }, 300)
      }
    }
  },
  { immediate: true }
)

onMounted(async () => {
  await loadConsultas()
  await loadDoctores()
  await loadPacientes()
  
  // Si hay un query parameter para editar, abrir el diálogo
  const codigoConsulta = route.query.editar
  if (codigoConsulta && typeof codigoConsulta === 'string') {
    const codigo = parseInt(codigoConsulta, 10)
    if (!isNaN(codigo)) {
      setTimeout(() => {
        abrirEdicionConsulta(codigo)
      }, 500)
    }
  }
})
</script>
