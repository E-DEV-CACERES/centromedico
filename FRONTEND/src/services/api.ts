import axios, { type AxiosInstance, type AxiosResponse } from 'axios'

const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
})

// Interceptor para manejar errores
api.interceptors.response.use(
  (response: AxiosResponse) => response,
  (error) => {
    if (error.response) {
      console.error('Error de API:', error.response.data)
    } else if (error.request) {
      console.error('Error de red:', error.request)
    } else {
      console.error('Error:', error.message)
    }
    return Promise.reject(error)
  }
)

export default api
