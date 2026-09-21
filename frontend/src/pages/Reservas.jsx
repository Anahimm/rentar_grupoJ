import { useState, useEffect } from 'react';
import { format } from 'date-fns';
import RangoFechas from '../components/RangoFechas';

const FILTROS_VACIOS = { clienteId: '', vehiculoId: '', tipoVehiculo: '', estado: '', fechaDesde: null, fechaHasta: null };

const QUERY_RESERVAS = `
    query Reservas($clienteId: Int, $vehiculoId: Int, $tipoVehiculo: String, $estado: String,
                   $fechaDesde: DateTime, $fechaHasta: DateTime) {
        reservas(clienteId: $clienteId, vehiculoId: $vehiculoId, tipoVehiculo: $tipoVehiculo,
                 estado: $estado, fechaDesde: $fechaDesde, fechaHasta: $fechaHasta) {
            id
            cliente
            vehiculo
            patente
            fechaInicio
            fechaFin
            precioDiario
            importeTotal
            estado
        }
    }
`;

// El sistema no tiene login: el rol y el cliente se envían en headers y el backend aplica la restricción
const headersDeRol = (rol, clienteActual) => ({
    'X-Rol': rol,
    ...(rol === 'CLIENTE' ? { 'X-Cliente-Id': clienteActual } : {})
});

const pedirReservas = (rol, clienteActual, filtros) => {
    // Los filtros vacíos se mandan como null para que GraphQL los ignore
    const variables = {
        clienteId: filtros.clienteId ? parseInt(filtros.clienteId) : null,
        vehiculoId: filtros.vehiculoId ? parseInt(filtros.vehiculoId) : null,
        tipoVehiculo: filtros.tipoVehiculo || null,
        estado: filtros.estado || null,
        fechaDesde: filtros.fechaDesde ? format(filtros.fechaDesde, "yyyy-MM-dd'T'HH:mm:ss") : null,
        fechaHasta: filtros.fechaHasta ? format(filtros.fechaHasta, "yyyy-MM-dd'T'HH:mm:ss") : null
    };

    return fetch('http://localhost:8000/graphql', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', ...headersDeRol(rol, clienteActual) },
        body: JSON.stringify({ query: QUERY_RESERVAS, variables })
    })
    .then(res => res.json())
    .then(resData => {
        if (resData.errors) throw new Error(resData.errors[0].message);
        return resData.data.reservas;
    });
};

const formatearFecha = (fecha) => new Date(fecha).toLocaleString('es-AR', { dateStyle: 'short', timeStyle: 'short' });

