import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { format } from 'date-fns';
import RangoFechas from '../components/RangoFechas';

const FORM_VACIO = { cliente_id: '', vehiculo_id: '', fecha_inicio: null, fecha_fin: null };

// Fecha local sin zona horaria, que es lo que espera el backend
const aTextoLocal = (fecha) => format(fecha, "yyyy-MM-dd'T'HH:mm:ss");

// Mismo criterio que el backend: se cobra por día iniciado, mínimo 1
const calcularDias = (inicio, fin) => {
    const horas = (fin - inicio) / 36e5;
    return Math.max(1, Math.ceil(horas / 24));
};

const NuevaReserva = () => {
    const [clientes, setClientes] = useState([]);
    const [vehiculos, setVehiculos] = useState([]);
    const [formData, setFormData] = useState(FORM_VACIO);
    const [mensaje, setMensaje] = useState({ texto: '', tipo: '' });
    const [enviando, setEnviando] = useState(false);

    useEffect(() => {
        // Solo clientes y vehículos activos pueden usarse en una reserva
        fetch('http://localhost:8000/clientes/')
            .then(res => res.json())
            .then(data => setClientes(data.filter(c => c.activo)))
            .catch(err => console.error("Error al cargar clientes:", err));
        fetch('http://localhost:8000/vehiculos/')
            .then(res => res.json())
            .then(data => setVehiculos(data.filter(v => v.activo)))
            .catch(err => console.error("Error al cargar vehículos:", err));
    }, []);

    const vehiculo = vehiculos.find(v => v.id === parseInt(formData.vehiculo_id));
    const fechasValidas = formData.fecha_inicio && formData.fecha_fin && formData.fecha_fin > formData.fecha_inicio;
    const dias = fechasValidas ? calcularDias(formData.fecha_inicio, formData.fecha_fin) : null;

    const handleSubmit = (e) => {
        e.preventDefault();
        setMensaje({ texto: '', tipo: '' });
        setEnviando(true);

        const payload = {
            cliente_id: parseInt(formData.cliente_id),
            vehiculo_id: parseInt(formData.vehiculo_id),
            fecha_inicio: aTextoLocal(formData.fecha_inicio),
            fecha_fin: aTextoLocal(formData.fecha_fin)
        };

        fetch('http://localhost:8000/reservas/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(async res => {
            const data = await res.json();
            if (!res.ok) {
                // FastAPI devuelve un string en errores de negocio y una lista en errores de validación
                const detalle = typeof data.detail === 'string' ? data.detail : 'Datos inválidos';
                setMensaje({ texto: detalle, tipo: 'danger' });
            } else {
                setMensaje({
                    texto: `Reserva #${data.id} ${data.estado}. Importe total: $${data.importe_total}`,
                    tipo: 'success'
                });
                setFormData(FORM_VACIO);
            }
        })
        .catch(() => setMensaje({ texto: 'Error de conexión con el servidor', tipo: 'danger' }))
        .finally(() => setEnviando(false));
    };

    return (
        <div>
            <h2 className="mb-4">Nueva Reserva</h2>

            {mensaje.texto && (
                <div className={`alert alert-${mensaje.tipo}`} role="alert">
                    {mensaje.texto}
                    {mensaje.tipo === 'success' && <> — <Link to="/reservas">Ver reservas</Link></>}
                </div>
            )}

            <form onSubmit={handleSubmit} className="mb-5 p-4 border rounded bg-light">
                <div className="row g-3">
                    <div className="col-md-6">
                        <label className="form-label">Cliente</label>
                        <select className="form-select" value={formData.cliente_id}
                            onChange={e => setFormData({ ...formData, cliente_id: e.target.value })} required>
                            <option value="">Seleccioná un cliente</option>
                            {clientes.map(c => (
                                <option key={c.id} value={c.id}>{c.nombre} {c.apellido} ({c.documento})</option>
                            ))}
                        </select>
                    </div>
                    <div className="col-md-6">
                        <label className="form-label">Vehículo</label>
                        <select className="form-select" value={formData.vehiculo_id}
                            onChange={e => setFormData({ ...formData, vehiculo_id: e.target.value })} required>
                            <option value="">Seleccioná un vehículo</option>
                            {vehiculos.map(v => (
                                <option key={v.id} value={v.id}>
                                    {v.marca} {v.modelo} - {v.patente} (${v.precio_diario}/día)
                                </option>
                            ))}
                        </select>
                    </div>

                    <RangoFechas
                        desde={formData.fecha_inicio}
                        hasta={formData.fecha_fin}
                        onChange={({ desde, hasta }) => setFormData({ ...formData, fecha_inicio: desde, fecha_fin: hasta })}
                        soloFuturas
                        requerido
                        etiquetaDesde="Retiro (fecha y hora)"
                        etiquetaHasta="Devolución (fecha y hora)" />

                    <div className="col-md-8">
                        {vehiculo && dias && (
                            <div className="text-muted">
                                {dias} día(s) x ${vehiculo.precio_diario} = <strong>${(dias * vehiculo.precio_diario).toFixed(2)}</strong> (estimado)
                            </div>
                        )}
                    </div>
                    <div className="col-md-4 text-end">
                        <button type="submit" className="btn btn-primary px-4" disabled={enviando}>
                            {enviando ? 'Reservando...' : 'Confirmar Reserva'}
                        </button>
                    </div>
                </div>
            </form>
        </div>
    );
};

export default NuevaReserva;
