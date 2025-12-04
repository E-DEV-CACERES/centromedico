import api from './api'

export interface UsuarioSistema {
  Codigo: number
  Usuario: string
  Contrasena?: string
  Codigo_Doctor?: number
  Rol?: string
  Activo?: number
  Ultimo_Acceso?: string
  Fecha_Creacion?: string
  Fecha_Modificacion?: string
}

export interface UsuarioSistemaCreate {
  Usuario: string
  Contrasena: string
  Codigo_Doctor?: number
  Rol?: string
  Activo?: number
}

export interface UsuarioSistemaUpdate {
  Usuario?: string
  Contrasena?: string
  Codigo_Doctor?: number
  Rol?: string
  Activo?: number
}

export interface UsuarioSistemaFilters {
  rol?: string
  activo?: boolean
}

export function getUsuarios(filters?: UsuarioSistemaFilters) {
  const params = new URLSearchParams()
  if (filters?.rol) params.append('rol', filters.rol)
  if (filters?.activo !== undefined) params.append('activo', filters.activo.toString())
  
  const query = params.toString()
  return api.get<UsuarioSistema[]>(`/api/usuarios${query ? `?${query}` : ''}`)
}

export function getUsuario(codigo: number) {
  return api.get<UsuarioSistema>(`/api/usuarios/${codigo}`)
}

export function createUsuario(data: UsuarioSistemaCreate) {
  return api.post<UsuarioSistema>('/api/usuarios', data)
}

export function updateUsuario(codigo: number, data: UsuarioSistemaUpdate) {
  return api.put<UsuarioSistema>(`/api/usuarios/${codigo}`, data)
}

export function deleteUsuario(codigo: number) {
  return api.delete(`/api/usuarios/${codigo}`)
}
