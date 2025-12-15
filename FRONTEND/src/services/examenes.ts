import api from './api'

export interface CitaInfo {
  Codigo: number
  Fecha_Hora?: string
  Estado?: string
  Motivo?: string
}

export interface ConsultaInfo {
  Codigo: number
  Fecha_de_Consulta?: string
  Estado?: string
  Tipo_de_Consulta?: string
  Diagnostico?: string
  Examenes_Solicitados?: boolean
  Examenes_Descripcion?: string
  Examenes_Sugeridos?: boolean
  Examenes_Sugeridos_Descripcion?: string
  Fecha_Creacion?: string
  Fecha_Modificacion?: string
}

export interface Examen {
  Codigo: number
  Codigo_Paciente: number
  Codigo_Doctor: number
  Codigo_Consulta?: number
  Codigo_Cita?: number
  Tipo_Examen: string
  Fecha_Solicitud?: string
  Fecha_Resultado?: string
  Resultado?: string
  Observaciones?: string
  Estado?: string
  Fecha_Creacion?: string
  Fecha_Modificacion?: string
  Cita_Info?: CitaInfo
  Consulta_Info?: ConsultaInfo
}

export interface ExamenCreate {
  Codigo_Paciente: number
  Codigo_Doctor: number
  Codigo_Consulta?: number
  Codigo_Cita?: number
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
  Codigo_Consulta?: number
  Codigo_Cita?: number
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
  codigo_consulta?: number
  codigo_cita?: number
  estado?: string
}

export function getExamenes(filters?: ExamenFilters) {
  const params = new URLSearchParams()
  if (filters?.codigo_paciente) params.append('codigo_paciente', filters.codigo_paciente.toString())
  if (filters?.codigo_doctor) params.append('codigo_doctor', filters.codigo_doctor.toString())
  if (filters?.codigo_consulta) params.append('codigo_consulta', filters.codigo_consulta.toString())
  if (filters?.codigo_cita) params.append('codigo_cita', filters.codigo_cita.toString())
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
