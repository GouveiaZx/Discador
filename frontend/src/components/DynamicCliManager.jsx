import React, { useState, useEffect } from 'react';
import { makeApiRequest } from '../services/api';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select } from './ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Badge } from './ui/badge';
import { Alert } from './ui/alert';

const DynamicCliManager = () => {
  const [activeTab, setActiveTab] = useState('config');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Estados para configurações de CLI
  const [cliConfigs, setCliConfigs] = useState([]);
  const [cliStats, setCliStats] = useState({});
  const [areaCodes, setAreaCodes] = useState({});
  
  // Estados para monitoramento em tempo real
  const [realTimeData, setRealTimeData] = useState({
    current_call: null,
    current_cli: null,
    dialed_number: null,
    clis_used_today: 0,
    active_calls: 0,
    cli_usage_by_type: {},
    did_usage_warnings: []
  });
  
  // Estados para formulários
  const [showConfigForm, setShowConfigForm] = useState(false);
  const [editingConfig, setEditingConfig] = useState(null);
  
  const [configForm, setConfigForm] = useState({
    nome: '',
    tipo_cli: 'MXN', // MXN, ALEATORIO, ALEATORIO1, DID, DID1
    country_code: '',
    dial_prefix: '',
    trunk_id: '',
    limite_diario: 100,
    codigos_area: '', // Para EUA/Canadá - códigos de área específicos
    usar_prefixo_1: false, // Para ALEATORIO1 e DID1
    ativo: true,
    descricao: '',
    digitos_aleatorios: 4, // Quantidade de dígitos aleatórios no final
    formato_display: '', // Como mostrar o CLI para o cliente
    lista_dids: [], // Lista de DIDs próprios para tipos DID/DID1
    estados_codigos: {}, // Mapeamento de estados e códigos de área
    // Novas configurações por país
    regras_brasil: {
      mostrar_ddd_celular: true,
      aleatorizar_ultimos_4: true,
      formato_exibicao: 'XX 9 XXXX-XXXX'
    },
    configuracoes_avancadas: {
      balanceamento_carga: false,
      rotacao_automatica: true,
      backup_cli: '',
      timeout_geracao: 5000,
      log_detalhado: false
    }
  });
  
  // Estados para monitoramento em tempo real
  const [realTimeStats, setRealTimeStats] = useState({
    chamadas_ativas: 0,
    cli_atual: '',
    numero_discado: '',
    clis_usados_hoje: 0,
    limite_atingido: false
  });
  
  // Estados para listas DNC
  const [dncLists, setDncLists] = useState([]);
  const [showDncForm, setShowDncForm] = useState(false);
  const [dncForm, setDncForm] = useState({
    nome: '',
    descricao: ''
  });

  useEffect(() => {
    fetchData();
    fetchRealTimeData();
    
    // Polling para dados em tempo real
    const interval = setInterval(() => {
      fetchRealTimeStats();
      fetchRealTimeData();
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        fetchCliConfigs(),
        fetchCliStats(),
        fetchAreaCodes(),
        fetchDncLists(),
        fetchRealTimeStats()
      ]);
    } catch (err) {
      setError('Erro ao carregar dados: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchCliConfigs = async () => {
    try {
      const response = await makeApiRequest('/dynamic-cli/configs');
      setCliConfigs(response.configs || []);
    } catch (err) {
      console.error('Erro ao buscar configurações CLI:', err);
    }
  };

  const fetchCliStats = async () => {
    try {
      const response = await makeApiRequest('/dynamic-cli/stats');
      setCliStats(response.stats || {});
    } catch (err) {
      console.error('Erro ao buscar estatísticas CLI:', err);
    }
  };

  const fetchAreaCodes = async () => {
    try {
      const response = await makeApiRequest('/dynamic-cli/area-codes');
      setAreaCodes(response.area_codes || {});
    } catch (err) {
      console.error('Erro ao buscar códigos de área:', err);
    }
  };

  const fetchDncLists = async () => {
    try {
      const response = await makeApiRequest('/dnc/lists');
      setDncLists(response.lists || []);
    } catch (err) {
      console.error('Erro ao buscar listas DNC:', err);
    }
  };

  const fetchRealTimeData = async () => {
    try {
      const response = await makeApiRequest('/dynamic-cli/real-time-data');
      setRealTimeData(response.data || {
        current_call: null,
        current_cli: null,
        dialed_number: null,
        clis_used_today: 0,
        active_calls: 0,
        cli_usage_by_type: {},
        did_usage_warnings: []
      });
    } catch (err) {
      console.error('Erro ao buscar dados em tempo real:', err);
    }
  };

  const fetchRealTimeStats = async () => {
    try {
      const response = await makeApiRequest('/dynamic-cli/real-time-stats');
      setRealTimeStats(response.stats || realTimeStats);
    } catch (err) {
      console.error('Erro ao buscar estatísticas em tempo real:', err);
    }
  };

  const handleConfigSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      
      if (editingConfig) {
        await makeApiRequest(`/dynamic-cli/configs/${editingConfig.id}`, 'PUT', configForm);
        setSuccess('Configuração atualizada com sucesso!');
      } else {
        await makeApiRequest('/dynamic-cli/configs', 'POST', configForm);
        setSuccess('Configuração criada com sucesso!');
      }
      
      await fetchCliConfigs();
      resetConfigForm();
    } catch (err) {
      setError('Erro ao salvar configuração: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteConfig = async (configId) => {
    if (!confirm('Tem certeza que deseja excluir esta configuração?')) return;
    
    try {
      setLoading(true);
      await makeApiRequest(`/dynamic-cli/configs/${configId}`, 'DELETE');
      await fetchCliConfigs();
      setSuccess('Configuração excluída com sucesso!');
    } catch (err) {
      setError('Erro ao excluir configuração: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const resetConfigForm = () => {
    setConfigForm({
      nome: '',
      tipo_cli: 'MXN',
      country_code: '',
      dial_prefix: '',
      trunk_id: '',
      limite_diario: 100,
      codigos_area: '',
      usar_prefixo_1: false,
      ativo: true,
      descricao: '',
      digitos_aleatorios: 4,
      formato_display: '',
      lista_dids: [],
      estados_codigos: {}
    });
    setEditingConfig(null);
    setShowConfigForm(false);
  };

  const generateCli = async (tipo, numero_destino) => {
    try {
      const response = await makeApiRequest('/dynamic-cli/generate', 'POST', {
        tipo_cli: tipo,
        numero_destino: numero_destino
      });
      return response.cli_gerado;
    } catch (err) {
      setError('Erro ao gerar CLI: ' + err.message);
      return null;
    }
  };

  const resetDailyCounters = async () => {
    if (!confirm('Tem certeza que deseja resetar os contadores diários?')) return;
    
    try {
      setLoading(true);
      await makeApiRequest('/dynamic-cli/reset-daily-counters', 'POST');
      await fetchCliStats();
      setSuccess('Contadores diários resetados com sucesso!');
    } catch (err) {
      setError('Erro ao resetar contadores: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const exportDncList = async (listId) => {
    try {
      const response = await makeApiRequest(`/dnc/lists/${listId}/export`);
      const blob = new Blob([response.csv_data], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `dnc_list_${listId}.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Erro ao exportar lista DNC: ' + err.message);
    }
  };

  const getTipoCliDescription = (tipo) => {
    const descriptions = {
      'MXN': 'México - Gera CLI baseado no código de área do destino',
      'BRA': 'Brasil - Gera CLI com DDD + 9 + 4 dígitos aleatórios',
      'ALEATORIO': 'USA/Canadá - CLI aleatório sem prefixo 1',
      'ALEATORIO1': 'USA/Canadá - CLI aleatório com prefixo 1',
      'DID': 'DID próprio - Usa DIDs comprados (limite 100/dia)',
      'DID1': 'DID próprio - Usa DIDs comprados com prefixo 1 (limite 100/dia)'
    };
    return descriptions[tipo] || tipo;
  };

  const getStatusBadge = (ativo) => {
    return ativo ? 
      <Badge className="bg-green-100 text-green-800">Ativo</Badge> :
      <Badge className="bg-red-100 text-red-800">Inativo</Badge>;
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Gestão de CLI Dinâmico</h1>
        <div className="flex space-x-2">
          <Button 
            onClick={() => setShowConfigForm(!showConfigForm)}
            className="bg-blue-600 hover:bg-blue-700"
          >
            {showConfigForm ? 'Cancelar' : 'Nova Configuração'}
          </Button>
          <Button 
            onClick={resetDailyCounters}
            variant="outline"
            className="border-orange-500 text-orange-600 hover:bg-orange-50"
          >
            Reset Contadores
          </Button>
        </div>
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

      {/* Monitoramento em Tempo Real */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4">Monitoramento em Tempo Real</h2>
        
        {/* Alertas de DID próximos ao limite */}
        {realTimeData.did_usage_warnings && realTimeData.did_usage_warnings.length > 0 && (
          <Alert className="border-yellow-200 bg-yellow-50 mb-4">
            <div className="text-yellow-800">
              <strong>Atenção:</strong> DIDs próximos ao limite diário:
              <ul className="mt-1 ml-4">
                {realTimeData.did_usage_warnings.map((warning, index) => (
                  <li key={index} className="text-sm">
                    {warning.did} - {warning.usage}/100 usos ({warning.percentage}%)
                  </li>
                ))}
              </ul>
            </div>
          </Alert>
        )}
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-sm text-blue-600 font-medium">Chamadas Ativas</div>
            <div className="text-2xl font-bold text-blue-900">
              {realTimeData.active_calls || 0}
            </div>
          </div>
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="text-sm text-green-600 font-medium">CLI Atual</div>
            <div className="text-lg font-mono text-green-900">
              {realTimeData.current_cli || 'Nenhum'}
            </div>
            {realTimeData.current_call && (
              <div className="text-xs text-green-600 mt-1">
                Chamada: {realTimeData.current_call}
              </div>
            )}
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="text-sm text-purple-600 font-medium">Número Discado</div>
            <div className="text-lg font-mono text-purple-900">
              {realTimeData.dialed_number || 'Nenhum'}
            </div>
          </div>
          <div className="bg-orange-50 p-4 rounded-lg">
            <div className="text-sm text-orange-600 font-medium">CLIs Usados Hoje</div>
            <div className="text-2xl font-bold text-orange-900">
              {realTimeData.clis_used_today || 0}
            </div>
          </div>
        </div>
        
        {/* Uso por Tipo de CLI */}
        {realTimeData.cli_usage_by_type && Object.keys(realTimeData.cli_usage_by_type).length > 0 && (
          <div className="mt-4">
            <h3 className="text-lg font-medium mb-2">Uso por Tipo de CLI Hoje</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {Object.entries(realTimeData.cli_usage_by_type).map(([tipo, count]) => (
                <div key={tipo} className="bg-gray-50 p-2 rounded text-center">
                  <div className="text-sm font-medium text-gray-600">{getTipoCliDescription(tipo)}</div>
                  <div className="text-lg font-bold text-gray-900">{count}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </Card>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="config">Configurações</TabsTrigger>
          <TabsTrigger value="stats">Estatísticas</TabsTrigger>
          <TabsTrigger value="dnc">Listas DNC</TabsTrigger>
          <TabsTrigger value="area-codes">Códigos de Área</TabsTrigger>
        </TabsList>

        <TabsContent value="config" className="space-y-6">
          {/* Formulário de Configuração */}
          {showConfigForm && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">
                {editingConfig ? 'Editar Configuração' : 'Nova Configuração CLI'}
              </h3>
              
              <form onSubmit={handleConfigSubmit} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="nome">Nome da Configuração</Label>
                    <Input
                      id="nome"
                      value={configForm.nome}
                      onChange={(e) => setConfigForm({...configForm, nome: e.target.value})}
                      placeholder="Ex: CLI México Principal"
                      required
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="tipo_cli">Tipo de CLI</Label>
                    <Select
                      value={configForm.tipo_cli}
                      onValueChange={(value) => setConfigForm({...configForm, tipo_cli: value})}
                    >
                      <option value="MXN">MXN (México - Regras específicas)</option>
                      <option value="BRA">BRA (Brasil - DDD + Celular)</option>
                      <option value="ALEATORIO">ALEATORIO (USA/Canadá)</option>
                      <option value="ALEATORIO1">ALEATORIO1 (USA/Canadá com prefixo 1)</option>
                      <option value="DID">DID (DIDs próprios)</option>
                      <option value="DID1">DID1 (DIDs próprios com prefixo 1)</option>
                    </Select>
                    <div className="text-xs text-gray-500 mt-1">
                      {getTipoCliDescription(configForm.tipo_cli)}
                    </div>
                  </div>
                  
                  <div>
                    <Label htmlFor="country_code">Código do País</Label>
                    <Input
                      id="country_code"
                      value={configForm.country_code}
                      onChange={(e) => setConfigForm({...configForm, country_code: e.target.value})}
                      placeholder="Ex: 52 (México), 1 (USA/Canadá)"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="dial_prefix">Prefixo de Discagem</Label>
                    <Input
                      id="dial_prefix"
                      value={configForm.dial_prefix}
                      onChange={(e) => setConfigForm({...configForm, dial_prefix: e.target.value})}
                      placeholder="Ex: 9797 (código do provedor)"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="limite_diario">Limite Diário (para DIDs)</Label>
                    <Input
                      id="limite_diario"
                      type="number"
                      value={configForm.limite_diario}
                      onChange={(e) => setConfigForm({...configForm, limite_diario: parseInt(e.target.value)})}
                      min="1"
                      max="1000"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="digitos_aleatorios">Dígitos Aleatórios no Final</Label>
                    <Select
                      value={configForm.digitos_aleatorios.toString()}
                      onValueChange={(value) => setConfigForm({...configForm, digitos_aleatorios: parseInt(value)})}
                    >
                      <option value="4">4 dígitos (XXXX)</option>
                      <option value="3">3 dígitos (XXX)</option>
                      <option value="2">2 dígitos (XX)</option>
                    </Select>
                  </div>
                  
                  <div>
                    <Label htmlFor="formato_display">Formato de Exibição</Label>
                    <Input
                      id="formato_display"
                      value={configForm.formato_display}
                      onChange={(e) => setConfigForm({...configForm, formato_display: e.target.value})}
                      placeholder="Ex: 55 2222-XXXX (MX), 212 XXX-XXXX (US)"
                    />
                    <div className="text-xs text-gray-500 mt-1">
                      Use X para representar dígitos aleatórios
                    </div>
                  </div>
                  
                  <div>
                    <Label htmlFor="trunk_id">Trunk Associado</Label>
                    <Input
                      id="trunk_id"
                      value={configForm.trunk_id}
                      onChange={(e) => setConfigForm({...configForm, trunk_id: e.target.value})}
                      placeholder="ID do trunk VoIP"
                    />
                  </div>
                </div>
                
                {configForm.tipo_cli === 'MXN' && (
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <Label>Regras para México</Label>
                    <div className="text-sm text-gray-600 space-y-1">
                      <p><strong>Cidade do México (55):</strong> 8 dígitos - Exibe 55 2222-XXXX</p>
                      <p><strong>Jalisco/Nuevo León:</strong> 8 dígitos - Exibe código área + XXXX</p>
                      <p><strong>Cancún (998):</strong> 7 dígitos - Exibe 998 222-XXXX</p>
                      <p><strong>Outros estados:</strong> Detecta automaticamente o formato</p>
                    </div>
                  </div>
                )}
                
                {configForm.tipo_cli === 'BRA' && (
                  <div className="bg-green-50 p-4 rounded-lg">
                    <Label>Regras para Brasil</Label>
                    <div className="text-sm text-gray-600 space-y-1">
                      <p><strong>Formato:</strong> DDD + 9 + 4 dígitos aleatórios</p>
                      <p><strong>Exemplo:</strong> 11 9 2222-XXXX (São Paulo), 21 9 3333-XXXX (Rio)</p>
                      <p><strong>DDDs suportados:</strong> Todos os códigos de área brasileiros</p>
                      <p><strong>Exibição:</strong> Formato padrão brasileiro XX 9 XXXX-XXXX</p>
                    </div>
                    <div className="mt-3 space-y-2">
                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id="mostrar_ddd_celular"
                          checked={configForm.regras_brasil?.mostrar_ddd_celular || true}
                          onChange={(e) => setConfigForm({
                            ...configForm,
                            regras_brasil: {
                              ...configForm.regras_brasil,
                              mostrar_ddd_celular: e.target.checked
                            }
                          })}
                          className="rounded"
                        />
                        <Label htmlFor="mostrar_ddd_celular">Mostrar DDD na exibição</Label>
                      </div>
                      <div className="flex items-center space-x-2">
                        <input
                          type="checkbox"
                          id="aleatorizar_ultimos_4"
                          checked={configForm.regras_brasil?.aleatorizar_ultimos_4 || true}
                          onChange={(e) => setConfigForm({
                            ...configForm,
                            regras_brasil: {
                              ...configForm.regras_brasil,
                              aleatorizar_ultimos_4: e.target.checked
                            }
                          })}
                          className="rounded"
                        />
                        <Label htmlFor="aleatorizar_ultimos_4">Aleatorizar últimos 4 dígitos</Label>
                      </div>
                    </div>
                  </div>
                )}
                
                {(configForm.country_code === '1') && (
                  <div>
                    <Label htmlFor="codigos_area">Códigos de Área (EUA/Canadá)</Label>
                    <Input
                      id="codigos_area"
                      value={configForm.codigos_area}
                      onChange={(e) => setConfigForm({...configForm, codigos_area: e.target.value})}
                      placeholder="Ex: 305,321,407,561,727,754,772,786,813,850"
                    />
                    <div className="text-xs text-gray-500 mt-1">
                      Para estados com múltiplos códigos, separe com vírgula
                    </div>
                  </div>
                )}
                
                {(configForm.country_code === '1') && configForm.tipo_cli === 'ALEATORIO' && (
                  <div>
                    <Label htmlFor="estados_codigos">Mapeamento Estados/Códigos de Área</Label>
                    <textarea
                      id="estados_codigos"
                      value={JSON.stringify(configForm.estados_codigos, null, 2)}
                      onChange={(e) => {
                        try {
                          setConfigForm({...configForm, estados_codigos: JSON.parse(e.target.value)});
                        } catch (err) {
                          // Ignora erro de parsing durante digitação
                        }
                      }}
                      className="w-full h-32 p-2 border rounded text-xs font-mono"
                      placeholder={`{
  "FL": ["239", "305", "321", "352", "386", "407", "561", "727", "754", "772", "786", "813", "850", "863", "904", "941", "954"],
  "NY": ["212", "315", "347", "516", "518", "585", "607", "631", "646", "716", "718", "845", "914", "917", "929"]
}`}
                    />
                    <div className="text-xs text-gray-500 mt-1">
                      JSON com estados e seus códigos de área. Para estados com múltiplos códigos, o sistema escolhe aleatoriamente.
                    </div>
                  </div>
                )}
                
                {(configForm.tipo_cli === 'DID' || configForm.tipo_cli === 'DID1') && (
                  <div>
                    <Label htmlFor="lista_dids">Lista de DIDs Próprios</Label>
                    <textarea
                      id="lista_dids"
                      value={configForm.lista_dids.join('\n')}
                      onChange={(e) => setConfigForm({...configForm, lista_dids: e.target.value.split('\n').filter(d => d.trim())})}
                      className="w-full h-24 p-2 border rounded text-sm"
                      placeholder="2125551234\n2125555678\n3055551234"
                    />
                    <div className="text-xs text-gray-500 mt-1">
                      Um DID por linha. Mínimo 300 DIDs recomendado.
                    </div>
                  </div>
                )}
                

                </div>
                
                <div>
                  <Label htmlFor="descricao">Descrição</Label>
                  <Input
                    id="descricao"
                    value={configForm.descricao}
                    onChange={(e) => setConfigForm({...configForm, descricao: e.target.value})}
                    placeholder="Descrição da configuração"
                  />
                </div>
                
                {(configForm.tipo_cli === 'ALEATORIO1' || configForm.tipo_cli === 'DID1') && (
                  <div className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id="usar_prefixo_1"
                      checked={configForm.usar_prefixo_1}
                      onChange={(e) => setConfigForm({...configForm, usar_prefixo_1: e.target.checked})}
                      className="rounded"
                    />
                    <Label htmlFor="usar_prefixo_1">Adicionar prefixo "1" ao CLI</Label>
                    <div className="text-xs text-gray-500">
                      Obrigatório para alguns provedores
                    </div>
                  </div>
                )}
                
                {/* Configurações Avançadas */}
                <div className="bg-purple-50 p-4 rounded-lg">
                  <Label>Configurações Avançadas</Label>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-3">
                    <div>
                      <Label htmlFor="backup_cli">CLI de Backup</Label>
                      <Input
                        id="backup_cli"
                        value={configForm.configuracoes_avancadas?.backup_cli || ''}
                        onChange={(e) => setConfigForm({
                          ...configForm,
                          configuracoes_avancadas: {
                            ...configForm.configuracoes_avancadas,
                            backup_cli: e.target.value
                          }
                        })}
                        placeholder="CLI para usar em caso de falha"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="timeout_geracao">Timeout de Geração (ms)</Label>
                      <Input
                        id="timeout_geracao"
                        type="number"
                        value={configForm.configuracoes_avancadas?.timeout_geracao || 5000}
                        onChange={(e) => setConfigForm({
                          ...configForm,
                          configuracoes_avancadas: {
                            ...configForm.configuracoes_avancadas,
                            timeout_geracao: parseInt(e.target.value)
                          }
                        })}
                        min="1000"
                        max="30000"
                      />
                    </div>
                  </div>
                  
                  <div className="mt-3 space-y-2">
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="balanceamento_carga"
                        checked={configForm.configuracoes_avancadas?.balanceamento_carga || false}
                        onChange={(e) => setConfigForm({
                          ...configForm,
                          configuracoes_avancadas: {
                            ...configForm.configuracoes_avancadas,
                            balanceamento_carga: e.target.checked
                          }
                        })}
                        className="rounded"
                      />
                      <Label htmlFor="balanceamento_carga">Balanceamento de carga entre DIDs</Label>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="rotacao_automatica"
                        checked={configForm.configuracoes_avancadas?.rotacao_automatica || true}
                        onChange={(e) => setConfigForm({
                          ...configForm,
                          configuracoes_avancadas: {
                            ...configForm.configuracoes_avancadas,
                            rotacao_automatica: e.target.checked
                          }
                        })}
                        className="rounded"
                      />
                      <Label htmlFor="rotacao_automatica">Rotação automática de CLIs</Label>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="log_detalhado"
                        checked={configForm.configuracoes_avancadas?.log_detalhado || false}
                        onChange={(e) => setConfigForm({
                          ...configForm,
                          configuracoes_avancadas: {
                            ...configForm.configuracoes_avancadas,
                            log_detalhado: e.target.checked
                          }
                        })}
                        className="rounded"
                      />
                      <Label htmlFor="log_detalhado">Log detalhado de geração de CLI</Label>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <input
                        type="checkbox"
                        id="ativo"
                        checked={configForm.ativo}
                        onChange={(e) => setConfigForm({...configForm, ativo: e.target.checked})}
                        className="rounded"
                      />
                      <Label htmlFor="ativo">Configuração ativa</Label>
                    </div>
                  </div>
                </div>
                
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-medium text-blue-900 mb-2">Tipo Selecionado:</h4>
                  <p className="text-sm text-blue-700">{getTipoCliDescription(configForm.tipo_cli)}</p>
                </div>
                
                <div className="flex space-x-2">
                  <Button type="submit" disabled={loading}>
                    {loading ? 'Salvando...' : (editingConfig ? 'Atualizar' : 'Criar')}
                  </Button>
                  <Button type="button" variant="outline" onClick={resetConfigForm}>
                    Cancelar
                  </Button>
                </div>
              </form>
            </Card>
          )}

          {/* Lista de Configurações */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Configurações Existentes</h3>
            
            {cliConfigs.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                Nenhuma configuração encontrada. Crie sua primeira configuração CLI.
              </div>
            ) : (
              <div className="space-y-4">
                {cliConfigs.map((config) => (
                  <div key={config.id} className="border rounded-lg p-4 hover:bg-gray-50">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h4 className="font-medium text-gray-900">{config.nome}</h4>
                          {getStatusBadge(config.ativo)}
                          <Badge className="bg-blue-100 text-blue-800">{config.tipo_cli}</Badge>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{config.descricao}</p>
                        <div className="text-xs text-gray-500 space-y-1">
                          <div>Código País: {config.country_code}</div>
                          <div>Prefixo: {config.dial_prefix}</div>
                          <div>Limite Diário: {config.limite_diario}</div>
                          {config.trunk_id && <div>Trunk: {config.trunk_id}</div>}
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setEditingConfig(config);
                            setConfigForm(config);
                            setShowConfigForm(true);
                          }}
                        >
                          Editar
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="border-red-300 text-red-600 hover:bg-red-50"
                          onClick={() => handleDeleteConfig(config.id)}
                        >
                          Excluir
                        </Button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </Card>
        </TabsContent>

        <TabsContent value="stats" className="space-y-6">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Estatísticas de Uso</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-green-50 p-4 rounded-lg">
                <div className="text-sm text-green-600 font-medium">Total de CLIs Gerados Hoje</div>
                <div className="text-2xl font-bold text-green-900">{cliStats.total_gerados_hoje || 0}</div>
              </div>
              <div className="bg-blue-50 p-4 rounded-lg">
                <div className="text-sm text-blue-600 font-medium">CLIs Únicos Utilizados</div>
                <div className="text-2xl font-bold text-blue-900">{cliStats.unicos_utilizados || 0}</div>
              </div>
              <div className="bg-purple-50 p-4 rounded-lg">
                <div className="text-sm text-purple-600 font-medium">Taxa de Sucesso</div>
                <div className="text-2xl font-bold text-purple-900">{cliStats.taxa_sucesso || '0%'}</div>
              </div>
            </div>
            
            {cliStats.por_tipo && (
              <div className="mt-6">
                <h4 className="font-medium mb-3">Uso por Tipo de CLI</h4>
                <div className="space-y-2">
                  {Object.entries(cliStats.por_tipo).map(([tipo, dados]) => (
                    <div key={tipo} className="flex justify-between items-center p-3 bg-gray-50 rounded">
                      <div>
                        <span className="font-medium">{tipo}</span>
                        <span className="text-sm text-gray-500 ml-2">{getTipoCliDescription(tipo)}</span>
                      </div>
                      <div className="text-right">
                        <div className="font-bold">{dados.total || 0}</div>
                        <div className="text-xs text-gray-500">usos hoje</div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </Card>
        </TabsContent>

        <TabsContent value="dnc" className="space-y-6">
          <Card className="p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-semibold">Listas de Não Chamar (DNC)</h3>
              <Button 
                onClick={() => setShowDncForm(!showDncForm)}
                className="bg-green-600 hover:bg-green-700"
              >
                {showDncForm ? 'Cancelar' : 'Nova Lista DNC'}
              </Button>
            </div>
            
            {showDncForm && (
              <div className="border rounded-lg p-4 mb-4 bg-gray-50">
                <form onSubmit={(e) => {
                  e.preventDefault();
                  // Implementar criação de lista DNC
                }} className="space-y-4">
                  <div>
                    <Label htmlFor="dnc_nome">Nome da Lista</Label>
                    <Input
                      id="dnc_nome"
                      value={dncForm.nome}
                      onChange={(e) => setDncForm({...dncForm, nome: e.target.value})}
                      placeholder="Ex: DNC Brasil Principal"
                      required
                    />
                  </div>
                  <div>
                    <Label htmlFor="dnc_descricao">Descrição</Label>
                    <Input
                      id="dnc_descricao"
                      value={dncForm.descricao}
                      onChange={(e) => setDncForm({...dncForm, descricao: e.target.value})}
                      placeholder="Descrição da lista"
                    />
                  </div>
                  <div className="flex space-x-2">
                    <Button type="submit">Criar Lista</Button>
                    <Button type="button" variant="outline" onClick={() => setShowDncForm(false)}>
                      Cancelar
                    </Button>
                  </div>
                </form>
              </div>
            )}
            
            <div className="space-y-4">
              {dncLists.map((list) => (
                <div key={list.id} className="border rounded-lg p-4 hover:bg-gray-50">
                  <div className="flex justify-between items-center">
                    <div>
                      <h4 className="font-medium">{list.nome}</h4>
                      <p className="text-sm text-gray-600">{list.descricao}</p>
                      <div className="text-xs text-gray-500 mt-1">
                        {list.total_numeros || 0} números • Criada em {new Date(list.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => exportDncList(list.id)}
                      >
                        Exportar CSV
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

        <TabsContent value="area-codes" className="space-y-6">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Códigos de Área por País/Estado</h3>
            
            {Object.entries(areaCodes).map(([country, states]) => (
              <div key={country} className="mb-6">
                <h4 className="font-medium text-lg mb-3 text-blue-900">{country}</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Object.entries(states).map(([state, codes]) => (
                    <div key={state} className="border rounded-lg p-3">
                      <h5 className="font-medium text-gray-900 mb-2">{state}</h5>
                      <div className="flex flex-wrap gap-1">
                        {codes.map((code) => (
                          <Badge key={code} variant="outline" className="text-xs">
                            {code}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default DynamicCliManager;