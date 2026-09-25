import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import App from './App'


const emptyPage = {
  items: [],
  page: 1,
  page_size: 10,
  total: 0,
  total_pages: 0,
}

const summary = {
  pedidos_registrados: 0,
  pedidos_pendientes: 0,
  pedidos_asignados: 0,
  conductores_disponibles: 0,
  vehiculos_disponibles: 0,
  actividad_reciente: [],
}

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

function mockApi(
  handler?: (url: string, init?: RequestInit) => Response | Promise<Response> | undefined,
) {
  const fetchMock = vi.fn(async (input: RequestInfo | URL, init?: RequestInit) => {
    const url = String(input)
    if (url.includes('/auth/me')) return jsonResponse({ id_usuario: 1, email: 'admin.demo@campologistica.bo', nombre: 'Administrador DEMO', rol: 'admin' })
    const custom = handler?.(url, init)
    if (custom) return custom
    if (url.includes('/operacion/resumen')) return jsonResponse(summary)
    if (url.includes('/pedidos')) return jsonResponse(emptyPage)
    if (url.includes('/conductores')) return jsonResponse({ ...emptyPage, page_size: 100 })
    if (url.includes('/vehiculos')) return jsonResponse({ ...emptyPage, page_size: 100 })
    if (url.includes('/asignaciones')) return jsonResponse(emptyPage)
    return jsonResponse({ detail: { code: 'not_found', message: 'No encontrado' } }, 404)
  })
  vi.stubGlobal('fetch', fetchMock)
  return fetchMock
}

