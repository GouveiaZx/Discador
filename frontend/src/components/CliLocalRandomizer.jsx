import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Select } from './ui/select';
import { Alert } from './ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import api from '../config/api';

const CliLocalRandomizer = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [countryPatterns, setCountryPatterns] = useState({});
  const [loading, setLoading] = useState(false);
  const [testNumber, setTestNumber] = useState('');
  const [selectedCountry, setSelectedCountry] = useState('');
  const [testResults, setTestResults] = useState([]);
  const [generationStats, setGenerationStats] = useState({});
  const [bulkNumbers, setBulkNumbers] = useState('');
  const [bulkResults, setBulkResults] = useState(null);

  // Bandeiras dos países
  const countryFlags = {
    'usa': '🇺🇸',
    'canada': '🇨🇦',
    'mexico': '🇲🇽',
    'brasil': '🇧🇷',
    'colombia': '🇨🇴',
    'argentina': '🇦🇷',
    'chile': '🇨🇱',
    'peru': '🇵🇪'
  };

  // Exemplos de números por país
  const exampleNumbers = {
    'usa': ['+13055551234', '+14255551234', '+12135551234'],
    'canada': '+14165551234',
    'mexico': ['+525555551234', '+528155551234', '+523355551234'],
    'brasil': ['+5511955551234', '+5521955551234', '+5531955551234'],
    'colombia': '+5715551234',
    'argentina': '+5491155551234',
    'chile': '+56225551234',
    'peru': '+5115551234'
  };

  useEffect(() => {
    loadCountryPatterns();
    loadGenerationStats();
  }, []);

  const loadCountryPatterns = async () => {
    try {
      setLoading(true);
      const response = await api.get('/performance/cli-local/patterns');
      if (response.data.status === 'success') {
        setCountryPatterns(response.data.data.countries);
      }
    } catch (error) {
      console.error('Erro ao carregar padrões:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadGenerationStats = async (country = null) => {
    try {
      const url = country ? `/performance/cli-local/stats?country=${country}` : '/performance/cli-local/stats';
      const response = await api.get(url);
      if (response.data.status === 'success') {
        setGenerationStats(response.data.data);
      }
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
    }
  };

  const generateTestCli = async () => {
    if (!testNumber.trim()) {
      alert('Digite um número para teste');
      return;
    }

    try {
      setLoading(true);
      const url = `/performance/cli-local/test/${encodeURIComponent(testNumber)}${selectedCountry ? `?country_override=${selectedCountry}` : ''}`;
      const response = await api.get(url);
      
      if (response.data.status === 'success') {
        setTestResults(response.data.data.generated_clis);
        loadGenerationStats(selectedCountry);
      } else {
        alert(`Erro: ${response.data.message}`);
      }
    } catch (error) {
      console.error('Erro ao gerar CLI:', error);
      alert('Erro ao gerar CLI de teste');
    } finally {
      setLoading(false);
    }
  };

  const generateBulkClis = async () => {
    const numbers = bulkNumbers.split('\n').filter(num => num.trim());
    if (numbers.length === 0) {
      alert('Digite números para geração em lote');
      return;
    }

    try {
      setLoading(true);
      const response = await api.post('/performance/cli-local/bulk-generate', {
        destination_numbers: numbers
      });
      
      if (response.data.status === 'success') {
        setBulkResults(response.data.data);
        loadGenerationStats();
      } else {
        alert(`Erro: ${response.data.message}`);
      }
    } catch (error) {
      console.error('Erro na geração em lote:', error);
      alert('Erro na geração em lote');
    } finally {
      setLoading(false);
    }
  };

  const fillExampleNumber = (country) => {
    const examples = exampleNumbers[country];
    if (examples) {
      setTestNumber(Array.isArray(examples) ? examples[0] : examples);
      setSelectedCountry(country);
    }
  };

  const getStrategyDescription = (strategy) => {
    const descriptions = {
      'area_code_preservation': 'Mantém código de área + prefixo personalizado + aleatorização',
      'local_area_randomization': 'Código de área fixo + aleatorização completa dos últimos dígitos',
      'ddd_preservation': 'Mantém DDD + indicador celular + aleatorização inteligente'
    };
    return descriptions[strategy] || strategy;
  };

  const formatExamplePattern = (country, config) => {
    switch (country) {
      case 'usa':
      case 'canada':
        return '+1 [305] 2xx-xxxx (Area Code + prefixo + 4 aleatórios)';
      case 'mexico':
        return '+52 [55] xxxxxxx (Código + 7 dígitos aleatórios)';
      case 'brasil':
        return '+55 [11] 9xxxx-xxxx (DDD + 9 + aleatorização)';
      default:
        return `${config.country_code} [área] + aleatorização`;
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-white">CLI Local Randomizer</h2>
          <p className="text-gray-400">
            Gera números de Caller ID que parecem locais para aumentar taxa de resposta
          </p>
        </div>
        <Button 
          onClick={loadCountryPatterns} 
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700"
        >
          {loading ? 'Carregando...' : 'Atualizar'}
        </Button>
      </div>

      {/* Alerta explicativo para México */}
      <Alert className="border-yellow-500 bg-yellow-500/10">
        <div className="flex items-start space-x-3">
          <span className="text-2xl">🇲🇽</span>
          <div>
            <h4 className="font-semibold text-yellow-300">Especial para México</h4>
            <p className="text-yellow-200">
              No México, usar CLIs locais é essencial para evitar contestadoras automáticas. 
              O sistema gera números que parecem da mesma cidade do cliente.
            </p>
          </div>
        </div>
      </Alert>

      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="overview">📊 Visão Geral</TabsTrigger>
          <TabsTrigger value="test">🧪 Teste Individual</TabsTrigger>
          <TabsTrigger value="bulk">📦 Geração em Lote</TabsTrigger>
          <TabsTrigger value="stats">📈 Estatísticas</TabsTrigger>
        </TabsList>

        {/* Visão Geral */}
        <TabsContent value="overview" className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {Object.entries(countryPatterns).map(([countryCode, config]) => (
              <Card key={countryCode} className="bg-gray-800 border-gray-700 hover:border-blue-500 transition-colors">
                <CardHeader className="pb-3">
                  <CardTitle className="flex items-center justify-between text-lg">
                    <span className="flex items-center space-x-2">
                      <span className="text-2xl">{countryFlags[countryCode] || '🌍'}</span>
                      <span className="text-white">{config.name}</span>
                    </span>
                    <Badge variant="outline" className="text-xs">
                      {config.country_code}
                    </Badge>
                  </CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  <div>
                    <p className="text-sm text-gray-400 mb-1">Estratégia:</p>
                    <p className="text-sm text-white">{getStrategyDescription(config.strategy)}</p>
                  </div>
                  
                  <div>
                    <p className="text-sm text-gray-400 mb-1">Exemplo de Padrão:</p>
                    <code className="text-xs bg-gray-900 px-2 py-1 rounded text-green-400 block">
                      {formatExamplePattern(countryCode, config)}
                    </code>
                  </div>
                  
                  <div>
                    <p className="text-sm text-gray-400 mb-1">Códigos de Área Disponíveis:</p>
                    <div className="flex flex-wrap gap-1">
                      {config.area_codes.slice(0, 6).map(code => (
                        <Badge key={code} variant="secondary" className="text-xs">
                          {code}
                        </Badge>
                      ))}
                      {config.area_codes.length > 6 && (
                        <Badge variant="outline" className="text-xs">
                          +{config.area_codes.length - 6} mais
                        </Badge>
                      )}
                    </div>
                  </div>

                  <Button 
                    onClick={() => fillExampleNumber(countryCode)}
                    size="sm"
                    className="w-full mt-3 bg-blue-600 hover:bg-blue-700"
                  >
                    Testar {config.name}
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Teste Individual */}
        <TabsContent value="test" className="space-y-6">
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white">🧪 Teste de Geração CLI</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Número de Destino
                  </label>
                  <Input
                    type="text"
                    value={testNumber}
                    onChange={(e) => setTestNumber(e.target.value)}
                    placeholder="+5511999999999"
                    className="bg-gray-700 border-gray-600 text-white"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Forçar País (Opcional)
                  </label>
                  <Select
                    value={selectedCountry}
                    onValueChange={setSelectedCountry}
                    className="bg-gray-700 border-gray-600"
                  >
                    <option value="">Detectar automaticamente</option>
                    {Object.entries(countryPatterns).map(([code, config]) => (
                      <option key={code} value={code}>
                        {countryFlags[code]} {config.name}
                      </option>
                    ))}
                  </Select>
                </div>
              </div>

              <div className="flex space-x-2">
                <Button 
                  onClick={generateTestCli}
                  disabled={loading}
                  className="bg-green-600 hover:bg-green-700"
                >
                  {loading ? 'Gerando...' : 'Gerar 5 CLIs de Teste'}
                </Button>
                
                <Button 
                  onClick={() => {setTestNumber(''); setTestResults([]);}}
                  variant="outline"
                  className="border-gray-600 text-gray-300 hover:bg-gray-700"
                >
                  Limpar
                </Button>
              </div>

              {/* Resultados do Teste */}
              {testResults.length > 0 && (
                <div className="mt-6 space-y-3">
                  <h4 className="text-lg font-semibold text-white">Resultados do Teste:</h4>
                  {testResults.map((result, index) => (
                    <Card key={index} className="bg-gray-900 border-gray-600">
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center space-x-3">
                            <span className="text-2xl">{countryFlags[result.country] || '🌍'}</span>
                            <div>
                              <p className="font-mono text-lg text-green-400">{result.cli}</p>
                              <p className="text-sm text-gray-400">
                                {result.country_name} • Área: {result.area_detected}
                              </p>
                            </div>
                          </div>
                          <div className="text-right">
                            <Badge variant={result.is_local ? "default" : "secondary"}>
                              {result.is_local ? '🎯 Local' : '🔄 Fallback'}
                            </Badge>
                            <p className="text-xs text-gray-500 mt-1">
                              {result.strategy}
                            </p>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Geração em Lote */}
        <TabsContent value="bulk" className="space-y-6">
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white">📦 Geração de CLIs em Lote</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-2">
                  Números de Destino (um por linha)
                </label>
                <textarea
                  value={bulkNumbers}
                  onChange={(e) => setBulkNumbers(e.target.value)}
                  placeholder={`+5511999999999
+5521999999999
+5531999999999
+13055551234
+525555551234`}
                  rows={8}
                  className="w-full bg-gray-700 border border-gray-600 rounded-lg px-3 py-2 text-white font-mono text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              <div className="flex space-x-2">
                <Button 
                  onClick={generateBulkClis}
                  disabled={loading}
                  className="bg-purple-600 hover:bg-purple-700"
                >
                  {loading ? 'Processando...' : 'Gerar CLIs em Lote'}
                </Button>
                
                <Button 
                  onClick={() => {setBulkNumbers(''); setBulkResults(null);}}
                  variant="outline"
                  className="border-gray-600 text-gray-300 hover:bg-gray-700"
                >
                  Limpar
                </Button>
              </div>

              {/* Resultados do Lote */}
              {bulkResults && (
                <div className="mt-6 space-y-4">
                  <div className="grid grid-cols-3 gap-4">
                    <Card className="bg-green-900/20 border-green-700">
                      <CardContent className="p-4 text-center">
                        <p className="text-2xl font-bold text-green-400">{bulkResults.successful}</p>
                        <p className="text-sm text-green-300">Sucessos</p>
                      </CardContent>
                    </Card>
                    
                    <Card className="bg-red-900/20 border-red-700">
                      <CardContent className="p-4 text-center">
                        <p className="text-2xl font-bold text-red-400">{bulkResults.failed}</p>
                        <p className="text-sm text-red-300">Falhas</p>
                      </CardContent>
                    </Card>
                    
                    <Card className="bg-blue-900/20 border-blue-700">
                      <CardContent className="p-4 text-center">
                        <p className="text-2xl font-bold text-blue-400">{bulkResults.total_processed}</p>
                        <p className="text-sm text-blue-300">Total</p>
                      </CardContent>
                    </Card>
                  </div>

                  <div className="max-h-96 overflow-y-auto space-y-2">
                    {bulkResults.results.map((result, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-900 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <span className="text-sm text-gray-400 font-mono">{result.destination_number}</span>
                          <span className="text-gray-600">→</span>
                          {result.success ? (
                            <span className="text-sm text-green-400 font-mono">{result.generated_cli}</span>
                          ) : (
                            <span className="text-sm text-red-400">Erro: {result.error}</span>
                          )}
                        </div>
                        <div className="flex items-center space-x-2">
                          {result.success && (
                            <>
                              <span>{countryFlags[result.country] || '🌍'}</span>
                              <Badge variant="outline" className="text-xs">
                                {result.area_detected}
                              </Badge>
                            </>
                          )}
                          <Badge variant={result.success ? "default" : "destructive"}>
                            {result.success ? 'OK' : 'ERRO'}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Estatísticas */}
        <TabsContent value="stats" className="space-y-6">
          <Card className="bg-gray-800 border-gray-700">
            <CardHeader>
              <CardTitle className="text-white">📈 Estatísticas de Geração</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(generationStats.countries || {}).map(([country, data]) => (
                  <Card key={country} className="bg-gray-900 border-gray-600">
                    <CardContent className="p-4 text-center">
                      <div className="text-2xl mb-2">{countryFlags[country] || '🌍'}</div>
                      <p className="text-lg font-bold text-white">{data.count}</p>
                      <p className="text-sm text-gray-400 capitalize">{country}</p>
                      <p className="text-xs text-gray-500">{Object.keys(data.areas || {}).length} áreas</p>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {generationStats.total_generated !== undefined && (
                <div className="mt-6 text-center">
                  <p className="text-2xl font-bold text-blue-400">{generationStats.total_generated}</p>
                  <p className="text-gray-400">Total de CLIs gerados hoje</p>
                  <p className="text-xs text-gray-500 mt-1">Data: {generationStats.date}</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CliLocalRandomizer; 