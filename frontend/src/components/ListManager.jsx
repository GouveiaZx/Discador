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
import { Progress } from './ui/progress';

const ListManager = () => {
  const [activeTab, setActiveTab] = useState('campaign-lists');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  
  // Estados para listas de campanha
  const [campaignLists, setCampaignLists] = useState([]);
  const [showListForm, setShowListForm] = useState(false);
  const [listForm, setListForm] = useState({
    nome: '',
    descricao: '',
    arquivo: null,
    formato: 'csv', // csv, txt, xlsx
    coluna_numero: 1,
    coluna_nome: 2,
    tem_cabecalho: true,
    separador: ',',
    campanha_id: ''
  });
  
  // Estados para listas DNC
  const [dncLists, setDncLists] = useState([]);
  const [showDncForm, setShowDncForm] = useState(false);
  const [dncForm, setDncForm] = useState({
    nome: '',
    descricao: '',
    arquivo: null,
    tipo: 'manual', // manual, automatico, transferidos, eliminados
    ativo: true
  });
  
  // Estados para números transferidos/eliminados
  const [transferredNumbers, setTransferredNumbers] = useState([]);
  const [eliminatedNumbers, setEliminatedNumbers] = useState([]);
  const [showTransferredForm, setShowTransferredForm] = useState(false);
  
  // Estados para estatísticas
  const [listStats, setListStats] = useState({
    total_numeros: 0,
    numeros_ativos: 0,
    numeros_dnc: 0,
    numeros_transferidos: 0,
    numeros_eliminados: 0,
    listas_ativas: 0
  });
  
  // Estados para processamento em lote
  const [batchProcessing, setBatchProcessing] = useState(false);
  const [processingStatus, setProcessingStatus] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        fetchCampaignLists(),
        fetchDncLists(),
        fetchTransferredNumbers(),
        fetchEliminatedNumbers(),
        fetchListStats()
      ]);
    } catch (err) {
      setError('Erro ao carregar dados: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchCampaignLists = async () => {
    try {
      const response = await makeApiRequest('/campaign-lists');
      setCampaignLists(response.lists || []);
    } catch (err) {
      console.error('Erro ao buscar listas de campanha:', err);
    }
  };

  const fetchDncLists = async () => {
    try {
      const response = await makeApiRequest('/dnc-lists');
      setDncLists(response.lists || []);
    } catch (err) {
      console.error('Erro ao buscar listas DNC:', err);
    }
  };

  const fetchTransferredNumbers = async () => {
    try {
      const response = await makeApiRequest('/transferred-numbers');
      setTransferredNumbers(response.numbers || []);
    } catch (err) {
      console.error('Erro ao buscar números transferidos:', err);
    }
  };

  const fetchEliminatedNumbers = async () => {
    try {
      const response = await makeApiRequest('/eliminated-numbers');
      setEliminatedNumbers(response.numbers || []);
    } catch (err) {
      console.error('Erro ao buscar números eliminados:', err);
    }
  };

  const fetchListStats = async () => {
    try {
      const response = await makeApiRequest('/list-stats');
      setListStats(response.stats || listStats);
    } catch (err) {
      console.error('Erro ao buscar estatísticas:', err);
    }
  };

  const handleListUpload = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      setUploadProgress(0);
      
      const formData = new FormData();
      Object.keys(listForm).forEach(key => {
        if (listForm[key] !== null && listForm[key] !== '') {
          formData.append(key, listForm[key]);
        }
      });
      
      // Simular progresso de upload
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return 90;
          }
          return prev + 10;
        });
      }, 200);
      
      const response = await makeApiRequest('/campaign-lists', 'POST', formData, {
        'Content-Type': 'multipart/form-data'
      });
      
      clearInterval(progressInterval);
      setUploadProgress(100);
      
      await fetchCampaignLists();
      await fetchListStats();
      resetListForm();
      setSuccess(`Lista carregada com sucesso! ${response.total_numbers || 0} números processados.`);
    } catch (err) {
      setError('Erro ao carregar lista: ' + err.message);
    } finally {
      setLoading(false);
      setTimeout(() => setUploadProgress(0), 2000);
    }
  };

  const handleDncUpload = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      
      const formData = new FormData();
      Object.keys(dncForm).forEach(key => {
        if (dncForm[key] !== null && dncForm[key] !== '') {
          formData.append(key, dncForm[key]);
        }
      });
      
      await makeApiRequest('/dnc-lists', 'POST', formData, {
        'Content-Type': 'multipart/form-data'
      });
      
      await fetchDncLists();
      await fetchListStats();
      resetDncForm();
      setSuccess('Lista DNC carregada com sucesso!');
    } catch (err) {
      setError('Erro ao carregar lista DNC: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadList = async (listId, type = 'campaign') => {
    try {
      setLoading(true);
      const endpoint = type === 'dnc' ? `/dnc-lists/${listId}/download` : `/campaign-lists/${listId}/download`;
      
      const response = await makeApiRequest(endpoint, 'GET', null, {
        'Accept': 'text/csv'
      });
      
      // Criar e baixar arquivo
      const blob = new Blob([response], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `lista_${type}_${listId}_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      setSuccess('Download iniciado com sucesso!');
    } catch (err) {
      setError('Erro ao baixar lista: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadTransferredNumbers = async () => {
    try {
      setLoading(true);
      const response = await makeApiRequest('/transferred-numbers/download', 'GET', null, {
        'Accept': 'text/csv'
      });
      
      const blob = new Blob([response], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `numeros_transferidos_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      setSuccess('Download de números transferidos iniciado!');
    } catch (err) {
      setError('Erro ao baixar números transferidos: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const downloadEliminatedNumbers = async () => {
    try {
      setLoading(true);
      const response = await makeApiRequest('/eliminated-numbers/download', 'GET', null, {
        'Accept': 'text/csv'
      });
      
      const blob = new Blob([response], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `numeros_eliminados_${new Date().toISOString().split('T')[0]}.csv`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      setSuccess('Download de números eliminados iniciado!');
    } catch (err) {
      setError('Erro ao baixar números eliminados: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const createDncFromTransferred = async () => {
    if (!confirm('Criar lista DNC com todos os números transferidos?')) return;
    
    try {
      setLoading(true);
      await makeApiRequest('/dnc-lists/from-transferred', 'POST', {
        nome: `DNC_Transferidos_${new Date().toISOString().split('T')[0]}`,
        descricao: 'Lista DNC criada automaticamente com números transferidos'
      });
      
      await fetchDncLists();
      await fetchListStats();
      setSuccess('Lista DNC criada com números transferidos!');
    } catch (err) {
      setError('Erro ao criar lista DNC: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const createDncFromEliminated = async () => {
    if (!confirm('Criar lista DNC com todos os números eliminados?')) return;
    
    try {
      setLoading(true);
      await makeApiRequest('/dnc-lists/from-eliminated', 'POST', {
        nome: `DNC_Eliminados_${new Date().toISOString().split('T')[0]}`,
        descricao: 'Lista DNC criada automaticamente com números eliminados'
      });
      
      await fetchDncLists();
      await fetchListStats();
      setSuccess('Lista DNC criada com números eliminados!');
    } catch (err) {
      setError('Erro ao criar lista DNC: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteList = async (listId, type = 'campaign') => {
    if (!confirm('Tem certeza que deseja excluir esta lista?')) return;
    
    try {
      setLoading(true);
      const endpoint = type === 'dnc' ? `/dnc-lists/${listId}` : `/campaign-lists/${listId}`;
      await makeApiRequest(endpoint, 'DELETE');
      
      if (type === 'dnc') {
        await fetchDncLists();
      } else {
        await fetchCampaignLists();
      }
      await fetchListStats();
      setSuccess('Lista excluída com sucesso!');
    } catch (err) {
      setError('Erro ao excluir lista: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const resetListForm = () => {
    setListForm({
      nome: '',
      descricao: '',
      arquivo: null,
      formato: 'csv',
      coluna_numero: 1,
      coluna_nome: 2,
      tem_cabecalho: true,
      separador: ',',
      campanha_id: ''
    });
    setShowListForm(false);
  };

  const resetDncForm = () => {
    setDncForm({
      nome: '',
      descricao: '',
      arquivo: null,
      tipo: 'manual',
      ativo: true
    });
    setShowDncForm(false);
  };

  const formatNumber = (num) => {
    return new Intl.NumberFormat('pt-BR').format(num || 0);
  };

  const getListStatusColor = (status) => {
    switch (status) {
      case 'ativa': return 'bg-green-100 text-green-800';
      case 'processando': return 'bg-yellow-100 text-yellow-800';
      case 'erro': return 'bg-red-100 text-red-800';
      case 'pausada': return 'bg-gray-100 text-gray-800';
      default: return 'bg-blue-100 text-blue-800';
    }
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Gestão de Listas</h1>
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

      {/* Estatísticas Gerais */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <Card className="p-4">
          <div className="text-2xl font-bold text-blue-600">{formatNumber(listStats.total_numeros)}</div>
          <div className="text-sm text-gray-600">Total de Números</div>
        </Card>
        <Card className="p-4">
          <div className="text-2xl font-bold text-green-600">{formatNumber(listStats.numeros_ativos)}</div>
          <div className="text-sm text-gray-600">Números Ativos</div>
        </Card>
        <Card className="p-4">
          <div className="text-2xl font-bold text-red-600">{formatNumber(listStats.numeros_dnc)}</div>
          <div className="text-sm text-gray-600">Números DNC</div>
        </Card>
        <Card className="p-4">
          <div className="text-2xl font-bold text-purple-600">{formatNumber(listStats.numeros_transferidos)}</div>
          <div className="text-sm text-gray-600">Transferidos</div>
        </Card>
        <Card className="p-4">
          <div className="text-2xl font-bold text-orange-600">{formatNumber(listStats.numeros_eliminados)}</div>
          <div className="text-sm text-gray-600">Eliminados</div>
        </Card>
        <Card className="p-4">
          <div className="text-2xl font-bold text-indigo-600">{formatNumber(listStats.listas_ativas)}</div>
          <div className="text-sm text-gray-600">Listas Ativas</div>
        </Card>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="campaign-lists">Listas de Campanha</TabsTrigger>
          <TabsTrigger value="dnc-lists">Listas DNC</TabsTrigger>
          <TabsTrigger value="transferred">Números Transferidos</TabsTrigger>
          <TabsTrigger value="eliminated">Números Eliminados</TabsTrigger>
        </TabsList>

        <TabsContent value="campaign-lists" className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Listas de Campanha</h2>
            <Button 
              onClick={() => setShowListForm(!showListForm)}
              className="bg-blue-600 hover:bg-blue-700"
            >
              {showListForm ? 'Cancelar' : 'Nova Lista'}
            </Button>
          </div>

          {showListForm && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Upload de Lista de Campanha</h3>
              
              <form onSubmit={handleListUpload} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="list_nome">Nome da Lista</Label>
                    <Input
                      id="list_nome"
                      value={listForm.nome}
                      onChange={(e) => setListForm({...listForm, nome: e.target.value})}
                      placeholder="Ex: Campanha Janeiro 2024"
                      required
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="list_formato">Formato do Arquivo</Label>
                    <Select
                      value={listForm.formato}
                      onValueChange={(value) => setListForm({...listForm, formato: value})}
                    >
                      <option value="csv">CSV</option>
                      <option value="txt">TXT</option>
                      <option value="xlsx">Excel (XLSX)</option>
                    </Select>
                  </div>
                  
                  <div>
                    <Label htmlFor="list_arquivo">Arquivo</Label>
                    <Input
                      id="list_arquivo"
                      type="file"
                      accept=".csv,.txt,.xlsx"
                      onChange={(e) => setListForm({...listForm, arquivo: e.target.files[0]})}
                      required
                    />
                    <div className="text-xs text-gray-500 mt-1">
                      Máximo 1 milhão de números. Sistema não para durante o carregamento.
                    </div>
                  </div>
                  
                  <div>
                    <Label htmlFor="coluna_numero">Coluna do Número</Label>
                    <Input
                      id="coluna_numero"
                      type="number"
                      value={listForm.coluna_numero}
                      onChange={(e) => setListForm({...listForm, coluna_numero: parseInt(e.target.value)})}
                      min="1"
                      max="50"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="coluna_nome">Coluna do Nome (Opcional)</Label>
                    <Input
                      id="coluna_nome"
                      type="number"
                      value={listForm.coluna_nome}
                      onChange={(e) => setListForm({...listForm, coluna_nome: parseInt(e.target.value)})}
                      min="1"
                      max="50"
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="separador">Separador (CSV/TXT)</Label>
                    <Select
                      value={listForm.separador}
                      onValueChange={(value) => setListForm({...listForm, separador: value})}
                    >
                      <option value=",">Vírgula (,)</option>
                      <option value=";">Ponto e vírgula (;)</option>
                      <option value="\t">Tab</option>
                      <option value="|">Pipe (|)</option>
                    </Select>
                  </div>
                </div>
                
                <div>
                  <Label htmlFor="list_descricao">Descrição</Label>
                  <Input
                    id="list_descricao"
                    value={listForm.descricao}
                    onChange={(e) => setListForm({...listForm, descricao: e.target.value})}
                    placeholder="Descrição da lista"
                  />
                </div>
                
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="tem_cabecalho"
                    checked={listForm.tem_cabecalho}
                    onChange={(e) => setListForm({...listForm, tem_cabecalho: e.target.checked})}
                    className="rounded"
                  />
                  <Label htmlFor="tem_cabecalho">Arquivo possui cabeçalho</Label>
                </div>
                
                {uploadProgress > 0 && (
                  <div className="space-y-2">
                    <div className="flex justify-between text-sm">
                      <span>Progresso do upload:</span>
                      <span>{uploadProgress}%</span>
                    </div>
                    <Progress value={uploadProgress} className="w-full" />
                  </div>
                )}
                
                <div className="flex space-x-2">
                  <Button type="submit" disabled={loading}>
                    {loading ? 'Carregando...' : 'Carregar Lista'}
                  </Button>
                  <Button type="button" variant="outline" onClick={resetListForm}>
                    Cancelar
                  </Button>
                </div>
              </form>
            </Card>
          )}

          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Listas de Campanha</h3>
            
            {campaignLists.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                Nenhuma lista encontrada. Carregue sua primeira lista de campanha.
              </div>
            ) : (
              <div className="space-y-4">
                {campaignLists.map((list) => (
                  <div key={list.id} className="border rounded-lg p-4 hover:bg-gray-50">
                    <div className="flex justify-between items-start">
                      <div className="flex-1">
                        <div className="flex items-center space-x-2 mb-2">
                          <h4 className="font-medium text-gray-900">{list.nome}</h4>
                          <Badge className={getListStatusColor(list.status)}>
                            {list.status}
                          </Badge>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{list.descricao}</p>
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-2 text-xs text-gray-500">
                          <div>Total: {formatNumber(list.total_numeros)}</div>
                          <div>Ativos: {formatNumber(list.numeros_ativos)}</div>
                          <div>Discados: {formatNumber(list.numeros_discados)}</div>
                          <div>Criada: {new Date(list.created_at).toLocaleDateString()}</div>
                        </div>
                      </div>
                      <div className="flex space-x-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => downloadList(list.id, 'campaign')}
                        >
                          Download
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          className="border-red-300 text-red-600 hover:bg-red-50"
                          onClick={() => deleteList(list.id, 'campaign')}
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

        <TabsContent value="dnc-lists" className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Listas DNC (Do Not Call)</h2>
            <Button 
              onClick={() => setShowDncForm(!showDncForm)}
              className="bg-red-600 hover:bg-red-700"
            >
              {showDncForm ? 'Cancelar' : 'Nova Lista DNC'}
            </Button>
          </div>

          {showDncForm && (
            <Card className="p-6">
              <h3 className="text-lg font-semibold mb-4">Nova Lista DNC</h3>
              
              <form onSubmit={handleDncUpload} className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <Label htmlFor="dnc_nome">Nome da Lista DNC</Label>
                    <Input
                      id="dnc_nome"
                      value={dncForm.nome}
                      onChange={(e) => setDncForm({...dncForm, nome: e.target.value})}
                      placeholder="Ex: DNC Principal"
                      required
                    />
                  </div>
                  
                  <div>
                    <Label htmlFor="dnc_tipo">Tipo de Lista</Label>
                    <Select
                      value={dncForm.tipo}
                      onValueChange={(value) => setDncForm({...dncForm, tipo: value})}
                    >
                      <option value="manual">Manual (Upload)</option>
                      <option value="automatico">Automática (Sistema)</option>
                      <option value="transferidos">Números Transferidos</option>
                      <option value="eliminados">Números Eliminados</option>
                    </Select>
                  </div>
                  
                  {dncForm.tipo === 'manual' && (
                    <div>
                      <Label htmlFor="dnc_arquivo">Arquivo CSV</Label>
                      <Input
                        id="dnc_arquivo"
                        type="file"
                        accept=".csv,.txt"
                        onChange={(e) => setDncForm({...dncForm, arquivo: e.target.files[0]})}
                        required
                      />
                      <div className="text-xs text-gray-500 mt-1">
                        Apenas números, um por linha ou separados por vírgula
                      </div>
                    </div>
                  )}
                </div>
                
                <div>
                  <Label htmlFor="dnc_descricao">Descrição</Label>
                  <Input
                    id="dnc_descricao"
                    value={dncForm.descricao}
                    onChange={(e) => setDncForm({...dncForm, descricao: e.target.value})}
                    placeholder="Descrição da lista DNC"
                  />
                </div>
                
                <div className="flex space-x-2">
                  <Button type="submit" disabled={loading}>
                    {loading ? 'Criando...' : 'Criar Lista DNC'}
                  </Button>
                  <Button type="button" variant="outline" onClick={resetDncForm}>
                    Cancelar
                  </Button>
                </div>
              </form>
            </Card>
          )}

          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Listas DNC Existentes</h3>
            
            <div className="space-y-4">
              {dncLists.map((list) => (
                <div key={list.id} className="border rounded-lg p-4 hover:bg-gray-50">
                  <div className="flex justify-between items-start">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <h4 className="font-medium text-gray-900">{list.nome}</h4>
                        <Badge className={list.ativo ? "bg-red-100 text-red-800" : "bg-gray-100 text-gray-800"}>
                          {list.ativo ? 'Ativa' : 'Inativa'}
                        </Badge>
                        <Badge className="bg-purple-100 text-purple-800">
                          {list.tipo}
                        </Badge>
                      </div>
                      <p className="text-sm text-gray-600 mb-2">{list.descricao}</p>
                      <div className="text-xs text-gray-500">
                        {formatNumber(list.total_numeros)} números • Criada em {new Date(list.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    <div className="flex space-x-2">
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => downloadList(list.id, 'dnc')}
                      >
                        Download
                      </Button>
                      <Button
                        size="sm"
                        variant="outline"
                        className="border-red-300 text-red-600 hover:bg-red-50"
                        onClick={() => deleteList(list.id, 'dnc')}
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

        <TabsContent value="transferred" className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Números Transferidos</h2>
            <div className="flex space-x-2">
              <Button 
                onClick={downloadTransferredNumbers}
                className="bg-green-600 hover:bg-green-700"
              >
                Download CSV
              </Button>
              <Button 
                onClick={createDncFromTransferred}
                className="bg-purple-600 hover:bg-purple-700"
              >
                Criar Lista DNC
              </Button>
            </div>
          </div>

          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Histórico de Transferências</h3>
            <p className="text-sm text-gray-600 mb-4">
              Números que foram transferidos com sucesso para agentes. Inclui informações da campanha, áudio usado, data/hora e duração da chamada.
            </p>
            
            <div className="space-y-4">
              {transferredNumbers.slice(0, 10).map((record, index) => (
                <div key={index} className="border rounded-lg p-4 hover:bg-gray-50">
                  <div className="grid grid-cols-1 md:grid-cols-5 gap-2 text-sm">
                    <div>
                      <span className="font-medium">Número:</span> {record.numero}
                    </div>
                    <div>
                      <span className="font-medium">Campanha:</span> {record.campanha_nome}
                    </div>
                    <div>
                      <span className="font-medium">Áudio:</span> {record.audio_nome}
                    </div>
                    <div>
                      <span className="font-medium">Data:</span> {new Date(record.data_transferencia).toLocaleString()}
                    </div>
                    <div>
                      <span className="font-medium">Duração:</span> {record.duracao_chamada}s
                    </div>
                  </div>
                </div>
              ))}
              
              {transferredNumbers.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  Nenhum número transferido encontrado.
                </div>
              )}
              
              {transferredNumbers.length > 10 && (
                <div className="text-center text-sm text-gray-500">
                  Mostrando 10 de {formatNumber(transferredNumbers.length)} registros. Use o download para ver todos.
                </div>
              )}
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="eliminated" className="space-y-6">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Números Eliminados</h2>
            <div className="flex space-x-2">
              <Button 
                onClick={downloadEliminatedNumbers}
                className="bg-orange-600 hover:bg-orange-700"
              >
                Download CSV
              </Button>
              <Button 
                onClick={createDncFromEliminated}
                className="bg-purple-600 hover:bg-purple-700"
              >
                Criar Lista DNC
              </Button>
            </div>
          </div>

          <Card className="p-6">
            <h3 className="text-lg font-semibold mb-4">Números Eliminados</h3>
            <p className="text-sm text-gray-600 mb-4">
              Números que foram removidos das listas de chamadas através de DTMF (ex: pressionaram 9 para sair).
            </p>
            
            <div className="space-y-4">
              {eliminatedNumbers.slice(0, 10).map((record, index) => (
                <div key={index} className="border rounded-lg p-4 hover:bg-gray-50">
                  <div className="grid grid-cols-1 md:grid-cols-4 gap-2 text-sm">
                    <div>
                      <span className="font-medium">Número:</span> {record.numero}
                    </div>
                    <div>
                      <span className="font-medium">Campanha:</span> {record.campanha_nome}
                    </div>
                    <div>
                      <span className="font-medium">Motivo:</span> {record.motivo_eliminacao}
                    </div>
                    <div>
                      <span className="font-medium">Data:</span> {new Date(record.data_eliminacao).toLocaleString()}
                    </div>
                  </div>
                </div>
              ))}
              
              {eliminatedNumbers.length === 0 && (
                <div className="text-center py-8 text-gray-500">
                  Nenhum número eliminado encontrado.
                </div>
              )}
              
              {eliminatedNumbers.length > 10 && (
                <div className="text-center text-sm text-gray-500">
                  Mostrando 10 de {formatNumber(eliminatedNumbers.length)} registros. Use o download para ver todos.
                </div>
              )}
            </div>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default ListManager;