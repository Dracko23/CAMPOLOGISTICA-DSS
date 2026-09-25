import { useEffect } from 'react'
import { CircleMarker, MapContainer, Popup, TileLayer, useMap } from 'react-leaflet'
import { latLngBounds } from 'leaflet'
import type { Pedido } from '@/lib/api'

function Bounds({ points }: { points: [number, number][] }) {
  const map = useMap()
  useEffect(() => {
    if (points.length > 1) map.fitBounds(latLngBounds(points), { padding: [35, 35], maxZoom: 14 })
    else if (points.length === 1) map.setView(points[0], 14)
  }, [map, points])
  return null
}

export function OperationalMap({ orders }: { orders: Pedido[] }) {
  const located = orders.flatMap((order) => {
    const lat = Number(order.ubicacion.latitud); const lng = Number(order.ubicacion.longitud)
    return Number.isFinite(lat) && Number.isFinite(lng) ? [{ order, point: [lat, lng] as [number, number] }] : []
  })
  const points = located.map(({ point }) => point)
  return <div className='relative h-[420px] overflow-hidden rounded-2xl bg-slate-100'>
    <MapContainer center={[-16.7, -64.7]} zoom={5} className='h-full w-full' scrollWheelZoom>
      <TileLayer attribution='&copy; OpenStreetMap contributors' url='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png' />
      <Bounds points={points} />
      {located.map(({ order, point }) => <CircleMarker key={order.id_pedido} center={point} radius={9} pathOptions={{ color: '#fff', weight: 3, fillColor: order.estado === 'en_camino' ? '#0891b2' : order.estado === 'pendiente' ? '#f59e0b' : '#10b981', fillOpacity: 1 }}><Popup><strong>{order.codigo}</strong><br />{order.ubicacion.direccion}<br /><small>{order.estado.replace('_', ' ')}</small></Popup></CircleMarker>)}
    </MapContainer>
    {!located.length && <div className='pointer-events-none absolute inset-x-4 bottom-4 z-[500] rounded-xl bg-white/95 p-3 text-center text-sm text-slate-600 shadow'>Los pedidos con ubicación confirmada aparecerán aquí.</div>}
  </div>
}