describe('aplicación operacional', () => {
  beforeEach(() => {
    localStorage.setItem('campo_token', 'test-token')
    window.history.pushState({}, '', '/')
  })

  it('renderiza el shell, navegación y módulos futuros deshabilitados', async () => {
    mockApi()
    render(<App />)
    expect(await screen.findByRole('heading', { name: /resumen operacional/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /^pedidos$/i })).toBeInTheDocument()
    expect(screen.getByRole('link', { name: /asignaciones/i })).toBeInTheDocument()
    expect(screen.getByText('Administrador DEMO')).toBeInTheDocument()
  })

  it('navega como SPA hacia pedidos', async () => {
    mockApi()
    const user = userEvent.setup()
    render(<App />)
    await screen.findByRole('heading', { name: /resumen operacional/i })
    await user.click(screen.getByRole('link', { name: /^pedidos$/i }))
    expect(await screen.findByRole('heading', { name: /^pedidos$/i })).toBeInTheDocument()
    expect(window.location.pathname).toBe('/app/pedidos')
  })

  it('muestra loading y luego empty state en pedidos', async () => {
    let resolveRequest: ((value: Response) => void) | undefined
    vi.stubGlobal(
      'fetch',
      vi.fn(
        (input: RequestInfo | URL) => {
          if (String(input).includes('/auth/me')) return Promise.resolve(jsonResponse({ id_usuario: 1, email: 'admin.demo@campologistica.bo', nombre: 'Administrador DEMO', rol: 'admin' }))
          return new Promise<Response>((resolve) => {
            resolveRequest = resolve
          })
        },
      ),
    )
    window.history.pushState({}, '', '/app/pedidos')
    render(<App />)
    expect(await screen.findByLabelText('Cargando pedidos')).toBeInTheDocument()
    resolveRequest?.(jsonResponse(emptyPage))
    expect(await screen.findByText(/aún no hay pedidos/i)).toBeInTheDocument()
  })

  it('muestra un error recuperable en el listado', async () => {
    mockApi(() => jsonResponse({ detail: { code: 'error', message: 'Fallo controlado' } }, 500))
    window.history.pushState({}, '', '/app/pedidos')
    render(<App />)
    expect(await screen.findByText(/no pudimos cargar los pedidos/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /reintentar/i })).toBeInTheDocument()
  })

  it('valida el formulario de pedido junto a los campos', async () => {
    mockApi()
    const user = userEvent.setup()
    window.history.pushState({}, '', '/app/pedidos/nuevo')
    render(<App />)
    await user.click(await screen.findByRole('button', { name: /nuevo cliente/i }))
    await user.click(await screen.findByRole('button', { name: /continuar/i }))
    expect(await screen.findByText(/el nombre es obligatorio/i)).toBeInTheDocument()
  })

  it('crea un pedido y muestra confirmación', async () => {
    const created = {
      id_pedido: 42,
      codigo: 'PED-WEB-001',
      estado: 'pendiente',
      cliente: { id_cliente: 1, nombre: 'Ana Flores' },
      ubicacion: { id_ubicacion: 1, direccion: 'Av. Las Américas', zona: 'Centro' },
      asignaciones: [],
      asignacion_actual: null,
    }
    const fetchMock = mockApi((url, init) => {
      if (url.endsWith('/pedidos') && init?.method === 'POST') return jsonResponse(created, 201)
      if (url.includes('/pedidos/42')) return jsonResponse(created)
      return undefined
    })
    const user = userEvent.setup()
    window.history.pushState({}, '', '/app/pedidos/nuevo')
    render(<App />)
    await user.click(await screen.findByRole('button', { name: /nuevo cliente/i }))
    await user.type(await screen.findByLabelText(/nombre del cliente/i), 'Ana Flores')
    await user.click(screen.getByRole('button', { name: /continuar/i }))
    await user.type(screen.getByLabelText(/dirección/i), 'Av. Las Américas')
    await user.type(screen.getByLabelText(/zona/i), 'Centro')
    await user.click(screen.getByRole('button', { name: /continuar/i }))
    await user.type(screen.getByLabelText(/código del pedido/i), 'PED-WEB-001')
    await user.type(screen.getByLabelText(/fecha.*límite/i), '2026-12-20T10:00')
    await user.type(screen.getByLabelText(/peso/i), '25')
    await user.click(screen.getByRole('button', { name: /continuar/i }))
    await user.click(screen.getByRole('button', { name: /registrar pedido/i }))
    expect(await screen.findByText(/pedido guardado correctamente/i)).toBeInTheDocument()
    expect(fetchMock).toHaveBeenCalledWith(
      expect.stringContaining('/pedidos'),
      expect.objectContaining({ method: 'POST' }),
    )
  })

  it('presenta selección y resumen antes de crear una asignación', async () => {
    mockApi((url) => {
      if (url.includes('/pedidos?')) {
        return jsonResponse({
          ...emptyPage,
          page_size: 100,
          total: 1,
          total_pages: 1,
          items: [
            {
              id_pedido: 1,
              codigo: 'PED-ASG-001',
              peso_kg: 120,
              urgencia: 4,
              estado: 'pendiente',
              cliente: { nombre: 'Cliente Demo' },
              ubicacion: { direccion: 'Calle Colón', zona: 'Centro' },
            },
          ],
        })
      }
      if (url.includes('/conductores?')) {
        return jsonResponse({
          ...emptyPage,
          page_size: 100,
          total: 1,
          total_pages: 1,
          items: [{ id_conductor: 2, nombre: 'Carlos Mendoza', licencia: 'LIC-2', disponible: true }],
        })
      }
      if (url.includes('/vehiculos?')) {
        return jsonResponse({
          ...emptyPage,
          page_size: 100,
          total: 1,
          total_pages: 1,
          items: [{ id_vehiculo: 3, placa: 'TJA-300', capacidad_kg: 500, rendimiento_km_l: 11, disponible: true }],
        })
      }
      return undefined
    })
    const user = userEvent.setup()
    window.history.pushState({}, '', '/app/asignaciones')
    render(<App />)
    await user.click(await screen.findByRole('button', { name: /nueva asignación/i }))
    await user.selectOptions(screen.getByLabelText(/pedido/i), '1')
    await user.selectOptions(screen.getByLabelText(/conductor/i), '2')
    await user.selectOptions(screen.getByLabelText(/vehículo/i), '3')
    expect(screen.getByText('PED-ASG-001')).toBeInTheDocument()
    expect(screen.getByText('Carlos Mendoza')).toBeInTheDocument()
    expect(screen.getByText('TJA-300')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /confirmar asignación/i })).toBeEnabled()
  })
})
