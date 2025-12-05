<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 to-indigo-100">
    <div class="w-full max-w-md">
      <el-card class="shadow-lg">
        <template #header>
          <div class="text-center">
            <h1 class="text-2xl font-bold text-gray-800">Sistema Centro Médico</h1>
            <p class="text-sm text-gray-600 mt-1">Iniciar Sesión</p>
          </div>
        </template>

        <el-form
          ref="loginFormRef"
          :model="form"
          :rules="rules"
          @submit.prevent="handleLogin"
          label-position="top"
        >
          <el-form-item label="Usuario" prop="Usuario">
            <el-input
              v-model="form.Usuario"
              placeholder="Ingrese su usuario"
              size="large"
              :prefix-icon="User"
              clearable
            />
          </el-form-item>

          <el-form-item label="Contraseña" prop="Contrasena">
            <el-input
              v-model="form.Contrasena"
              type="password"
              placeholder="Ingrese su contraseña"
              size="large"
              :prefix-icon="Lock"
              show-password
              clearable
              @keyup.enter="handleLogin"
            />
          </el-form-item>

          <el-alert
            v-if="authStore.error"
            :title="authStore.error"
            type="error"
            :closable="false"
            class="mb-4"
            show-icon
          />

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="authStore.isLoading"
              @click="handleLogin"
              class="w-full"
            >
              {{ authStore.isLoading ? 'Iniciando sesión...' : 'Iniciar Sesión' }}
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>

      <div class="text-center mt-4 text-sm text-gray-600">
        <p>Sistema de Gestión Médica v1.0</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const loginFormRef = ref<FormInstance>()

const form = reactive({
  Usuario: '',
  Contrasena: ''
})

const rules = reactive<FormRules>({
  Usuario: [
    { required: true, message: 'Por favor ingrese su usuario', trigger: 'blur' }
  ],
  Contrasena: [
    { required: true, message: 'Por favor ingrese su contraseña', trigger: 'blur' },
    { min: 6, message: 'La contraseña debe tener al menos 6 caracteres', trigger: 'blur' }
  ]
})

async function handleLogin() {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      const result = await authStore.login(form)
      
      if (result.success) {
        ElMessage.success('Inicio de sesión exitoso')
        router.push('/')
      } else {
        ElMessage.error(result.error || 'Error al iniciar sesión')
      }
    }
  })
}

onMounted(() => {
  // Si ya está autenticado, redirigir
  if (authStore.isAuthenticated) {
    router.push('/')
  }
})
</script>

<style scoped>
:deep(.el-card__header) {
  padding: 2rem 1.5rem 1rem;
}

:deep(.el-card__body) {
  padding: 1.5rem;
}
</style>
