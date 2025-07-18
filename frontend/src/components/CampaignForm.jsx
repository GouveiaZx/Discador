import React, { useEffect, useState } from 'react';
import { makeApiRequest } from '../config/api';

function CampaignForm({ campaign, onSaved, onCancel }) {
    const [form, setForm] = useState({
    nombre: '', 
    descricao: '', 
    trunk_id: '', 
    cps: 10, 
    sleep_time: 1,
    wait_time: '0.5',
    dnc_list_id: '',
    language: 'es-AR',
    shuffle_contacts: true,
    allow_multiple_calls_same_number: false,
    press_2_audio_id: '',
    max_channels: 10,
  });
  
  const [trunks, setTrunks] = useState([]);
  const [audios, setAudios] = useState([]);
  const [dncLists, setDncLists] = useState([]);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [validationErrors, setValidationErrors] = useState({});
  const [showPreview, setShowPreview] = useState(false);

  useEffect(() => {
    if (campaign) {
      setForm({ ...form, ...campaign });
    }
    loadFormData();
  }, [campaign]);

  const loadFormData = async () => {
    setLoading(true);
    try {
      const [trunksRes, audiosRes, dncRes] = await Promise.all([
        makeApiRequest('/trunks'),
        makeApiRequest('/audios'),
        makeApiRequest('/dnc')
      ]);
      
      setTrunks(trunksRes.data || []);
      setAudios(audiosRes.data || []);
      setDncLists(dncRes.data || []);
    } catch (error) {
      setError('Erro ao carregar dados necessários');
    } finally {
      setLoading(false);
    }
  };

  const validateForm = () => {
    const errors = {};
    
    if (!form.nombre.trim()) {
      errors.nombre = 'Nombre de la campaña es obligatorio';
    }
    
    if (!form.trunk_id) {
      errors.trunk_id = 'Selecione um trunk';
    }
    
    if (form.cps < 1 || form.cps > 100) {
      errors.cps = 'CPS debe estar entre 1 y 100';
    }
    
    if (form.max_channels < 1 || form.max_channels > 1000) {
      errors.max_channels = 'Canales debe estar entre 1 y 1000';
    }
    
    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    const newValue = type === 'checkbox' ? checked : value;
    
    setForm({ ...form, [name]: newValue });
    
    // Limpiar error de validación cuando usuario corrija
    if (validationErrors[name]) {
      setValidationErrors({ ...validationErrors, [name]: '' });
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setSaving(true);
    setError(null);
    
    try {
      const method = campaign ? 'PUT' : 'POST';
      const url = campaign ? `/campaigns/${campaign.id}` : '/campaigns';
      
      await makeApiRequest(url, {
        method,
        body: JSON.stringify(form)
      });
      
      // Reset form only if creating new campaign
      if (!campaign) {
        setForm({
          nombre: '', 
          descricao: '', 
          trunk_id: '', 
          cps: 10, 
          sleep_time: 1, 
          wait_time: '0.5', 
          dnc_list_id: '', 
          language: 'es-AR', 
          shuffle_contacts: true, 
          allow_multiple_calls_same_number: false, 
          press_2_audio_id: '', 
          max_channels: 10,
        });
      }
      
      if (onSaved) onSaved();
    } catch (err) {
      setError('Error al guardar campaña. Verifique los datos e intente nuevamente.');
    } finally {
      setSaving(false);
    }
  };

  const getSelectedTrunk = () => {
    return trunks.find(t => t.id.toString() === form.trunk_id.toString());
  };

  const getSelectedAudio = () => {
    return audios.find(a => a.id.toString() === form.press_2_audio_id.toString());
  };

  const getSelectedDnc = () => {
    return dncLists.find(d => d.id.toString() === form.dnc_list_id.toString());
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-6">
        <div className="flex items-center justify-center py-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-gray-600">Cargando formulario...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg">
      <div className="px-6 py-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-gray-800">
              {campaign ? 'Editar Campaña' : 'Nueva Campaña'}
            </h2>
            <p className="text-gray-600 text-sm mt-1">
              Configure los parámetros avanzados de la campaña
            </p>
          </div>
          <div className="flex space-x-2">
            <button
              type="button"
              onClick={() => setShowPreview(!showPreview)}
              className="text-blue-600 hover:text-blue-700 text-sm font-medium"
            >
              {showPreview ? 'Ocultar' : 'Vista Previa'}
            </button>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="p-6">
        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
            <div className="flex">
              <svg className="w-5 h-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span className="text-red-700 text-sm">{error}</span>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Informações Básicas */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-800 border-b pb-2">Información Básica</h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nombre de la Campaña *
              </label>
              <input
                name="nombre"
                value={form.nombre}
                onChange={handleChange}
                placeholder="Ingrese el nombre de la campaña"
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  validationErrors.nombre ? 'border-red-300' : 'border-gray-300'
                }`}
                required
              />
              {validationErrors.nombre && (
                <p className="text-red-500 text-xs mt-1">{validationErrors.nombre}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Descripción
              </label>
              <textarea
                name="descricao"
                value={form.descricao}
                onChange={handleChange}
                placeholder="Descripción opcional de la campaña"
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Idioma
              </label>
              <select
                name="language"
                value={form.language}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="pt-BR">🇧🇷 Português (Brasileiro)</option>
                <option value="es-ES">🇪🇸 Espanhol</option>
                <option value="en-US">🇺🇸 Inglês</option>
              </select>
            </div>
          </div>

          {/* Configurações Técnicas */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-800 border-b pb-2">Configuraciones Técnicas</h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Trunk SIP *
              </label>
              <select
                name="trunk_id"
                value={form.trunk_id}
                onChange={handleChange}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                  validationErrors.trunk_id ? 'border-red-300' : 'border-gray-300'
                }`}
                required
              >
                <option value="">Selecione o Trunk</option>
                {trunks.map(t => (
                  <option key={t.id} value={t.id}>
                    {t.name} ({t.host}:{t.port})
                  </option>
                ))}
              </select>
              {validationErrors.trunk_id && (
                <p className="text-red-500 text-xs mt-1">{validationErrors.trunk_id}</p>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  CPS (Llamadas/s)
                </label>
                <input
                  name="cps"
                  type="number"
                  min="1"
                  max="100"
                  value={form.cps}
                  onChange={handleChange}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    validationErrors.cps ? 'border-red-300' : 'border-gray-300'
                  }`}
                />
                {validationErrors.cps && (
                  <p className="text-red-500 text-xs mt-1">{validationErrors.cps}</p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Canales Simultáneos
                </label>
                <input
                  name="max_channels"
                  type="number"
                  min="1"
                  max="1000"
                  value={form.max_channels}
                  onChange={handleChange}
                  className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent ${
                    validationErrors.max_channels ? 'border-red-300' : 'border-gray-300'
                  }`}
                />
                {validationErrors.max_channels && (
                  <p className="text-red-500 text-xs mt-1">{validationErrors.max_channels}</p>
                )}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Sleep Time (s)
                </label>
                <input
                  name="sleep_time"
                  type="number"
                  step="0.1"
                  min="0"
                  value={form.sleep_time}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Wait Time (s)
                </label>
                <input
                  name="wait_time"
                  step="0.1"
                  min="0"
                  value={form.wait_time}
                  onChange={handleChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>
            </div>
          </div>

          {/* Configurações Avançadas */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium text-gray-800 border-b pb-2">Configuraciones Avanzadas</h3>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Lista DNC (Opcional)
              </label>
              <select
                name="dnc_list_id"
                value={form.dnc_list_id}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Ninguna lista DNC</option>
                {dncLists.map(d => (
                  <option key={d.id} value={d.id}>
                    {d.name} ({d.total_numbers || 0} números)
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Audio Press 2 (Opcional)
              </label>
              <select
                name="press_2_audio_id"
                value={form.press_2_audio_id}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Ningún audio</option>
                {audios.map(a => (
                  <option key={a.id} value={a.id}>
                    {a.name} ({a.type})
                  </option>
                ))}
              </select>
            </div>

            <div className="space-y-3">
              <div className="flex items-center">
                <input
                  name="shuffle_contacts"
                  type="checkbox"
                  checked={form.shuffle_contacts}
                  onChange={handleChange}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label className="ml-2 block text-sm text-gray-700">
                  Mezclar contactos al iniciar campaña
                </label>
              </div>

              <div className="flex items-center">
                <input
                  name="allow_multiple_calls_same_number"
                  type="checkbox"
                  checked={form.allow_multiple_calls_same_number}
                  onChange={handleChange}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label className="ml-2 block text-sm text-gray-700">
                  Permitir múltiples llamadas al mismo número
                </label>
              </div>
            </div>
          </div>

          {/* Preview */}
          {showPreview && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-800 border-b pb-2">Vista Previa de la Configuración</h3>
              
              <div className="bg-gray-50 rounded-lg p-4 space-y-2 text-sm">
                <div><strong>Nombre:</strong> {form.nombre || 'No definido'}</div>
                <div><strong>Trunk:</strong> {getSelectedTrunk()?.name || 'No seleccionado'}</div>
                <div><strong>CPS:</strong> {form.cps} llamadas/segundo</div>
                <div><strong>Canales:</strong> {form.max_channels} simultáneos</div>
                <div><strong>Idioma:</strong> {form.language}</div>
                <div><strong>DNC:</strong> {getSelectedDnc()?.name || 'Ninguna'}</div>
                <div><strong>Audio Press 2:</strong> {getSelectedAudio()?.name || 'Ninguno'}</div>
                <div><strong>Mezclar:</strong> {form.shuffle_contacts ? 'Sí' : 'No'}</div>
                <div><strong>Múltiples llamadas:</strong> {form.allow_multiple_calls_same_number ? 'Sí' : 'No'}</div>
              </div>
            </div>
          )}
        </div>

        <div className="flex items-center justify-end space-x-3 mt-8 pt-6 border-t border-gray-200">
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="px-4 py-2 text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Cancelar
            </button>
          )}
          <button
            type="submit"
            disabled={saving}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
          >
            {saving && (
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
            )}
            {saving ? 'Guardando...' : (campaign ? 'Guardar Cambios' : 'Crear Campaña')}
          </button>
        </div>
      </form>
    </div>
  );
}

export default CampaignForm;