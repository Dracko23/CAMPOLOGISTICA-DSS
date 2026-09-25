import { Navigate, Outlet, Route, Routes, useParams } from 'react-router-dom'
import { useAuth } from '@/app/auth'
import { AppShell } from '@/components/AppShell'
import { PortalLayout } from '@/components/PortalLayout'
import { AsignacionesPage } from '@/pages/AsignacionesPage'
import { ClientPage } from '@/pages/ClientPage'
import { ClientesPage } from '@/pages/ClientesPage'
import { ConductoresPage } from '@/pages/ConductoresPage'
import { DriverPage } from '@/pages/DriverPage'
import { LoginPage } from '@/pages/LoginPage'
import { NewPedidoPage } from '@/pages/NewPedidoPage'
import { OverviewPage } from '@/pages/OverviewPage'
import { PedidoDetailPage } from '@/pages/PedidoDetailPage'
import { PedidosPage } from '@/pages/PedidosPage'
import { VehiculosPage } from '@/pages/VehiculosPage'

function Guard({ role }: { role: 'admin'|'conductor'|'cliente' }) { const {user,loading}=useAuth(); if(loading)return <div className='grid min-h-screen place-items-center'>Cargando…</div>; if(!user)return <Navigate to='/login' replace/>; if(user.rol!==role)return <Navigate to={user.rol==='admin'?'/app':user.rol==='conductor'?'/driver':'/client'} replace/>; return <Outlet/> }
function LegacyOrderRedirect(){const {id}=useParams();return <Navigate to={`/app/pedidos/${id}`} replace/>}

export function AppRouter() { return <Routes>
  <Route path='/login' element={<LoginPage/>}/>
  <Route element={<Guard role='admin'/>}><Route path='/' element={<Navigate to='/app' replace/>}/></Route>
  <Route element={<Guard role='admin'/>}><Route path='/app/*' element={<AppShell><Routes><Route index element={<OverviewPage/>}/><Route path='pedidos' element={<PedidosPage/>}/><Route path='pedidos/nuevo' element={<NewPedidoPage/>}/><Route path='pedidos/:id' element={<PedidoDetailPage/>}/><Route path='clientes' element={<ClientesPage/>}/><Route path='conductores' element={<ConductoresPage/>}/><Route path='vehiculos' element={<VehiculosPage/>}/><Route path='asignaciones' element={<AsignacionesPage/>}/></Routes></AppShell>}/></Route>
  <Route element={<Guard role='admin'/>}><Route path='/pedidos/:id' element={<LegacyOrderRedirect/>}/><Route path='/pedidos' element={<Navigate to='/app/pedidos' replace/>}/><Route path='/pedidos/nuevo' element={<Navigate to='/app/pedidos/nuevo' replace/>}/><Route path='/asignaciones' element={<Navigate to='/app/asignaciones' replace/>}/><Route path='/conductores' element={<Navigate to='/app/conductores' replace/>}/><Route path='/vehiculos' element={<Navigate to='/app/vehiculos' replace/>}/></Route>
  <Route element={<Guard role='conductor'/>}><Route path='/driver/*' element={<PortalLayout kind='driver'><Routes><Route index element={<DriverPage/>}/><Route path='delivery' element={<DriverPage/>}/><Route path='route' element={<DriverPage view='route'/>}/><Route path='history' element={<DriverPage view='history'/>}/><Route path='profile' element={<DriverPage view='profile'/>}/></Routes></PortalLayout>}/></Route>
  <Route element={<Guard role='cliente'/>}><Route path='/client/*' element={<PortalLayout kind='client'><Routes><Route index element={<ClientPage/>}/><Route path='shipments' element={<ClientPage view='shipments'/>}/><Route path='tracking' element={<ClientPage view='tracking'/>}/><Route path='tracking/:pedido' element={<ClientPage view='tracking'/>}/><Route path='history' element={<ClientPage view='history'/>}/><Route path='profile' element={<ClientPage view='profile'/>}/></Routes></PortalLayout>}/></Route>
  <Route path='*' element={<Navigate to='/login' replace/>}/>
</Routes> }