const Reservas = () => {
    const [rol, setRol] = useState('ADMIN');
    const [clienteActual, setClienteActual] = useState('');
    const [clientes, setClientes] = useState([]);
    const [vehiculos, setVehiculos] = useState([]);
    const [filtros, setFiltros] = useState(FILTROS_VACIOS);
    const [filtrosAplicados, setFiltrosAplicados] = useState(FILTROS_VACIOS);
    const [recarga, setRecarga] = useState(0);
    const [reservas, setReservas] = useState([]);
    const [mensaje, setMensaje] = useState({ texto: '', tipo: '' });

    const faltaCliente = rol === 'CLIENTE' && !clienteActual;

    useEffect(() => {
        fetch('http://localhost:8000/clientes/')
            .then(res => res.json())
            .then(data => setClientes(data))
            .catch(err => console.error("Error al cargar clientes:", err));
        fetch('http://localhost:8000/vehiculos/')
            .then(res => res.json())
            .then(data => setVehiculos(data))
            .catch(err => console.error("Error al cargar vehículos:", err));
    }, []);

    useEffect(() => {
        if (faltaCliente) return;
        pedirReservas(rol, clienteActual, filtrosAplicados)
            .then(data => setReservas(data))
            .catch(err => setMensaje({ texto: err.message, tipo: 'danger' }));
    }, [rol, clienteActual, filtrosAplicados, recarga, faltaCliente]);

    const handleBuscar = (e) => {
        e.preventDefault();
        setMensaje({ texto: '', tipo: '' });
        setFiltrosAplicados(filtros);
    };

    const handleLimpiar = () => {
        setFiltros(FILTROS_VACIOS);
        setFiltrosAplicados(FILTROS_VACIOS);
    };

    const handleCancelar = (id) => {
        if (!window.confirm('¿Confirmás cancelar esta reserva?')) return;
        setMensaje({ texto: '', tipo: '' });

        fetch(`http://localhost:8000/reservas/${id}/cancelar`, {
            method: 'PATCH',
            headers: headersDeRol(rol, clienteActual)
        })
        .then(async res => {
            const data = await res.json();
            if (!res.ok) {
                setMensaje({ texto: data.detail || 'No se pudo cancelar la reserva', tipo: 'danger' });
            } else {
                setMensaje({ texto: `Reserva #${id} cancelada`, tipo: 'success' });
                setRecarga(r => r + 1);
            }
        })
        .catch(() => setMensaje({ texto: 'Error de conexión con el servidor', tipo: 'danger' }));
    };

    const cancelable = (r) => r.estado === 'CONFIRMADA' && new Date(r.fechaInicio) > new Date();

    return (
        <div>
            <h2 className="mb-4">Reservas</h2>

            {/* Simulación de usuario: el administrador ve todas, el cliente solo las suyas */}
            <div className="row g-3 align-items-end mb-3">
                <div className="col-md-3">
                    <label className="form-label">Ver como</label>
                    <select className="form-select" value={rol} onChange={e => setRol(e.target.value)}>
                        <option value="ADMIN">Administrador</option>
                        <option value="CLIENTE">Cliente</option>
                    </select>
                </div>
                {rol === 'CLIENTE' && (
                    <div className="col-md-4">
                        <label className="form-label">Cliente</label>
                        <select className="form-select" value={clienteActual} onChange={e => setClienteActual(e.target.value)}>
                            <option value="">Seleccioná un cliente</option>
                            {clientes.map(c => (
                                <option key={c.id} value={c.id}>{c.nombre} {c.apellido} ({c.documento})</option>
                            ))}
                        </select>
                    </div>
                )}
            </div>

            <form onSubmit={handleBuscar} className="mb-4 p-4 border rounded bg-light">
                <h4>Filtros</h4>
                <div className="row g-3">
                    {rol === 'ADMIN' && (
                        <div className="col-md-4">
                            <select className="form-select" value={filtros.clienteId}
                                onChange={e => setFiltros({ ...filtros, clienteId: e.target.value })}>
                                <option value="">Todos los clientes</option>
                                {clientes.map(c => (
                                    <option key={c.id} value={c.id}>{c.nombre} {c.apellido}</option>
                                ))}
                            </select>
                        </div>
                    )}
                    <div className="col-md-4">
                        <select className="form-select" value={filtros.vehiculoId}
                            onChange={e => setFiltros({ ...filtros, vehiculoId: e.target.value })}>
                            <option value="">Todos los vehículos</option>
                            {vehiculos.map(v => (
                                <option key={v.id} value={v.id}>{v.marca} {v.modelo} - {v.patente}</option>
                            ))}
                        </select>
                    </div>
                    <div className="col-md-2">
                        <select className="form-select" value={filtros.tipoVehiculo}
                            onChange={e => setFiltros({ ...filtros, tipoVehiculo: e.target.value })}>
                            <option value="">Todos los tipos</option>
                            <option value="SEDAN">SEDAN</option>
                            <option value="SUV">SUV</option>
                            <option value="PICKUP">PICKUP</option>
                            <option value="COUPE">COUPE</option>
                            <option value="HATCHBACK">HATCHBACK</option>
                        </select>
                    </div>
                    <div className="col-md-2">
                        <select className="form-select" value={filtros.estado}
                            onChange={e => setFiltros({ ...filtros, estado: e.target.value })}>
                            <option value="">Todos los estados</option>
                            <option value="CONFIRMADA">CONFIRMADA</option>
                            <option value="CANCELADA">CANCELADA</option>
                        </select>
                    </div>
                    <RangoFechas
                        desde={filtros.fechaDesde}
                        hasta={filtros.fechaHasta}
                        onChange={({ desde, hasta }) => setFiltros({ ...filtros, fechaDesde: desde, fechaHasta: hasta })} />
                    <div className="col-12 d-flex justify-content-end gap-2">
                        <button type="button" className="btn btn-outline-secondary px-4" onClick={handleLimpiar}>Limpiar</button>
                        <button type="submit" className="btn btn-primary px-4">Buscar</button>
                    </div>
                </div>
            </form>

            {mensaje.texto && (
                <div className={`alert alert-${mensaje.tipo}`} role="alert">
                    {mensaje.texto}
                </div>
            )}

            {faltaCliente ? (
                <p className="text-muted">Seleccioná un cliente para ver sus reservas.</p>
            ) : (
                <table className="table table-striped table-hover">
                    <thead className="table-dark">
                        <tr>
                            <th>ID</th><th>Cliente</th><th>Vehículo</th><th>Patente</th><th>Inicio</th><th>Fin</th>
                            <th>Precio Diario</th><th>Importe Total</th><th>Estado</th><th>Acciones</th>
                        </tr>
                    </thead>
                    <tbody>
                        {reservas.length === 0 ? (
                            <tr><td colSpan="10" className="text-center text-muted py-3">No hay reservas para mostrar</td></tr>
                        ) : (
                            reservas.map(r => (
                                <tr key={r.id}>
                                    <td>{r.id}</td>
                                    <td>{r.cliente}</td>
                                    <td>{r.vehiculo}</td>
                                    <td>{r.patente}</td>
                                    <td>{formatearFecha(r.fechaInicio)}</td>
                                    <td>{formatearFecha(r.fechaFin)}</td>
                                    <td>${r.precioDiario}</td>
                                    <td>${r.importeTotal}</td>
                                    <td>
                                        <span className={`badge ${r.estado === 'CONFIRMADA' ? 'bg-success' : 'bg-secondary'}`}>
                                            {r.estado}
                                        </span>
                                    </td>
                                    <td>
                                        {cancelable(r) && (
                                            <button className="btn btn-sm btn-danger" onClick={() => handleCancelar(r.id)}>Cancelar</button>
                                        )}
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

export default Reservas;
