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
    { code: 'en', name: 'English', flag: '🇺🇸' },
    { code: 'es', name: 'Español', flag: '🇪🇸' },
    { code: 'pt', name: 'Português', flag: '🇧🇷' },
    { code: 'fr', name: 'Français', flag: '🇫🇷' },
    { code: 'de', name: 'Deutsch', flag: '🇩🇪' }
  ];

  const messageTypes = [
    { value: 'opt_out', label: 'Opt-Out (Pressione 2)', icon: '🚫' },
    { value: 'confirmation', label: 'Confirmação', icon: '✅' },
    { value: 'error', label: 'Erro', icon: '❌' }
  ];

  const templateMessages = {
    en: {
      opt_out: 'Thank you for your call. To remove your number from our calling list, please press 2 now. Your number will be removed within 24 hours. Thank you.',
      confirmation: 'Your number has been successfully removed from our calling list. You will not receive any more calls from us. Thank you.',
      error: 'We apologize, but there was an error processing your request. Please try again or contact our support team.'
    },
    es: {
      opt_out: 'Gracias por su llamada. Para remover su número de nuestra lista de llamadas, presione 2 ahora. Su número será removido en 24 horas. Gracias.',
      confirmation: 'Su número ha sido removido exitosamente de nuestra lista de llamadas. No recibirá más llamadas de nosotros. Gracias.',
      error: 'Disculpe, pero hubo un error procesando su solicitud. Por favor intente nuevamente o contacte nuestro equipo de soporte.'
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
      console.error('Erro ao carregar mensagens DNC:', error);
      // Usar dados mock se a API não existir
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
        // Simular atualização
        setMessages(prev => prev.map(msg => 
          msg.id === editingMessage.id 
            ? { ...msg, ...messageData, updated_at: new Date().toISOString() }
            : msg
        ));
      } else {
        // Simular criação
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
      console.error('Erro ao salvar mensagem:', error);
      alert('Erro ao salvar mensagem. Tente novamente.');
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
    if (window.confirm('Tem certeza que deseja excluir esta mensagem?')) {
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
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        <span className="ml-2 text-gray-600">Carregando mensagens DNC...</span>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      {/* Cabeçalho */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">🌍 Mensagens DNC Multi-idioma</h2>
          <p className="text-gray-600 mt-1">Configure mensagens de opt-out em diferentes idiomas</p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center transition-colors"
        >
          <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          Nova Mensagem
        </button>
      </div>

      {/* Filtros */}
      <div className="flex space-x-4 mb-6">
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-1">Filtrar por Idioma</label>
          <select
            value={selectedLanguage}
            onChange={(e) => setSelectedLanguage(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">Todos os idiomas</option>
            {languages.map(lang => (
              <option key={lang.code} value={lang.code}>
                {lang.flag} {lang.name}
              </option>
            ))}
          </select>
        </div>
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-1">Filtrar por Tipo</label>
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">Todos os tipos</option>
            {messageTypes.map(type => (
              <option key={type.value} value={type.value}>
                {type.icon} {type.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Formulário Modal */}
      {showForm && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-90vh overflow-y-auto">
            <h3 className="text-lg font-semibold mb-4">
              {editingMessage ? 'Editar Mensagem DNC' : 'Nova Mensagem DNC'}
            </h3>
            <form onSubmit={handleSubmit}>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Idioma</label>
                  <select
                    value={formData.language_code}
                    onChange={(e) => setFormData({...formData, language_code: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    required
                  >
                    <option value="">Selecione o idioma</option>
                    {languages.map(lang => (
                      <option key={lang.code} value={lang.code}>
                        {lang.flag} {lang.name}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Tipo de Mensagem</label>
                  <select
                    value={formData.message_type}
                    onChange={(e) => setFormData({...formData, message_type: e.target.value})}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
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
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">Título</label>
                <input
                  type="text"
                  value={formData.title}
                  onChange={(e) => setFormData({...formData, title: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Título da mensagem"
                  required
                />
              </div>
              
              <div className="mb-4">
                <div className="flex justify-between items-center mb-1">
                  <label className="block text-sm font-medium text-gray-700">Mensagem</label>
                  <button
                    type="button"
                    onClick={loadTemplate}
                    className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                  >
                    📋 Carregar Template
                  </button>
                </div>
                <textarea
                  value={formData.message}
                  onChange={(e) => setFormData({...formData, message: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={6}
                  placeholder="Digite a mensagem que será reproduzida..."
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  Esta mensagem será convertida em áudio ou reproduzida via TTS
                </p>
              </div>
              
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">Arquivo de Áudio (opcional)</label>
                <input
                  type="file"
                  accept="audio/*"
                  onChange={(e) => setFormData({...formData, audio_file: e.target.files[0]})}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Se não fornecido, será usado TTS para gerar o áudio
                </p>
              </div>
              
              <div className="mb-4">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={formData.is_active}
                    onChange={(e) => setFormData({...formData, is_active: e.target.checked})}
                    className="rounded text-blue-600"
                  />
                  <span className="text-sm font-medium text-gray-700">Mensagem ativa</span>
                </label>
              </div>
              
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  onClick={() => {
                    setShowForm(false);
                    resetForm();
                  }}
                  className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  {editingMessage ? 'Atualizar' : 'Criar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Lista de Mensagens */}
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
        {filteredMessages.length === 0 ? (
          <div className="col-span-full text-center py-12">
            <div className="text-6xl mb-4 opacity-50">🌐</div>
            <h3 className="mt-2 text-sm font-medium text-gray-900">Nenhuma mensagem encontrada</h3>
            <p className="mt-1 text-sm text-gray-500">Crie mensagens DNC para diferentes idiomas</p>
          </div>
        ) : (
          filteredMessages.map((message) => (
            <div key={message.id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  <span className="text-2xl">{getLanguageFlag(message.language_code)}</span>
                  <span className="text-xl">{getTypeIcon(message.message_type)}</span>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800">{message.title}</h3>
                    <p className="text-sm text-gray-500">{message.language_name}</p>
                  </div>
                </div>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  message.is_active 
                    ? 'bg-green-100 text-green-800' 
                    : 'bg-red-100 text-red-800'
                }`}>
                  {message.is_active ? 'Ativa' : 'Inativa'}
                </span>
              </div>
              
              <div className="space-y-2 text-sm text-gray-600 mb-4">
                <div className="flex justify-between">
                  <span className="font-medium">Tipo:</span>
                  <span className="capitalize">{messageTypes.find(t => t.value === message.message_type)?.label}</span>
                </div>
                <div>
                  <span className="font-medium">Mensagem:</span>
                  <p className="text-xs text-gray-500 mt-1 leading-relaxed line-clamp-3">
                    {message.message}
                  </p>
                </div>
              </div>
              
              <div className="flex justify-between items-center pt-3 border-t">
                <button
                  onClick={() => handleEdit(message)}
                  className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                >
                  Editar
                </button>
                <button
                  onClick={() => handleDelete(message.id)}
                  className="text-red-600 hover:text-red-800 text-sm font-medium"
                >
                  Excluir
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Demonstração de Uso */}
      <div className="mt-8 bg-gray-50 rounded-lg p-4">
        <h4 className="font-semibold text-gray-800 mb-2">💡 Como Funciona</h4>
        <div className="text-sm text-gray-600 space-y-2">
          <p><strong>1. Pressionar 2:</strong> Quando o usuário pressiona 2 durante uma chamada, a mensagem de "opt_out" no idioma detectado é reproduzida.</p>
          <p><strong>2. Confirmação:</strong> Após o processamento, a mensagem de "confirmation" é enviada via SMS ou nova chamada.</p>
          <p><strong>3. Detecção de Idioma:</strong> O sistema detecta o idioma baseado no código do país ou configuração da campanha.</p>
          <p><strong>4. TTS Automático:</strong> Se não houver arquivo de áudio, o sistema gera automaticamente usando Text-to-Speech.</p>
        </div>
      </div>
    </div>
  );
};

export default DNCMultiLanguageManager; 