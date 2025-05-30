import React, { useState } from 'react';
import MonitorLlamadasEnProgreso from './components/MonitorLlamadasEnProgreso';
import HistoricoLlamadas from './components/HistoricoLlamadas';
import GestionCampanhas from './components/GestionCampanhas';
import UploadListas from './components/UploadListas';

/**
 * Componente principal da aplicação
 * 
 * @returns {JSX.Element} Componente JSX
 */
function App() {
  const [activeTab, setActiveTab] = useState('monitor');
  
  return (
    <div className="min-h-screen bg-gray-900 text-white">
      <header className="bg-gray-800 shadow-md">
        <div className="container mx-auto px-4 py-4">
          <div className="flex justify-between items-center">
            <h1 className="text-xl font-bold text-blue-400">
              Discador - Panel de Control
            </h1>
            <div className="text-sm text-gray-400">
              Sistema de monitoreo de llamadas
            </div>
          </div>
          
          <nav className="mt-4">
            <ul className="flex space-x-1">
              <li>
                <button 
                  onClick={() => setActiveTab('monitor')}
                  className={`px-4 py-2 rounded-t-lg transition-colors ${
                    activeTab === 'monitor' 
                      ? 'bg-gray-900 text-white' 
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  Monitoreo
                </button>
              </li>
              <li>
                <button 
                  onClick={() => setActiveTab('campanhas')}
                  className={`px-4 py-2 rounded-t-lg transition-colors ${
                    activeTab === 'campanhas' 
                      ? 'bg-gray-900 text-white' 
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  Campañas
                </button>
              </li>
              <li>
                <button 
                  onClick={() => setActiveTab('listas')}
                  className={`px-4 py-2 rounded-t-lg transition-colors ${
                    activeTab === 'listas' 
                      ? 'bg-gray-900 text-white' 
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  Listas
                </button>
              </li>
              <li>
                <button 
                  onClick={() => setActiveTab('historico')}
                  className={`px-4 py-2 rounded-t-lg transition-colors ${
                    activeTab === 'historico' 
                      ? 'bg-gray-900 text-white' 
                      : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                  }`}
                >
                  Historial
                </button>
              </li>
            </ul>
          </nav>
        </div>
      </header>
      
      <main>
        {activeTab === 'monitor' && <MonitorLlamadasEnProgreso />}
        {activeTab === 'campanhas' && <GestionCampanhas />}
        {activeTab === 'listas' && <UploadListas />}
        {activeTab === 'historico' && <HistoricoLlamadas />}
      </main>
      
      <footer className="bg-gray-800 py-4 mt-8">
        <div className="container mx-auto px-4">
          <p className="text-center text-gray-400 text-sm">
            &copy; {new Date().getFullYear()} Discador - Todos los derechos reservados
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App; 