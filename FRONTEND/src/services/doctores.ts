import api from './api'

export interface Doctor {
  Codigo: number
  Nombre: string
  Apellidos: string
  Especialidad?: string
  Direccion?: string
  Correo?: string
  Genero?: string
  Numero_Celular?: number
  Numero_Colegiado?: string
  Fecha_Contratacion?: string
  Estado?: string
  Salario?: number
  Fecha_Creacion?: string
  Fecha_Modificacion?: string
}

export interface DoctorCreate {
  Nombre: string
  Apellidos: string
  Especialidad?: string
  Direccion?: string
  Correo?: string
  Genero?: string
  Numero_Celular?: number
  Numero_Colegiado?: string
  Fecha_Contratacion?: string
  Estado?: string
  Salario?: number
}

export interface DoctorUpdate {
  Nombre?: string
  Apellidos?: string
  Especialidad?: string
  Direccion?: string
  Correo?: string
  Genero?: string
  Numero_Celular?: number
  Numero_Colegiado?: string
  Fecha_Contratacion?: string
  Estado?: string
  Salario?: number
}

export function getDoctores() {
  return api.get<Doctor[]>('/api/doctores')
}

export function getDoctor(codigo: number) {
  return api.get<Doctor>(`/api/doctores/${codigo}`)
}

export function createDoctor(data: DoctorCreate) {
  return api.post<Doctor>('/api/doctores', data)
}

export function updateDoctor(codigo: number, data: DoctorUpdate) {
  return api.put<Doctor>(`/api/doctores/${codigo}`, data)
}

export function deleteDoctor(codigo: number) {
  return api.delete(`/api/doctores/${codigo}`)
}
