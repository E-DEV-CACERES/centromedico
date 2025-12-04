<template>
  <AppLayout>
    <div class="p-6">
      <div class="mb-4 flex justify-between items-center">
        <h2 class="text-2xl font-bold text-gray-800">Gestión de Doctores</h2>
        <el-button type="primary" @click="handleCreate">
          <el-icon class="mr-2"><Plus /></el-icon>
          Nuevo Doctor
        </el-button>
      </div>

      <el-card>
        <el-table :data="doctores" v-loading="loading" stripe>
          <el-table-column prop="Codigo" label="Código" width="100" />
          <el-table-column prop="Nombre" label="Nombre" />
          <el-table-column prop="Apellidos" label="Apellidos" />
          <el-table-column prop="Especialidad" label="Especialidad" />
          <el-table-column prop="Numero_Colegiado" label="N° Colegiado" />
          <el-table-column prop="Correo" label="Correo" />
          <el-table-column prop="Estado" label="Estado" width="100" />
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
        :title="isEdit ? 'Editar Doctor' : 'Nuevo Doctor'"
        width="600px"
      >
        <el-form :model="form" label-width="150px">
          <el-form-item label="Nombre" required>
            <el-input v-model="form.Nombre" />
          </el-form-item>
          <el-form-item label="Apellidos" required>
            <el-input v-model="form.Apellidos" />
          </el-form-item>
          <el-form-item label="Especialidad">
            <el-input v-model="form.Especialidad" />
          </el-form-item>
          <el-form-item label="Dirección">
            <el-input v-model="form.Direccion" type="textarea" />
          </el-form-item>
          <el-form-item label="Correo">
            <el-input v-model="form.Correo" type="email" />
          </el-form-item>
          <el-form-item label="Género">
            <el-select v-model="form.Genero" placeholder="Seleccionar">
              <el-option label="Masculino" value="Masculino" />
              <el-option label="Femenino" value="Femenino" />
            </el-select>
          </el-form-item>
          <el-form-item label="Número Celular">
            <el-input v-model.number="form.Numero_Celular" type="number" />
          </el-form-item>
          <el-form-item label="N° Colegiado">
            <el-input v-model="form.Numero_Colegiado" />
          </el-form-item>
          <el-form-item label="Fecha Contratación">
            <el-date-picker
              v-model="form.Fecha_Contratacion"
              type="date"
              format="YYYY-MM-DD"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item label="Estado">
            <el-select v-model="form.Estado" placeholder="Seleccionar">
              <el-option label="Activo" value="Activo" />
              <el-option label="Inactivo" value="Inactivo" />
            </el-select>
          </el-form-item>
          <el-form-item label="Salario">
            <el-input v-model.number="form.Salario" type="number" />
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
  getDoctores,
  createDoctor,
  updateDoctor,
  deleteDoctor,
  type Doctor,
  type DoctorCreate
} from '@/services/doctores'

const doctores = ref<Doctor[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const isEdit = ref(false)
const form = ref<DoctorCreate & { Codigo?: number }>({
  Nombre: '',
  Apellidos: '',
  Especialidad: '',
  Direccion: '',
  Correo: '',
  Genero: '',
  Numero_Celular: undefined,
  Numero_Colegiado: '',
  Fecha_Contratacion: undefined,
  Estado: '',
  Salario: undefined
})

async function loadDoctores() {
  loading.value = true
  try {
    const response = await getDoctores()
    doctores.value = response.data
  } catch (error) {
    ElMessage.error('Error al cargar doctores')
  } finally {
    loading.value = false
  }
}

function handleCreate() {
  isEdit.value = false
  form.value = {
    Nombre: '',
    Apellidos: '',
    Especialidad: '',
    Direccion: '',
    Correo: '',
    Genero: '',
    Numero_Celular: undefined,
    Numero_Colegiado: '',
    Fecha_Contratacion: undefined,
    Estado: '',
    Salario: undefined
  }
  dialogVisible.value = true
}

function handleEdit(row: Doctor) {
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
      await updateDoctor(form.value.Codigo, form.value)
      ElMessage.success('Doctor actualizado correctamente')
    } else {
      await createDoctor(form.value)
      ElMessage.success('Doctor creado correctamente')
    }
    dialogVisible.value = false
    loadDoctores()
  } catch (error) {
    ElMessage.error('Error al guardar doctor')
  }
}

async function handleDelete(codigo: number) {
  try {
    await ElMessageBox.confirm('¿Está seguro de eliminar este doctor?', 'Confirmar', {
      type: 'warning'
    })
    await deleteDoctor(codigo)
    ElMessage.success('Doctor eliminado correctamente')
    loadDoctores()
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('Error al eliminar doctor')
    }
  }
}

onMounted(() => {
  loadDoctores()
})
</script>
