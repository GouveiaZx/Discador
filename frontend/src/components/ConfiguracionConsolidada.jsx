import React, { useState } from 'react';
import SipTrunkConfig from './SipTrunkConfig';
import DNCMultiLanguageManager from './DNCMultiLanguageManager';

const ConfiguracionConsolidada = () => {
  const [activeConfigTab, setActiveConfigTab] = useState('sip-trunks');

  const configTabs = [
    { id: 'sip-trunks', label: 'SIP Trunks', icon: '📞' },
    { id: 'dnc-messages', label: 'Mensajes DNC', icon: '🔕' }
  ];

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gradient-primary mb-2">
          Configuración del Sistema
        </h1>
        <p className="text-secondary-400">
          Configuración avanzada de trunks SIP y mensajes DNC multiidioma
        </p>
      </div>

      {/* Navigation Tabs */}
      <div className="card-glass">
        <div className="flex flex-wrap border-b border-white/10">
          {configTabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveConfigTab(tab.id)}
              className={`
                px-6 py-4 font-medium transition-all duration-200 border-b-2 
                ${activeConfigTab === tab.id
                  ? 'border-primary-500 text-primary-400 bg-primary-500/10'
                  : 'border-transparent text-secondary-400 hover:text-white hover:bg-white/5'
                }
              `}
            >
              <div className="flex items-center space-x-2">
                <span className="text-lg">{tab.icon}</span>
                <span>{tab.label}</span>
              </div>
            </button>
          ))}
        </div>

        {/* Tab Content */}
        <div className="p-6">
          {activeConfigTab === 'sip-trunks' && (
            <div className="space-y-6">
              <div className="text-center mb-6">
                <h3 className="text-xl font-semibold text-white mb-2">
                  Configuración de Trunks SIP
                </h3>
                <p className="text-secondary-400">
                  Configure seus trunks SIP com códigos de país e configurações específicas
                </p>
              </div>
              <SipTrunkConfig />
            </div>
          )}

          {activeConfigTab === 'dnc-messages' && (
            <div className="space-y-6">
              <div className="text-center mb-6">
                <h3 className="text-xl font-semibold text-white mb-2">
                  Mensajes DNC Multiidioma
                </h3>
                <p className="text-secondary-400">
                  Configure mensagens para quando o cliente pressiona 2 para ser removido da lista
                </p>
              </div>
              <DNCMultiLanguageManager />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ConfiguracionConsolidada; 