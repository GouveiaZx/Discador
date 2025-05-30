import React from 'react';
import PropTypes from 'prop-types';
import MultiSelect from './MultiSelect';
import DateRangePicker from './DateRangePicker';
import Select from './Select';

/**
 * Componente de filtros para historial de llamadas
 * 
 * @param {Object} props - Propiedades del componente
 * @returns {JSX.Element} Componente JSX
 */
const HistoricoFilters = ({ 
  filters, 
  setFilters,
  usuarios,
  onExportCSV,
  isExporting = false,
  onReset
}) => {
  // Opciones para filtro de estados
  const estadosOptions = [
    { value: 'en_progreso', label: 'En curso' },
    { value: 'pendiente', label: 'Pendiente' },
    { value: 'finalizada', label: 'Finalizada' }
  ];

  // Opciones para filtro de resultados
  const resultadosOptions = [
    { value: 'finalizada_exito', label: 'Finalizada con éxito' },
    { value: 'finalizada_por_admin', label: 'Finalizada por admin' },
    { value: 'ocupado', label: 'Ocupado' },
    { value: 'no_responde', label: 'No responde' },
    { value: 'error', label: 'Error' },
    { value: 'fallida', label: 'Fallida' }
  ];

  // Actualizar estado de los filtros
  const handleFilterChange = (name, value) => {
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Actualizar fechas
  const handleFechaInicioChange = (value) => {
    setFilters(prev => ({
      ...prev,
      fecha_inicio: value
    }));
  };

  const handleFechaFinChange = (value) => {
    setFilters(prev => ({
      ...prev,
      fecha_fin: value
    }));
  };

  // Exportar resultados a CSV
  const handleExport = () => {
    onExportCSV();
  };

  // Resetear todos los filtros
  const handleReset = () => {
    onReset();
  };

  return (
    <div className="bg-gray-800 p-4 rounded-lg shadow mb-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
        <div>
          <label htmlFor="estados" className="block text-sm font-medium text-gray-300 mb-1">
            Estado
          </label>
          <MultiSelect
            options={estadosOptions}
            selectedValues={filters.estados || []}
            onChange={(values) => handleFilterChange('estados', values)}
            placeholder="Todos los estados"
          />
        </div>
        
        <div>
          <label htmlFor="resultados" className="block text-sm font-medium text-gray-300 mb-1">
            Resultado
          </label>
          <MultiSelect
            options={resultadosOptions}
            selectedValues={filters.resultados || []}
            onChange={(values) => handleFilterChange('resultados', values)}
            placeholder="Todos los resultados"
          />
        </div>
        
        <div>
          <label htmlFor="usuario" className="block text-sm font-medium text-gray-300 mb-1">
            Usuario
          </label>
          <Select
            options={usuarios}
            value={filters.usuario || ''}
            onChange={(value) => handleFilterChange('usuario', value)}
            placeholder="Todos los usuarios"
          />
        </div>
        
        <div>
          <label htmlFor="fecha" className="block text-sm font-medium text-gray-300 mb-1">
            Período
          </label>
          <DateRangePicker
            startDate={filters.fecha_inicio || ''}
            endDate={filters.fecha_fin || ''}
            onChangeStartDate={handleFechaInicioChange}
            onChangeEndDate={handleFechaFinChange}
          />
        </div>
      </div>
      
      <div className="flex flex-col sm:flex-row justify-end space-y-2 sm:space-y-0 sm:space-x-2">
        <button
          onClick={handleReset}
          className="px-4 py-2 text-gray-300 border border-gray-600 rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
        >
          Limpiar filtros
        </button>
        
        <button
          onClick={handleExport}
          disabled={isExporting}
          className="px-4 py-2 bg-green-700 text-white rounded-md hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500 flex items-center justify-center"
        >
          {isExporting ? (
            <>
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Exportando...
            </>
          ) : (
            <>
              <svg className="-ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
              </svg>
              Exportar CSV
            </>
          )}
        </button>
      </div>
    </div>
  );
};

HistoricoFilters.propTypes = {
  filters: PropTypes.shape({
    estados: PropTypes.array,
    resultados: PropTypes.array,
    usuario: PropTypes.string,
    fecha_inicio: PropTypes.string,
    fecha_fin: PropTypes.string
  }).isRequired,
  setFilters: PropTypes.func.isRequired,
  usuarios: PropTypes.arrayOf(
    PropTypes.shape({
      value: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired
    })
  ).isRequired,
  onExportCSV: PropTypes.func.isRequired,
  isExporting: PropTypes.bool,
  onReset: PropTypes.func.isRequired
};

export default HistoricoFilters; 