import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, logout as logoutApi, getCurrentUser } from '@/services/auth'
import type { UsuarioSistema } from '@/services/usuarios'
import type { LoginRequest } from '@/services/auth'

export const useAuthStore = defineStore('auth', () => {
  const usuario = ref<Omit<UsuarioSistema, 'Contrasena'> | null>(null)
  const token = ref<string | null>(null)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const isAuthenticated = computed(() => !!usuario.value && !!token.value)

  const userRole = computed(() => usuario.value?.Rol || null)

  function setAuth(user: Omit<UsuarioSistema, 'Contrasena'>, authToken?: string) {
    usuario.value = user
    token.value = authToken || null
    error.value = null
    
    // Guardar en localStorage
    if (authToken) {
      localStorage.setItem('auth_token', authToken)
    }
    localStorage.setItem('auth_user', JSON.stringify(user))
  }

  function clearAuth() {
    usuario.value = null
    token.value = null
    error.value = null
    localStorage.removeItem('auth_token')
    localStorage.removeItem('auth_user')
  }

  async function login(credentials: LoginRequest) {
    isLoading.value = true
    error.value = null
    
    try {
      const response = await loginApi(credentials)
      const { usuario: user, token: authToken } = response.data
      
      setAuth(user, authToken)
      return { success: true }
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || err.response?.data?.message || 'Error al iniciar sesión'
      error.value = errorMessage
      return { success: false, error: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  async function logout() {
    try {
      await logoutApi()
    } catch (err) {
      console.error('Error al cerrar sesión:', err)
    } finally {
      clearAuth()
    }
  }

  async function checkAuth() {
    // Intentar recuperar del localStorage
    const storedToken = localStorage.getItem('auth_token')
    const storedUser = localStorage.getItem('auth_user')
    
    if (storedToken && storedUser) {
      try {
        usuario.value = JSON.parse(storedUser)
        token.value = storedToken
        
        // Por ahora, solo verificar que tenemos los datos
        // En producción, aquí se verificaría con el servidor usando el endpoint /me
        // const response = await getCurrentUser()
        // setAuth(response.data)
        return true
      } catch (err) {
        // Si falla, limpiar
        clearAuth()
        return false
      }
    }
    
    return false
  }

  // Inicializar desde localStorage al cargar
  function initAuth() {
    const storedToken = localStorage.getItem('auth_token')
    const storedUser = localStorage.getItem('auth_user')
    
    if (storedToken && storedUser) {
      try {
        usuario.value = JSON.parse(storedUser)
        token.value = storedToken
      } catch (err) {
        clearAuth()
      }
    }
  }

  return {
    usuario,
    token,
    isLoading,
    error,
    isAuthenticated,
    userRole,
    login,
    logout,
    checkAuth,
    initAuth,
    clearAuth
  }
})
