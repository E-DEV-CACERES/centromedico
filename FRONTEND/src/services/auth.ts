import api from './api'
import type { UsuarioSistema } from './usuarios'

export interface LoginRequest {
  Usuario: string
  Contrasena: string
}

export interface LoginResponse {
  usuario: Omit<UsuarioSistema, 'Contrasena'>
  token?: string
}

export function login(credentials: LoginRequest) {
  return api.post<LoginResponse>('/api/auth/login', credentials)
}

export function logout() {
  return api.post('/api/auth/logout')
}

export function getCurrentUser() {
  return api.get<Omit<UsuarioSistema, 'Contrasena'>>('/api/auth/me')
}
