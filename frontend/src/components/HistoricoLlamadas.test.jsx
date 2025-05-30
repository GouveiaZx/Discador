import React from 'react';
import { render, screen, act, waitFor, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import HistoricoLlamadas from './HistoricoLlamadas';
import { obtenerHistoricoLlamadas, exportarHistoricoCSV } from '../services/llamadasService';

// Mock dos serviços de chamadas
jest.mock('../services/llamadasService', () => ({
  obtenerHistoricoLlamadas: jest.fn(),
  exportarHistoricoCSV: jest.fn(),
  obtenerDetalleLlamada: jest.fn()
}));

// Mock dos componentes filhos para simplificar os testes
jest.mock('./HistoricoLlamadasTable', () => {
  return function MockTable({
    llamadas,
    totalItems,
    page,
    totalPages,
    onChangePage,
    onViewDetails
  }) {
    return (
      <div data-testid="historico-table">
        <span>Total: {totalItems}</span>
        <span>Página: {page} de {totalPages}</span>
        {llamadas.map(llamada => (
          <div key={llamada.id} data-testid={`llamada-${llamada.id}`}>
            <span>{llamada.numero_destino}</span>
            <button onClick={() => onViewDetails(llamada.id)}>Detalhes</button>
          </div>
        ))}
        <button data-testid="next-page" onClick={() => onChangePage(page + 1)}>
          Próxima
        </button>
      </div>
    );
  };
});

jest.mock('./HistoricoFilters', () => {
  return function MockFilters({
    filters,
    setFilters,
    onExportCSV,
    onReset
  }) {
    return (
      <div data-testid="historico-filters">
        <button 
          data-testid="export-button" 
          onClick={onExportCSV}
        >
          Exportar
        </button>
        <button 
          data-testid="reset-button" 
          onClick={onReset}
        >
          Resetar
        </button>
        <button 
          data-testid="filter-estado" 
          onClick={() => setFilters(prev => ({
            ...prev,
            estados: ['finalizada']
          }))}
        >
          Filtrar Estado
        </button>
      </div>
    );
  };
});

jest.mock('./LlamadaDetalle', () => {
  return function MockDetalhes({ llamadaId, isOpen, onClose }) {
    if (!isOpen) return null;
    return (
      <div data-testid="llamada-detalle-modal">
        <span>Detalhes da chamada ID: {llamadaId}</span>
        <button onClick={onClose}>Fechar</button>
      </div>
    );
  };
});

describe('HistoricoLlamadas', () => {
  const mockLlamadas = [
    {
      id: 123,
      numero_destino: '+5491112345678',
      usuario_email: 'usuario@test.com',
      fecha_asignacion: '2023-05-20T10:00:00',
      fecha_finalizacion: '2023-05-20T10:05:30',
      estado: 'finalizada',
      resultado: 'finalizada_exito'
    },
    {
      id: 124,
      numero_destino: '+5491187654321',
      usuario_email: 'otro@test.com',
      fecha_asignacion: '2023-05-20T11:00:00',
      fecha_finalizacion: '2023-05-20T11:03:45',
      estado: 'finalizada',
      resultado: 'ocupado'
    }
  ];
  
  const mockApiResponse = {
    llamadas: mockLlamadas,
    total: 2,
    usuarios: [
      { email: 'usuario@test.com', nombre: 'Usuario Test' },
      { email: 'otro@test.com', nombre: 'Otro Usuario' }
    ]
  };
  
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock de resposta da API
    obtenerHistoricoLlamadas.mockResolvedValue(mockApiResponse);
    
    // Mock para exportação CSV
    const mockBlob = new Blob(['dados,csv'], { type: 'text/csv' });
    exportarHistoricoCSV.mockResolvedValue(mockBlob);
    
    // Mock para createObjectURL
    window.URL.createObjectURL = jest.fn(() => 'mock-url');
    window.URL.revokeObjectURL = jest.fn();
  });
  
  test('carrega e exibe o histórico de chamadas', async () => {
    render(<HistoricoLlamadas />);
    
    // Verificar que a chamada à API foi feita
    expect(obtenerHistoricoLlamadas).toHaveBeenCalledTimes(1);
    
    // Esperar pelo carregamento dos dados
    await waitFor(() => {
      expect(screen.getByTestId('historico-table')).toBeInTheDocument();
    });
    
    // Verificar que os dados são exibidos
    expect(screen.getByText('Total: 2')).toBeInTheDocument();
    expect(screen.getByText('Página: 1 de 1')).toBeInTheDocument();
  });
  
  test('aplica filtros e atualiza a lista', async () => {
    render(<HistoricoLlamadas />);
    
    // Esperar pelo carregamento inicial
    await waitFor(() => {
      expect(screen.getByTestId('historico-table')).toBeInTheDocument();
    });
    
    // Resetar mock da API para verificar a próxima chamada
    obtenerHistoricoLlamadas.mockClear();
    
    // Aplicar filtro
    const filterButton = screen.getByTestId('filter-estado');
    fireEvent.click(filterButton);
    
    // Verificar que a API foi chamada com os filtros
    await waitFor(() => {
      expect(obtenerHistoricoLlamadas).toHaveBeenCalledTimes(1);
    });
  });
  
  test('muda de página e atualiza a lista', async () => {
    // Mock para segunda página
    const mockPage2Response = {
      ...mockApiResponse,
      llamadas: [
        {
          id: 125,
          numero_destino: '+5491199999999',
          usuario_email: 'page2@test.com',
          fecha_asignacion: '2023-05-21T10:00:00',
          fecha_finalizacion: '2023-05-21T10:05:30',
          estado: 'finalizada',
          resultado: 'finalizada_exito'
        }
      ]
    };
    
    // Mock da API para retornar diferente na segunda chamada
    obtenerHistoricoLlamadas
      .mockResolvedValueOnce(mockApiResponse)
      .mockResolvedValueOnce(mockPage2Response);
    
    render(<HistoricoLlamadas />);
    
    // Esperar pelo carregamento inicial
    await waitFor(() => {
      expect(screen.getByTestId('historico-table')).toBeInTheDocument();
    });
    
    // Clicar para avançar página
    const nextButton = screen.getByTestId('next-page');
    fireEvent.click(nextButton);
    
    // Verificar que a API foi chamada novamente com a nova página
    await waitFor(() => {
      expect(obtenerHistoricoLlamadas).toHaveBeenCalledTimes(2);
    });
  });
  
  test('abre o modal de detalhes ao clicar em uma chamada', async () => {
    render(<HistoricoLlamadas />);
    
    // Esperar pelo carregamento inicial
    await waitFor(() => {
      expect(screen.getByTestId('historico-table')).toBeInTheDocument();
    });
    
    // Encontrar e clicar no botão de detalhes da primeira chamada
    const detailsButton = screen.getAllByText('Detalhes')[0];
    fireEvent.click(detailsButton);
    
    // Verificar que o modal foi aberto com o ID correto
    await waitFor(() => {
      expect(screen.getByTestId('llamada-detalle-modal')).toBeInTheDocument();
      expect(screen.getByText('Detalhes da chamada ID: 123')).toBeInTheDocument();
    });
    
    // Fechar o modal
    const closeButton = screen.getByText('Fechar');
    fireEvent.click(closeButton);
    
    // Verificar que o modal foi fechado
    await waitFor(() => {
      expect(screen.queryByTestId('llamada-detalle-modal')).not.toBeInTheDocument();
    });
  });
  
  test('exporta dados para CSV', async () => {
    const mockAppendChild = jest.fn();
    const mockRemoveChild = jest.fn();
    const mockClick = jest.fn();
    
    // Mock de document.createElement
    document.createElement = jest.fn().mockImplementation(() => ({
      style: {},
      href: '',
      download: '',
      click: mockClick
    }));
    
    // Mock de document.body
    document.body = {
      ...document.body,
      appendChild: mockAppendChild,
      removeChild: mockRemoveChild
    };
    
    render(<HistoricoLlamadas />);
    
    // Esperar pelo carregamento inicial
    await waitFor(() => {
      expect(screen.getByTestId('historico-table')).toBeInTheDocument();
    });
    
    // Clicar no botão de exportar
    const exportButton = screen.getByTestId('export-button');
    fireEvent.click(exportButton);
    
    // Verificar que a função de exportação foi chamada
    await waitFor(() => {
      expect(exportarHistoricoCSV).toHaveBeenCalledTimes(1);
      expect(mockClick).toHaveBeenCalledTimes(1);
    });
  });
  
  test('reseta os filtros', async () => {
    render(<HistoricoLlamadas />);
    
    // Esperar pelo carregamento inicial
    await waitFor(() => {
      expect(screen.getByTestId('historico-table')).toBeInTheDocument();
    });
    
    // Aplicar filtro primeiro
    const filterButton = screen.getByTestId('filter-estado');
    fireEvent.click(filterButton);
    
    // Limpar mocks para facilitar a verificação
    obtenerHistoricoLlamadas.mockClear();
    
    // Clicar no botão de resetar
    const resetButton = screen.getByTestId('reset-button');
    fireEvent.click(resetButton);
    
    // Verificar que a API foi chamada novamente
    await waitFor(() => {
      expect(obtenerHistoricoLlamadas).toHaveBeenCalledTimes(1);
    });
  });
}); 