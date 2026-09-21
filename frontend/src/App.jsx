import { BrowserRouter, Routes, Route, Link, Navigate } from 'react-router-dom';
import Vehiculos from './pages/Vehiculos';
import Clientes from './pages/Clientes';
import Historial from './pages/Historial';
import BuscadorDisponibilidad from './pages/BuscadorDisponibilidad';

export default function App() {
  return (
    <BrowserRouter>
      {/* Barra de Navegación Bootstrap */}
      <nav className="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
        <div className="container">
          <Link className="navbar-brand" to="/">🚗 Rentar (Grupo J)</Link>

          <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
            <span className="navbar-toggler-icon"></span>
          </button>

          <div className="collapse navbar-collapse" id="navbarNav">
            <ul className="navbar-nav me-auto">
              <li className="nav-item">
                <Link className="nav-link" to="/vehiculos">Flota (ABM)</Link>
              </li>
              <li className="nav-item">
                <Link className="nav-link" to="/buscar">Buscar Disponibilidad</Link>
              </li>
              <li className="nav-item">
                <Link className="nav-link" to="/clientes">Clientes</Link>
              </li>
              <li className="nav-item">
                <Link className="nav-link" to="/historial">Historial</Link>
              </li>
            </ul>
          </div>
        </div>
      </nav>

      {/* Contenedor dinámico donde se cargan las pantallas */}
      <div className="container">
        <Routes>
          <Route path="/" element={<Navigate to="/vehiculos" replace />} />
          {/* Dominio Anahi */}
          <Route path="/vehiculos" element={<Vehiculos />} />
          <Route path="/buscar" element={<BuscadorDisponibilidad />} />

          {/* Dominio Marcos */}
          <Route path="/clientes" element={<Clientes />} />
          <Route path="/historial" element={<Historial />} />
        </Routes>
      </div>
    </BrowserRouter>
  );
}


