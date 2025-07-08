import React from 'react';
import { render, screen, act, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import MonitorLlamadasEnProgreso from './MonitorLlamadasEnProgreso';
import { obtenerLlamadasEnProgreso, finalizarLlamadaManualmente } from '../services/llamadasService';

// Mock dos serviços de chamadas
jest.mock('../services/llamadasService', () => ({
  obtenerLlamadasEnProgreso: jest.fn(),
  finalizarLlamadaManualmente: jest.fn()
}));

// Mock do componente de tabela para simplificar os testes
jest.mock('./LlamadasEnProgresoTable', () => {
  return function MockLlamadasTable({ llamadas, onFinalizarLlamada }) {
    return (
      <div data-testid="mock-tabla">
        <span>Total llamadas: {llamadas.length}</span>
        {llamadas.map(llamada => (
          <div key={llamada.id} data-testid={`llamada-${llamada.id}`}>
            {llamada.numero_destino}
            <button 
              onClick={() => onFinalizarLlamada(llamada.id)}
              data-testid={`finalizar-${llamada.id}`}
            >
              Finalizar
            </button>
          </div>
        ))}
      </div>
    );
  };
});

describe('MonitorLlamadasEnProgreso', () => {
  const mockLlamadas = [
    {
      id: 123,
      numero_destino: '+5491112345678',
      usuario_email: 'usuario@test.com',
      fecha_asignacion: '2023-05-20T10:00:00',
      estado: 'en_progreso'
    },
    {
      id: 124,
      numero_destino: '+5491187654321',
      usuario_email: 'otro@test.com',
      fecha_asignacion: '2023-05-20T11:00:00',
      estado: 'en_progreso'
    }
  ];
  
  beforeEach(() => {
    jest.clearAllMocks();
    jest.useFakeTimers();
    
    // Mock da resposta da API
    obtenerLlamadasEnProgreso.mockResolvedValue({
      llamadas: mockLlamadas
    });
    
    finalizarLlamadaManualmente.mockResolvedValue({
      mensaje: "Llamada finalizada correctamente"
    });
  });
  
  afterEach(() => {
    jest.useRealTimers();
  });
  
  test('carga las llamadas al iniciar y configura polling', async () => {
    render(<MonitorLlamadasEnProgreso />);
    
    // Verifica que se haya llamado a la API al montar
    expect(obtenerLlamadasEnProgreso).toHaveBeenCalledTimes(1);
    
    // Avanza el tiempo para que ocurra una actualización
    await act(async () => {
      jest.advanceTimersByTime(5000);
    });
    
    // Verifica que se haya llamado a la API de nuevo
    expect(obtenerLlamadasEnProgreso).toHaveBeenCalledTimes(2);
    
    // Avanza el tiempo para otra actualización
    await act(async () => {
      jest.advanceTimersByTime(5000);
    });
    
    // Verifica que se haya llamado a la API por tercera vez
    expect(obtenerLlamadasEnProgreso).toHaveBeenCalledTimes(3);
  });
  
  test('muestra los datos de las llamadas', async () => {
    render(<MonitorLlamadasEnProgreso />);
    
    // Espera a que se muestren los datos
    await waitFor(() => {
      expect(screen.getByText('Total llamadas: 2')).toBeInTheDocument();
    });
  });
  
  test('muestra error cuando falla la carga', async () => {
    // Mock para simular error en la API
    obtenerLlamadasEnProgreso.mockRejectedValueOnce(new Error('Error de conexión'));
    
    render(<MonitorLlamadasEnProgreso />);
    
    // Espera a que se muestre el mensaje de error
    await waitFor(() => {
      expect(screen.getByText(/Error al cargar las llamadas/)).toBeInTheDocument();
    });
  });
  
  test('finaliza llamada correctamente', async () => {
    // Cuando se finaliza la llamada 123
    finalizarLlamadaManualmente.mockResolvedValueOnce({
      mensaje: "Llamada finalizada correctamente"
    });
    
    const { getByTestId } = render(<MonitorLlamadasEnProgreso />);
    
    // Espera a que se carguen las llamadas
    await waitFor(() => {
      expect(screen.getByText('Total llamadas: 2')).toBeInTheDocument();
    });
    
    // Busca el botón de finalizar para la llamada 123 y hace clic
    const finalizarButton = await waitFor(() => getByTestId('finalizar-123'));
    act(() => {
      finalizarButton.click();
    });
    
    // Verifica que se haya llamado al servicio
    await waitFor(() => {
      expect(finalizarLlamadaManualmente).toHaveBeenCalledWith(123);
    });
  });
}); 