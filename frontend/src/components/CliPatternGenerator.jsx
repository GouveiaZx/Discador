import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Select } from './ui/select';
import { Alert } from './ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import api from '../config/api';

const CliPatternGenerator = () => {
  const [activeTab, setActiveTab] = useState('generator');
  const [loading, setLoading] = useState(false);
  const [countries, setCountries] = useState([]);
  const [selectedCountry, setSelectedCountry] = useState('');
  const [selectedAreaCode, setSelectedAreaCode] = useState('');
  const [customPattern, setCustomPattern] = useState('');
  const [destinationNumber, setDestinationNumber] = useState('');
  const [generatedClis, setGeneratedClis] = useState([]);
  const [bulkNumbers, setBulkNumbers] = useState('');
  const [bulkResults, setBulkResults] = useState(null);
  const [availablePatterns, setAvailablePatterns] = useState({});
  const [quantity, setQuantity] = useState(5);
  const [stats, setStats] = useState({});
  const [error, setError] = useState('');

  // Bandeiras e dados dos países
  const countryInfo = {
    'usa': { flag: '🇺🇸', name: 'Estados Unidos', code: '+1' },
    'canada': { flag: '🇨🇦', name: 'Canadá', code: '+1' },
    'mexico': { flag: '🇲🇽', name: 'México', code: '+52' },
    'brasil': { flag: '🇧🇷', name: 'Brasil', code: '+55' },
    'colombia': { flag: '🇨🇴', name: 'Colombia', code: '+57' },
    'argentina': { flag: '🇦🇷', name: 'Argentina', code: '+54' },
    'chile': { flag: '🇨🇱', name: 'Chile', code: '+56' },
    'peru': { flag: '🇵🇪', name: 'Perú', code: '+51' }
  };

  // Exemplos de números por país
  const exampleNumbers = {
    'usa': ['+13055551234', '+14255551234', '+12135551234'],
    'canada': ['+14165551234', '+15145551234', '+16045551234'],
    'mexico': ['+525555551234', '+528155551234', '+523355551234'],
    'brasil': ['+5511955551234', '+5521955551234', '+5531955551234'],
    'colombia': ['+5715551234', '+5745551234', '+5755551234'],
    'argentina': ['+5491155551234', '+5434155551234', '+5435155551234'],
    'chile': ['+56225551234', '+56325551234', '+56415551234'],
    'peru': ['+5115551234', '+5144555123', '+5175551234']
  };

  useEffect(() => {
    loadSupportedCountries();
  }, []);

  useEffect(() => {
    if (selectedCountry) {
      loadCountryPatterns(selectedCountry);
    }
  }, [selectedCountry]);

  const loadSupportedCountries = async () => {
    try {
      setLoading(true);
      const response = await api.get('/performance/cli-pattern/countries');
      if (response.data.success) {
        setCountries(response.data.data);
      }
    } catch (error) {
      console.error('Erro ao carregar países:', error);
      setError('Erro ao carregar países suportados');
    } finally {
      setLoading(false);
    }
  };

  const loadCountryPatterns = async (country) => {
    try {
      const response = await api.get(`/performance/cli-pattern/patterns/${country}`);
      if (response.data.success) {
        setAvailablePatterns(response.data.data);
      }
    } catch (error) {
      console.error('Erro ao carregar padrões:', error);
    }
  };

  const generateCliPattern = async () => {
    if (!destinationNumber.trim()) {
      setError('Digite um número de destino');
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      const payload = {
        destination_number: destinationNumber,
        quantity: quantity
      };

      if (customPattern) {
        payload.custom_pattern = customPattern;
      }

      if (selectedCountry) {
        payload.country_override = selectedCountry;
      }

      if (selectedAreaCode) {
        payload.custom_area_code = selectedAreaCode;
      }

      const response = await api.post('/performance/cli-pattern/generate', payload);
      
      if (response.data.success) {
        setGeneratedClis(response.data.data.generated_clis);
        loadStats();
      } else {
        setError(response.data.error || 'Erro ao gerar CLIs');
      }
    } catch (error) {
      console.error('Erro ao gerar CLI:', error);
      setError('Erro ao gerar padrões CLI');
    } finally {
      setLoading(false);
    }
  };

  const generateBulkPatterns = async () => {
    const numbers = bulkNumbers.split('\n').filter(num => num.trim());
    if (numbers.length === 0) {
      setError('Digite números para geração em lote');
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      const payload = {
        destination_numbers: numbers
      };

      if (customPattern) {
        payload.custom_pattern = customPattern;
      }

      const response = await api.post('/performance/cli-pattern/bulk-generate', payload);
      
      if (response.data.success) {
        setBulkResults(response.data.data);
        loadStats();
      } else {
        setError(response.data.error || 'Erro na geração em lote');
      }
    } catch (error) {
      console.error('Erro na geração em lote:', error);
      setError('Erro na geração em lote');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await api.get('/performance/cli-pattern/stats');
      if (response.data.success) {
        setStats(response.data.data);
      }
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
    }
  };

  const fillExampleNumber = (country) => {
    const examples = exampleNumbers[country];
    if (examples) {
      setDestinationNumber(Array.isArray(examples) ? examples[0] : examples);
      setSelectedCountry(country);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    // Aqui você pode adicionar uma notificação de sucesso
  };

  const getPatternDescription = (pattern) => {
    const descriptions = {
      'area_code_prefix': 'Mantém código de área + prefixo personalizado',
      'area_code_full': 'Código de área + aleatorização completa',
      'ddd_celular': 'DDD + indicador celular + aleatorização',
      'area_code_celular': 'Código de área + celular + aleatorização'
    };
    return descriptions[pattern] || pattern;
  };

  const renderPatternExamples = (country) => {
    const examples = {
      'usa': [
        { pattern: '2xx-xxxx', description: 'Prefixo 2 + 5 aleatórios', example: '305-221-4567' },
        { pattern: '25x-xxxx', description: 'Prefixo 25 + 4 aleatórios', example: '305-250-8901' },
        { pattern: '3xx-xxxx', description: 'Prefixo 3 + 5 aleatórios', example: '305-321-4567' }
      ],
      'mexico': [
        { pattern: 'xxxx-xxxx', description: '8 dígitos aleatórios', example: '55-1234-5678' },
        { pattern: 'xxx-xxxx', description: '7 dígitos aleatórios', example: '222-123-4567' }
      ],
      'brasil': [
        { pattern: '9xxxx-xxxx', description: 'Celular 9 + 8 aleatórios', example: '11-99123-4567' },
        { pattern: '8xxxx-xxxx', description: 'Celular 8 + 8 aleatórios', example: '11-88765-4321' }
      ]
    };

    return examples[country] || [];
  };

  const renderGeneratorTab = () => (
    <div className="space-y-6">
      {/* Seção de Configuração */}
      <Card className="bg-secondary-900 border-secondary-700">
        <CardHeader>
          <CardTitle className="text-primary-400">🎯 Configuração de Padrões</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Número de Destino */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-secondary-300">
              Número de Destino *
            </label>
            <div className="flex space-x-2">
              <Input
                value={destinationNumber}
                onChange={(e) => setDestinationNumber(e.target.value)}
                placeholder="Ex: +13055551234"
                className="flex-1"
              />
              <Select
                value={selectedCountry}
                onValueChange={setSelectedCountry}
                className="w-48"
              >
                <option value="">Detectar automaticamente</option>
                {countries.map(country => (
                  <option key={country.country_code} value={country.country_code}>
                    {countryInfo[country.country_code]?.flag} {countryInfo[country.country_code]?.name}
                  </option>
                ))}
              </Select>
            </div>
          </div>

          {/* Exemplos por País */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-secondary-300">
              Exemplos Rápidos
            </label>
            <div className="flex flex-wrap gap-2">
              {Object.entries(countryInfo).map(([code, info]) => (
                <Button
                  key={code}
                  variant="outline"
                  size="sm"
                  onClick={() => fillExampleNumber(code)}
                  className="text-xs"
                >
                  {info.flag} {info.name}
                </Button>
              ))}
            </div>
          </div>

          {/* Padrão Customizado */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-secondary-300">
              Padrão Customizado (Opcional)
            </label>
            <Input
              value={customPattern}
              onChange={(e) => setCustomPattern(e.target.value)}
              placeholder="Ex: 2xx-xxxx, 35x-xxxx, xxxx-xxxx"
            />
            <p className="text-xs text-secondary-400">
              Use 'x' para dígitos aleatórios. Ex: "2xx-xxxx" = 2 + 5 dígitos aleatórios
            </p>
          </div>

          {/* Área Code Específico */}
          {selectedCountry && availablePatterns.area_codes && (
            <div className="space-y-2">
              <label className="text-sm font-medium text-secondary-300">
                Código de Área Específico
              </label>
              <Select
                value={selectedAreaCode}
                onValueChange={setSelectedAreaCode}
              >
                <option value="">Detectar do número de destino</option>
                {Object.entries(availablePatterns.area_codes).map(([code, info]) => (
                  <option key={code} value={code}>
                    {code} - {info.name}
                  </option>
                ))}
              </Select>
            </div>
          )}

          {/* Quantidade */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-secondary-300">
              Quantidade de CLIs
            </label>
            <Input
              type="number"
              value={quantity}
              onChange={(e) => setQuantity(Math.max(1, Math.min(20, parseInt(e.target.value) || 1)))}
              min="1"
              max="20"
              className="w-24"
            />
          </div>

          {/* Botão de Geração */}
          <Button
            onClick={generateCliPattern}
            disabled={loading || !destinationNumber.trim()}
            className="w-full"
            size="lg"
          >
            {loading ? 'Gerando...' : `🎯 Gerar ${quantity} CLIs`}
          </Button>

          {error && (
            <Alert variant="destructive">
              {error}
            </Alert>
          )}
        </CardContent>
      </Card>

      {/* Padrões Disponíveis */}
      {selectedCountry && availablePatterns.area_codes && (
        <Card className="bg-secondary-900 border-secondary-700">
          <CardHeader>
            <CardTitle className="text-primary-400">
              📋 Padrões Disponíveis - {countryInfo[selectedCountry]?.flag} {countryInfo[selectedCountry]?.name}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {Object.entries(availablePatterns.area_codes).map(([areaCode, info]) => (
                <div key={areaCode} className="p-4 bg-secondary-800 rounded-lg">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-semibold text-white">
                      {areaCode} - {info.name}
                    </h4>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => setSelectedAreaCode(areaCode)}
                    >
                      Usar
                    </Button>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {info.patterns.map((pattern, index) => (
                      <div key={index} className="flex items-center space-x-2">
                        <Badge variant="outline" className="text-xs">
                          {pattern.mask}
                        </Badge>
                        <span className="text-xs text-secondary-400">
                          {pattern.description}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Resultados */}
      {generatedClis.length > 0 && (
        <Card className="bg-secondary-900 border-secondary-700">
          <CardHeader>
            <CardTitle className="text-green-400">✅ CLIs Gerados</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {generatedClis.map((cli, index) => (
                <div key={index} className="flex justify-between items-center p-3 bg-secondary-800 rounded-lg">
                  <code className="text-green-400 font-mono text-lg">{cli}</code>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => copyToClipboard(cli)}
                  >
                    📋 Copiar
                  </Button>
                </div>
              ))}
            </div>
            <div className="mt-4 pt-4 border-t border-secondary-700">
              <Button
                variant="outline"
                onClick={() => copyToClipboard(generatedClis.join('\n'))}
                className="w-full"
              >
                📋 Copiar Todos os CLIs
              </Button>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );

  const renderBulkTab = () => (
    <div className="space-y-6">
      <Card className="bg-secondary-900 border-secondary-700">
        <CardHeader>
          <CardTitle className="text-primary-400">📦 Geração em Lote</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-secondary-300">
              Números de Destino (um por linha)
            </label>
            <textarea
              value={bulkNumbers}
              onChange={(e) => setBulkNumbers(e.target.value)}
              placeholder={`+13055551234\n+14255551234\n+12135551234`}
              className="w-full h-32 px-3 py-2 bg-secondary-800 border border-secondary-600 rounded-lg text-white focus:border-primary-500 focus:outline-none"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-secondary-300">
              Padrão Customizado (Opcional)
            </label>
            <Input
              value={customPattern}
              onChange={(e) => setCustomPattern(e.target.value)}
              placeholder="Ex: 2xx-xxxx, 35x-xxxx"
            />
          </div>

          <Button
            onClick={generateBulkPatterns}
            disabled={loading || !bulkNumbers.trim()}
            className="w-full"
            size="lg"
          >
            {loading ? 'Gerando...' : '📦 Gerar CLIs em Lote'}
          </Button>

          {error && (
            <Alert variant="destructive">
              {error}
            </Alert>
          )}
        </CardContent>
      </Card>

      {bulkResults && (
        <Card className="bg-secondary-900 border-secondary-700">
          <CardHeader>
            <CardTitle className="text-green-400">✅ Resultados da Geração em Lote</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {bulkResults.results.map((result, index) => (
                <div key={index} className="p-4 bg-secondary-800 rounded-lg">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <div className="font-semibold text-white">
                        {result.destination_number}
                      </div>
                      <div className="text-sm text-secondary-400">
                        {countryInfo[result.country]?.flag} {result.country_name} - {result.area_name}
                      </div>
                    </div>
                    <Badge variant="outline">
                      {result.generated_clis.length} CLIs
                    </Badge>
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                    {result.generated_clis.map((cli, cliIndex) => (
                      <div key={cliIndex} className="flex justify-between items-center p-2 bg-secondary-700 rounded">
                        <code className="text-green-400 font-mono">{cli}</code>
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => copyToClipboard(cli)}
                        >
                          📋
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );

  const renderGuideTab = () => (
    <div className="space-y-6">
      <Card className="bg-secondary-900 border-secondary-700">
        <CardHeader>
          <CardTitle className="text-primary-400">📚 Guia de Uso</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">Como Funciona</h3>
            
            <div className="space-y-4">
              {Object.entries(countryInfo).map(([code, info]) => (
                <div key={code} className="p-4 bg-secondary-800 rounded-lg">
                  <h4 className="font-semibold text-white mb-2">
                    {info.flag} {info.name} ({info.code})
                  </h4>
                  <p className="text-secondary-300 mb-3">
                    {getPatternDescription(availablePatterns[code]?.pattern_type || 'area_code_prefix')}
                  </p>
                  
                  <div className="space-y-2">
                    <h5 className="font-medium text-secondary-200">Exemplos de Padrões:</h5>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                      {renderPatternExamples(code).map((example, index) => (
                        <div key={index} className="p-2 bg-secondary-700 rounded text-sm">
                          <code className="text-green-400">{example.pattern}</code>
                          <div className="text-xs text-secondary-400 mt-1">
                            {example.description}
                          </div>
                          <div className="text-xs text-blue-400 mt-1">
                            Ex: {example.example}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">Dicas Avançadas</h3>
            
            <div className="space-y-3">
              <Alert className="bg-blue-900/40 border-blue-500/50">
                <div className="space-y-2">
                  <h4 className="font-semibold text-blue-200">🇺🇸 Estados Unidos</h4>
                  <p className="text-blue-100">
                    Use padrões como "2xx-xxxx" para Miami (305) ou "3xx-xxxx" para outras áreas. 
                    Evite começar com 0 ou 1.
                  </p>
                </div>
              </Alert>

              <Alert className="bg-red-900/40 border-red-500/50">
                <div className="space-y-2">
                  <h4 className="font-semibold text-red-200">🇲🇽 México</h4>
                  <p className="text-red-100">
                    Para México é CRÍTICO usar CLIs locais. Use "xxxx-xxxx" para CDMX (55) e 
                    "xxx-xxxx" para outras cidades. Isso evita contestadoras automáticas.
                  </p>
                </div>
              </Alert>

              <Alert className="bg-green-900/40 border-green-500/50">
                <div className="space-y-2">
                  <h4 className="font-semibold text-green-200">🇧🇷 Brasil</h4>
                  <p className="text-green-100">
                    Use "9xxxx-xxxx" para celulares modernos ou "8xxxx-xxxx" para compatibilidade. 
                    O DDD é sempre mantido.
                  </p>
                </div>
              </Alert>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-primary-900/50 to-secondary-900/50 p-6 rounded-xl border border-primary-500/20">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold text-white mb-2">
              🎯 Gerador de Padrões CLI Customizados
            </h2>
            <p className="text-secondary-300 text-lg">
              Sistema avançado para gerar CLIs locais com padrões personalizados por país
            </p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-primary-400">
              {countries.length}
            </div>
            <div className="text-sm text-secondary-400">
              Países Suportados
            </div>
          </div>
        </div>
      </div>

      {/* Aviso Importante */}
      <Alert className="bg-gradient-to-r from-yellow-900/40 to-orange-900/40 border-2 border-yellow-500/50">
        <div className="flex items-start space-x-4">
          <span className="text-4xl">🚀</span>
          <div>
            <h4 className="font-semibold text-yellow-200 text-lg mb-2">
              Sistema Avançado de CLIs Locais
            </h4>
            <p className="text-yellow-100 leading-relaxed">
              Este sistema permite criar padrões personalizados para cada país, como 
              <code className="mx-1 px-2 py-1 bg-black/30 rounded">"305 2xx-xxxx"</code> para Miami ou 
              <code className="mx-1 px-2 py-1 bg-black/30 rounded">"55 xxxx-xxxx"</code> para CDMX. 
              Aumenta significativamente a taxa de resposta fazendo as chamadas parecerem locais.
            </p>
          </div>
        </div>
      </Alert>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="generator">🎯 Gerador</TabsTrigger>
          <TabsTrigger value="bulk">📦 Lote</TabsTrigger>
          <TabsTrigger value="guide">📚 Guia</TabsTrigger>
        </TabsList>

        <TabsContent value="generator" className="mt-6">
          {renderGeneratorTab()}
        </TabsContent>

        <TabsContent value="bulk" className="mt-6">
          {renderBulkTab()}
        </TabsContent>

        <TabsContent value="guide" className="mt-6">
          {renderGuideTab()}
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CliPatternGenerator; 