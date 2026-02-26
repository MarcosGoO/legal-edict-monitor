import { HashRouter, Routes, Route } from 'react-router-dom'
import AppShell from './components/layout/AppShell'

// Pages (lazy imports will be added progressively)
import DashboardPage from './pages/Dashboard/DashboardPage'

function App() {
  return (
    <HashRouter>
      <Routes>
        <Route element={<AppShell />}>
          <Route path="/" element={<DashboardPage />} />
          {/* More routes will be added in future tasks */}
        </Route>
      </Routes>
    </HashRouter>
  )
}

export default App
