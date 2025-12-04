import api from './api'

export interface Paciente {
  Codigo: number
  Nombre: string
  Apellidos: string
  Edad?: string
  Direccion?: string
  Numero_Celular?: number
  Fecha_Nacimiento?: string
  Tipo_Sangre?: string
  Alergias?: string
  Contacto_Emergencia?: string
  Telefono_Emergencia?: number
  Codigo_Seguro?: number
  Fecha_Creacion?: string
  Fecha_Modificacion?: string
}

export interface PacienteCreate {
  Nombre: string
  Apellidos: string
  Edad?: string
  Direccion?: string
  Numero_Celular?: number
  Fecha_Nacimiento?: string
  Tipo_Sangre?: string
  Alergias?: string
  Contacto_Emergencia?: string
  Telefono_Emergencia?: number
  Codigo_Seguro?: number
}

export interface PacienteUpdate {
  Nombre?: string
  Apellidos?: string
  Edad?: string
  Direccion?: string
  Numero_Celular?: number
  Fecha_Nacimiento?: string
  Tipo_Sangre?: string
  Alergias?: string
  Contacto_Emergencia?: string
  Telefono_Emergencia?: number
  Codigo_Seguro?: number
}

export function getPacientes() {
  return api.get<Paciente[]>('/api/pacientes')
}

export function getPaciente(codigo: number) {
  return api.get<Paciente>(`/api/pacientes/${codigo}`)
}

export function createPaciente(data: PacienteCreate) {
  return api.post<Paciente>('/api/pacientes', data)
}

export function updatePaciente(codigo: number, data: PacienteUpdate) {
  return api.put<Paciente>(`/api/pacientes/${codigo}`, data)
}

export function deletePaciente(codigo: number) {
  return api.delete(`/api/pacientes/${codigo}`)
}
