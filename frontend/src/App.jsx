import { BrowserRouter, Routes, Route, Link, Navigate } from 'react-router-dom';
import Vehiculos from './pages/Vehiculos';
import Clientes from './pages/Clientes';
import Historial from './pages/Historial';

function App() {
  return (
    <BrowserRouter>
      {/* Barra de navegación común */}
      <nav className="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
        <div className="container">
          <span className="navbar-brand fw-bold">Rentar - Grupo J</span>
          <div className="navbar-nav">
            <Link className="nav-link" to="/vehiculos">Vehículos</Link>
            <Link className="nav-link" to="/clientes">Clientes</Link>
            <Link className="nav-link" to="/historial">Historial (GraphQL)</Link>
          </div>
        </div>
      </nav>

      {/* Contenedor principal de Bootstrap */}
      <div className="container">
        <Routes>
          <Route path="/" element={<Navigate to="/vehiculos" replace />} />
          <Route path="/vehiculos" element={<Vehiculos />} />
          <Route path="/clientes" element={<Clientes />} />
          <Route path="/historial" element={<Historial />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;