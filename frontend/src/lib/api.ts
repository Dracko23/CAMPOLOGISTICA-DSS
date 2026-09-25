export type Page<T> = {
  items: T[]
  page: number
  page_size: number
  total: number
  total_pages: number
}

export type PedidoEstado = 'pendiente' | 'asignado' | 'en_camino' | 'entregado' | 'cancelado'
export type AsignacionEstado = 'asignada' | 'aceptada' | 'en_camino' | 'llegue' | 'entregada' | 'cancelada'

export type Cliente = {
  id_cliente: number
  nombre: string
  telefono?: string | null
  email?: string | null
}

export type Ubicacion = {
  id_ubicacion: number
  direccion: string
  zona: string
  ciudad?: string | null
  departamento?: string | null
  latitud?: number | string | null
  longitud?: number | string | null
}

export type Conductor = {
  id_conductor: number
  nombre: string
  licencia: string | null
  disponible: boolean
}

export type Vehiculo = {
  id_vehiculo: number
  placa: string | null
  capacidad_kg: number | string | null
  rendimiento_km_l: number | string | null
  disponible: boolean
}

export type AsignacionResumen = {
  id_asignacion: number
  estado: AsignacionEstado
  fecha_asignacion?: string
  fecha_salida?: string | null
  fecha_aceptacion?: string | null
  fecha_llegada?: string | null
  fecha_entrega?: string | null
  conductor: Conductor
  vehiculo: Vehiculo
}

export type Pedido = {
  id_pedido: number
  codigo: string
  peso_kg: number | string
  urgencia: number
  fecha_limite?: string | null
  estado: PedidoEstado
  fecha_registro?: string
  cliente: Cliente
  ubicacion: Ubicacion
  asignacion_actual?: AsignacionResumen | null
  asignaciones?: AsignacionResumen[]
}

export type Asignacion = {
  id_asignacion: number
  estado: AsignacionEstado
  fecha_asignacion?: string
  fecha_salida?: string | null
  fecha_aceptacion?: string | null
  fecha_llegada?: string | null
  fecha_entrega?: string | null
  distancia_km?: number | string | null
  combustible_litros?: number | string | null
  costo_combustible?: number | string | null
  pedido: Pick<Pedido, 'id_pedido' | 'codigo' | 'estado' | 'peso_kg' | 'urgencia' | 'ubicacion'>
  conductor: Conductor
  vehiculo: Vehiculo
}

export type Actividad = {
  tipo: string
  id: number
  titulo: string
  detalle: string
  fecha?: string | null
}

export type Resumen = {
  pedidos_registrados: number
  pedidos_pendientes: number
  pedidos_asignados: number
  conductores_disponibles: number
  vehiculos_disponibles: number
  actividad_reciente: Actividad[]
}

export type PedidoInput = {
  cliente?: { nombre: string; telefono?: string; email?: string }
  id_cliente?: number
  ubicacion: { direccion: string; zona: string; ciudad?: string; departamento?: string; latitud?: number; longitud?: number }
  pedido: {
    codigo: string
    peso_kg: number
    urgencia: number
    fecha_limite: string
  }
}

export type ConductorInput = { nombre: string; licencia: string; disponible: boolean }
export type VehiculoInput = { placa: string; capacidad_kg: number; rendimiento_km_l: number; disponible: boolean }

export class ApiError extends Error {
  status: number
  code: string
  field?: string

  constructor(status: number, message: string, code = 'request_error', field?: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.code = code
    this.field = field
  }
}

const configuredApiUrl = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/$/, '')
const API_URL = configuredApiUrl.endsWith('/api/v1') ? configuredApiUrl : `${configuredApiUrl}/api/v1`

function queryString(params: Record<string, string | number | boolean | undefined>) {
  const search = new URLSearchParams()
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== '') search.set(key, String(value))
  })
  const value = search.toString()
  return value ? `?${value}` : ''
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = localStorage.getItem('campo_token')
  const response = await fetch(`${API_URL}${path}`, {
    ...init,
    headers: {
      ...(init?.body ? { 'Content-Type': 'application/json' } : {}),
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...init?.headers,
    },
  })
  if (!response.ok) {
    let detail: { message?: string; code?: string; field?: string } = {}
    try {
      const body = await response.json() as { detail?: typeof detail | string | Array<{ msg?: string; loc?: Array<string | number> }> }
      if (typeof body.detail === 'string') detail = { message: body.detail }
      else if (Array.isArray(body.detail)) {
        const first = body.detail[0]
        detail = { message: first?.msg ? `Revisa los datos enviados: ${first.msg}` : 'Revisa los campos e intenta nuevamente.', field: first?.loc?.at(-1)?.toString() }
      } else detail = body.detail ?? {}
    } catch {
      detail = {}
    }
    throw new ApiError(response.status, detail.message || 'No fue posible completar la solicitud.', detail.code, detail.field)
  }
  if (response.status === 204) return undefined as T
  return response.json() as Promise<T>
}

