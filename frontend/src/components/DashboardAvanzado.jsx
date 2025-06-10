import React, { useState, useEffect } from 'react';
import { makeApiRequest } from '../config/api';

const DashboardAvanzado = () => {
  const [data, setData] = useState({
    metricas: {},
    multiSip: { provedores: [], ultimaSeleccion: null },
    code2base: { clis: [], estadisticas: {} },
    audio: { contextos: [], sesionesActivas: 0 },
    campanhasPoliticas: []
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    cargarDatos();
    const interval = setInterval(cargarDatos, 30000); // Actualizar cada 30s
    return () => clearInterval(interval);
  }, []);

  const cargarDatos = async () => {
    try {
      setLoading(true);
      
      // Cargar datos de múltiples APIs en paralelo
      const [
        metricasRes,
        provedoresRes,
        clisRes,
        contextosRes,
        campanhasRes
      ] = await Promise.allSettled([
        makeApiRequest('/monitoring/dashboard'),
        makeApiRequest('/multi-sip/provedores'),
        makeApiRequest('/code2base/clis'),
        makeApiRequest('/audio/contextos'),
        makeApiRequest('/campanha-politica/campanhas')
      ]);

      setData({
        metricas: metricasRes.status === 'fulfilled' ? metricasRes.value : {},
        multiSip: {
          provedores: provedoresRes.status === 'fulfilled' ? provedoresRes.value : [],
          ultimaSeleccion: null
        },
        code2base: {
          clis: clisRes.status === 'fulfilled' ? clisRes.value : [],
          estadisticas: {}
        },
        audio: {
          contextos: contextosRes.status === 'fulfilled' ? contextosRes.value : [],
          sesionesActivas: Math.floor(Math.random() * 10) // Mock
        },
        campanhasPoliticas: campanhasRes.status === 'fulfilled' ? campanhasRes.value : []
      });
    } catch (error) {
      console.error('Error cargando dashboard avanzado:', error);
      // Datos mock para demonstración
      setData({
        metricas: {
          llamadasActivas: 18,
          efectividad: 48,
          operadoresOnline: 12
        },
        multiSip: {
          provedores: [
            { id: 1, nome: 'SIP Provider 1', status: 'ativo', llamadas: 45 },
            { id: 2, nome: 'SIP Provider 2', status: 'ativo', llamadas: 32 }
          ],
          ultimaSeleccion: { provedor: 'SIP Provider 1', motivo: 'Menor costo' }
        },
        code2base: {
          clis: [
            { id: 1, numero: '+5491112345678', activo: true, llamadas_hoy: 123 },
            { id: 2, numero: '+5491187654321', activo: true, llamadas_hoy: 89 }
          ],
          estadisticas: { eficiencia: 78, clis_activos: 2 }
        },
        audio: {
          contextos: [
            { id: 1, nome: 'Presione 1 Padrao', activo: true },
            { id: 2, nome: 'IVR Personalizado', activo: false }
          ],
          sesionesActivas: 8
        },
        campanhasPoliticas: [
          { id: 1, nome: 'Campanha Federal 2024', status: 'ativa', compliance: true }
        ]
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="container mx-auto px-4 py-6">
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-white">📊 Dashboard Avanzado</h2>
        <div className="text-sm text-gray-400">
          Última actualización: {new Date().toLocaleTimeString()}
        </div>
      </div>

      {/* Métricas Principais */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-gray-400 text-sm">Llamadas Activas</h3>
              <p className="text-2xl font-bold text-green-400">{data.metricas.llamadasActivas || 0}</p>
            </div>
            <div className="text-green-400">📞</div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-gray-400 text-sm">Efectividad</h3>
              <p className="text-2xl font-bold text-blue-400">{data.metricas.efectividad || 0}%</p>
            </div>
            <div className="text-blue-400">📈</div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-gray-400 text-sm">Operadores Online</h3>
              <p className="text-2xl font-bold text-purple-400">{data.metricas.operadoresOnline || 0}</p>
            </div>
            <div className="text-purple-400">👥</div>
          </div>
        </div>

        <div className="bg-gray-800 rounded-lg p-6">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-gray-400 text-sm">Sesiones Audio</h3>
              <p className="text-2xl font-bold text-orange-400">{data.audio.sesionesActivas}</p>
            </div>
            <div className="text-orange-400">🤖</div>
          </div>
        </div>
      </div>

      {/* Sistemas Avançados */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        
        {/* Multi-SIP Status */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">📡 Multi-SIP Status</h3>
          <div className="space-y-3">
            {data.multiSip.provedores.length === 0 ? (
              <p className="text-gray-400">Nenhum provedor configurado</p>
            ) : (
              data.multiSip.provedores.map((provedor) => (
                <div key={provedor.id} className="flex justify-between items-center bg-gray-700 p-3 rounded">
                  <div>
                    <span className="text-white font-medium">{provedor.nome}</span>
                    <span className="text-gray-300 text-sm ml-2">
                      {provedor.llamadas || 0} llamadas
                    </span>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs ${
                    provedor.status === 'ativo' ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
                  }`}>
                    {provedor.status}
                  </span>
                </div>
              ))
            )}
            {data.multiSip.ultimaSeleccion && (
              <div className="mt-4 p-3 bg-blue-900 border border-blue-700 rounded">
                <p className="text-blue-100 text-sm">
                  <strong>Última seleção:</strong> {data.multiSip.ultimaSeleccion.provedor}
                  <br />
                  <span className="text-blue-200">Motivo: {data.multiSip.ultimaSeleccion.motivo}</span>
                </p>
              </div>
            )}
          </div>
        </div>

        {/* CODE2BASE Status */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">🎯 CODE2BASE Status</h3>
          <div className="space-y-3">
            {data.code2base.clis.length === 0 ? (
              <p className="text-gray-400">Nenhum CLI configurado</p>
            ) : (
              data.code2base.clis.map((cli) => (
                <div key={cli.id} className="flex justify-between items-center bg-gray-700 p-3 rounded">
                  <div>
                    <span className="text-white font-medium">{cli.numero}</span>
                    <span className="text-gray-300 text-sm ml-2">
                      {cli.llamadas_hoy || 0} hoy
                    </span>
                  </div>
                  <span className={`px-2 py-1 rounded text-xs ${
                    cli.activo ? 'bg-green-600 text-white' : 'bg-red-600 text-white'
                  }`}>
                    {cli.activo ? 'Ativo' : 'Inativo'}
                  </span>
                </div>
              ))
            )}
            {data.code2base.estadisticas.eficiencia && (
              <div className="mt-4 p-3 bg-green-900 border border-green-700 rounded">
                <p className="text-green-100 text-sm">
                  <strong>Eficiência:</strong> {data.code2base.estadisticas.eficiencia}%
                  <br />
                  <span className="text-green-200">CLIs ativos: {data.code2base.estadisticas.clis_activos}</span>
                </p>
              </div>
            )}
          </div>
        </div>

      </div>

      {/* Audio Inteligente e Campanhas Políticas */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Audio Inteligente */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">🤖 Áudio Inteligente</h3>
          <div className="space-y-3">
            <div className="flex justify-between items-center">
              <span className="text-gray-300">Sesiones Activas:</span>
              <span className="text-white font-bold">{data.audio.sesionesActivas}</span>
            </div>
            
            <div className="space-y-2">
              <h4 className="text-gray-400 text-sm">Contextos Disponíveis:</h4>
              {data.audio.contextos.length === 0 ? (
                <p className="text-gray-500 text-sm">Nenhum contexto configurado</p>
              ) : (
                data.audio.contextos.map((contexto) => (
                  <div key={contexto.id} className="flex justify-between items-center bg-gray-700 p-2 rounded text-sm">
                    <span className="text-white">{contexto.nome}</span>
                    <span className={`px-2 py-1 rounded text-xs ${
                      contexto.activo ? 'bg-purple-600 text-white' : 'bg-gray-600 text-white'
                    }`}>
                      {contexto.activo ? 'Ativo' : 'Inativo'}
                    </span>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Campanhas Políticas */}
        <div className="bg-gray-800 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-white mb-4">🗳️ Campanhas Políticas</h3>
          <div className="space-y-3">
            {data.campanhasPoliticas.length === 0 ? (
              <p className="text-gray-400">Nenhuma campanha política ativa</p>
            ) : (
              data.campanhasPoliticas.map((campanha) => (
                <div key={campanha.id} className="bg-gray-700 p-3 rounded">
                  <div className="flex justify-between items-start">
                    <div>
                      <span className="text-white font-medium">{campanha.nome}</span>
                      <div className="flex items-center mt-1">
                        <span className={`px-2 py-1 rounded text-xs mr-2 ${
                          campanha.status === 'ativa' ? 'bg-green-600 text-white' : 'bg-gray-600 text-white'
                        }`}>
                          {campanha.status}
                        </span>
                        {campanha.compliance && (
                          <span className="px-2 py-1 rounded text-xs bg-blue-600 text-white">
                            ✓ Compliance
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

      </div>

      {/* Ações Rápidas */}
      <div className="bg-gray-800 rounded-lg p-6 mt-6">
        <h3 className="text-lg font-semibold text-white mb-4">⚡ Ações Rápidas</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button 
            onClick={() => window.open('/docs', '_blank')}
            className="bg-blue-600 hover:bg-blue-700 text-white p-3 rounded text-sm font-medium transition-colors"
          >
            📚 API Docs
          </button>
          <button 
            onClick={() => cargarDatos()}
            className="bg-green-600 hover:bg-green-700 text-white p-3 rounded text-sm font-medium transition-colors"
          >
            🔄 Atualizar
          </button>
          <button 
            onClick={() => alert('Funcionalidade em desenvolvimento')}
            className="bg-purple-600 hover:bg-purple-700 text-white p-3 rounded text-sm font-medium transition-colors"
          >
            📊 Relatórios
          </button>
          <button 
            onClick={() => alert('Funcionalidade em desenvolvimento')}
            className="bg-orange-600 hover:bg-orange-700 text-white p-3 rounded text-sm font-medium transition-colors"
          >
            ⚙️ Configurar
          </button>
        </div>
      </div>
    </div>
  );
};

export default DashboardAvanzado; 