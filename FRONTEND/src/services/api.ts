import axios, { type AxiosInstance, type AxiosResponse } from 'axios'

const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  },
  timeout: 10000, // 10 segundos de timeout
  withCredentials: false // No enviar cookies automáticamente
})

// Interceptor para agregar token a las peticiones
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor para manejar errores
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    if (error.response) {
      // El servidor respondió con un código de error
      // Si es error 401 (no autorizado), limpiar auth y redirigir a login
      if (error.response.status === 401) {
        localStorage.removeItem('auth_token')
        localStorage.removeItem('auth_user')
        // Solo redirigir si no estamos ya en login
        if (window.location.pathname !== '/login') {
          window.location.href = '/login'
        }
      }
      console.error('Error de API:', {
        status: error.response.status,
        data: error.response.data,
        url: error.config?.url
      })
    } else if (error.request) {
      // La petición se hizo pero no hubo respuesta
      console.error('Error de red - No se recibió respuesta del servidor:', {
        url: error.config?.url,
        method: error.config?.method,
        baseURL: error.config?.baseURL,
        message: 'Verifica que el servidor esté corriendo en ' + (error.config?.baseURL || 'http://localhost:8000')
      })
    } else {
      // Error al configurar la petición
      console.error('Error al configurar la petición:', error.message)
    }
    return Promise.reject(error)
  }
)

export default api
