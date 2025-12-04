import api from './api'

export interface Historial {
  Codigo_Historial: number
  Codigo_Paciente?: number
  Fecha_Ingreso?: string
  Diagnostico?: string
  Tratamiento?: string
  Observaciones?: string
  Fecha_Creacion?: string
  Fecha_Modificacion?: string
}

export interface HistorialCreate {
  Codigo_Paciente?: number
  Fecha_Ingreso?: string
  Diagnostico?: string
  Tratamiento?: string
  Observaciones?: string
}

export interface HistorialUpdate {
  Codigo_Paciente?: number
  Fecha_Ingreso?: string
  Diagnostico?: string
  Tratamiento?: string
  Observaciones?: string
}

export interface HistorialFilters {
  codigo_paciente?: number
}

export function getHistoriales(filters?: HistorialFilters) {
  const params = new URLSearchParams()
  if (filters?.codigo_paciente) params.append('codigo_paciente', filters.codigo_paciente.toString())
  
  const query = params.toString()
  return api.get<Historial[]>(`/api/historial${query ? `?${query}` : ''}`)
}

export function getHistorialPaciente(codigoPaciente: number) {
  return api.get<Historial[]>(`/api/historial/paciente/${codigoPaciente}`)
}

export function getHistorial(codigo: number) {
  return api.get<Historial>(`/api/historial/${codigo}`)
}

export function createHistorial(data: HistorialCreate) {
  return api.post<Historial>('/api/historial', data)
}

export function updateHistorial(codigo: number, data: HistorialUpdate) {
  return api.put<Historial>(`/api/historial/${codigo}`, data)
}

export function deleteHistorial(codigo: number) {
  return api.delete(`/api/historial/${codigo}`)
}
