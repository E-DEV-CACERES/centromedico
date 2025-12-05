<template>
  <AppLayout>
    <div class="p-6">
      <h2 class="text-2xl font-bold text-gray-800 mb-4">Gestión de Usuarios y Copias de Seguridad</h2>

      <el-tabs v-model="activeTab" type="border-card">
        <!-- Tab de Usuarios -->
        <el-tab-pane label="Usuarios del Sistema" name="usuarios">
          <div class="mb-4 flex justify-between items-center">
            <h3 class="text-xl font-semibold text-gray-700">Usuarios del Sistema</h3>
            <el-button type="primary" @click="handleCreate">
              <el-icon class="mr-1"><Plus /></el-icon>
              Nuevo Usuario
            </el-button>
          </div>

          <!-- Filtros -->
          <el-card class="mb-4">
            <el-form :inline="true" :model="filtros" class="demo-form-inline">
              <el-form-item label="Rol">
                <el-select
                  v-model="filtros.rol"
                  placeholder="Todos los roles"
                  filterable
                  clearable
                  style="width: 200px"
                >
                  <el-option label="Admin" value="Admin" />
                  <el-option label="Doctor" value="Doctor" />
                  <el-option label="Recepcionista" value="Recepcionista" />
                </el-select>
              </el-form-item>
              <el-form-item label="Estado">
                <el-select
                  v-model="filtros.activo"
                  placeholder="Todos los estados"
                  clearable
                  style="width: 150px"
                >
                  <el-option label="Activo" :value="true" />
                  <el-option label="Inactivo" :value="false" />
                </el-select>
              </el-form-item>
              <el-form-item>
                <el-button type="primary" @click="aplicarFiltros">Buscar</el-button>
                <el-button @click="limpiarFiltros">Limpiar</el-button>
              </el-form-item>
            </el-form>
          </el-card>

          <!-- Tabla de usuarios -->
          <el-card>
            <el-table :data="usuariosFiltrados" v-loading="loading" stripe>
              <el-table-column prop="Codigo" label="Código" width="100" />
              <el-table-column prop="Usuario" label="Usuario" width="150" />
              <el-table-column label="Doctor Asociado" width="200">
                <template #default="{ row }">
                  <span v-if="row.Codigo_Doctor && doctores.length > 0">
                    {{ getDoctorNombre(row.Codigo_Doctor) }}
                  </span>
                  <span v-else class="text-gray-400">N/A</span>
                </template>
              </el-table-column>
              <el-table-column prop="Rol" label="Rol" width="120">
                <template #default="{ row }">
                  <el-tag :type="getRolTagType(row.Rol)" size="small">
                    {{ row.Rol || 'Recepcionista' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="Estado" width="100">
                <template #default="{ row }">
                  <el-tag :type="row.Activo ? 'success' : 'danger'" size="small">
                    {{ row.Activo ? 'Activo' : 'Inactivo' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="Ultimo_Acceso" label="Último Acceso" width="180">
                <template #default="{ row }">
                  {{ formatearFecha(row.Ultimo_Acceso) }}
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
          </el-card>
        </el-tab-pane>

        <!-- Tab de Copias de Seguridad -->
        <el-tab-pane label="Copias de Seguridad" name="backup">
          <div class="mb-4 flex justify-between items-center">
            <h3 class="text-xl font-semibold text-gray-700">Gestión de Copias de Seguridad</h3>
            <el-button type="primary" @click="crearBackup" :loading="creandoBackup">
              <el-icon class="mr-1"><FolderOpened /></el-icon>
              Crear Copia de Seguridad
            </el-button>
          </div>

          <el-card>
            <el-alert
              title="Información"
              type="info"
              :closable="false"
              class="mb-4"
            >
              <template #default>
                <p>Las copias de seguridad se crean automáticamente con un nombre único basado en la fecha y hora.</p>
                <p>Se recomienda crear copias de seguridad regularmente para proteger los datos del sistema.</p>
              </template>
            </el-alert>

            <el-table :data="backups" v-loading="loadingBackups" stripe>
              <el-table-column prop="filename" label="Nombre del Archivo" min-width="250" />
              <el-table-column label="Tamaño" width="120">
                <template #default="{ row }">
                  {{ formatearTamaño(row.size) }}
                </template>
              </el-table-column>
              <el-table-column prop="created" label="Fecha de Creación" width="180">
                <template #default="{ row }">
                  {{ formatearFecha(row.created) }}
                </template>
              </el-table-column>
              <el-table-column label="Acciones" width="120" fixed="right" align="center">
                <template #default="{ row }">
                  <el-button 
                    size="small" 
                    type="primary" 
                    @click="descargarBackup(row.filename)"
                    :loading="descargando === row.filename"
                    :icon="ArrowDown"
                    circle
                    title="Descargar"
                  />
                </template>
              </el-table-column>
            </el-table>

            <div v-if="backups.length === 0 && !loadingBackups" class="text-center py-8 text-gray-500">
              <el-icon class="text-4xl mb-2"><FolderOpened /></el-icon>
              <p>No hay copias de seguridad disponibles</p>
            </div>
          </el-card>
        </el-tab-pane>
      </el-tabs>

      <!-- Dialog para crear/editar usuario -->
      <el-dialog
        v-model="dialogVisible"
        :title="isEdit ? 'Editar Usuario' : 'Nuevo Usuario'"
        width="600px"
      >
        <el-form :model="form" :rules="rules" ref="formRef" label-width="150px">
          <el-form-item label="Usuario" prop="Usuario">
            <el-input
              v-model="form.Usuario"
              placeholder="Nombre de usuario"
            />
          </el-form-item>
          <el-form-item :label="isEdit ? 'Nueva Contraseña' : 'Contraseña'" :prop="isEdit ? undefined : 'Contrasena'">
            <el-input
              v-model="form.Contrasena"
              type="password"
              :placeholder="isEdit ? 'Dejar en blanco para no cambiar' : 'Mínimo 6 caracteres'"
              show-password
            />
          </el-form-item>
          <el-form-item label="Doctor Asociado">
            <el-select
              v-model="form.Codigo_Doctor"
              placeholder="Seleccione un doctor (opcional)"
              filterable
              clearable
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
          <el-form-item label="Rol" prop="Rol">
            <el-select
              v-model="form.Rol"
              placeholder="Seleccione el rol"
              style="width: 100%"
            >
              <el-option label="Admin" value="Admin" />
              <el-option label="Doctor" value="Doctor" />
              <el-option label="Recepcionista" value="Recepcionista" />
            </el-select>
          </el-form-item>
          <el-form-item label="Estado">
            <el-switch
              v-model="form.Activo"
              active-text="Activo"
              inactive-text="Inactivo"
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
        title="Detalles del Usuario"
        width="700px"
      >
        <el-descriptions :column="2" border v-if="usuarioSeleccionado">
          <el-descriptions-item label="Código">
            {{ usuarioSeleccionado.Codigo }}
          </el-descriptions-item>
          <el-descriptions-item label="Estado">
            <el-tag :type="usuarioSeleccionado.Activo ? 'success' : 'danger'" size="small">
              {{ usuarioSeleccionado.Activo ? 'Activo' : 'Inactivo' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Usuario">
            {{ usuarioSeleccionado.Usuario }}
          </el-descriptions-item>
          <el-descriptions-item label="Rol">
            <el-tag :type="getRolTagType(usuarioSeleccionado.Rol)" size="small">
              {{ usuarioSeleccionado.Rol || 'Recepcionista' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="Doctor Asociado" v-if="usuarioSeleccionado.Codigo_Doctor">
            {{ getDoctorNombre(usuarioSeleccionado.Codigo_Doctor) }}
          </el-descriptions-item>
          <el-descriptions-item label="Último Acceso" v-if="usuarioSeleccionado.Ultimo_Acceso">
            {{ formatearFecha(usuarioSeleccionado.Ultimo_Acceso) }}
          </el-descriptions-item>
          <el-descriptions-item label="Fecha de Creación" v-if="usuarioSeleccionado.Fecha_Creacion">
            {{ formatearFecha(usuarioSeleccionado.Fecha_Creacion) }}
          </el-descriptions-item>
          <el-descriptions-item label="Última Modificación" v-if="usuarioSeleccionado.Fecha_Modificacion">
            {{ formatearFecha(usuarioSeleccionado.Fecha_Modificacion) }}
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
import { Plus, View, Edit, Close, FolderOpened, ArrowDown } from '@element-plus/icons-vue'
import AppLayout from '@/components/AppLayout.vue'
import {
  getUsuarios,
  createUsuario,
  updateUsuario,
  deleteUsuario,
  crearBackup as crearBackupAPI,
  listarBackups as listarBackupsAPI,
  descargarBackup as descargarBackupAPI,
  type UsuarioSistema,
  type UsuarioSistemaCreate,
  type UsuarioSistemaUpdate,
  type UsuarioSistemaFilters,
  type BackupInfo
} from '@/services/usuarios'
import { getDoctores, type Doctor } from '@/services/doctores'

const activeTab = ref('usuarios')
const usuarios = ref<UsuarioSistema[]>([])
const doctores = ref<Doctor[]>([])
const backups = ref<BackupInfo[]>([])
const loading = ref(false)
const loadingBackups = ref(false)
const creandoBackup = ref(false)
const descargando = ref<string | null>(null)
const submitting = ref(false)
const dialogVisible = ref(false)
const dialogDetallesVisible = ref(false)
const isEdit = ref(false)
const usuarioSeleccionado = ref<UsuarioSistema | null>(null)
const formRef = ref<FormInstance>()

const filtros = ref<UsuarioSistemaFilters>({
  rol: undefined,
  activo: undefined
})

const form = ref<UsuarioSistemaCreate & { Codigo?: number; Activo?: number }>({
  Usuario: '',
  Contrasena: '',
  Codigo_Doctor: undefined,
  Rol: 'Recepcionista',
  Activo: 1
})

const rules: FormRules = {
  Usuario: [
    { required: true, message: 'Por favor ingrese el nombre de usuario', trigger: 'blur' }
  ],
  Contrasena: [
    { required: true, message: 'Por favor ingrese la contraseña', trigger: 'blur' },
    { min: 6, message: 'La contraseña debe tener al menos 6 caracteres', trigger: 'blur' }
  ],
  Rol: [
    { required: true, message: 'Por favor seleccione el rol', trigger: 'change' }
  ]
}

// Mapeos para búsqueda rápida
const doctoresMap = computed(() => {
  const map = new Map<number, Doctor>()
  doctores.value.forEach(d => map.set(d.Codigo, d))
  return map
})

// Usuarios filtrados
const usuariosFiltrados = computed(() => {
  let resultado = [...usuarios.value]

  if (filtros.value.rol) {
    resultado = resultado.filter(u => u.Rol === filtros.value.rol)
  }

  if (filtros.value.activo !== undefined) {
    resultado = resultado.filter(u => (u.Activo ? 1 : 0) === (filtros.value.activo ? 1 : 0))
  }

  return resultado.sort((a, b) => (b.Codigo || 0) - (a.Codigo || 0))
})

async function loadUsuarios() {
  loading.value = true
  try {
    const response = await getUsuarios()
    usuarios.value = response.data
  } catch (error) {
    ElMessage.error('Error al cargar usuarios')
    console.error('Error al cargar usuarios:', error)
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
    console.error('Error al cargar doctores:', error)
  }
}

async function loadBackups() {
  loadingBackups.value = true
  try {
    const response = await listarBackupsAPI()
    backups.value = response.data.backups
  } catch (error) {
    ElMessage.error('Error al cargar copias de seguridad')
    console.error('Error al cargar backups:', error)
  } finally {
    loadingBackups.value = false
  }
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

function formatearTamaño(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(2)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
}

function getRolTagType(rol: string | undefined): string {
  switch (rol) {
    case 'Admin':
      return 'danger'
    case 'Doctor':
      return 'warning'
    case 'Recepcionista':
      return 'info'
    default:
      return 'info'
  }
}

function aplicarFiltros() {
  ElMessage.success('Filtros aplicados')
}

function limpiarFiltros() {
  filtros.value = {
    rol: undefined,
    activo: undefined
  }
  ElMessage.info('Filtros limpiados')
}

function handleCreate() {
  isEdit.value = false
  form.value = {
    Usuario: '',
    Contrasena: '',
    Codigo_Doctor: undefined,
    Rol: 'Recepcionista',
    Activo: 1
  }
  dialogVisible.value = true
  nextTick(() => {
    formRef.value?.clearValidate()
  })
}

function handleEdit(row: UsuarioSistema) {
  isEdit.value = true
  form.value = {
    Codigo: row.Codigo,
    Usuario: row.Usuario,
    Contrasena: '',
    Codigo_Doctor: row.Codigo_Doctor,
    Rol: row.Rol || 'Recepcionista',
    Activo: row.Activo ? 1 : 0
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
        const datosEnvio: UsuarioSistemaUpdate = {
          Usuario: form.value.Usuario,
          Codigo_Doctor: form.value.Codigo_Doctor,
          Rol: form.value.Rol,
          Activo: form.value.Activo
        }

        // Solo incluir contraseña si se proporcionó
        if (form.value.Contrasena && form.value.Contrasena.trim() !== '') {
          datosEnvio.Contrasena = form.value.Contrasena
        }

        updateUsuario(codigo, datosEnvio)
          .then(() => {
            ElMessage.success('Usuario actualizado exitosamente')
            dialogVisible.value = false
            loadUsuarios()
          })
          .catch((error) => {
            ElMessage.error('Error al actualizar el usuario')
            console.error('Error:', error)
          })
          .finally(() => {
            submitting.value = false
          })
      } else {
        // Crear
        const datosEnvio: UsuarioSistemaCreate = {
          Usuario: form.value.Usuario,
          Contrasena: form.value.Contrasena!,
          Codigo_Doctor: form.value.Codigo_Doctor,
          Rol: form.value.Rol!,
          Activo: form.value.Activo
        }

        createUsuario(datosEnvio)
          .then(() => {
            ElMessage.success('Usuario creado exitosamente')
            dialogVisible.value = false
            loadUsuarios()
          })
          .catch((error) => {
            ElMessage.error('Error al crear el usuario')
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
    '¿Está seguro de que desea eliminar este usuario? Esta acción no se puede deshacer.',
    'Confirmar eliminación',
    {
      confirmButtonText: 'Eliminar',
      cancelButtonText: 'Cancelar',
      type: 'warning'
    }
  )
    .then(() => {
      deleteUsuario(codigo)
        .then(() => {
          ElMessage.success('Usuario eliminado exitosamente')
          loadUsuarios()
        })
        .catch((error) => {
          ElMessage.error('Error al eliminar el usuario')
          console.error('Error:', error)
        })
    })
    .catch(() => {
      // Usuario canceló
    })
}

function verDetalles(usuario: UsuarioSistema) {
  usuarioSeleccionado.value = usuario
  dialogDetallesVisible.value = true
}

async function crearBackup() {
  creandoBackup.value = true
  try {
    const response = await crearBackupAPI()
    ElMessage.success(`Copia de seguridad creada: ${response.data.filename}`)
    await loadBackups()
  } catch (error) {
    ElMessage.error('Error al crear la copia de seguridad')
    console.error('Error:', error)
  } finally {
    creandoBackup.value = false
  }
}

async function descargarBackup(filename: string) {
  descargando.value = filename
  try {
    const response = await descargarBackupAPI(filename)
    
    // Crear un enlace temporal para descargar el archivo
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', filename)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('Copia de seguridad descargada exitosamente')
  } catch (error) {
    ElMessage.error('Error al descargar la copia de seguridad')
    console.error('Error:', error)
  } finally {
    descargando.value = null
  }
}

onMounted(() => {
  loadUsuarios()
  loadDoctores()
  loadBackups()
})
</script>

<style scoped>
.whitespace-pre-wrap {
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>
