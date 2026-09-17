import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';

// Importación de tus pantallas
import Vehiculos from './pages/Vehiculos';
import BuscadorDisponibilidad from './pages/BuscadorDisponibilidad';

export default function App() {
  return (
    <Router>
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
                <Link className="nav-link" to="/">Flota (ABM)</Link>
              </li>
              <li className="nav-item">
                <Link className="nav-link" to="/buscar">Buscar Disponibilidad</Link>
              </li>
              {/* Acá van los Links a Clientes y Reservas */}
            </ul>
          </div>
        </div>
      </nav>

      {/* Contenedor dinámico donde se cargan las pantallas */}
      <div className="container">
        <Routes>
          {/* Tu Dominio: Vehículos */}
          <Route path="/" element={<Vehiculos />} />
          <Route path="/buscar" element={<BuscadorDisponibilidad />} />

          {/* Dominio Clientes - Comentado hasta que lo armen */}
          {/* <Route path="/clientes" element={<Clientes />} /> */}

          {/* Dominio Reservas - Comentado hasta que lo armen */}
          {/* <Route path="/reservas" element={<Reservas />} /> */}
        </Routes>
      </div>
    </Router>
  );
}