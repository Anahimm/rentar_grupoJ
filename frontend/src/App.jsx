import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Vehiculos from './pages/Vehiculos';

function App() {
  return (
    <BrowserRouter>
      {/* Contenedor principal de Bootstrap */}
      <div className="container mt-5">
        <Routes>
          {/* Redirige a la pantalla de Vehiculos */}
          <Route path="/" element={<Navigate to="/vehiculos" replace />} />
          <Route path="/vehiculos" element={<Vehiculos />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App