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
