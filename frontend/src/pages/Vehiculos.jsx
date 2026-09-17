import React, { useState, useEffect } from 'react';

const Vehiculos = () => {
    const [vehiculos, setVehiculos] = useState([]);
    const [modoEdicion, setModoEdicion] = useState(false);
    const [formData, setFormData] = useState({
        patente: '', marca: '', modelo: '', anio: '', color: '', tipo_vehiculo: 'SEDAN', precio_diario: ''
    });

    const cargarVehiculos = () => {
        fetch('http://localhost:8000/vehiculos/')
            .then(res => res.json())
            .then(data => setVehiculos(data))
            .catch(err => console.error("Error al cargar:", err));
    };

    useEffect(() => {
        cargarVehiculos();
    }, []);

    const handleSubmit = (e) => {
        e.preventDefault();
        // Para la edición (PUT) hay que armar el endpoint en FastAPI, por ahora solo está el POST listo
        fetch('http://localhost:8000/vehiculos/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        }).then(() => {
            cargarVehiculos(); // Recarga la tabla
            setFormData({ patente: '', marca: '', modelo: '', anio: '', color: '', tipo_vehiculo: 'SEDAN', precio_diario: '' });
        });
    };

    const handleBaja = (id) => {
        fetch(`http://localhost:8000/vehiculos/${id}`, { method: 'DELETE' })
            .then(() => cargarVehiculos());
    };

    return (
        <div>
            <h2 className="mb-4">Flota de Vehículos</h2>

            <form onSubmit={handleSubmit} className="mb-5 p-4 border rounded bg-light">
                <h4>{modoEdicion ? 'Editar Vehículo' : 'Nuevo Vehículo'}</h4>
                <div className="row g-3">
                    <div className="col-md-3">
                        <input className="form-control" type="text" placeholder="Patente" disabled={modoEdicion}
                            value={formData.patente} onChange={e => setFormData({ ...formData, patente: e.target.value })} required />
                    </div>
                    <div className="col-md-3">
                        <input className="form-control" type="text" placeholder="Marca"
                            value={formData.marca} onChange={e => setFormData({ ...formData, marca: e.target.value })} required />
                    </div>
                    <div className="col-md-3">
                        <input className="form-control" type="text" placeholder="Modelo"
                            value={formData.modelo} onChange={e => setFormData({ ...formData, modelo: e.target.value })} required />
                    </div>
                    <div className="col-md-3">
                        <input className="form-control" type="number" placeholder="Año"
                            value={formData.anio} onChange={e => setFormData({ ...formData, anio: parseInt(e.target.value) })} required />
                    </div>
                    <div className="col-md-3">
                        <input className="form-control" type="text" placeholder="Color"
                            value={formData.color} onChange={e => setFormData({ ...formData, color: e.target.value })} />
                    </div>
                    <div className="col-md-3">
                        <select className="form-select" value={formData.tipo_vehiculo} onChange={e => setFormData({ ...formData, tipo_vehiculo: e.target.value })}>
                            <option value="SEDAN">SEDAN</option>
                            <option value="SUV">SUV</option>
                            <option value="PICKUP">PICKUP</option>
                            <option value="COUPE">COUPE</option>
                            <option value="HATCHBACK">HATCHBACK</option>
                        </select>
                    </div>
                    <div className="col-md-3">
                        <input className="form-control" type="number" step="0.01" placeholder="Precio Diario ($)"
                            value={formData.precio_diario} onChange={e => setFormData({ ...formData, precio_diario: parseFloat(e.target.value) })} required />
                    </div>
                    <div className="col-md-3">
                        <button type="submit" className="btn btn-primary w-100">Guardar</button>
                    </div>
                </div>
            </form>

            <table className="table table-striped table-hover">
                <thead className="table-dark">
                    <tr>
                        <th>Patente</th><th>Marca</th><th>Modelo</th><th>Año</th><th>Tipo</th><th>Precio</th><th>Estado</th><th>Activo</th><th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    {vehiculos.map(v => (
                        <tr key={v.id}>
                            <td>{v.patente}</td><td>{v.marca}</td><td>{v.modelo}</td><td>{v.anio}</td>
                            <td>{v.tipo_vehiculo}</td><td>${v.precio_diario}</td><td>{v.estado}</td>
                            <td>{v.activo ? 'Sí' : 'No'}</td>
                            <td>
                                <button className="btn btn-sm btn-danger" onClick={() => handleBaja(v.id)}>Dar de baja</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default Vehiculos;