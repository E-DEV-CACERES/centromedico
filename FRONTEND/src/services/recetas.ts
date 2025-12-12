import api from './api'

export interface Receta {
  Codigo: number
  Codigo_Paciente?: number
  Codigo_Doctor?: number
  Codigo_Consulta?: number
  Nombre_Paciente?: string
  Fecha_Receta?: string
  Medicamento?: string
  Instrucciones?: string
  Fecha_Creacion?: string
  Fecha_Modificacion?: string
}

export interface RecetaCreate {
  Codigo_Paciente?: number
  Codigo_Doctor?: number
  Codigo_Consulta?: number
  Nombre_Paciente?: string
  Fecha_Receta?: string
  Medicamento?: string
  Instrucciones?: string
}

export interface RecetaUpdate {
  Codigo_Paciente?: number
  Codigo_Doctor?: number
  Codigo_Consulta?: number
  Nombre_Paciente?: string
  Fecha_Receta?: string
  Medicamento?: string
  Instrucciones?: string
}

export interface RecetaFilters {
  codigo_paciente?: number
  codigo_doctor?: number
}

export function getRecetas(filters?: RecetaFilters) {
  const params = new URLSearchParams()
  if (filters?.codigo_paciente) params.append('codigo_paciente', filters.codigo_paciente.toString())
  if (filters?.codigo_doctor) params.append('codigo_doctor', filters.codigo_doctor.toString())
  
  const query = params.toString()
  return api.get<Receta[]>(`/api/recetas${query ? `?${query}` : ''}`)
}

export function getReceta(codigo: number) {
  return api.get<Receta>(`/api/recetas/${codigo}`)
}

export function createReceta(data: RecetaCreate) {
  return api.post<Receta>('/api/recetas', data)
}

export function updateReceta(codigo: number, data: RecetaUpdate) {
  return api.put<Receta>(`/api/recetas/${codigo}`, data)
}

export function deleteReceta(codigo: number) {
  return api.delete(`/api/recetas/${codigo}`)
}

// Interfaz para receta completa con información de tablas relacionadas
export interface RecetaCompleta {
  receta: Receta
  paciente: {
    Codigo: number
    Nombre: string
    Apellidos: string
    Telefono?: string
    Email?: string
    Fecha_Nacimiento?: string
  } | null
  doctor: {
    Codigo: number
    Nombre: string
    Apellidos: string
    Especialidad?: string
    Telefono?: string
    Email?: string
    Estado?: string
  } | null
  consulta: {
    Codigo: number
    Tipo_de_Consulta?: string
    Fecha_de_Consulta?: string
    Estado?: string
    Diagnostico?: string
    Examenes_Solicitados?: boolean
    Examenes_Descripcion?: string
    Examenes_Sugeridos?: boolean
    Examenes_Sugeridos_Descripcion?: string
  } | null
}

export function getRecetasCompletas(codigo_doctor?: number) {
  const params = new URLSearchParams()
  if (codigo_doctor) params.append('codigo_doctor', codigo_doctor.toString())
  
  const query = params.toString()
  return api.get<RecetaCompleta[]>(`/api/recetas/completas${query ? `?${query}` : ''}`)
}
