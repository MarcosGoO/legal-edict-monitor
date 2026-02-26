import { HashRouter, Routes, Route } from 'react-router-dom'
import AppShell from './components/layout/AppShell'
import DashboardPage from './pages/Dashboard/DashboardPage'
import ClientListPage from './pages/Clients/ClientListPage'
import CreateClientPage from './pages/Clients/CreateClientPage'
import EditClientPage from './pages/Clients/EditClientPage'
import ClientDetailPage from './pages/Clients/ClientDetailPage'
import DocumentsPage from './pages/Documents/DocumentsPage'

function App() {
  return (
    <HashRouter>
      <Routes>
        <Route element={<AppShell />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/clients" element={<ClientListPage />} />
          <Route path="/clients/new" element={<CreateClientPage />} />
          <Route path="/clients/:id" element={<ClientDetailPage />} />
          <Route path="/clients/:id/edit" element={<EditClientPage />} />
          <Route path="/documents" element={<DocumentsPage />} />
        </Route>
      </Routes>
    </HashRouter>
  )
}

export default App
