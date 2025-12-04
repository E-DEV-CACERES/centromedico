import api from './api'

export interface Examen {
  Codigo: number
  Codigo_Paciente: number
  Codigo_Doctor: number
  Tipo_Examen: string
  Fecha_Solicitud?: string
  Fecha_Resultado?: string
  Resultado?: string
  Observaciones?: string
  Estado?: string
  Fecha_Creacion?: string
  Fecha_Modificacion?: string
}

export interface ExamenCreate {
  Codigo_Paciente: number
  Codigo_Doctor: number
  Tipo_Examen: string
  Fecha_Solicitud?: string
  Fecha_Resultado?: string
  Resultado?: string
  Observaciones?: string
  Estado?: string
}

export interface ExamenUpdate {
  Codigo_Paciente?: number
  Codigo_Doctor?: number
  Tipo_Examen?: string
  Fecha_Solicitud?: string
  Fecha_Resultado?: string
  Resultado?: string
  Observaciones?: string
  Estado?: string
}

export interface ExamenFilters {
  codigo_paciente?: number
  codigo_doctor?: number
  estado?: string
}

export function getExamenes(filters?: ExamenFilters) {
  const params = new URLSearchParams()
  if (filters?.codigo_paciente) params.append('codigo_paciente', filters.codigo_paciente.toString())
  if (filters?.codigo_doctor) params.append('codigo_doctor', filters.codigo_doctor.toString())
  if (filters?.estado) params.append('estado', filters.estado)
  
  const query = params.toString()
  return api.get<Examen[]>(`/api/examenes${query ? `?${query}` : ''}`)
}

export function getExamen(codigo: number) {
  return api.get<Examen>(`/api/examenes/${codigo}`)
}

export function createExamen(data: ExamenCreate) {
  return api.post<Examen>('/api/examenes', data)
}

export function updateExamen(codigo: number, data: ExamenUpdate) {
  return api.put<Examen>(`/api/examenes/${codigo}`, data)
}

export function deleteExamen(codigo: number) {
  return api.delete(`/api/examenes/${codigo}`)
}
