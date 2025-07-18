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
import { Switch } from './ui/switch';
import { Textarea } from './ui/textarea';

const TrunkManager = () => {
  const [activeTab, setActiveTab] = useState('outbound');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Estados para trunks
  const [outboundTrunks, setOutboundTrunks] = useState([]);
  const [transferTrunks, setTransferTrunks] = useState([]);
  const [showTrunkForm, setShowTrunkForm] = useState(false);
  const [editingTrunk, setEditingTrunk] = useState(null);
  
  // Formulário de trunk
  const [trunkForm, setTrunkForm] = useState({
    nome: '',
    tipo: 'outbound', // outbound, transfer
    host: '',
    porta: 5060,
    usuario: '',
    senha: '',
    contexto: 'from-trunk',
    codec: 'ulaw,alaw,g729',
    dtmf_mode: 'rfc2833',
    qualify: 'yes',
    nat: 'force_rport,comedia',
    canreinvite: 'no',
    insecure: 'port,invite',
    dial_string: '', // Ex: SIP/DV/9797
    country_code: '', // Ex: 52 para México
    exit_code: '', // Ex: 1 para saída
    provider_code: '', // Ex: 9797 do provedor
    bridge_number: '', // Para transferência
    max_channels: 30,
    ativo: true,
    descricao: '',
    // Configurações avançadas
    register_string: '', // Para registro SIP
    fromuser: '',
    fromdomain: '',
    defaultuser: '',
    secret: '',
    type: 'peer',
    disallow: 'all',
    allow: 'ulaw,alaw,g729',
    // Configurações específicas do provedor
    provider_settings: {
      requires_auth: true,
      auth_user: '',
      auth_password: '',
      outbound_proxy: '',
      registration_required: false
    }
  });
  
  // Estados para monitoramento
  const [trunkStatus, setTrunkStatus] = useState({});
  const [callStats, setCallStats] = useState({});

  useEffect(() => {
    fetchData();
    // Polling para status dos trunks
    const interval = setInterval(fetchTrunkStatus, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        fetchOutboundTrunks(),
        fetchTransferTrunks(),
        fetchTrunkStatus(),
        fetchCallStats()
      ]);
    } catch (err) {
      setError('Erro ao carregar dados: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchOutboundTrunks = async () => {
    try {
      const response = await makeApiRequest('/trunks/outbound');
      setOutboundTrunks(response.trunks || []);
    } catch (err) {
      console.error('Erro ao buscar trunks de saída:', err);
    }
  };

  const fetchTransferTrunks = async () => {
    try {
      const response = await makeApiRequest('/trunks/transfer');
      setTransferTrunks(response.trunks || []);
    } catch (err) {
      console.error('Erro ao buscar trunks de transferência:', err);
    }
  };

  const fetchTrunkStatus = async () => {
    try {
      const response = await makeApiRequest('/trunks/status');
      setTrunkStatus(response.status || {});
    } catch (err) {
      console.error('Erro ao buscar status dos trunks:', err);
    }
  };

  const fetchCallStats = async () => {
    try {
      const response = await makeApiRequest('/trunks/call-stats');
      setCallStats(response.stats || {});
    } catch (err) {
      console.error('Erro ao buscar estatísticas de chamadas:', err);
    }
  };

  const handleTrunkSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      
      // Gerar dial string automaticamente se não fornecida
      if (!trunkForm.dial_string && trunkForm.provider_code) {
        const dialString = `SIP/${trunkForm.nome}/${trunkForm.provider_code}${trunkForm.exit_code || ''}`;
        trunkForm.dial_string = dialString;
      }
      
      if (editingTrunk) {
        await makeApiRequest(`/trunks/${editingTrunk.id}`, 'PUT', trunkForm);
        setSuccess('Trunk atualizado com sucesso!');
      } else {
        await makeApiRequest('/trunks', 'POST', trunkForm);
        setSuccess('Trunk criado com sucesso!');
      }
      
      await fetchData();
      resetTrunkForm();
    } catch (err) {
      setError('Erro ao salvar trunk: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteTrunk = async (trunkId) => {
    if (!confirm('Tem certeza que deseja excluir este trunk?')) return;
    
    try {
      setLoading(true);
      await makeApiRequest(`/trunks/${trunkId}`, 'DELETE');
      await fetchData();
      setSuccess('Trunk excluído com sucesso!');
    } catch (err) {
      setError('Erro ao excluir trunk: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleTrunkStatus = async (trunkId, currentStatus) => {
    try {
      setLoading(true);
      await makeApiRequest(`/trunks/${trunkId}/toggle`, 'PATCH', {
        ativo: !currentStatus
      });
      await fetchData();
      setSuccess('Status do trunk atualizado!');
    } catch (err) {
      setError('Erro ao alterar status: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const testTrunkConnection = async (trunkId) => {
    try {
      setLoading(true);
      const response = await makeApiRequest(`/trunks/${trunkId}/test`, 'POST');
      if (response.success) {
        setSuccess('Teste de conexão bem-sucedido!');
      } else {
        setError('Falha no teste de conexão: ' + response.error);
      }
    } catch (err) {
      setError('Erro ao testar conexão: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const generateSipConfig = async (trunkId) => {
    try {
      const response = await makeApiRequest(`/trunks/${trunkId}/sip-config`);
      const blob = new Blob([response.config], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `trunk_${trunkId}_sip.conf`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (err) {
      setError('Erro ao gerar configuração SIP: ' + err.message);
    }
  };

  const resetTrunkForm = () => {
    setTrunkForm({
      nome: '',
      tipo: 'outbound',
      host: '',
      porta: 5060,
      usuario: '',
      senha: '',
      contexto: 'from-trunk',
      codec: 'ulaw,alaw,g729',
      dtmf_mode: 'rfc2833',
      qualify: 'yes',
      nat: 'force_rport,comedia',
      canreinvite: 'no',
      insecure: 'port,invite',
      dial_string: '',
      country_code: '',
      exit_code: '',
      provider_code: '',
      bridge_number: '',
      max_channels: 30,
      ativo: true,
      descricao: '',
      register_string: '',
      fromuser: '',
      fromdomain: '',
      defaultuser: '',
      secret: '',
      type: 'peer',
      disallow: 'all',
      allow: 'ulaw,alaw,g729',
      provider_settings: {
        requires_auth: true,
        auth_user: '',
        auth_password: '',
        outbound_proxy: '',
        registration_required: false
      }
    });
    setEditingTrunk(null);
    setShowTrunkForm(false);
  };

  const getStatusBadge = (status) => {
    const statusMap = {
      'online': { color: 'bg-green-100 text-green-800', text: 'Online' },
      'offline': { color: 'bg-red-100 text-red-800', text: 'Offline' },
      'unreachable': { color: 'bg-yellow-100 text-yellow-800', text: 'Inalcançável' },
      'unknown': { color: 'bg-gray-100 text-gray-800', text: 'Desconhecido' }
    };
    
    const statusInfo = statusMap[status] || statusMap.unknown;
    return <Badge className={statusInfo.color}>{statusInfo.text}</Badge>;
  };

  const getTrunkTypeDescription = (tipo) => {
    return tipo === 'outbound' ? 'Saída (Discagem)' : 'Transferência (Clientes)';
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Gestão de Trunks VoIP</h1>
        <div className="flex space-x-2">
          <Button 
            onClick={() => setShowTrunkForm(!showTrunkForm)}
            className="bg-blue-600 hover:bg-blue-700"
          >
            {showTrunkForm ? 'Cancelar' : 'Novo Trunk'}
          </Button>
          <Button 
            onClick={fetchData}
            variant="outline"
            className="border-green-500 text-green-600 hover:bg-green-50"
          >
            Atualizar Status
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

      {/* Status Geral dos Trunks */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4">Status Geral dos Trunks</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-green-50 p-4 rounded-lg">
            <div className="text-sm text-green-600 font-medium">Trunks Online</div>
            <div className="text-2xl font-bold text-green-900">
              {Object.values(trunkStatus).filter(s => s === 'online').length}
            </div>
          </div>
          <div className="bg-red-50 p-4 rounded-lg">
            <div className="text-sm text-red-600 font-medium">Trunks Offline</div>
            <div className="text-2xl font-bold text-red-900">
              {Object.values(trunkStatus).filter(s => s === 'offline').length}
            </div>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="text-sm text-blue-600 font-medium">Chamadas Ativas</div>
            <div className="text-2xl font-bold text-blue-900">
              {callStats.active_calls || 0}
            </div>
          </div>
          <div className="bg-purple-50 p-4 rounded-lg">
            <div className="text-sm text-purple-600 font-medium">Total Hoje</div>
            <div className="text-2xl font-bold text-purple-900">
              {callStats.total_today || 0}
            </div>
          </div>
        </div>
      </Card>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="outbound">Trunks de Saída</TabsTrigger>
          <TabsTrigger value="transfer">Trunks de Transferência</TabsTrigger>
          <TabsTrigger value="config">Configuração</TabsTrigger>
        </TabsList>

        <TabsContent value="outbound" className="space-y-6">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Trunks de Saída (Discagem)</h3>
            
            {outboundTrunks.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                Nenhum trunk de saída configurado. Configure seu primeiro trunk para começar a discar.
              </div>
            ) : (
              <div className="space-y-4">
                {outboundTrunks.map((trunk) => (
                  <div key={trunk.id} className="border rounded-lg p-4 hover:bg-gray-50">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h4 className="font-medium text-gray-900">{trunk.nome}</h4>
                          {getStatusBadge(trunkStatus[trunk.id])}
                          <Badge className="bg-blue-100 text-blue-800">
                            {getTrunkTypeDescription(trunk.tipo)}
                          </Badge>
                          {trunk.ativo ? (
                            <Badge className="bg-green-100 text-green-800">Ativo</Badge>
                          ) : (
                            <Badge className="bg-red-100 text-red-800">Inativo</Badge>
                          )}
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{trunk.descricao}</p>
                        <div className="text-xs text-gray-500 space-y-1">
                          <div>Host: {trunk.host}:{trunk.porta}</div>
                          <div>Dial String: {trunk.dial_string}</div>
                          <div>País: {trunk.country_code} | Código Provedor: {trunk.provider_code}</div>
                          <div>Canais Máx: {trunk.max_channels}</div>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => testTrunkConnection(trunk.id)}
                          className="border-blue-300 text-blue-600 hover:bg-blue-50"
                        >
                          Testar
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => generateSipConfig(trunk.id)}
                          className="border-purple-300 text-purple-600 hover:bg-purple-50"
                        >
                          SIP Config
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setEditingTrunk(trunk);
                            setTrunkForm(trunk);
                            setShowTrunkForm(true);
                          }}
                        >
                          Editar
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => toggleTrunkStatus(trunk.id, trunk.ativo)}
                          className={trunk.ativo ? 
                            'border-red-300 text-red-600 hover:bg-red-50' : 
                            'border-green-300 text-green-600 hover:bg-green-50'
                          }
                        >
                          {trunk.ativo ? 'Desativar' : 'Ativar'}
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="border-red-300 text-red-600 hover:bg-red-50"
                          onClick={() => handleDeleteTrunk(trunk.id)}
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

        <TabsContent value="transfer" className="space-y-6">
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Trunks de Transferência (Clientes)</h3>
            
            {transferTrunks.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                Nenhum trunk de transferência configurado. Configure trunks para transferir chamadas aos clientes.
              </div>
            ) : (
              <div className="space-y-4">
                {transferTrunks.map((trunk) => (
                  <div key={trunk.id} className="border rounded-lg p-4 hover:bg-gray-50">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h4 className="font-medium text-gray-900">{trunk.nome}</h4>
                          {getStatusBadge(trunkStatus[trunk.id])}
                          <Badge className="bg-orange-100 text-orange-800">
                            {getTrunkTypeDescription(trunk.tipo)}
                          </Badge>
                          {trunk.ativo ? (
                            <Badge className="bg-green-100 text-green-800">Ativo</Badge>
                          ) : (
                            <Badge className="bg-red-100 text-red-800">Inativo</Badge>
                          )}
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{trunk.descricao}</p>
                        <div className="text-xs text-gray-500 space-y-1">
                          <div>Host: {trunk.host}:{trunk.porta}</div>
                          <div>Bridge Number: {trunk.bridge_number}</div>
                          <div>Contexto: {trunk.contexto}</div>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => testTrunkConnection(trunk.id)}
                          className="border-blue-300 text-blue-600 hover:bg-blue-50"
                        >
                          Testar
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => {
                            setEditingTrunk(trunk);
                            setTrunkForm(trunk);
                            setShowTrunkForm(true);
                          }}
                        >
                          Editar
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => toggleTrunkStatus(trunk.id, trunk.ativo)}
                          className={trunk.ativo ? 
                            'border-red-300 text-red-600 hover:bg-red-50' : 
                            'border-green-300 text-green-600 hover:bg-green-50'
                          }
                        >
                          {trunk.ativo ? 'Desativar' : 'Ativar'}
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="border-red-300 text-red-600 hover:bg-red-50"
                          onClick={() => handleDeleteTrunk(trunk.id)}
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

        <TabsContent value="config" className="space-y-6">
          {/* Formulário de Configuração de Trunk */}
          {showTrunkForm && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">
                {editingTrunk ? 'Editar Trunk' : 'Novo Trunk VoIP'}
              </h3>
              
              <form onSubmit={handleTrunkSubmit} className="space-y-6">
                {/* Informações Básicas */}
                <div className="bg-gray-50 p-4 rounded-lg">
                  <h4 className="font-medium mb-3">Informações Básicas</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="nome">Nome do Trunk</Label>
                      <Input
                        id="nome"
                        value={trunkForm.nome}
                        onChange={(e) => setTrunkForm({...trunkForm, nome: e.target.value})}
                        placeholder="Ex: Trunk México Principal"
                        required
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="tipo">Tipo de Trunk</Label>
                      <Select
                        value={trunkForm.tipo}
                        onValueChange={(value) => setTrunkForm({...trunkForm, tipo: value})}
                      >
                        <option value="outbound">Saída (Discagem)</option>
                        <option value="transfer">Transferência (Clientes)</option>
                      </Select>
                    </div>
                    
                    <div>
                      <Label htmlFor="host">Host/IP do Provedor</Label>
                      <Input
                        id="host"
                        value={trunkForm.host}
                        onChange={(e) => setTrunkForm({...trunkForm, host: e.target.value})}
                        placeholder="Ex: sip.provedor.com"
                        required
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="porta">Porta SIP</Label>
                      <Input
                        id="porta"
                        type="number"
                        value={trunkForm.porta}
                        onChange={(e) => setTrunkForm({...trunkForm, porta: parseInt(e.target.value)})}
                        min="1"
                        max="65535"
                      />
                    </div>
                  </div>
                </div>

                {/* Autenticação */}
                <div className="bg-blue-50 p-4 rounded-lg">
                  <h4 className="font-medium mb-3">Autenticação</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="usuario">Usuário</Label>
                      <Input
                        id="usuario"
                        value={trunkForm.usuario}
                        onChange={(e) => setTrunkForm({...trunkForm, usuario: e.target.value})}
                        placeholder="Usuário do provedor"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="senha">Senha</Label>
                      <Input
                        id="senha"
                        type="password"
                        value={trunkForm.senha}
                        onChange={(e) => setTrunkForm({...trunkForm, senha: e.target.value})}
                        placeholder="Senha do provedor"
                      />
                    </div>
                  </div>
                </div>

                {/* Configurações de Discagem (apenas para trunks de saída) */}
                {trunkForm.tipo === 'outbound' && (
                  <div className="bg-green-50 p-4 rounded-lg">
                    <h4 className="font-medium mb-3">Configurações de Discagem</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="country_code">Código do País</Label>
                        <Input
                          id="country_code"
                          value={trunkForm.country_code}
                          onChange={(e) => setTrunkForm({...trunkForm, country_code: e.target.value})}
                          placeholder="Ex: 52 (México), 1 (USA/Canadá), 55 (Brasil)"
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="provider_code">Código do Provedor</Label>
                        <Input
                          id="provider_code"
                          value={trunkForm.provider_code}
                          onChange={(e) => setTrunkForm({...trunkForm, provider_code: e.target.value})}
                          placeholder="Ex: 9797 (código de saída do provedor)"
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="exit_code">Código de Saída</Label>
                        <Input
                          id="exit_code"
                          value={trunkForm.exit_code}
                          onChange={(e) => setTrunkForm({...trunkForm, exit_code: e.target.value})}
                          placeholder="Ex: 1 (para saída), 55 (Brasil)"
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="dial_string">Dial String</Label>
                        <Input
                          id="dial_string"
                          value={trunkForm.dial_string}
                          onChange={(e) => setTrunkForm({...trunkForm, dial_string: e.target.value})}
                          placeholder="Ex: SIP/DV/9797 (gerado automaticamente)"
                        />
                        <div className="text-xs text-gray-500 mt-1">
                          Deixe vazio para gerar automaticamente
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Configurações de Transferência (apenas para trunks de transferência) */}
                {trunkForm.tipo === 'transfer' && (
                  <div className="bg-orange-50 p-4 rounded-lg">
                    <h4 className="font-medium mb-3">Configurações de Transferência</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      <div>
                        <Label htmlFor="bridge_number">Bridge Number</Label>
                        <Input
                          id="bridge_number"
                          value={trunkForm.bridge_number}
                          onChange={(e) => setTrunkForm({...trunkForm, bridge_number: e.target.value})}
                          placeholder="Ex: 1001 (extensão de transferência)"
                        />
                      </div>
                      
                      <div>
                        <Label htmlFor="contexto">Contexto</Label>
                        <Input
                          id="contexto"
                          value={trunkForm.contexto}
                          onChange={(e) => setTrunkForm({...trunkForm, contexto: e.target.value})}
                          placeholder="Ex: from-internal"
                        />
                      </div>
                    </div>
                  </div>
                )}

                {/* Configurações Avançadas */}
                <div className="bg-purple-50 p-4 rounded-lg">
                  <h4 className="font-medium mb-3">Configurações Avançadas</h4>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <Label htmlFor="max_channels">Canais Máximos</Label>
                      <Input
                        id="max_channels"
                        type="number"
                        value={trunkForm.max_channels}
                        onChange={(e) => setTrunkForm({...trunkForm, max_channels: parseInt(e.target.value)})}
                        min="1"
                        max="1000"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="codec">Codecs</Label>
                      <Input
                        id="codec"
                        value={trunkForm.codec}
                        onChange={(e) => setTrunkForm({...trunkForm, codec: e.target.value})}
                        placeholder="ulaw,alaw,g729"
                      />
                    </div>
                    
                    <div>
                      <Label htmlFor="dtmf_mode">Modo DTMF</Label>
                      <Select
                        value={trunkForm.dtmf_mode}
                        onValueChange={(value) => setTrunkForm({...trunkForm, dtmf_mode: value})}
                      >
                        <option value="rfc2833">RFC2833</option>
                        <option value="inband">Inband</option>
                        <option value="info">SIP INFO</option>
                      </Select>
                    </div>
                    
                    <div>
                      <Label htmlFor="qualify">Qualify</Label>
                      <Select
                        value={trunkForm.qualify}
                        onValueChange={(value) => setTrunkForm({...trunkForm, qualify: value})}
                      >
                        <option value="yes">Sim</option>
                        <option value="no">Não</option>
                        <option value="2000">2000ms</option>
                        <option value="5000">5000ms</option>
                      </Select>
                    </div>
                  </div>
                  
                  <div className="mt-4">
                    <Label htmlFor="register_string">String de Registro (se necessário)</Label>
                    <Input
                      id="register_string"
                      value={trunkForm.register_string}
                      onChange={(e) => setTrunkForm({...trunkForm, register_string: e.target.value})}
                      placeholder="Ex: usuario:senha@provedor.com/usuario"
                    />
                  </div>
                </div>

                <div>
                  <Label htmlFor="descricao">Descrição</Label>
                  <Textarea
                    id="descricao"
                    value={trunkForm.descricao}
                    onChange={(e) => setTrunkForm({...trunkForm, descricao: e.target.value})}
                    placeholder="Descrição do trunk e observações"
                    rows={3}
                  />
                </div>
                
                <div className="flex items-center space-x-2">
                  <Switch
                    id="ativo"
                    checked={trunkForm.ativo}
                    onCheckedChange={(checked) => setTrunkForm({...trunkForm, ativo: checked})}
                  />
                  <Label htmlFor="ativo">Trunk ativo</Label>
                </div>
                
                <div className="flex space-x-2">
                  <Button type="submit" disabled={loading}>
                    {loading ? 'Salvando...' : (editingTrunk ? 'Atualizar' : 'Criar')}
                  </Button>
                  <Button type="button" variant="outline" onClick={resetTrunkForm}>
                    Cancelar
                  </Button>
                </div>
              </form>
            </Card>
          )}

          {/* Guia de Configuração */}
          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Guia de Configuração</h3>
            
            <div className="space-y-4">
              <div className="bg-blue-50 p-4 rounded-lg">
                <h4 className="font-medium text-blue-900 mb-2">Trunks de Saída (Discagem)</h4>
                <ul className="text-sm text-blue-700 space-y-1">
                  <li>• Configure o host e credenciais do seu provedor VoIP</li>
                  <li>• Defina o código do país (52 para México, 1 para USA/Canadá, 55 para Brasil)</li>
                  <li>• O código do provedor é fornecido pelo seu provedor (ex: 9797)</li>
                  <li>• O dial string será gerado automaticamente: SIP/NomeTrunk/CodigoProvedor</li>
                  <li>• Para Brasil: use código de saída 55 (ex: SIP/DV/979755)</li>
                </ul>
              </div>
              
              <div className="bg-orange-50 p-4 rounded-lg">
                <h4 className="font-medium text-orange-900 mb-2">Trunks de Transferência (Clientes)</h4>
                <ul className="text-sm text-orange-700 space-y-1">
                  <li>• Configure para receber chamadas transferidas dos clientes</li>
                  <li>• Bridge Number é a extensão onde as chamadas serão transferidas</li>
                  <li>• Pode ser VoIP (usando extensão) ou telefone regular (usando bridge number)</li>
                  <li>• Configure o contexto apropriado (geralmente from-internal)</li>
                </ul>
              </div>
              
              <div className="bg-green-50 p-4 rounded-lg">
                <h4 className="font-medium text-green-900 mb-2">Exemplos de Configuração</h4>
                <div className="text-sm text-green-700 space-y-2">
                  <div>
                    <strong>México:</strong> Código País: 52, Provedor: 9797, Dial String: SIP/MX/9797
                  </div>
                  <div>
                    <strong>USA/Canadá:</strong> Código País: 1, Provedor: 9797, Dial String: SIP/US/97971
                  </div>
                  <div>
                    <strong>Brasil:</strong> Código País: 55, Provedor: 9797, Dial String: SIP/BR/979755
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default TrunkManager;