import api from './api'

export interface Consulta {
  Codigo: number
  Codigo_Paciente?: number
  Codigo_Doctor?: number
  Tipo_de_Consulta?: string
  Fecha_de_Consulta?: string
  Diagnostico?: string
  Estado?: string
  Examenes_Solicitados?: boolean
  Examenes_Descripcion?: string
  Examenes_Sugeridos?: boolean
  Examenes_Sugeridos_Descripcion?: string
  Fecha_Creacion?: string
  Fecha_Modificacion?: string
}

export interface ConsultaCreate {
  Codigo_Paciente?: number
  Codigo_Doctor?: number
  Tipo_de_Consulta?: string
  Fecha_de_Consulta?: string
  Diagnostico?: string
  Estado?: string
  Examenes_Solicitados?: boolean
  Examenes_Descripcion?: string
  Examenes_Sugeridos?: boolean
  Examenes_Sugeridos_Descripcion?: string
}

export interface ConsultaUpdate {
  Codigo_Paciente?: number
  Codigo_Doctor?: number
  Tipo_de_Consulta?: string
  Fecha_de_Consulta?: string
  Diagnostico?: string
  Estado?: string
  Examenes_Solicitados?: boolean
  Examenes_Descripcion?: string
  Examenes_Sugeridos?: boolean
  Examenes_Sugeridos_Descripcion?: string
}

export interface ConsultaFilters {
  codigo_paciente?: number
  codigo_doctor?: number
  estado?: string
}

export function getConsultas(filters?: ConsultaFilters) {
  const params = new URLSearchParams()
  if (filters?.codigo_paciente) params.append('codigo_paciente', filters.codigo_paciente.toString())
  if (filters?.codigo_doctor) params.append('codigo_doctor', filters.codigo_doctor.toString())
  if (filters?.estado) params.append('estado', filters.estado)
  
  const query = params.toString()
  return api.get<Consulta[]>(`/api/consultas${query ? `?${query}` : ''}`)
}

export function getConsulta(codigo: number) {
  return api.get<Consulta>(`/api/consultas/${codigo}`)
}

export function createConsulta(data: ConsultaCreate) {
  return api.post<Consulta>('/api/consultas', data)
}

export function updateConsulta(codigo: number, data: ConsultaUpdate) {
  return api.put<Consulta>(`/api/consultas/${codigo}`, data)
}

export function deleteConsulta(codigo: number) {
  return api.delete(`/api/consultas/${codigo}`)
}
