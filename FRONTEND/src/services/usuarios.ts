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

// Funciones de backup
export interface BackupInfo {
  filename: string
  size: number
  created: string
  modified: string
}

export interface BackupListResponse {
  backups: BackupInfo[]
  count: number
}

export interface BackupCreateResponse {
  message: string
  filename: string
  path: string
  timestamp: string
}

export function crearBackup() {
  return api.post<BackupCreateResponse>('/api/usuarios/backup')
}

export function listarBackups() {
  return api.get<BackupListResponse>('/api/usuarios/backup/list')
}

export function descargarBackup(filename: string) {
  return api.get(`/api/usuarios/backup/download/${filename}`, {
    responseType: 'blob'
  })
}
