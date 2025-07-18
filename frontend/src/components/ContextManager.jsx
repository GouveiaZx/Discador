import React, { useState, useEffect } from 'react';
import { makeApiRequest } from '../services/api';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Textarea } from './ui/textarea';
import { Select } from './ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Badge } from './ui/badge';
import { Alert } from './ui/alert';
import { Switch } from './ui/switch';
import { PlayIcon, PauseIcon, UploadIcon, DownloadIcon, TrashIcon, EditIcon, TestTubeIcon } from 'lucide-react';

const ContextManager = () => {
  const [activeTab, setActiveTab] = useState('contexts');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Estados para contextos
  const [contexts, setContexts] = useState([]);
  const [showContextForm, setShowContextForm] = useState(false);
  const [editingContext, setEditingContext] = useState(null);
  
  const [contextForm, setContextForm] = useState({
    nome: '',
    descricao: '',
    numeros_transferencia: '3', // Números para transferir (ex: 3,4 ou 1,2,3,4,5)
    numeros_exclusao: '9', // Números para excluir da lista (ex: 9 ou 0,9)
    audio_principal_id: null, // Áudio de interação principal
    audio_espera_id: null, // Áudio de espera para transferência
    timeout_resposta: 10, // Timeout em segundos para resposta
    tentativas_maximas: 3, // Máximo de tentativas
    trunk_transferencia_id: '',
    bridge_number: '',
    ativo: true,
    configuracoes_avancadas: {
      detectar_caixa_postal: true,
      tempo_deteccao_humano: 3000,
      volume_audio: 80,
      repetir_audio: false,
      intervalo_repeticao: 5000
    }
  });
  
  // Estados para áudios
  const [audios, setAudios] = useState([]);
  const [showAudioForm, setShowAudioForm] = useState(false);
  const [editingAudio, setEditingAudio] = useState(null);
  const [audioPreview, setAudioPreview] = useState(null);
  const [audioForm, setAudioForm] = useState({
    nome: '',
    arquivo: null,
    tipo: 'interacao', // interacao, espera, sistema
    duracao: 0,
    formato: 'wav',
    qualidade: 'alta',
    volume_padrao: 80,
    ativo: true,
    descricao: ''
  });
  
  // Estados para trunks de transferência
  const [transferTrunks, setTransferTrunks] = useState([]);
  const [showTrunkForm, setShowTrunkForm] = useState(false);
  const [trunkForm, setTrunkForm] = useState({
    nome: '',
    tipo: 'voip', // voip, pstn
    host: '',
    porta: '5060',
    usuario: '',
    senha: '',
    contexto: 'from-transfer',
    bridge_number: '',
    codec: 'ulaw,alaw',
    ativo: true
  });
  
  // Estados para timer de operação
  const [timerConfig, setTimerConfig] = useState({
    horario_inicio: '08:00',
    horario_fim: '18:00',
    horario_almoco_inicio: '12:00',
    horario_almoco_fim: '13:00',
    dias_semana: ['segunda', 'terca', 'quarta', 'quinta', 'sexta'],
    timezone: 'America/Sao_Paulo',
    ativo: true
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        fetchContexts(),
        fetchAudios(),
        fetchTransferTrunks(),
        fetchTimerConfig()
      ]);
    } catch (err) {
      setError('Erro ao carregar dados: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchContexts = async () => {
    try {
      const response = await makeApiRequest('/contexts');
      setContexts(response.contexts || []);
    } catch (err) {
      console.error('Erro ao buscar contextos:', err);
    }
  };

  const fetchAudios = async () => {
    try {
      const response = await makeApiRequest('/audios');
      setAudios(response.audios || []);
    } catch (err) {
      console.error('Erro ao buscar áudios:', err);
    }
  };

  const fetchTransferTrunks = async () => {
    try {
      const response = await makeApiRequest('/transfer-trunks');
      setTransferTrunks(response.trunks || []);
    } catch (err) {
      console.error('Erro ao buscar trunks de transferência:', err);
    }
  };

  const fetchTimerConfig = async () => {
    try {
      const response = await makeApiRequest('/timer-config');
      if (response.config) {
        setTimerConfig(response.config);
      }
    } catch (err) {
      console.error('Erro ao buscar configuração de timer:', err);
    }
  };

  const handleContextSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      
      if (editingContext) {
        await makeApiRequest(`/contexts/${editingContext.id}`, 'PUT', contextForm);
        setSuccess('Contexto atualizado com sucesso!');
      } else {
        await makeApiRequest('/contexts', 'POST', contextForm);
        setSuccess('Contexto criado com sucesso!');
      }
      
      await fetchContexts();
      resetContextForm();
    } catch (err) {
      setError('Erro ao salvar contexto: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAudioUpload = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      
      const formData = new FormData();
      formData.append('nome', audioForm.nome);
      formData.append('arquivo', audioForm.arquivo);
      formData.append('tipo', audioForm.tipo);
      formData.append('duracao_maxima', audioForm.duracao_maxima);
      formData.append('descricao', audioForm.descricao);
      
      await makeApiRequest('/audios', 'POST', formData, {
        'Content-Type': 'multipart/form-data'
      });
      
      await fetchAudios();
      resetAudioForm();
      setSuccess('Áudio enviado com sucesso!');
    } catch (err) {
      setError('Erro ao enviar áudio: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTrunkSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      
      await makeApiRequest('/transfer-trunks', 'POST', trunkForm);
      await fetchTransferTrunks();
      resetTrunkForm();
      setSuccess('Trunk de transferência criado com sucesso!');
    } catch (err) {
      setError('Erro ao criar trunk: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleTimerSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      
      await makeApiRequest('/timer-config', 'PUT', timerConfig);
      setSuccess('Configuração de timer atualizada com sucesso!');
    } catch (err) {
      setError('Erro ao salvar configuração de timer: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const resetContextForm = () => {
    setContextForm({
      nome: '',
      descricao: '',
      numeros_transferencia: '3',
      numeros_exclusao: '9',
      audio_principal_id: null,
      audio_espera_id: null,
      timeout_resposta: 10,
      tentativas_maximas: 3,
      trunk_transferencia_id: '',
      bridge_number: '',
      ativo: true,
      configuracoes_avancadas: {
        detectar_caixa_postal: true,
        tempo_deteccao_humano: 3000,
        volume_audio: 80,
        repetir_audio: false,
        intervalo_repeticao: 5000
      }
    });
    setEditingContext(null);
    setShowContextForm(false);
  };

  const resetAudioForm = () => {
    setAudioForm({
      nome: '',
      arquivo: null,
      tipo: 'interacao',
      duracao: 0,
      formato: 'wav',
      qualidade: 'alta',
      volume_padrao: 80,
      ativo: true,
      descricao: ''
    });
    setEditingAudio(null);
    setShowAudioForm(false);
    setAudioPreview(null);
  };

  const resetTrunkForm = () => {
    setTrunkForm({
      nome: '',
      tipo: 'voip',
      host: '',
      porta: '5060',
      usuario: '',
      senha: '',
      contexto: 'from-transfer',
      bridge_number: '',
      codec: 'ulaw,alaw',
      ativo: true
    });
    setShowTrunkForm(false);
  };

  const playAudio = async (audioId) => {
    try {
      if (audioPreview === audioId) {
        setAudioPreview(null);
        return;
      }
      
      const response = await makeApiRequest(`/audios/${audioId}/play`, 'GET');
      if (response.success) {
        setAudioPreview(audioId);
        // Simular reprodução por 3 segundos
        setTimeout(() => setAudioPreview(null), 3000);
      }
    } catch (err) {
      setError('Erro ao reproduzir áudio: ' + err.message);
    }
  };

  const downloadAudio = async (audioId, nome) => {
    try {
      const response = await makeApiRequest(`/audios/${audioId}/download`, 'GET');
      if (response.success) {
        // Simular download
        const link = document.createElement('a');
        link.href = response.data.url;
        link.download = `${nome}.wav`;
        link.click();
        setSuccess('Download iniciado!');
      }
    } catch (err) {
      setError('Erro ao baixar áudio: ' + err.message);
    }
  };

  const editAudio = (audio) => {
    setEditingAudio(audio.id);
    setAudioForm({
      nome: audio.nome,
      arquivo: null,
      tipo: audio.tipo,
      duracao: audio.duracao,
      formato: audio.formato,
      qualidade: audio.qualidade,
      volume_padrao: audio.volume_padrao,
      ativo: audio.ativo,
      descricao: audio.descricao
    });
    setShowAudioForm(true);
  };

  const editContext = (context) => {
    setEditingContext(context);
    setContextForm({
      ...context,
      configuracoes_avancadas: {
        detectar_caixa_postal: context.configuracoes_avancadas?.detectar_caixa_postal || true,
        tempo_deteccao_humano: context.configuracoes_avancadas?.tempo_deteccao_humano || 3000,
        volume_audio: context.configuracoes_avancadas?.volume_audio || 80,
        repetir_audio: context.configuracoes_avancadas?.repetir_audio || false,
        intervalo_repeticao: context.configuracoes_avancadas?.intervalo_repeticao || 5000
      }
    });
    setShowContextForm(true);
  };

  const deleteContext = async (contextId) => {
    if (!confirm('Tem certeza que deseja excluir este contexto?')) return;
    
    try {
      setLoading(true);
      await makeApiRequest(`/contexts/${contextId}`, 'DELETE');
      await fetchContexts();
      setSuccess('Contexto excluído com sucesso!');
    } catch (err) {
      setError('Erro ao excluir contexto: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteAudio = async (audioId) => {
    if (!confirm('Tem certeza que deseja excluir este áudio?')) return;

    try {
      setLoading(true);
      await makeApiRequest(`/audios/${audioId}`, 'DELETE');
      await fetchAudios();
      setSuccess('Áudio excluído com sucesso!');
    } catch (err) {
      setError('Erro ao excluir áudio: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Validar tipo de arquivo
      const allowedTypes = ['audio/wav', 'audio/mp3', 'audio/ogg'];
      if (!allowedTypes.includes(file.type)) {
        setError('Formato de arquivo não suportado. Use WAV, MP3 ou OGG.');
        return;
      }
      
      // Validar tamanho (máximo 10MB)
      if (file.size > 10 * 1024 * 1024) {
        setError('Arquivo muito grande. Máximo 10MB.');
        return;
      }
      
      setAudioForm(prev => ({ ...prev, arquivo: file }));
      
      // Obter duração do áudio
      const audio = new Audio();
      audio.src = URL.createObjectURL(file);
      audio.onloadedmetadata = () => {
        setAudioForm(prev => ({ ...prev, duracao: Math.round(audio.duration) }));
      };
    }
  };

  const formatDTMFNumbers = (numbers) => {
    if (!numbers) return 'Nenhum';
    return numbers.split(',').map(n => n.trim()).join(', ');
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Gestão de Contextos e Áudios</h1>
      </div>

      {error && (
        <Alert className="border-red-200 bg-red-50">
          <div className="text-red-800">{error}</div>
        </Alert>
      )}

      {success && (
        <Alert className="border-green-200 bg-green-50">
          <div className="text-green-800">{success}</div>
        </Alert>
      )}

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="contexts">Contextos DTMF</TabsTrigger>
          <TabsTrigger value="audios">Gestão de Áudios</TabsTrigger>
          <TabsTrigger value="trunks">Trunks Transferência</TabsTrigger>
          <TabsTrigger value="timer">Timer Operação</TabsTrigger>
        </TabsList>

        <TabsContent value="contexts" className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Contextos DTMF</h2>
            <Button 
              onClick={() => setShowContextForm(!showContextForm)}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {showContextForm ? 'Cancelar' : 'Novo Contexto'}
            </Button>
          </div>

          {showContextForm && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">
                {editingContext ? 'Editar Contexto' : 'Novo Contexto DTMF'}
              </h3>
              
              <form onSubmit={handleContextSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="nome">Nome do Contexto</Label>
                    <Input
                      id="nome"
                      value={contextForm.nome}
                      onChange={(e) => setContextForm({...contextForm, nome: e.target.value})}
                      placeholder="Ex: Contexto Principal"
                      required
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="timeout_resposta">Timeout Resposta (segundos)</Label>
                    <Input
                      id="timeout_resposta"
                      type="number"
                      value={contextForm.timeout_resposta}
                      onChange={(e) => setContextForm({...contextForm, timeout_resposta: parseInt(e.target.value)})}
                      min="5"
                      max="60"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="audio_principal_id">Áudio de Interação</Label>
                    <Select
                      value={contextForm.audio_principal_id || ''}
                      onValueChange={(value) => setContextForm({...contextForm, audio_principal_id: value || null})}
                    >
                      <option value="">Selecione um áudio</option>
                      {audios.filter(a => a.tipo === 'interacao' && a.ativo).map(audio => (
                        <option key={audio.id} value={audio.id}>{audio.nome}</option>
                      ))}
                    </Select>
                    <div className="text-xs text-gray-500 mt-1">
                      Áudio que dá as instruções ao cliente
                    </div>
                  </div>
                  
                  <div>
                    <Label htmlFor="audio_espera_id">Áudio de Espera</Label>
                    <Select
                      value={contextForm.audio_espera_id || ''}
                      onValueChange={(value) => setContextForm({...contextForm, audio_espera_id: value || null})}
                    >
                      <option value="">Selecione um áudio</option>
                      {audios.filter(a => a.tipo === 'espera' && a.ativo).map(audio => (
                        <option key={audio.id} value={audio.id}>{audio.nome}</option>
                      ))}
                    </Select>
                    <div className="text-xs text-gray-500 mt-1">
                      Áudio tocado enquanto aguarda transferência
                    </div>
                  </div>
                  
                  <div>
                    <Label htmlFor="numeros_transferencia">Números de Transferência</Label>
                    <Input
                      id="numeros_transferencia"
                      value={contextForm.numeros_transferencia}
                      onChange={(e) => setContextForm({...contextForm, numeros_transferencia: e.target.value})}
                      placeholder="Ex: 3 ou 1,2,3,4,5"
                    />
                    <div className="text-xs text-gray-500 mt-1">
                      Teclas DTMF para transferir para agente (separadas por vírgula)
                    </div>
                    <div className="text-xs text-blue-600 mt-1">
                      Exemplos: "3" (apenas tecla 3) ou "1,2,3,4,5" (múltiplas opções)
                    </div>
                  </div>
                  
                  <div>
                    <Label htmlFor="numeros_exclusao">Números de Exclusão</Label>
                    <Input
                      id="numeros_exclusao"
                      value={contextForm.numeros_exclusao}
                      onChange={(e) => setContextForm({...contextForm, numeros_exclusao: e.target.value})}
                      placeholder="Ex: 9 ou 0,9"
                    />
                    <div className="text-xs text-gray-500 mt-1">
                      Teclas DTMF para remover da lista de chamadas (separadas por vírgula)
                    </div>
                    <div className="text-xs text-blue-600 mt-1">
                      Exemplos: "9" (apenas tecla 9) ou "0,9" (teclas 0 e 9)
                    </div>
                  </div>
                  
                  <div>
                    <Label htmlFor="tentativas_maximas">Tentativas Máximas</Label>
                    <Input
                      id="tentativas_maximas"
                      type="number"
                      value={contextForm.tentativas_maximas}
                      onChange={(e) => setContextForm({...contextForm, tentativas_maximas: parseInt(e.target.value)})}
                      min="1"
                      max="5"
                    />
                    <div className="text-xs text-gray-500 mt-1">
                      Número máximo de tentativas
                    </div>
                  </div>
                  
                  <div>
                    <Label htmlFor="trunk_transferencia_id">Trunk de Transferência</Label>
                    <Select
                      value={contextForm.trunk_transferencia_id}
                      onValueChange={(value) => setContextForm({...contextForm, trunk_transferencia_id: value})}
                    >
                      <option value="">Selecione um trunk</option>
                      {transferTrunks.map(trunk => (
                        <option key={trunk.id} value={trunk.id}>{trunk.nome} ({trunk.tipo})</option>
                      ))}
                    </Select>
                    <div className="text-xs text-gray-500 mt-1">
                      Trunk usado para transferir chamadas
                    </div>
                  </div>
                  
                  <div>
                    <Label htmlFor="bridge_number">Bridge Number</Label>
                    <Input
                      id="bridge_number"
                      value={contextForm.bridge_number}
                      onChange={(e) => setContextForm({...contextForm, bridge_number: e.target.value})}
                      placeholder="Ex: 1001 ou 5511999999999"
                    />
                    <div className="text-xs text-gray-500 mt-1">
                      Extensão ou número para transferência
                    </div>
                  </div>
                </div>
                
                {/* Configurações Avançadas */}
                <div className="border-t pt-4">
                  <h4 className="text-lg font-medium text-gray-900 mb-4">Configurações Avançadas</h4>
                  
                  <div className="grid grid-cols-2 gap-4">
                    <div className="flex items-center space-x-2">
                      <Switch
                        id="detectar-caixa-postal"
                        checked={contextForm.configuracoes_avancadas.detectar_caixa_postal}
                        onCheckedChange={(checked) => setContextForm(prev => ({
                          ...prev,
                          configuracoes_avancadas: {
                            ...prev.configuracoes_avancadas,
                            detectar_caixa_postal: checked
                          }
                        }))}
                      />
                      <Label htmlFor="detectar-caixa-postal">Detectar caixa postal</Label>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <Switch
                        id="repetir-audio"
                        checked={contextForm.configuracoes_avancadas.repetir_audio}
                        onCheckedChange={(checked) => setContextForm(prev => ({
                          ...prev,
                          configuracoes_avancadas: {
                            ...prev.configuracoes_avancadas,
                            repetir_audio: checked
                          }
                        }))}
                      />
                      <Label htmlFor="repetir-audio">Repetir áudio automaticamente</Label>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-3 gap-4 mt-4">
                    <div>
                      <Label htmlFor="tempo-deteccao">Tempo Detecção Humano (ms)</Label>
                      <Input
                        id="tempo-deteccao"
                        type="number"
                        value={contextForm.configuracoes_avancadas.tempo_deteccao_humano}
                        onChange={(e) => setContextForm(prev => ({
                          ...prev,
                          configuracoes_avancadas: {
                            ...prev.configuracoes_avancadas,
                            tempo_deteccao_humano: parseInt(e.target.value)
                          }
                        }))}
                        min="1000"
                        max="10000"
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        Tempo para detectar se é humano ou máquina
                      </p>
                    </div>
                    
                    <div>
                      <Label htmlFor="volume-audio">Volume do Áudio (%)</Label>
                      <Input
                        id="volume-audio"
                        type="number"
                        value={contextForm.configuracoes_avancadas.volume_audio}
                        onChange={(e) => setContextForm(prev => ({
                          ...prev,
                          configuracoes_avancadas: {
                            ...prev.configuracoes_avancadas,
                            volume_audio: parseInt(e.target.value)
                          }
                        }))}
                        min="10"
                        max="100"
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        Volume de reprodução dos áudios
                      </p>
                    </div>
                    
                    <div>
                      <Label htmlFor="intervalo-repeticao">Intervalo Repetição (ms)</Label>
                      <Input
                        id="intervalo-repeticao"
                        type="number"
                        value={contextForm.configuracoes_avancadas.intervalo_repeticao}
                        onChange={(e) => setContextForm(prev => ({
                          ...prev,
                          configuracoes_avancadas: {
                            ...prev.configuracoes_avancadas,
                            intervalo_repeticao: parseInt(e.target.value)
                          }
                        }))}
                        min="1000"
                        max="30000"
                        disabled={!contextForm.configuracoes_avancadas.repetir_audio}
                      />
                      <p className="text-xs text-gray-500 mt-1">
                        Intervalo entre repetições do áudio
                      </p>
                    </div>
                  </div>
                </div>
                
                <div>
                  <Label htmlFor="descricao">Descrição</Label>
                  <Input
                    id="descricao"
                    value={contextForm.descricao}
                    onChange={(e) => setContextForm({...contextForm, descricao: e.target.value})}
                    placeholder="Descrição do contexto"
                  />
                </div>
                
                <div className="flex items-center space-x-2">
                  <Switch
                    id="context_ativo"
                    checked={contextForm.ativo}
                    onCheckedChange={(checked) => setContextForm({...contextForm, ativo: checked})}
                  />
                  <Label htmlFor="context_ativo">Contexto ativo</Label>
                </div>
                
                <div className="flex space-x-2">
                  <Button type="submit" disabled={loading}>
                    {loading ? 'Salvando...' : (editingContext ? 'Atualizar' : 'Criar')}
                  </Button>
                  <Button type="button" variant="outline" onClick={resetContextForm}>
                    Cancelar
                  </Button>
                </div>
              </form>
            </Card>
          )}

          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Contextos Existentes</h3>
            
            {contexts.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                Nenhum contexto encontrado. Crie seu primeiro contexto DTMF.
              </div>
            ) : (
              <div className="space-y-4">
                {contexts.map((context) => (
                  <div key={context.id} className="border rounded-lg p-4 hover:bg-gray-50">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h4 className="font-medium text-gray-900">{context.nome}</h4>
                          <Badge className={context.ativo ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}>
                            {context.ativo ? 'Ativo' : 'Inativo'}
                          </Badge>
                          {context.configuracoes_avancadas?.detectar_caixa_postal && (
                            <Badge className="bg-blue-100 text-blue-800">
                              Detecta VM
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-gray-600 mb-3">{context.descricao}</p>
                        
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
                          <div className="bg-gray-50 p-2 rounded">
                            <div className="font-medium text-gray-700">Transferência</div>
                            <div className="text-gray-600">{formatDTMFNumbers(context.numeros_transferencia)}</div>
                          </div>
                          <div className="bg-gray-50 p-2 rounded">
                            <div className="font-medium text-gray-700">Exclusão</div>
                            <div className="text-gray-600">{formatDTMFNumbers(context.numeros_exclusao || context.numeros_eliminacao)}</div>
                          </div>
                          <div className="bg-gray-50 p-2 rounded">
                            <div className="font-medium text-gray-700">Timeout</div>
                            <div className="text-gray-600">{context.timeout_resposta || context.timeout_dtmf}s</div>
                          </div>
                        </div>
                        
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm mt-2">
                          <div className="bg-gray-50 p-2 rounded">
                            <div className="font-medium text-gray-700">Tentativas</div>
                            <div className="text-gray-600">{context.tentativas_maximas || 3}</div>
                          </div>
                          <div className="bg-gray-50 p-2 rounded">
                            <div className="font-medium text-gray-700">Bridge</div>
                            <div className="text-gray-600">{context.bridge_number || 'N/A'}</div>
                          </div>
                          <div className="bg-gray-50 p-2 rounded">
                            <div className="font-medium text-gray-700">Volume</div>
                            <div className="text-gray-600">{context.configuracoes_avancadas?.volume_audio || 80}%</div>
                          </div>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => editContext(context)}
                          className="flex items-center space-x-1"
                        >
                          <EditIcon className="h-4 w-4" />
                          <span>Editar</span>
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="border-red-300 text-red-600 hover:bg-red-50 flex items-center space-x-1"
                          onClick={() => deleteContext(context.id)}
                        >
                          <TrashIcon className="h-4 w-4" />
                          <span>Excluir</span>
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </TabsContent>

        <TabsContent value="audios" className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Gestão de Áudios</h2>
            <Button 
              onClick={() => setShowAudioForm(!showAudioForm)}
              className="bg-green-600 hover:bg-green-700"
            >
              {showAudioForm ? 'Cancelar' : 'Novo Áudio'}
            </Button>
          </div>

          {showAudioForm && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Upload de Áudio</h3>
              
              <form onSubmit={handleAudioUpload} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="audio_nome">Nome do Áudio</Label>
                    <Input
                      id="audio_nome"
                      value={audioForm.nome}
                      onChange={(e) => setAudioForm({...audioForm, nome: e.target.value})}
                      placeholder="Ex: Mensagem Principal"
                      required
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="audio_tipo">Tipo de Áudio</Label>
                    <Select
                      value={audioForm.tipo}
                      onValueChange={(value) => setAudioForm({...audioForm, tipo: value})}
                    >
                      <option value="interacao">Interação Principal</option>
                      <option value="espera">Espera para Transferência</option>
                      <option value="sistema">Sistema/Outros</option>
                    </Select>
                  </div>
                  
                  <div>
                    <Label htmlFor="audio_arquivo">Arquivo de Áudio</Label>
                    <Input
                      id="audio_arquivo"
                      type="file"
                      accept=".wav,.mp3,.ogg"
                      onChange={handleFileChange}
                      required
                    />
                    <div className="text-xs text-gray-500 mt-1">
                      Formatos aceitos: WAV, MP3, OGG
                    </div>
                    {audioForm.duracao > 0 && (
                      <div className="text-xs text-blue-600 mt-1">
                        Duração: {audioForm.duracao}s
                      </div>
                    )}
                  </div>
                  
                  <div>
                    <Label htmlFor="audio_formato">Formato</Label>
                    <Select
                      value={audioForm.formato}
                      onValueChange={(value) => setAudioForm({...audioForm, formato: value})}
                    >
                      <option value="wav">WAV (Recomendado)</option>
                      <option value="mp3">MP3</option>
                      <option value="ogg">OGG</option>
                    </Select>
                  </div>
                  
                  <div>
                    <Label htmlFor="audio_qualidade">Qualidade</Label>
                    <Select
                      value={audioForm.qualidade}
                      onValueChange={(value) => setAudioForm({...audioForm, qualidade: value})}
                    >
                      <option value="alta">Alta (16kHz)</option>
                      <option value="media">Média (8kHz)</option>
                      <option value="baixa">Baixa (4kHz)</option>
                    </Select>
                  </div>
                  
                  <div>
                    <Label htmlFor="audio_volume">Volume Padrão (%)</Label>
                    <Input
                      id="audio_volume"
                      type="number"
                      value={audioForm.volume_padrao}
                      onChange={(e) => setAudioForm({...audioForm, volume_padrao: parseInt(e.target.value)})}
                      min="10"
                      max="100"
                    />
                  </div>
                </div>
                
                <div>
                  <Label htmlFor="audio_descricao">Descrição</Label>
                  <Textarea
                    id="audio_descricao"
                    value={audioForm.descricao}
                    onChange={(e) => setAudioForm({...audioForm, descricao: e.target.value})}
                    placeholder="Descrição detalhada do áudio e seu uso"
                    rows={3}
                  />
                </div>
                
                <div className="flex items-center space-x-2">
                  <Switch
                    id="audio_ativo"
                    checked={audioForm.ativo}
                    onCheckedChange={(checked) => setAudioForm({...audioForm, ativo: checked})}
                  />
                  <Label htmlFor="audio_ativo">Áudio ativo</Label>
                </div>
                
                <div className="flex space-x-2">
                  <Button type="submit" disabled={loading}>
                    {loading ? 'Salvando...' : (editingAudio ? 'Atualizar Áudio' : 'Criar Áudio')}
                  </Button>
                  <Button type="button" variant="outline" onClick={resetAudioForm}>
                    Cancelar
                  </Button>
                </div>
              </form>
            </Card>
          )}

          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Áudios Disponíveis</h3>
            
            <div className="space-y-4">
              {audios.map((audio) => (
                <div key={audio.id} className="border rounded-lg p-4 hover:bg-gray-50">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h4 className="font-medium text-gray-900">{audio.nome}</h4>
                        <Badge className={audio.tipo === 'interacao' ? "bg-blue-100 text-blue-800" : audio.tipo === 'espera' ? "bg-purple-100 text-purple-800" : "bg-gray-100 text-gray-800"}>
                          {audio.tipo === 'interacao' ? 'Interação' : audio.tipo === 'espera' ? 'Espera' : 'Sistema'}
                        </Badge>
                        <Badge className={audio.ativo ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}>
                          {audio.ativo ? 'Ativo' : 'Inativo'}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{audio.descricao}</p>
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs text-gray-500">
                        <div>Duração: {audio.duracao || 'N/A'}s</div>
                        <div>Formato: {audio.formato?.toUpperCase() || 'N/A'}</div>
                        <div>Qualidade: {audio.qualidade || 'N/A'}</div>
                        <div>Volume: {audio.volume_padrao || 80}%</div>
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => playAudio(audio.id)}
                        className="flex items-center space-x-1"
                      >
                        {audioPreview === audio.id ? (
                          <PauseIcon className="h-4 w-4" />
                        ) : (
                          <PlayIcon className="h-4 w-4" />
                        )}
                        <span>{audioPreview === audio.id ? 'Pausar' : 'Reproduzir'}</span>
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => downloadAudio(audio.id, audio.nome)}
                        className="flex items-center space-x-1"
                      >
                        <DownloadIcon className="h-4 w-4" />
                        <span>Download</span>
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => editAudio(audio)}
                        className="flex items-center space-x-1"
                      >
                        <EditIcon className="h-4 w-4" />
                        <span>Editar</span>
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="border-red-300 text-red-600 hover:bg-red-50 flex items-center space-x-1"
                        onClick={() => deleteAudio(audio.id)}
                      >
                        <TrashIcon className="h-4 w-4" />
                        <span>Excluir</span>
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="trunks" className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Trunks de Transferência</h2>
            <Button 
              onClick={() => setShowTrunkForm(!showTrunkForm)}
              className="bg-purple-600 hover:bg-purple-700"
            >
              {showTrunkForm ? 'Cancelar' : 'Novo Trunk'}
            </Button>
          </div>

          {showTrunkForm && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Novo Trunk de Transferência</h3>
              
              <form onSubmit={handleTrunkSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="trunk_nome">Nome do Trunk</Label>
                    <Input
                      id="trunk_nome"
                      value={trunkForm.nome}
                      onChange={(e) => setTrunkForm({...trunkForm, nome: e.target.value})}
                      placeholder="Ex: Cliente Principal"
                      required
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="trunk_tipo">Tipo</Label>
                    <Select
                      value={trunkForm.tipo}
                      onValueChange={(value) => setTrunkForm({...trunkForm, tipo: value})}
                    >
                      <option value="voip">VoIP</option>
                      <option value="pstn">PSTN</option>
                    </Select>
                  </div>
                  
                  {trunkForm.tipo === 'voip' && (
                    <>
                      <div>
                        <Label htmlFor="trunk_host">Host</Label>
                        <Input
                          id="trunk_host"
                          value={trunkForm.host}
                          onChange={(e) => setTrunkForm({...trunkForm, host: e.target.value})}
                          placeholder="Ex: sip.cliente.com"
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="trunk_porta">Porta</Label>
                        <Input
                          id="trunk_porta"
                          value={trunkForm.porta}
                          onChange={(e) => setTrunkForm({...trunkForm, porta: e.target.value})}
                          placeholder="5060"
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="trunk_usuario">Usuário</Label>
                        <Input
                          id="trunk_usuario"
                          value={trunkForm.usuario}
                          onChange={(e) => setTrunkForm({...trunkForm, usuario: e.target.value})}
                          placeholder="Usuário SIP"
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="trunk_senha">Senha</Label>
                        <Input
                          id="trunk_senha"
                          type="password"
                          value={trunkForm.senha}
                          onChange={(e) => setTrunkForm({...trunkForm, senha: e.target.value})}
                          placeholder="Senha SIP"
                        />
                      </div>
                    </>
                  )}
                  
                  <div>
                    <Label htmlFor="trunk_bridge_number">Bridge Number</Label>
                    <Input
                      id="trunk_bridge_number"
                      value={trunkForm.bridge_number}
                      onChange={(e) => setTrunkForm({...trunkForm, bridge_number: e.target.value})}
                      placeholder="Ex: 1001 ou +5511999999999"
                    />
                    <div className="text-xs text-gray-500 mt-1">
                      Extensão VoIP ou número telefônico regular
                    </div>
                  </div>
                  
                  <div>
                    <Label htmlFor="trunk_contexto">Contexto</Label>
                    <Input
                      id="trunk_contexto"
                      value={trunkForm.contexto}
                      onChange={(e) => setTrunkForm({...trunkForm, contexto: e.target.value})}
                      placeholder="from-transfer"
                    />
                  </div>
                </div>
                
                <div className="flex space-x-2">
                  <Button type="submit" disabled={loading}>
                    {loading ? 'Criando...' : 'Criar Trunk'}
                  </Button>
                  <Button type="button" variant="outline" onClick={resetTrunkForm}>
                    Cancelar
                  </Button>
                </div>
              </form>
            </Card>
          )}

          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Trunks de Transferência</h3>
            
            <div className="space-y-4">
              {transferTrunks.map((trunk) => (
                <div key={trunk.id} className="border rounded-lg p-4 hover:bg-gray-50">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h4 className="font-medium text-gray-900">{trunk.nome}</h4>
                        <Badge className={trunk.tipo === 'voip' ? "bg-blue-100 text-blue-800" : "bg-green-100 text-green-800"}>
                          {trunk.tipo.toUpperCase()}
                        </Badge>
                        <Badge className={trunk.ativo ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}>
                          {trunk.ativo ? 'Ativo' : 'Inativo'}
                        </Badge>
                      </div>
                      <div className="text-sm text-gray-600 space-y-1">
                        {trunk.tipo === 'voip' && (
                          <div>Host: {trunk.host}:{trunk.porta}</div>
                        )}
                        <div>Bridge: {trunk.bridge_number}</div>
                        <div>Contexto: {trunk.contexto}</div>
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <Button size="sm" variant="outline">
                        Editar
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="border-red-300 text-red-600 hover:bg-red-50"
                      >
                        Excluir
                      </Button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="timer" className="space-y-6">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Configuração de Timer de Operação</h3>
            
            <form onSubmit={handleTimerSubmit} className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <Label htmlFor="horario_inicio">Horário de Início</Label>
                  <Input
                    id="horario_inicio"
                    type="time"
                    value={timerConfig.horario_inicio}
                    onChange={(e) => setTimerConfig({...timerConfig, horario_inicio: e.target.value})}
                  />
                </div>
                
                <div>
                  <Label htmlFor="horario_fim">Horário de Fim</Label>
                  <Input
                    id="horario_fim"
                    type="time"
                    value={timerConfig.horario_fim}
                    onChange={(e) => setTimerConfig({...timerConfig, horario_fim: e.target.value})}
                  />
                </div>
                
                <div>
                  <Label htmlFor="horario_almoco_inicio">Início do Almoço</Label>
                  <Input
                    id="horario_almoco_inicio"
                    type="time"
                    value={timerConfig.horario_almoco_inicio}
                    onChange={(e) => setTimerConfig({...timerConfig, horario_almoco_inicio: e.target.value})}
                  />
                </div>
                
                <div>
                  <Label htmlFor="horario_almoco_fim">Fim do Almoço</Label>
                  <Input
                    id="horario_almoco_fim"
                    type="time"
                    value={timerConfig.horario_almoco_fim}
                    onChange={(e) => setTimerConfig({...timerConfig, horario_almoco_fim: e.target.value})}
                  />
                </div>
                
                <div>
                  <Label htmlFor="timezone">Fuso Horário</Label>
                  <Select
                    value={timerConfig.timezone}
                    onValueChange={(value) => setTimerConfig({...timerConfig, timezone: value})}
                  >
                    <option value="America/Sao_Paulo">São Paulo (GMT-3)</option>
                    <option value="America/Mexico_City">Cidade do México (GMT-6)</option>
                    <option value="America/New_York">Nova York (GMT-5)</option>
                    <option value="America/Los_Angeles">Los Angeles (GMT-8)</option>
                  </Select>
                </div>
              </div>
              
              <div>
                <Label>Dias da Semana</Label>
                <div className="flex flex-wrap gap-2 mt-2">
                  {['segunda', 'terca', 'quarta', 'quinta', 'sexta', 'sabado', 'domingo'].map(dia => (
                    <label key={dia} className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        checked={timerConfig.dias_semana.includes(dia)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setTimerConfig({
                              ...timerConfig,
                              dias_semana: [...timerConfig.dias_semana, dia]
                            });
                          } else {
                            setTimerConfig({
                              ...timerConfig,
                              dias_semana: timerConfig.dias_semana.filter(d => d !== dia)
                            });
                          }
                        }}
                        className="rounded"
                      />
                      <span className="text-sm capitalize">{dia}</span>
                    </label>
                  ))}
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="timer_ativo"
                  checked={timerConfig.ativo}
                  onChange={(e) => setTimerConfig({...timerConfig, ativo: e.target.checked})}
                  className="rounded"
                />
                <Label htmlFor="timer_ativo">Timer Ativo</Label>
              </div>
              
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-medium text-blue-900 mb-2">Resumo da Configuração:</h4>
                <div className="text-sm text-blue-700 space-y-1">
                  <div>Operação: {timerConfig.horario_inicio} às {timerConfig.horario_fim}</div>
                  <div>Almoço: {timerConfig.horario_almoco_inicio} às {timerConfig.horario_almoco_fim}</div>
                  <div>Dias: {timerConfig.dias_semana.join(', ')}</div>
                  <div>Fuso: {timerConfig.timezone}</div>
                  <div>Status: {timerConfig.ativo ? 'Ativo' : 'Inativo'}</div>
                </div>
              </div>
              
              <Button type="submit" disabled={loading}>
                {loading ? 'Salvando...' : 'Salvar Configuração'}
              </Button>
            </form>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ContextManager;