export const api = {
  login: (email: string, password: string) => request<AuthSession>('/auth/login', { method: 'POST', body: JSON.stringify({ email, password }) }),
  me: () => request<User>('/auth/me'),
  logout: () => request<void>('/auth/logout', { method: 'POST' }),
  resumen: () => request<Resumen>('/operacion/resumen'),
  clientes: (q?: string) => request<Cliente[]>(`/clientes${queryString({ q })}`),
  pedidos: (params: Record<string, string | number | undefined> = {}) =>
    request<Page<Pedido>>(`/pedidos${queryString(params)}`),
  pedido: (id: number) => request<Pedido>(`/pedidos/${id}`),
  crearPedido: (input: PedidoInput) => request<Pedido>('/pedidos', { method: 'POST', body: JSON.stringify(input) }),
  editarPedido: (id: number, input: Partial<PedidoInput>) => request<Pedido>(`/pedidos/${id}`, { method: 'PATCH', body: JSON.stringify(input) }),
  eliminarPedido: (id: number) => request<void>(`/pedidos/${id}`, { method: 'DELETE' }),
  conductores: (params: Record<string, string | number | boolean | undefined> = {}) =>
    request<Page<Conductor>>(`/conductores${queryString(params)}`),
  crearConductor: (input: ConductorInput) => request<Conductor>('/conductores', { method: 'POST', body: JSON.stringify(input) }),
  editarConductor: (id: number, input: Partial<ConductorInput>) => request<Conductor>(`/conductores/${id}`, { method: 'PATCH', body: JSON.stringify(input) }),
  eliminarConductor: (id: number) => request<void>(`/conductores/${id}`, { method: 'DELETE' }),
  vehiculos: (params: Record<string, string | number | boolean | undefined> = {}) =>
    request<Page<Vehiculo>>(`/vehiculos${queryString(params)}`),
  crearVehiculo: (input: VehiculoInput) => request<Vehiculo>('/vehiculos', { method: 'POST', body: JSON.stringify(input) }),
  editarVehiculo: (id: number, input: Partial<VehiculoInput>) => request<Vehiculo>(`/vehiculos/${id}`, { method: 'PATCH', body: JSON.stringify(input) }),
  eliminarVehiculo: (id: number) => request<void>(`/vehiculos/${id}`, { method: 'DELETE' }),
  asignaciones: (params: Record<string, string | number | undefined> = {}) =>
    request<Page<Asignacion>>(`/asignaciones${queryString(params)}`),
  crearAsignacion: (input: { id_pedido: number; id_conductor: number; id_vehiculo: number }) =>
    request<Asignacion>('/asignaciones', { method: 'POST', body: JSON.stringify(input) }),
  estadoAsignacion: (id: number, estado: AsignacionEstado) =>
    request<Asignacion>(`/asignaciones/${id}`, { method: 'PATCH', body: JSON.stringify({ estado }) }),
  driverAssignments: () => request<Asignacion[]>('/driver/asignaciones'),
  driverAssignment: (id: number) => request<Asignacion>(`/driver/asignaciones/${id}`),
  driverStatus: (id: number, estado: AsignacionEstado) => request<Asignacion>(`/driver/asignaciones/${id}/estado`, { method: 'PATCH', body: JSON.stringify({ estado }) }),
  clientOrders: () => request<Pedido[]>('/client/pedidos'),
  clientOrder: (id: number) => request<Pedido>(`/client/pedidos/${id}`),
  tracking: (id: number) => request<TrackingPosition>(`/tracking/asignaciones/${id}`),
  demoTracking: (id: number, progreso: number) => request<TrackingPosition>(`/admin/asignaciones/${id}/simulacion`, { method: 'POST', body: JSON.stringify({ progreso }) }),
  publishPosition: (id: number, input: { latitud:number; longitud:number; precision_m?:number }) => request<TrackingPosition>(`/driver/asignaciones/${id}/posicion`, { method: 'POST', body: JSON.stringify(input) }),
}

export function trackingStreamUrl(id: number) { return `${API_URL}/tracking/asignaciones/${id}/stream` }

export type User = { id_usuario: number; email: string; nombre: string; rol: 'admin' | 'conductor' | 'cliente'; id_conductor?: number | null; id_cliente?: number | null }
export type AuthSession = { access_token: string; token_type: string; user: User }
export type TrackingPosition = { id_asignacion:number; id_vehiculo:number; latitud:number; longitud:number; destino_latitud:number; destino_longitud:number; progreso:number; fuente:'simulacion'|'gps'|'manual'; fecha_hora:string }

export function errorMessage(error: unknown) {
  return error instanceof Error ? error.message : 'Ocurrió un error inesperado.'
}
