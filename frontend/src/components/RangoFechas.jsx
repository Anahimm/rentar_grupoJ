import { useRef } from 'react';
import DatePicker, { registerLocale } from 'react-datepicker';
import { es } from 'date-fns/locale';
import 'react-datepicker/dist/react-datepicker.css';

registerLocale('es', es);

// Selector de período (retiro -> devolución). Al terminar de elegir el inicio se abre
// automáticamente el calendario de fin, y ambos muestran el rango marcado.
const RangoFechas = ({ desde, hasta, onChange, soloFuturas = false, requerido = false,
                       etiquetaDesde = 'Desde', etiquetaHasta = 'Hasta' }) => {
    const finRef = useRef(null);
    const minimo = soloFuturas ? new Date() : null;

    const cambiarDesde = (fecha) => {
        // Si el fin quedó antes del nuevo inicio se borra para volver a elegirlo
        onChange({ desde: fecha, hasta: hasta && fecha && hasta <= fecha ? null : hasta });
    };

    const alCerrarDesde = () => {
        if (desde && !hasta) {
            // Se espera a que termine de cerrarse el primer calendario antes de abrir el segundo
            setTimeout(() => finRef.current?.setOpen(true), 0);
        }
    };

    // Horarios permitidos: no antes del mínimo (ahora) ni, para el fin, antes del inicio
    const horaValidaDesde = (hora) => !minimo || hora > minimo;
    const horaValidaHasta = (hora) => (!desde || hora > desde) && horaValidaDesde(hora);

    const comunes = {
        locale: 'es',
        showTimeSelect: true,
        timeIntervals: 30,
        timeCaption: 'Hora',
        dateFormat: 'dd/MM/yyyy HH:mm',
        className: 'form-control',
        wrapperClassName: 'w-100',
        startDate: desde,
        endDate: hasta,
        required: requerido,
        isClearable: !requerido,
        autoComplete: 'off'
    };

    return (
        <>
            <div className="col-md-6">
                <label className="form-label">{etiquetaDesde}</label>
                <DatePicker {...comunes}
                    selected={desde}
                    onChange={cambiarDesde}
                    onCalendarClose={alCerrarDesde}
                    selectsStart
                    minDate={minimo}
                    filterTime={horaValidaDesde}
                    placeholderText="Elegí día y hora" />
            </div>
            <div className="col-md-6">
                <label className="form-label">{etiquetaHasta}</label>
                <DatePicker {...comunes}
                    ref={finRef}
                    selected={hasta}
                    onChange={(fecha) => onChange({ desde, hasta: fecha })}
                    selectsEnd
                    minDate={desde || minimo}
                    openToDate={hasta || desde || undefined}
                    filterTime={horaValidaHasta}
                    placeholderText={desde ? 'Elegí día y hora' : 'Primero elegí el inicio'} />
            </div>
        </>
    );
};

export default RangoFechas;
