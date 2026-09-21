import React, { useState, useEffect } from 'react';

const Clientes = () => {
    const [clientes, setClientes] = useState([]);
    const [mensaje, setMensaje] = useState({ texto: '', tipo: '' });
    const [formData, setFormData] = useState({
        documento: '', nombre: '', apellido: '', email: '', telefono: '', fecha_nacimiento: ''
    });

    const cargarClientes = () => {
        fetch('http://localhost:8000/clientes/')
            .then(res => res.json())
            .then(data => setClientes(data))
            .catch(err => console.error("Error al cargar clientes:", err));
    };

    useEffect(() => {
        cargarClientes();
    }, []);

    const handleSubmit = (e) => {
        e.preventDefault();
        setMensaje({ texto: '', tipo: '' });

        const payload = {
            ...formData,
            telefono: formData.telefono || null,
            fecha_nacimiento: formData.fecha_nacimiento || null
        };

        fetch('http://localhost:8000/clientes/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        })
        .then(async res => {
            const data = await res.json();
            if (!res.ok) {
                setMensaje({ texto: data.detail || 'Error al registrar cliente', tipo: 'danger' });
            } else {
                setMensaje({ texto: 'Cliente registrado exitosamente', tipo: 'success' });
                setFormData({ documento: '', nombre: '', apellido: '', email: '', telefono: '', fecha_nacimiento: '' });
                cargarClientes();
            }
        })
        .catch(() => setMensaje({ texto: 'Error de conexión con el servidor', tipo: 'danger' }));
    };

    const handleBaja = (id) => {
        if (!window.confirm('¿Confirmás dar de baja a este cliente?')) return;
        fetch(`http://localhost:8000/clientes/${id}`, { method: 'DELETE' })
            .then(() => cargarClientes());
    };

    return (
        <div>
            <h2 className="mb-4">Gestión de Clientes</h2>

            {mensaje.texto && (
                <div className={`alert alert-${mensaje.tipo}`} role="alert">
                    {mensaje.texto}
                </div>
            )}

            <form onSubmit={handleSubmit} className="mb-5 p-4 border rounded bg-light">
                <h4>Nuevo Cliente</h4>
                <div className="row g-3">
                    <div className="col-md-4">
                        <input className="form-control" type="text" placeholder="Documento (DNI/Pasaporte)"
                            value={formData.documento} onChange={e => setFormData({ ...formData, documento: e.target.value })} required />
                    </div>
                    <div className="col-md-4">
                        <input className="form-control" type="text" placeholder="Nombre"
                            value={formData.nombre} onChange={e => setFormData({ ...formData, nombre: e.target.value })} required />
                    </div>
                    <div className="col-md-4">
                        <input className="form-control" type="text" placeholder="Apellido"
                            value={formData.apellido} onChange={e => setFormData({ ...formData, apellido: e.target.value })} required />
                    </div>
                    <div className="col-md-4">
                        <input className="form-control" type="email" placeholder="Email"
                            value={formData.email} onChange={e => setFormData({ ...formData, email: e.target.value })} required />
                    </div>
                    <div className="col-md-4">
                        <input className="form-control" type="text" placeholder="Teléfono"
                            value={formData.telefono} onChange={e => setFormData({ ...formData, telefono: e.target.value })} />
                    </div>
                    <div className="col-md-4">
                        <input className="form-control" type="date" placeholder="Fecha Nacimiento"
                            value={formData.fecha_nacimiento} onChange={e => setFormData({ ...formData, fecha_nacimiento: e.target.value })} />
                    </div>
                    <div className="col-12 text-end">
                        <button type="submit" className="btn btn-primary px-4">Guardar Cliente</button>
                    </div>
                </div>
            </form>

            <table className="table table-striped table-hover">
                <thead className="table-dark">
                    <tr>
                        <th>ID</th><th>Documento</th><th>Nombre y Apellido</th><th>Email</th><th>Teléfono</th><th>Estado</th><th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    {clientes.length === 0 ? (
                        <tr><td colSpan="7" className="text-center text-muted py-3">No hay clientes registrados</td></tr>
                    ) : (
                        clientes.map(c => (
                            <tr key={c.id}>
                                <td>{c.id}</td>
                                <td>{c.documento}</td>
                                <td>{c.nombre} {c.apellido}</td>
                                <td>{c.email}</td>
                                <td>{c.telefono || '-'}</td>
                                <td>{c.activo ? <span className="badge bg-success">Activo</span> : <span className="badge bg-danger">Inactivo</span>}</td>
                                <td>
                                    {c.activo && (
                                        <button className="btn btn-sm btn-danger" onClick={() => handleBaja(c.id)}>Dar de baja</button>
                                    )}
                                </td>
                            </tr>
                        ))
                    )}
                </tbody>
            </table>
        </div>
    );
};

export default Clientes;