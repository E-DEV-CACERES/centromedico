import api from './api'

export interface Cita {
  Codigo: number
  Codigo_Paciente: number
  Codigo_Doctor: number
  Fecha_Hora: string
  Estado?: string
  Motivo?: string
  Observaciones?: string
  Fecha_Creacion?: string
  Fecha_Modificacion?: string
}

export interface CitaCreate {
  Codigo_Paciente: number
  Codigo_Doctor: number
  Fecha_Hora: string
  Estado?: string
  Motivo?: string
  Observaciones?: string
}

export interface CitaUpdate {
  Codigo_Paciente?: number
  Codigo_Doctor?: number
  Fecha_Hora?: string
  Estado?: string
  Motivo?: string
  Observaciones?: string
}

export interface CitaFilters {
  estado?: string
  codigo_doctor?: number
  codigo_paciente?: number
}

export function getCitas(filters?: CitaFilters) {
  const params = new URLSearchParams()
  if (filters?.estado) params.append('estado', filters.estado)
  if (filters?.codigo_doctor) params.append('codigo_doctor', filters.codigo_doctor.toString())
  if (filters?.codigo_paciente) params.append('codigo_paciente', filters.codigo_paciente.toString())
  
  const query = params.toString()
  return api.get<Cita[]>(`/api/citas${query ? `?${query}` : ''}`)
}

export function getCita(codigo: number) {
  return api.get<Cita>(`/api/citas/${codigo}`)
}

export function createCita(data: CitaCreate) {
  return api.post<Cita>('/api/citas', data)
}

export function updateCita(codigo: number, data: CitaUpdate) {
  return api.put<Cita>(`/api/citas/${codigo}`, data)
}

export function deleteCita(codigo: number) {
  return api.delete(`/api/citas/${codigo}`)
}
