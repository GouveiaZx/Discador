import React, { useState, useEffect } from 'react';
import { makeApiRequest } from '../config/api';

const DNCMultiLanguageManager = () => {
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingMessage, setEditingMessage] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState('all');
  const [selectedType, setSelectedType] = useState('all');
  
  const [formData, setFormData] = useState({
    language_code: '',
    language_name: '',
    message_type: 'opt_out',
    title: '',
    message: '',
    audio_file: null,
    is_active: true
  });

  const languages = [
    { code: 'es', name: 'Español', flag: '🇦🇷' },
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'pt', name: 'Português', flag: '🇧🇷' },
    { code: 'fr', name: 'Français', flag: '🇫🇷' },
    { code: 'de', name: 'Deutsch', flag: '🇩🇪' }
  ];

  const messageTypes = [
    { value: 'opt_out', label: 'Opt-Out (Presione 2)', icon: '🚫' },
    { value: 'confirmation', label: 'Confirmación', icon: '✅' },
    { value: 'error', label: 'Error', icon: '❌' }
  ];

  const templateMessages = {
    es: {
      opt_out: 'Gracias por su llamada. Para remover su número de nuestra lista de llamadas, presione 2 ahora. Su número será removido en 24 horas. Gracias.',
      confirmation: 'Su número ha sido removido exitosamente de nuestra lista de llamadas. No recibirá más llamadas de nosotros. Gracias.',
      error: 'Disculpe, pero hubo un error procesando su solicitud. Por favor intente nuevamente o contacte nuestro equipo de soporte.'
    },
    en: {
      opt_out: 'Thank you for your call. To remove your number from our calling list, please press 2 now. Your number will be removed within 24 hours. Thank you.',
      confirmation: 'Your number has been successfully removed from our calling list. You will not receive any more calls from us. Thank you.',
      error: 'We apologize, but there was an error processing your request. Please try again or contact our support team.'
    },
    pt: {
      opt_out: 'Obrigado pela sua ligação. Para remover seu número da nossa lista de chamadas, pressione 2 agora. Seu número será removido em 24 horas. Obrigado.',
      confirmation: 'Seu número foi removido com sucesso da nossa lista de chamadas. Você não receberá mais ligações nossas. Obrigado.',
      error: 'Desculpe, mas houve um erro ao processar sua solicitação. Tente novamente ou entre em contato com nossa equipe de suporte.'
    }
  };

  const loadMessages = async () => {
    try {
      setLoading(true);
      const response = await makeApiRequest('/dnc/messages');
      setMessages(response.data || []);
    } catch (error) {
      console.error('Error al cargar mensajes DNC:', error);
      // Usar datos mock si la API no existe aún
      const mockMessages = [];
      Object.keys(templateMessages).forEach(lang => {
        Object.keys(templateMessages[lang]).forEach(type => {
          mockMessages.push({
            id: `${lang}_${type}`,
            language_code: lang,
            language_name: languages.find(l => l.code === lang)?.name || lang,
            message_type: type,
            title: `${type.charAt(0).toUpperCase() + type.slice(1)} - ${languages.find(l => l.code === lang)?.name}`,
            message: templateMessages[lang][type],
            is_active: true,
            created_at: new Date().toISOString()
          });
        });
      });
      setMessages(mockMessages);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMessages();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    try {
      const messageData = {
        ...formData,
        language_name: languages.find(l => l.code === formData.language_code)?.name || formData.language_code
      };

      if (editingMessage) {
        // Simular actualización
        setMessages(prev => prev.map(msg => 
          msg.id === editingMessage.id 
            ? { ...msg, ...messageData, updated_at: new Date().toISOString() }
            : msg
        ));
      } else {
        // Simular creación
        const newMessage = {
          id: Date.now().toString(),
          ...messageData,
          created_at: new Date().toISOString(),
          updated_at: new Date().toISOString()
        };
        setMessages(prev => [...prev, newMessage]);
      }
      
      setShowForm(false);
      setEditingMessage(null);
      resetForm();
    } catch (error) {
      console.error('Error al guardar mensaje:', error);
      alert('Error al guardar mensaje. Intente nuevamente.');
    }
  };

  const handleEdit = (message) => {
    setEditingMessage(message);
    setFormData({
      language_code: message.language_code,
      language_name: message.language_name,
      message_type: message.message_type,
      title: message.title,
      message: message.message,
      audio_file: null,
      is_active: message.is_active
    });
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (window.confirm('¿Está seguro que desea eliminar este mensaje?')) {
      setMessages(prev => prev.filter(msg => msg.id !== id));
    }
  };

  const resetForm = () => {
    setFormData({
      language_code: '',
      language_name: '',
      message_type: 'opt_out',
      title: '',
      message: '',
      audio_file: null,
      is_active: true
    });
    setEditingMessage(null);
  };

  const loadTemplate = () => {
    const { language_code, message_type } = formData;
    if (language_code && message_type && templateMessages[language_code]) {
      const template = templateMessages[language_code][message_type];
      if (template) {
        setFormData(prev => ({
          ...prev,
          message: template,
          title: `${message_type.charAt(0).toUpperCase() + message_type.slice(1)} - ${languages.find(l => l.code === language_code)?.name}`
        }));
      }
    }
  };

  const filteredMessages = messages.filter(message => {
    const languageMatch = selectedLanguage === 'all' || message.language_code === selectedLanguage;
    const typeMatch = selectedType === 'all' || message.message_type === selectedType;
    return languageMatch && typeMatch;
  });

  const getLanguageFlag = (code) => {
    return languages.find(l => l.code === code)?.flag || '🌐';
  };

  const getTypeIcon = (type) => {
    return messageTypes.find(t => t.value === type)?.icon || '📝';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        <span className="ml-2 text-gray-400">Cargando mensajes DNC...</span>
      </div>
    );
  }

  return (
    <div className="bg-gray-800/40 backdrop-blur-xl rounded-xl border border-gray-700/50 p-6">
      {/* Cabecera */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-white">🌍 Mensajes DNC Multi-idioma</h2>
          <p className="text-gray-400 mt-1">Configure mensajes de opt-out en diferentes idiomas</p>
        </div>
        <button
          onClick={() => setShowForm(!showForm)}
          className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center"
        >
          <span className="mr-2">{showForm ? '❌' : '+'}</span>
          {showForm ? 'Cancelar' : 'Nuevo Mensaje'}
        </button>
      </div>

      {/* Filtros */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div>
          <label className="block text-sm text-gray-400 mb-2">Filtrar por Idioma</label>
          <select
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value)}
            className="w-full px-4 py-2 bg-gray-700/50 border border-gray-600/50 rounded-lg text-white focus:outline-none focus:border-blue-500"
          >
            <option value="all">Todos los idiomas</option>
            {languages.map(lang => (
              <option key={lang.code} value={lang.code}>
                {lang.flag} {lang.name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm text-gray-400 mb-2">Filtrar por Tipo</label>
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="w-full px-4 py-2 bg-gray-700/50 border border-gray-600/50 rounded-lg text-white focus:outline-none focus:border-blue-500"
          >
            <option value="all">Todos los tipos</option>
            {messageTypes.map(type => (
              <option key={type.value} value={type.value}>
                {type.icon} {type.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Formulario */}
      {showForm && (
        <div className="bg-gray-700/30 border border-gray-600/30 rounded-lg p-6 mb-6">
          <h3 className="text-lg font-semibold text-white mb-4">
            {editingMessage ? 'Editar Mensaje DNC' : 'Nuevo Mensaje DNC'}
          </h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-2">Idioma *</label>
                <select
                  value={formData.language_code}
                  onChange={(e) => setFormData({...formData, language_code: e.target.value})}
                  className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600/50 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  required
                >
                  <option value="">Seleccionar idioma</option>
                  {languages.map(lang => (
                    <option key={lang.code} value={lang.code}>
                      {lang.flag} {lang.name}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-2">Tipo de Mensaje *</label>
                <select
                  value={formData.message_type}
                  onChange={(e) => setFormData({...formData, message_type: e.target.value})}
                  className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600/50 rounded-lg text-white focus:outline-none focus:border-blue-500"
                  required
                >
                  {messageTypes.map(type => (
                    <option key={type.value} value={type.value}>
                      {type.icon} {type.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm text-gray-400 mb-2">Título *</label>
              <input
                type="text"
                value={formData.title}
                onChange={(e) => setFormData({...formData, title: e.target.value})}
                className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600/50 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                placeholder="Ej: Opt-Out - Español"
                required
              />
            </div>

            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="text-sm text-gray-400">Mensaje *</label>
                <button
                  type="button"
                  onClick={loadTemplate}
                  className="px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white text-xs rounded transition-colors"
                  disabled={!formData.language_code || !formData.message_type}
                >
                  📝 Cargar Plantilla
                </button>
              </div>
              <textarea
                value={formData.message}
                onChange={(e) => setFormData({...formData, message: e.target.value})}
                className="w-full px-4 py-3 bg-gray-700/50 border border-gray-600/50 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:border-blue-500"
                rows={4}
                placeholder="Escriba el mensaje que se reproducirá..."
                required
              />
              <p className="text-xs text-gray-500 mt-1">
                Este mensaje se reproducirá cuando el cliente presione la tecla correspondiente
              </p>
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="is_active"
                checked={formData.is_active}
                onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                className="rounded border-gray-600 text-blue-600 focus:ring-blue-500"
              />
              <label htmlFor="is_active" className="text-white text-sm">
                Mensaje activo
              </label>
            </div>

            <div className="flex space-x-4">
              <button
                type="submit"
                className="px-6 py-3 bg-green-600 hover:bg-green-700 text-white font-medium rounded-lg transition-colors"
              >
                {editingMessage ? 'Actualizar' : 'Crear'} Mensaje
              </button>
              <button
                type="button"
                onClick={() => {
                  setShowForm(false);
                  resetForm();
                }}
                className="px-6 py-3 bg-gray-600 hover:bg-gray-700 text-white font-medium rounded-lg transition-colors"
              >
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Lista de Mensajes */}
      <div className="space-y-4">
        {filteredMessages.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">🌍</div>
            <h3 className="text-xl font-semibold text-white mb-2">
              {selectedLanguage !== 'all' || selectedType !== 'all' 
                ? 'No hay mensajes que coincidan con los filtros'
                : 'No hay mensajes DNC configurados'
              }
            </h3>
            <p className="text-gray-400 mb-4">
              {selectedLanguage !== 'all' || selectedType !== 'all'
                ? 'Pruebe cambiar los filtros o crear un nuevo mensaje'
                : 'Cree mensajes DNC para diferentes idiomas'
              }
            </p>
            {(selectedLanguage === 'all' && selectedType === 'all') && (
              <button
                onClick={() => setShowForm(true)}
                className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
              >
                + Crear Primer Mensaje
              </button>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
            {filteredMessages.map((message) => (
              <div key={message.id} className="bg-gray-700/30 border border-gray-600/30 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <span className="text-lg">{getLanguageFlag(message.language_code)}</span>
                    <span className="text-sm font-medium text-white">{message.language_name}</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <span className="text-lg">{getTypeIcon(message.message_type)}</span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      message.is_active 
                        ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                        : 'bg-red-500/20 text-red-400 border border-red-500/30'
                    }`}>
                      {message.is_active ? 'Activo' : 'Inactivo'}
                    </span>
                  </div>
                </div>

                <h4 className="font-medium text-white mb-2 truncate">{message.title}</h4>
                <p className="text-gray-400 text-sm line-clamp-3 mb-4">{message.message}</p>

                <div className="flex space-x-2">
                  <button
                    onClick={() => handleEdit(message)}
                    className="flex-1 px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded transition-colors"
                  >
                    ✏️ Editar
                  </button>
                  <button
                    onClick={() => handleDelete(message.id)}
                    className="flex-1 px-3 py-2 bg-red-600 hover:bg-red-700 text-white text-sm rounded transition-colors"
                  >
                    🗑️ Eliminar
                  </button>
                </div>

                <div className="mt-3 pt-3 border-t border-gray-600/30">
                  <p className="text-xs text-gray-500">
                    Tipo: {messageTypes.find(t => t.value === message.message_type)?.label}
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Información sobre el funcionamiento */}
      <div className="mt-8 bg-blue-500/10 border border-blue-500/30 rounded-lg p-4">
        <div className="flex items-start">
          <span className="text-xl mr-3">💡</span>
          <div>
            <h4 className="text-blue-100 font-medium mb-2">¿Cómo Funciona?</h4>
            <div className="text-blue-200/80 text-sm space-y-1">
              <p><strong>1. Presione 2:</strong> Cuando el usuario presiona 2 durante una llamada, la mensagem de "opt_out" en el idioma detectado es reproducida.</p>
              <p><strong>2. Confirmación:</strong> Após el procesamiento, la mensagem de "confirmation" é enviada via SMS o nova chamada.</p>
              <p><strong>3. Detección de Idioma:</strong> O sistema detecta el idioma baseado en el código de país ou configuración da campanha.</p>
              <p><strong>4. TTS Automático:</strong> Se no houver arquivo de áudio, o sistema gera automaticamente usando Text-to-Speech.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DNCMultiLanguageManager; 