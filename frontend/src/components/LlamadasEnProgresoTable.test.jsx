import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import LlamadasEnProgresoTable from './LlamadasEnProgresoTable';

// Mock do módulo Timer para evitar problemas com tempo real nos testes
jest.mock('./Timer', () => {
  return function MockTimer({ startTime }) {
    return <span data-testid="timer">00:05:30</span>;
  };
});

describe('LlamadasEnProgresoTable', () => {
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
  
  const mockFinalizarLlamada = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  test('renderiza correctamente con llamadas', () => {
    render(
      <LlamadasEnProgresoTable 
        llamadas={mockLlamadas} 
        onFinalizarLlamada={mockFinalizarLlamada} 
      />
    );
    
    // Verifica que se muestren los datos de las llamadas
    expect(screen.getByText('123')).toBeInTheDocument();
    expect(screen.getByText('+5491112345678')).toBeInTheDocument();
    expect(screen.getByText('usuario@test.com')).toBeInTheDocument();
    expect(screen.getByText('124')).toBeInTheDocument();
    expect(screen.getByText('+5491187654321')).toBeInTheDocument();
    
    // Verifica que existan los botones de finalizar
    const finalizarButtons = screen.getAllByText('Finalizar');
    expect(finalizarButtons).toHaveLength(2);
  });
  
  test('muestra mensaje cuando no hay llamadas', () => {
    render(
      <LlamadasEnProgresoTable 
        llamadas={[]} 
        onFinalizarLlamada={mockFinalizarLlamada} 
      />
    );
    
    expect(screen.getByText('No hay llamadas en progreso actualmente')).toBeInTheDocument();
  });
  
  test('llama a onFinalizarLlamada cuando se confirma finalizar', () => {
    // Mock de window.confirm para que retorne true
    window.confirm = jest.fn(() => true);
    
    render(
      <LlamadasEnProgresoTable 
        llamadas={mockLlamadas} 
        onFinalizarLlamada={mockFinalizarLlamada} 
      />
    );
    
    // Hacer clic en el primer botón de finalizar
    const finalizarButtons = screen.getAllByText('Finalizar');
    fireEvent.click(finalizarButtons[0]);
    
    // Verificar que se haya mostrado el confirm
    expect(window.confirm).toHaveBeenCalledWith(
      '¿Está seguro que desea finalizar esta llamada manualmente?'
    );
    
    // Verificar que se haya llamado a la función con el ID correcto
    expect(mockFinalizarLlamada).toHaveBeenCalledWith(123);
  });
  
  test('no llama a onFinalizarLlamada cuando se cancela', () => {
    // Mock de window.confirm para que retorne false
    window.confirm = jest.fn(() => false);
    
    render(
      <LlamadasEnProgresoTable 
        llamadas={mockLlamadas} 
        onFinalizarLlamada={mockFinalizarLlamada} 
      />
    );
    
    // Hacer clic en el primer botón de finalizar
    const finalizarButtons = screen.getAllByText('Finalizar');
    fireEvent.click(finalizarButtons[0]);
    
    // Verificar que se haya mostrado el confirm
    expect(window.confirm).toHaveBeenCalledWith(
      '¿Está seguro que desea finalizar esta llamada manualmente?'
    );
    
    // Verificar que NO se haya llamado a la función
    expect(mockFinalizarLlamada).not.toHaveBeenCalled();
  });
}); 