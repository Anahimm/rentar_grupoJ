import { useState } from 'react';
import DatePicker, { registerLocale } from 'react-datepicker';
import es from 'date-fns/locale/es';
import "react-datepicker/dist/react-datepicker.css";
registerLocale('es', es);

export default function BuscadorDisponibilidad() {
    const [vehiculos, setVehiculos] = useState([]);
    const [marca, setMarca] = useState('');
    const [precioMaximo, setPrecioMaximo] = useState('');
    
    // Ahora los estados inicializan en null porque van a guardar objetos Date
    const [fechaDesde, setFechaDesde] = useState(null);
    const [fechaHasta, setFechaHasta] = useState(null);

    const buscarDisponibilidad = async (e) => {
        e.preventDefault();

        if (!fechaDesde || !fechaHasta) {
            alert("Por favor, seleccioná la fecha de retiro y devolución.");
            return;
        }

        // Convertimos el objeto Date a formato ISO (texto) para que GraphQL lo entienda
        const query = `
        query {
            consultarDisponibilidad(
            fechaDesde: "${fechaDesde.toISOString()}"
            fechaHasta: "${fechaHasta.toISOString()}"
            ${marca ? `marca: "${marca}"` : ""}
            ${precioMaximo ? `precioMaximo: ${precioMaximo}` : ""}
            ) {
            patente
            marca
            modelo
            tipoVehiculo
            precioDiario
            }
        }
    `;

        try {
            const response = await fetch('http://localhost:8000/graphql', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });
            const result = await response.json();
            setVehiculos(result.data.consultarDisponibilidad);
        } catch (error) {
            console.error("Error consultando a GraphQL:", error);
        }
    };

    return (
        <div className="container mt-4">
            <h2>Buscar Vehículos Disponibles</h2>

            <form onSubmit={buscarDisponibilidad} className="row g-3 mb-4 align-items-end">
                <div className="col-auto">
                    <label className="form-label mb-1" style={{fontSize: '0.85rem', color: '#6c757d'}}>Retiro (fecha y hora) *</label>
                    <DatePicker
                        selected={fechaDesde}
                        onChange={(date) => setFechaDesde(date)}
                        showTimeSelect
                        timeFormat="HH:mm"
                        timeIntervals={30}
                        timeCaption="Hora"
                        dateFormat="dd/MM/yyyy HH:mm"
                        locale="es"
                        className="form-control"
                        placeholderText="Elegí día y hora"
                        required
                    />
                </div>
                <div className="col-auto">
                    <label className="form-label mb-1" style={{fontSize: '0.85rem', color: '#6c757d'}}>Devolución (fecha y hora) *</label>
                    <DatePicker
                        selected={fechaHasta}
                        onChange={(date) => setFechaHasta(date)}
                        showTimeSelect
                        timeFormat="HH:mm"
                        timeIntervals={30}
                        timeCaption="Hora"
                        dateFormat="dd/MM/yyyy HH:mm"
                        locale="es"
                        className="form-control"
                        placeholderText="Elegí día y hora"
                        required
                    />
                </div>

                <div className="col-auto">
                    <input
                        type="text"
                        className="form-control"
                        placeholder="Marca (ej. Toyota)"
                        value={marca}
                        onChange={(e) => setMarca(e.target.value)}
                    />
                </div>
                <div className="col-auto">
                    <input
                        type="number"
                        className="form-control"
                        placeholder="Precio máximo"
                        value={precioMaximo}
                        onChange={(e) => setPrecioMaximo(e.target.value)}
                    />
                </div>
                <div className="col-auto">
                    <button type="submit" className="btn btn-primary">Buscar</button>
                </div>
            </form>

            <table className="table table-striped">
                <thead>
                    <tr>
                        <th>Marca</th>
                        <th>Modelo</th>
                        <th>Tipo</th>
                        <th>Precio Diario</th>
                    </tr>
                </thead>
                <tbody>
                    {vehiculos.map((v) => (
                        <tr key={v.patente}>
                            <td>{v.marca}</td>
                            <td>{v.modelo}</td>
                            <td>{v.tipoVehiculo}</td>
                            <td>${v.precioDiario}</td>
                        </tr>
                    ))}
                    {vehiculos.length === 0 && (
                        <tr>
                            <td colSpan="4" className="text-center">No hay vehículos para mostrar</td>
                        </tr>
                    )}
                </tbody>
            </table>
        </div>
    );
}