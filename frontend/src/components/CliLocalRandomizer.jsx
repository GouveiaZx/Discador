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
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold text-white mb-2">🎯 CLI Local Randomizer</h2>
            <p className="text-gray-300 text-lg">
              Gera números de Caller ID que parecem locais para aumentar taxa de resposta
            </p>
          </div>
          <Button 
            onClick={loadCountryPatterns} 
            disabled={loading}
            variant="success"
            size="lg"
          >
            {loading ? 'Carregando...' : '🔄 Atualizar'}
          </Button>
        </div>

        {/* Alerta explicativo para México */}
        <Alert variant="warning" className="bg-gradient-to-r from-yellow-900/40 to-orange-900/40 border-2 border-yellow-500/50 backdrop-blur-sm">
          <div className="flex items-start space-x-4">
            <span className="text-4xl">🇲🇽</span>
            <div>
              <h4 className="font-semibold text-yellow-200 text-lg mb-2">🔥 Especial para México</h4>
              <p className="text-yellow-100 leading-relaxed">
                No México, usar CLIs locais é <strong>essencial</strong> para evitar contestadoras automáticas. 
                O sistema gera números que parecem da mesma cidade do cliente, aumentando significativamente a taxa de resposta.
              </p>
            </div>
          </div>
        </Alert>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-4 mb-8">
            <TabsTrigger value="overview">📊 Visão Geral</TabsTrigger>
            <TabsTrigger value="test">🧪 Teste Individual</TabsTrigger>
            <TabsTrigger value="bulk">📦 Geração em Lote</TabsTrigger>
            <TabsTrigger value="stats">📈 Estatísticas</TabsTrigger>
          </TabsList>

          {/* Visão Geral */}
          <TabsContent value="overview" className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {Object.entries(countryPatterns).map(([countryCode, config]) => (
                <Card key={countryCode} className="hover:border-blue-500 transition-all duration-300 hover:shadow-2xl hover:scale-105">
                  <CardHeader className="pb-3">
                    <CardTitle className="flex items-center justify-between text-lg">
                      <span className="flex items-center space-x-2">
                        <span className="text-3xl">{countryFlags[countryCode] || '🌍'}</span>
                        <span className="text-white font-bold">{config.name}</span>
                      </span>
                      <Badge variant="default" className="text-xs font-semibold">
                        {config.country_code}
                      </Badge>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div>
                      <p className="text-sm text-gray-400 mb-2 font-medium">Estratégia:</p>
                      <p className="text-sm text-white leading-relaxed">{getStrategyDescription(config.strategy)}</p>
                    </div>
                    
                    <div>
                      <p className="text-sm text-gray-400 mb-2 font-medium">Exemplo de Padrão:</p>
                      <code className="text-xs bg-gray-900 px-3 py-2 rounded-lg text-green-400 block font-mono">
                        {formatExamplePattern(countryCode, config)}
                      </code>
                    </div>
                    
                    <div>
                      <p className="text-sm text-gray-400 mb-2 font-medium">Códigos de Área Disponíveis:</p>
                      <div className="flex flex-wrap gap-2">
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
                      className="w-full mt-4"
                      variant="success"
                    >
                      🧪 Testar {config.name}
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Teste Individual */}
          <TabsContent value="test" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-white text-xl flex items-center space-x-2">
                  <span>🧪</span>
                  <span>Teste de Geração CLI</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-3">
                      Número de Destino
                    </label>
                    <Input
                      type="text"
                      value={testNumber}
                      onChange={(e) => setTestNumber(e.target.value)}
                      placeholder="+5511999999999"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-3">
                      Forçar País (Opcional)
                    </label>
                    <Select
                      value={selectedCountry}
                      onValueChange={setSelectedCountry}
                    >
                      <option value="">Detectar automaticamente</option>
                      {Object.entries(countryPatterns).map(([code, config]) => (
                        <option key={code} value={code} className="bg-gray-700 text-white">
                          {countryFlags[code]} {config.name}
                        </option>
                      ))}
                    </Select>
                  </div>
                </div>

                <div className="flex space-x-3">
                  <Button 
                    onClick={generateTestCli}
                    disabled={loading}
                    variant="success"
                    size="lg"
                  >
                    {loading ? 'Gerando...' : '🎯 Gerar 5 CLIs de Teste'}
                  </Button>
                  
                  <Button 
                    onClick={() => {setTestNumber(''); setTestResults([]);}}
                    variant="outline"
                    size="lg"
                  >
                    🗑️ Limpar
                  </Button>
                </div>

                {/* Resultados do Teste */}
                {testResults.length > 0 && (
                  <div className="mt-8 space-y-4">
                    <h4 className="text-xl font-semibold text-white flex items-center space-x-2">
                      <span>✅</span>
                      <span>Resultados do Teste:</span>
                    </h4>
                    {testResults.map((result, index) => (
                      <Card key={index} className="bg-gray-900/80 border-gray-600 hover:border-green-500 transition-colors">
                        <CardContent className="p-6">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-4">
                              <span className="text-3xl">{countryFlags[result.country] || '🌍'}</span>
                              <div>
                                <p className="font-mono text-xl text-green-400 font-bold">{result.cli}</p>
                                <p className="text-sm text-gray-400 mt-1">
                                  <span className="font-semibold">{result.country_name}</span> • Área: <span className="text-blue-400">{result.area_detected}</span>
                                </p>
                              </div>
                            </div>
                            <div className="text-right space-y-2">
                              <Badge variant={result.is_local ? "success" : "secondary"} className="text-sm px-3 py-1">
                                {result.is_local ? '🎯 Local' : '🔄 Fallback'}
                              </Badge>
                              <p className="text-xs text-gray-500">
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
            <Card>
              <CardHeader>
                <CardTitle className="text-white text-xl flex items-center space-x-2">
                  <span>📦</span>
                  <span>Geração de CLIs em Lote</span>
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-3">
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
                    rows={10}
                    className="w-full bg-gray-700 border-2 border-gray-600 rounded-lg px-4 py-3 text-white font-mono text-sm 
                             focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200
                             placeholder:text-gray-400 hover:border-gray-500 resize-y"
                  />
                </div>

                <div className="flex space-x-3">
                  <Button 
                    onClick={generateBulkClis}
                    disabled={loading}
                    variant="warning"
                    size="lg"
                  >
                    {loading ? 'Processando...' : '⚡ Gerar CLIs em Lote'}
                  </Button>
                  
                  <Button 
                    onClick={() => {setBulkNumbers(''); setBulkResults(null);}}
                    variant="outline"
                    size="lg"
                  >
                    🗑️ Limpar
                  </Button>
                </div>

                {/* Resultados do Lote */}
                {bulkResults && (
                  <div className="mt-8 space-y-6">
                    <div className="grid grid-cols-3 gap-6">
                      <Card className="bg-gradient-to-r from-green-900/40 to-green-800/40 border-green-500">
                        <CardContent className="p-6 text-center">
                          <p className="text-3xl font-bold text-green-400 mb-2">{bulkResults.successful}</p>
                          <p className="text-sm text-green-300 font-medium">✅ Sucessos</p>
                        </CardContent>
                      </Card>
                      
                      <Card className="bg-gradient-to-r from-red-900/40 to-red-800/40 border-red-500">
                        <CardContent className="p-6 text-center">
                          <p className="text-3xl font-bold text-red-400 mb-2">{bulkResults.failed}</p>
                          <p className="text-sm text-red-300 font-medium">❌ Falhas</p>
                        </CardContent>
                      </Card>
                      
                      <Card className="bg-gradient-to-r from-blue-900/40 to-blue-800/40 border-blue-500">
                        <CardContent className="p-6 text-center">
                          <p className="text-3xl font-bold text-blue-400 mb-2">{bulkResults.total_processed}</p>
                          <p className="text-sm text-blue-300 font-medium">📊 Total</p>
                        </CardContent>
                      </Card>
                    </div>

                    <div className="max-h-96 overflow-y-auto space-y-3 border border-gray-600 rounded-lg p-4 bg-gray-800/50">
                      {bulkResults.results.map((result, index) => (
                        <div key={index} className="flex items-center justify-between p-4 bg-gray-900/80 rounded-lg border border-gray-700 hover:border-gray-600 transition-colors">
                          <div className="flex items-center space-x-4">
                            <span className="text-sm text-gray-400 font-mono bg-gray-800 px-2 py-1 rounded">{result.destination_number}</span>
                            <span className="text-gray-600 text-lg">→</span>
                            {result.success ? (
                              <span className="text-sm text-green-400 font-mono font-bold">{result.generated_cli}</span>
                            ) : (
                              <span className="text-sm text-red-400">❌ Erro: {result.error}</span>
                            )}
                          </div>
                          <div className="flex items-center space-x-3">
                            {result.success && (
                              <>
                                <span className="text-2xl">{countryFlags[result.country] || '🌍'}</span>
                                <Badge variant="outline" className="text-xs">
                                  {result.area_detected}
                                </Badge>
                              </>
                            )}
                            <Badge variant={result.success ? "success" : "destructive"}>
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
            <Card>
              <CardHeader>
                <CardTitle className="text-white text-xl flex items-center space-x-2">
                  <span>📈</span>
                  <span>Estatísticas de Geração</span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                  {Object.entries(generationStats.countries || {}).map(([country, data]) => (
                    <Card key={country} className="bg-gradient-to-br from-gray-900/80 to-gray-800/80 border-gray-600 hover:border-blue-500 transition-all hover:scale-105">
                      <CardContent className="p-6 text-center">
                        <div className="text-4xl mb-3">{countryFlags[country] || '🌍'}</div>
                        <p className="text-2xl font-bold text-white mb-1">{data.count}</p>
                        <p className="text-sm text-gray-400 capitalize font-medium">{country}</p>
                        <p className="text-xs text-gray-500 mt-2">{Object.keys(data.areas || {}).length} áreas ativas</p>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                {generationStats.total_generated !== undefined && (
                  <div className="mt-8 text-center bg-gradient-to-r from-blue-900/40 to-purple-900/40 rounded-xl p-8 border border-blue-500/50">
                    <p className="text-4xl font-bold text-blue-400 mb-2">{generationStats.total_generated}</p>
                    <p className="text-gray-300 text-lg mb-1">Total de CLIs gerados hoje</p>
                    <p className="text-xs text-gray-500">Data: {generationStats.date}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default CliLocalRandomizer; 