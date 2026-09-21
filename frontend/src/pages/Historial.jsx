import React, { useState } from 'react';

const Historial = () => {
    const [clienteId, setClienteId] = useState('');
    const [historial, setHistorial] = useState([]);
    const [consultado, setConsultado] = useState(false);
    const [loading, setLoading] = useState(false);

    const consultarHistorial = (e) => {
        e.preventDefault();
        if (!clienteId) return;

        setLoading(true);
        setConsultado(true);

        const query = `
            query {
                historialAlquileres(clienteId: ${clienteId}) {
                    id
                    vehiculoMarca
                    vehiculoModelo
                    vehiculoPatente
                    fechaInicio
                    fechaFin
                    estado
                    dias
                    importe
                }
            }
        `;

        fetch('http://localhost:8000/graphql', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        })
        .then(res => res.json())
        .then(resData => {
            setHistorial(resData.data?.historialAlquileres || []);
        })
        .catch(err => console.error("Error al consultar GraphQL:", err))
        .finally(() => setLoading(false));
    };

    return (
        <div>
            <h2 className="mb-4">Historial de Alquileres (GraphQL)</h2>

            <form onSubmit={consultarHistorial} className="mb-5 p-4 border rounded bg-light">
                <h4>Consultar Historial por Cliente</h4>
                <div className="row g-3 align-items-end">
                    <div className="col-md-4">
                        <label className="form-label">ID del Cliente</label>
                        <input className="form-control" type="number" placeholder="Ej: 1"
                            value={clienteId} onChange={e => setClienteId(e.target.value)} required />
                    </div>
                    <div className="col-md-3">
                        <button type="submit" className="btn btn-primary w-100" disabled={loading}>
                            {loading ? 'Consultando...' : 'Buscar Historial'}
                        </button>
                    </div>
                </div>
            </form>

            {consultado && (
                <table className="table table-striped table-hover">
                    <thead className="table-dark">
                        <tr>
                            <th>ID Alquiler</th><th>Vehículo</th><th>Patente</th><th>Fecha Inicio</th><th>Fecha Fin</th><th>Días</th><th>Importe</th><th>Estado</th>
                        </tr>
                    </thead>
                    <tbody>
                        {historial.length === 0 ? (
                            <tr><td colSpan="8" className="text-center text-muted py-3">No registra alquileres finalizados o cancelados</td></tr>
                        ) : (
                            historial.map(h => (
                                <tr key={h.id}>
                                    <td>{h.id}</td>
                                    <td>{h.vehiculoMarca} {h.vehiculoModelo}</td>
                                    <td>{h.vehiculoPatente}</td>
                                    <td>{h.fechaInicio}</td>
                                    <td>{h.fechaFin}</td>
                                    <td>{h.dias}</td>
                                    <td>${h.importe}</td>
                                    <td>
                                        <span className={`badge ${h.estado === 'FINALIZADO' ? 'bg-secondary' : 'bg-warning text-dark'}`}>
                                            {h.estado}
                                        </span>
                                    </td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            )}
        </div>
    );
};

export default Historial;