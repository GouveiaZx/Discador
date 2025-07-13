import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Select } from './ui/select';
import { Tabs, TabsList, TabsTrigger, TabsContent } from './ui/tabs';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import api from '../config/api';

const CountryConfigManager = () => {
  const [selectedCountry, setSelectedCountry] = useState('mexico');
  const [countryConfig, setCountryConfig] = useState(null);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [activeTab, setActiveTab] = useState('dtmf');

  // Estados para diferentes configurações
  const [dtmfConfig, setDtmfConfig] = useState({
    connect_key: '1',
    dnc_key: '2',
    disconnect_key: '9',
    repeat_key: '0',
    menu_timeout: 10,
    instructions: {
      spanish: '',
      english: ''
    }
  });

  const [cliStats, setCliStats] = useState(null);
  const [dncStats, setDncStats] = useState(null);
  const [newCliList, setNewCliList] = useState('');
  const [newDncNumber, setNewDncNumber] = useState('');

  const countries = [
    // América do Norte
    { value: 'usa', label: 'Estados Unidos', flag: '🇺🇸' },
    { value: 'canada', label: 'Canadá', flag: '🇨🇦' },
    
    // América Latina
    { value: 'mexico', label: 'México', flag: '🇲🇽' },
    { value: 'brasil', label: 'Brasil', flag: '🇧🇷' },
    { value: 'argentina', label: 'Argentina', flag: '🇦🇷' },
    { value: 'colombia', label: 'Colombia', flag: '🇨🇴' },
    { value: 'chile', label: 'Chile', flag: '🇨🇱' },
    { value: 'peru', label: 'Peru', flag: '🇵🇪' },
    { value: 'venezuela', label: 'Venezuela', flag: '🇻🇪' },
    { value: 'ecuador', label: 'Ecuador', flag: '🇪🇨' },
    { value: 'bolivia', label: 'Bolivia', flag: '🇧🇴' },
    { value: 'uruguay', label: 'Uruguay', flag: '🇺🇾' },
    { value: 'paraguay', label: 'Paraguay', flag: '🇵🇾' },
    { value: 'costa_rica', label: 'Costa Rica', flag: '🇨🇷' },
    { value: 'panama', label: 'Panamá', flag: '🇵🇦' },
    { value: 'guatemala', label: 'Guatemala', flag: '🇬🇹' },
    { value: 'honduras', label: 'Honduras', flag: '🇭🇳' },
    { value: 'el_salvador', label: 'El Salvador', flag: '🇸🇻' },
    { value: 'nicaragua', label: 'Nicaragua', flag: '🇳🇮' },
    { value: 'republica_dominicana', label: 'República Dominicana', flag: '🇩🇴' },
    { value: 'porto_rico', label: 'Porto Rico', flag: '🇵🇷' },
    
    // Europa
    { value: 'espanha', label: 'España', flag: '🇪🇸' },
    { value: 'portugal', label: 'Portugal', flag: '🇵🇹' },
    { value: 'franca', label: 'França', flag: '🇫🇷' },
    { value: 'alemanha', label: 'Alemanha', flag: '🇩🇪' },
    { value: 'italia', label: 'Itália', flag: '🇮🇹' },
    { value: 'reino_unido', label: 'Reino Unido', flag: '🇬🇧' },
    { value: 'holanda', label: 'Holanda', flag: '🇳🇱' },
    { value: 'belgica', label: 'Bélgica', flag: '🇧🇪' },
    { value: 'suica', label: 'Suíça', flag: '🇨🇭' },
    { value: 'austria', label: 'Áustria', flag: '🇦🇹' },
    
    // Ásia
    { value: 'india', label: 'Índia', flag: '🇮🇳' },
    { value: 'filipinas', label: 'Filipinas', flag: '🇵🇭' },
    { value: 'malasia', label: 'Malásia', flag: '🇲🇾' },
    { value: 'singapura', label: 'Singapura', flag: '🇸🇬' },
    { value: 'tailandia', label: 'Tailândia', flag: '🇹🇭' },
    { value: 'indonesia', label: 'Indonésia', flag: '🇮🇩' },
    
    // Oceania
    { value: 'australia', label: 'Austrália', flag: '🇦🇺' },
    { value: 'nova_zelandia', label: 'Nova Zelândia', flag: '🇳🇿' },
    
    // África
    { value: 'africa_do_sul', label: 'África do Sul', flag: '🇿🇦' },
    
    // Oriente Médio
    { value: 'israel', label: 'Israel', flag: '🇮🇱' }
  ];

  const availableKeys = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '0'];

  useEffect(() => {
    if (selectedCountry) {
      loadCountryConfig();
    }
  }, [selectedCountry]);

  const loadCountryConfig = async () => {
    setLoading(true);
    try {
      // Carregar configuração completa do país
      const response = await api.get(`/performance/country-config/${selectedCountry}`);
      
      if (response.data.status === 'success') {
        const config = response.data.data;
        setCountryConfig(config);
        
        // Configurar DTMF
        if (config.dtmf) {
          setDtmfConfig({
            connect_key: config.dtmf.connect_key || '1',
            dnc_key: config.dtmf.dnc_key || '2',
            disconnect_key: config.dtmf.disconnect_key || '9',
            repeat_key: config.dtmf.repeat_key || '0',
            menu_timeout: config.dtmf.menu_timeout || 10,
            instructions: config.dtmf.instructions || { spanish: '', english: '' }
          });
        }

        // Configurar CLI stats
        setCliStats(config.caller_id);
        
        // Configurar DNC stats
        setDncStats(config.dnc);
      }
    } catch (error) {
      console.error('Erro ao carregar configuração do país:', error);
      setMessage({
        type: 'error',
        text: `Erro ao carregar configuração: ${error.response?.data?.message || error.message}`
      });
    } finally {
      setLoading(false);
    }
  };

  const saveDtmfConfig = async () => {
    setLoading(true);
    try {
      const response = await api.post(`/performance/dtmf/config/${selectedCountry}`, dtmfConfig);
      
      if (response.data.status === 'success') {
        setMessage({
          type: 'success',
          text: `Configuração DTMF atualizada para ${selectedCountry}`
        });
        loadCountryConfig(); // Recarregar para ver as mudanças
      } else {
        setMessage({
          type: 'error',
          text: response.data.message || 'Erro ao salvar configuração'
        });
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: `Erro ao salvar: ${error.response?.data?.message || error.message}`
      });
    } finally {
      setLoading(false);
    }
  };

  const loadCliList = async () => {
    if (!newCliList.trim()) {
      setMessage({ type: 'error', text: 'Lista de CLIs não pode estar vazia' });
      return;
    }

    setLoading(true);
    try {
      const cliArray = newCliList.split('\n').map(cli => cli.trim()).filter(cli => cli);
      
      const response = await api.post(`/performance/caller-id/load/${selectedCountry}`, {
        cli_list: cliArray
      });
      
      if (response.data.status === 'success') {
        setMessage({
          type: 'success',
          text: `${cliArray.length} CLIs carregados para ${selectedCountry}`
        });
        setNewCliList('');
        loadCountryConfig();
      } else {
        setMessage({
          type: 'error',
          text: response.data.message || 'Erro ao carregar CLIs'
        });
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: `Erro ao carregar CLIs: ${error.response?.data?.message || error.message}`
      });
    } finally {
      setLoading(false);
    }
  };

  const resetCliUsage = async () => {
    setLoading(true);
    try {
      const response = await api.post(`/performance/caller-id/reset/${selectedCountry}`);
      
      if (response.data.status === 'success') {
        setMessage({
          type: 'success',
          text: `Uso de CLIs resetado para ${selectedCountry}`
        });
        loadCountryConfig();
      } else {
        setMessage({
          type: 'error',
          text: response.data.message || 'Erro ao resetar uso'
        });
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: `Erro ao resetar: ${error.response?.data?.message || error.message}`
      });
    } finally {
      setLoading(false);
    }
  };

  const addToDnc = async () => {
    if (!newDncNumber.trim()) {
      setMessage({ type: 'error', text: 'Número para DNC não pode estar vazio' });
      return;
    }

    setLoading(true);
    try {
      const response = await api.post('/performance/dnc/add', {
        phone_number: newDncNumber,
        country: selectedCountry,
        reason: 'manual_add'
      });
      
      if (response.data.status === 'success') {
        setMessage({
          type: 'success',
          text: `Número ${newDncNumber} adicionado à DNC de ${selectedCountry}`
        });
        setNewDncNumber('');
        loadCountryConfig();
      } else {
        setMessage({
          type: 'error',
          text: response.data.message || 'Erro ao adicionar à DNC'
        });
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: `Erro ao adicionar à DNC: ${error.response?.data?.message || error.message}`
      });
    } finally {
      setLoading(false);
    }
  };

  const generateDialplan = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/performance/dtmf/dialplan/${selectedCountry}`);
      
      if (response.data.status === 'success') {
        // Criar arquivo para download
        const blob = new Blob([response.data.data.dialplan], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `dtmf-${selectedCountry}-dialplan.conf`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        setMessage({
          type: 'success',
          text: `Dialplan gerado e baixado para ${selectedCountry}`
        });
      } else {
        setMessage({
          type: 'error',
          text: response.data.message || 'Erro ao gerar dialplan'
        });
      }
    } catch (error) {
      setMessage({
        type: 'error',
        text: `Erro ao gerar dialplan: ${error.response?.data?.message || error.message}`
      });
    } finally {
      setLoading(false);
    }
  };

  const selectedCountryInfo = countries.find(c => c.value === selectedCountry);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900">
          Configuración por País
        </h1>
        <div className="flex items-center space-x-4">
          <Select 
            value={selectedCountry} 
            onValueChange={setSelectedCountry}
            className="w-48"
          >
            {countries.map(country => (
              <option key={country.value} value={country.value}>
                {country.flag} {country.label}
              </option>
            ))}
          </Select>
          <Button 
            onClick={loadCountryConfig} 
            disabled={loading}
            variant="outline"
          >
            🔄 Recargar
          </Button>
        </div>
      </div>

      {message && (
        <Alert className={message.type === 'error' ? 'border-red-500 bg-red-50' : 'border-green-500 bg-green-50'}>
          <AlertDescription className={message.type === 'error' ? 'text-red-700' : 'text-green-700'}>
            {message.text}
          </AlertDescription>
        </Alert>
      )}

      {selectedCountryInfo && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center space-x-2">
              <span className="text-2xl">{selectedCountryInfo.flag}</span>
              <span>Configuración de {selectedCountryInfo.label}</span>
              {loading && <div className="animate-spin h-4 w-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Tabs value={activeTab} onValueChange={setActiveTab}>
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="dtmf">DTMF</TabsTrigger>
                <TabsTrigger value="caller-id">Caller ID</TabsTrigger>
                <TabsTrigger value="dnc">Lista Negra</TabsTrigger>
                <TabsTrigger value="overview">Resumen</TabsTrigger>
              </TabsList>

              {/* Tab DTMF */}
              <TabsContent value="dtmf" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Configuración DTMF</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium mb-2">
                          Tecla de Conexión
                        </label>
                        <Select 
                          value={dtmfConfig.connect_key} 
                          onValueChange={(value) => setDtmfConfig({...dtmfConfig, connect_key: value})}
                        >
                          {availableKeys.map(key => (
                            <option key={key} value={key}>Tecla {key}</option>
                          ))}
                        </Select>
                        {selectedCountry === 'mexico' && dtmfConfig.connect_key === '1' && (
                          <p className="text-sm text-orange-600 mt-1">
                            ⚠️ En México se recomienda usar tecla 3 para evitar contestadoras
                          </p>
                        )}
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-2">
                          Tecla de Lista Negra (DNC)
                        </label>
                        <Select 
                          value={dtmfConfig.dnc_key} 
                          onValueChange={(value) => setDtmfConfig({...dtmfConfig, dnc_key: value})}
                        >
                          {availableKeys.map(key => (
                            <option key={key} value={key}>Tecla {key}</option>
                          ))}
                        </Select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-2">
                          Tecla de Desconexión
                        </label>
                        <Select 
                          value={dtmfConfig.disconnect_key} 
                          onValueChange={(value) => setDtmfConfig({...dtmfConfig, disconnect_key: value})}
                        >
                          {availableKeys.map(key => (
                            <option key={key} value={key}>Tecla {key}</option>
                          ))}
                        </Select>
                      </div>

                      <div>
                        <label className="block text-sm font-medium mb-2">
                          Timeout del Menú (segundos)
                        </label>
                        <Input
                          type="number"
                          value={dtmfConfig.menu_timeout}
                          onChange={(e) => setDtmfConfig({...dtmfConfig, menu_timeout: parseInt(e.target.value)})}
                          min="5"
                          max="30"
                        />
                      </div>
                    </div>

                    <div className="space-y-2">
                      <label className="block text-sm font-medium">
                        Instrucciones en Español
                      </label>
                      <Input
                        value={dtmfConfig.instructions.spanish || ''}
                        onChange={(e) => setDtmfConfig({
                          ...dtmfConfig, 
                          instructions: {...dtmfConfig.instructions, spanish: e.target.value}
                        })}
                        placeholder="Presione 3 para conectar, 2 para ser removido de la lista..."
                      />
                    </div>

                    <div className="space-y-2">
                      <label className="block text-sm font-medium">
                        Instrucciones en Inglés
                      </label>
                      <Input
                        value={dtmfConfig.instructions.english || ''}
                        onChange={(e) => setDtmfConfig({
                          ...dtmfConfig, 
                          instructions: {...dtmfConfig.instructions, english: e.target.value}
                        })}
                        placeholder="Press 3 to connect, 2 to be removed from list..."
                      />
                    </div>

                    <div className="flex space-x-2">
                      <Button onClick={saveDtmfConfig} disabled={loading}>
                        💾 Guardar Configuración DTMF
                      </Button>
                      <Button onClick={generateDialplan} variant="outline" disabled={loading}>
                        📄 Generar Dialplan Asterisk
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Tab Caller ID */}
              <TabsContent value="caller-id" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Gestión de Caller ID</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {cliStats && (
                      <div className="grid grid-cols-3 gap-4 mb-4">
                        <div className="bg-blue-50 p-3 rounded-lg">
                          <div className="text-2xl font-bold text-blue-600">{cliStats.total_clis || 0}</div>
                          <div className="text-sm text-blue-600">Total CLIs</div>
                        </div>
                        <div className="bg-green-50 p-3 rounded-lg">
                          <div className="text-2xl font-bold text-green-600">
                            {cliStats.daily_limit === 0 ? '∞' : cliStats.daily_limit}
                          </div>
                          <div className="text-sm text-green-600">Límite Diario</div>
                        </div>
                        <div className="bg-orange-50 p-3 rounded-lg">
                          <div className="text-2xl font-bold text-orange-600">{cliStats.used_today || 0}</div>
                          <div className="text-sm text-orange-600">Usados Hoy</div>
                        </div>
                      </div>
                    )}

                    <div>
                      <label className="block text-sm font-medium mb-2">
                        Cargar Lista de CLIs (uno por línea)
                      </label>
                      <textarea
                        value={newCliList}
                        onChange={(e) => setNewCliList(e.target.value)}
                        placeholder="+525555551000&#10;+525555551001&#10;+525555551002"
                        rows="5"
                        className="w-full border border-gray-300 rounded-md p-2"
                      />
                    </div>

                    <div className="flex space-x-2">
                      <Button onClick={loadCliList} disabled={loading}>
                        📤 Cargar Lista CLIs
                      </Button>
                      <Button onClick={resetCliUsage} variant="outline" disabled={loading}>
                        🔄 Reset Uso Diario
                      </Button>
                    </div>

                    {(selectedCountry === 'usa' || selectedCountry === 'canada') && (
                      <Alert className="border-yellow-500 bg-yellow-50">
                        <AlertDescription className="text-yellow-700">
                          ⚠️ {selectedCountryInfo.label} tiene restricción de 100 CLIs por día
                        </AlertDescription>
                      </Alert>
                    )}
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Tab DNC */}
              <TabsContent value="dnc" className="space-y-4">
                <Card>
                  <CardHeader>
                    <CardTitle>Lista Negra (Do Not Call)</CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    {dncStats && (
                      <div className="grid grid-cols-3 gap-4 mb-4">
                        <div className="bg-red-50 p-3 rounded-lg">
                          <div className="text-2xl font-bold text-red-600">{dncStats.total_entries || 0}</div>
                          <div className="text-sm text-red-600">Total en DNC</div>
                        </div>
                        <div className="bg-green-50 p-3 rounded-lg">
                          <div className="text-2xl font-bold text-green-600">{dncStats.active_entries || 0}</div>
                          <div className="text-sm text-green-600">Activos</div>
                        </div>
                        <div className="bg-gray-50 p-3 rounded-lg">
                          <div className="text-2xl font-bold text-gray-600">{dncStats.expired_entries || 0}</div>
                          <div className="text-sm text-gray-600">Expirados</div>
                        </div>
                      </div>
                    )}

                    <div>
                      <label className="block text-sm font-medium mb-2">
                        Agregar Número a Lista Negra
                      </label>
                      <div className="flex space-x-2">
                        <Input
                          value={newDncNumber}
                          onChange={(e) => setNewDncNumber(e.target.value)}
                          placeholder="+525555551234"
                          className="flex-1"
                        />
                        <Button onClick={addToDnc} disabled={loading}>
                          ➕ Agregar
                        </Button>
                      </div>
                    </div>

                    <div className="bg-gray-50 p-3 rounded-lg">
                      <h4 className="font-medium mb-2">Configuración DNC</h4>
                      <p className="text-sm text-gray-600">
                        Tecla para remoción: <Badge>{dtmfConfig.dnc_key}</Badge>
                      </p>
                      <p className="text-sm text-gray-600 mt-1">
                        Los clientes pueden presionar la tecla {dtmfConfig.dnc_key} para ser removidos automáticamente de la lista.
                      </p>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Tab Overview */}
              <TabsContent value="overview" className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">DTMF</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span>Conectar:</span>
                          <Badge>{dtmfConfig.connect_key}</Badge>
                        </div>
                        <div className="flex justify-between">
                          <span>Lista Negra:</span>
                          <Badge>{dtmfConfig.dnc_key}</Badge>
                        </div>
                        <div className="flex justify-between">
                          <span>Timeout:</span>
                          <Badge>{dtmfConfig.menu_timeout}s</Badge>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Caller ID</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span>Total CLIs:</span>
                          <Badge variant="outline">{cliStats?.total_clis || 0}</Badge>
                        </div>
                        <div className="flex justify-between">
                          <span>Límite:</span>
                          <Badge variant={cliStats?.daily_limit === 0 ? 'default' : 'destructive'}>
                            {cliStats?.daily_limit === 0 ? 'Ilimitado' : `${cliStats?.daily_limit}/día`}
                          </Badge>
                        </div>
                        <div className="flex justify-between">
                          <span>Usado hoy:</span>
                          <Badge variant="secondary">{cliStats?.used_today || 0}</Badge>
                        </div>
                      </div>
                    </CardContent>
                  </Card>

                  <Card>
                    <CardHeader>
                      <CardTitle className="text-lg">Lista Negra</CardTitle>
                    </CardHeader>
                    <CardContent>
                      <div className="space-y-2">
                        <div className="flex justify-between">
                          <span>Total DNC:</span>
                          <Badge variant="destructive">{dncStats?.total_entries || 0}</Badge>
                        </div>
                        <div className="flex justify-between">
                          <span>Activos:</span>
                          <Badge variant="outline">{dncStats?.active_entries || 0}</Badge>
                        </div>
                        <div className="flex justify-between">
                          <span>Tecla:</span>
                          <Badge>{dtmfConfig.dnc_key}</Badge>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>

                {selectedCountry === 'mexico' && (
                  <Alert className="border-blue-500 bg-blue-50">
                    <AlertDescription className="text-blue-700">
                      🇲🇽 <strong>México:</strong> Configurado con tecla {dtmfConfig.connect_key} para conexión (recomendado para evitar contestadoras automáticas)
                    </AlertDescription>
                  </Alert>
                )}

                {(selectedCountry === 'usa' || selectedCountry === 'canada') && (
                  <Alert className="border-yellow-500 bg-yellow-50">
                    <AlertDescription className="text-yellow-700">
                      {selectedCountryInfo.flag} <strong>{selectedCountryInfo.label}:</strong> Restricción de 100 CLIs por día por regulaciones locales
                    </AlertDescription>
                  </Alert>
                )}
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default CountryConfigManager; 