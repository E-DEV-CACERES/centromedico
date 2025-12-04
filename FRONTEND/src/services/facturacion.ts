import api from './api'

export interface Facturacion {
  Codigo: number
  Codigo_Paciente: number
  Codigo_Consulta?: number
  Monto: number
  Metodo_Pago?: string
  Estado_Pago?: string
  Numero_Factura?: string
  Fecha_Factura?: string
  Fecha_Creacion?: string
  Fecha_Modificacion?: string
}

export interface FacturacionCreate {
  Codigo_Paciente: number
  Codigo_Consulta?: number
  Monto: number
  Metodo_Pago?: string
  Estado_Pago?: string
  Numero_Factura?: string
  Fecha_Factura?: string
}

export interface FacturacionUpdate {
  Codigo_Paciente?: number
  Codigo_Consulta?: number
  Monto?: number
  Metodo_Pago?: string
  Estado_Pago?: string
  Numero_Factura?: string
  Fecha_Factura?: string
}

export interface FacturacionFilters {
  codigo_paciente?: number
  estado_pago?: string
}

export function getFacturas(filters?: FacturacionFilters) {
  const params = new URLSearchParams()
  if (filters?.codigo_paciente) params.append('codigo_paciente', filters.codigo_paciente.toString())
  if (filters?.estado_pago) params.append('estado_pago', filters.estado_pago)
  
  const query = params.toString()
  return api.get<Facturacion[]>(`/api/facturacion${query ? `?${query}` : ''}`)
}

export function getFactura(codigo: number) {
  return api.get<Facturacion>(`/api/facturacion/${codigo}`)
}

export function createFactura(data: FacturacionCreate) {
  return api.post<Facturacion>('/api/facturacion', data)
}

export function updateFactura(codigo: number, data: FacturacionUpdate) {
  return api.put<Facturacion>(`/api/facturacion/${codigo}`, data)
}

export function deleteFactura(codigo: number) {
  return api.delete(`/api/facturacion/${codigo}`)
}
