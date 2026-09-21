import { useState } from 'react';

export default function BuscadorDisponibilidad() {
    const [vehiculos, setVehiculos] = useState([]);
    const [marca, setMarca] = useState('');
    const [precioMaximo, setPrecioMaximo] = useState('');

    const buscarDisponibilidad = async (e) => {
        e.preventDefault();

        // Consulta GraphQL dinámica según los inputs
        const query = `
        query {
            consultarDisponibilidad(
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

            {/* Formulario de Filtros */}
            <form onSubmit={buscarDisponibilidad} className="row g-3 mb-4">
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

            {/* Tabla de Resultados */}
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