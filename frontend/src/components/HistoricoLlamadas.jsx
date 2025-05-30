import React, { useState, useEffect, useCallback } from 'react';
import HistoricoLlamadasTable from './HistoricoLlamadasTable';
import HistoricoFilters from './HistoricoFilters';
import LlamadaDetalle from './LlamadaDetalle';
import SpinnerLoading from './SpinnerLoading';
import { obtenerHistoricoLlamadas, exportarHistoricoCSV } from '../services/llamadasService';

/**
 * Componente principal para página de historial de llamadas
 * 
 * @returns {JSX.Element} Componente JSX
 */
const HistoricoLlamadas = () => {
  // Estados para almacenar datos y estado de la UI
  const [llamadas, setLlamadas] = useState([]);
  const [totalItems, setTotalItems] = useState(0);
  const [totalPages, setTotalPages] = useState(1);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize] = useState(10);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [isExporting, setIsExporting] = useState(false);
  
  // Estados para modal de detalles
  const [selectedLlamadaId, setSelectedLlamadaId] = useState(null);
  const [detailModalOpen, setDetailModalOpen] = useState(false);
  
  // Estados para filtros
  const [filters, setFilters] = useState({
    estados: [],
    resultados: [],
    usuario: '',
    fecha_inicio: '',
    fecha_fin: ''
  });
  
  // Lista de usuarios para el filtro
  const [usuarios, setUsuarios] = useState([]);
  
  // Preparar parámetros de filtro para la API
  const prepareApiFilters = useCallback(() => {
    const apiFilters = {};
    
    if (filters.estados && filters.estados.length > 0) {
      apiFilters.estados = filters.estados.join(',');
    }
    
    if (filters.resultados && filters.resultados.length > 0) {
      apiFilters.resultados = filters.resultados.join(',');
    }
    
    if (filters.usuario) {
      apiFilters.usuario = filters.usuario;
    }
    
    if (filters.fecha_inicio) {
      apiFilters.fecha_inicio = filters.fecha_inicio;
    }
    
    if (filters.fecha_fin) {
      apiFilters.fecha_fin = filters.fecha_fin;
    }
    
    return apiFilters;
  }, [filters]);
  
  // Cargar datos de la API
  const cargarHistorico = useCallback(async () => {
    setLoading(true);
    try {
      const apiFilters = prepareApiFilters();
      const data = await obtenerHistoricoLlamadas(apiFilters, currentPage, pageSize);
      
      setLlamadas(data.llamadas || []);
      setTotalItems(data.total || 0);
      setTotalPages(Math.ceil((data.total || 0) / pageSize));
      
      // Extraer lista de usuarios únicos para el filtro
      if (data.usuarios && !usuarios.length) {
        const usuariosOptions = data.usuarios.map(usuario => ({
          value: usuario.email,
          label: usuario.nombre ? `${usuario.nombre} (${usuario.email})` : usuario.email
        }));
        setUsuarios(usuariosOptions);
      }
      
      setError(null);
    } catch (err) {
      console.error('Error al obtener historial de llamadas:', err);
      setError('Error al cargar historial de llamadas. Por favor, intentá nuevamente.');
    } finally {
      setLoading(false);
    }
  }, [currentPage, pageSize, prepareApiFilters, usuarios.length]);
  
  // Efecto para cargar datos cuando la página o filtros cambien
  useEffect(() => {
    cargarHistorico();
  }, [cargarHistorico, currentPage, filters]);
  
  // Handler para cambio de página
  const handlePageChange = (newPage) => {
    setCurrentPage(newPage);
  };
  
  // Handler para abrir modal de detalles
  const handleViewDetails = (llamadaId) => {
    setSelectedLlamadaId(llamadaId);
    setDetailModalOpen(true);
  };
  
  // Handler para cerrar modal de detalles
  const handleCloseDetails = () => {
    setDetailModalOpen(false);
  };
  
  // Exportar datos a CSV
  const handleExportCSV = async () => {
    setIsExporting(true);
    try {
      const apiFilters = prepareApiFilters();
      const blob = await exportarHistoricoCSV(apiFilters);
      
      // Crear URL para descarga
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.style.display = 'none';
      a.href = url;
      
      // Nombre del archivo con fecha actual
      const date = new Date().toISOString().split('T')[0];
      a.download = `historial-llamadas-${date}.csv`;
      
      // Activar descarga y limpiar
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err) {
      console.error('Error al exportar CSV:', err);
      alert('Error al exportar datos a CSV. Por favor, intentá nuevamente.');
    } finally {
      setIsExporting(false);
    }
  };
  
  // Resetear filtros
  const handleResetFilters = () => {
    setFilters({
      estados: [],
      resultados: [],
      usuario: '',
      fecha_inicio: '',
      fecha_fin: ''
    });
    setCurrentPage(1);
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex flex-col space-y-4">
        <div>
          <h1 className="text-2xl font-bold text-white mb-6">Historial de Llamadas</h1>
          
          <HistoricoFilters
            filters={filters}
            setFilters={setFilters}
            usuarios={usuarios}
            onExportCSV={handleExportCSV}
            isExporting={isExporting}
            onReset={handleResetFilters}
          />
        </div>
        
        {loading ? (
          <div className="flex justify-center py-12">
            <SpinnerLoading isLoading={true} />
          </div>
        ) : error ? (
          <div className="bg-red-900 text-white p-4 rounded-lg">
            {error}
          </div>
        ) : (
          <HistoricoLlamadasTable
            llamadas={llamadas}
            totalItems={totalItems}
            page={currentPage}
            totalPages={totalPages}
            onChangePage={handlePageChange}
            onViewDetails={handleViewDetails}
          />
        )}
      </div>
      
      <LlamadaDetalle
        llamadaId={selectedLlamadaId}
        isOpen={detailModalOpen}
        onClose={handleCloseDetails}
      />
    </div>
  );
};

export default HistoricoLlamadas; 