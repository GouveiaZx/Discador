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
  const [success, setSuccess] = useState('');

  // Información de países en español argentino
  const countryInfo = {
    // América do Norte
    'usa': { flag: '🇺🇸', name: 'Estados Unidos', code: '+1' },
    'canada': { flag: '🇨🇦', name: 'Canadá', code: '+1' },
    
    // América Latina
    'mexico': { flag: '🇲🇽', name: 'México', code: '+52' },
    'brasil': { flag: '🇧🇷', name: 'Brasil', code: '+55' },
    'argentina': { flag: '🇦🇷', name: 'Argentina', code: '+54' },
    'colombia': { flag: '🇨🇴', name: 'Colombia', code: '+57' },
    'chile': { flag: '🇨🇱', name: 'Chile', code: '+56' },
    'peru': { flag: '🇵🇪', name: 'Perú', code: '+51' },
    'venezuela': { flag: '🇻🇪', name: 'Venezuela', code: '+58' },
    'ecuador': { flag: '🇪🇨', name: 'Ecuador', code: '+593' },
    'bolivia': { flag: '🇧🇴', name: 'Bolivia', code: '+591' },
    'uruguay': { flag: '🇺🇾', name: 'Uruguay', code: '+598' },
    'paraguay': { flag: '🇵🇾', name: 'Paraguay', code: '+595' },
    'costa_rica': { flag: '🇨🇷', name: 'Costa Rica', code: '+506' },
    'panama': { flag: '🇵🇦', name: 'Panamá', code: '+507' },
    'guatemala': { flag: '🇬🇹', name: 'Guatemala', code: '+502' },
    'honduras': { flag: '🇭🇳', name: 'Honduras', code: '+504' },
    'el_salvador': { flag: '🇸🇻', name: 'El Salvador', code: '+503' },
    'nicaragua': { flag: '🇳🇮', name: 'Nicaragua', code: '+505' },
    'republica_dominicana': { flag: '🇩🇴', name: 'República Dominicana', code: '+1' },
    'porto_rico': { flag: '🇵🇷', name: 'Porto Rico', code: '+1' },
    
    // Europa
    'espanha': { flag: '🇪🇸', name: 'España', code: '+34' },
    'portugal': { flag: '🇵🇹', name: 'Portugal', code: '+351' },
    'franca': { flag: '🇫🇷', name: 'França', code: '+33' },
    'alemanha': { flag: '🇩🇪', name: 'Alemanha', code: '+49' },
    'italia': { flag: '🇮🇹', name: 'Itália', code: '+39' },
    'reino_unido': { flag: '🇬🇧', name: 'Reino Unido', code: '+44' },
    'holanda': { flag: '🇳🇱', name: 'Holanda', code: '+31' },
    'belgica': { flag: '🇧🇪', name: 'Bélgica', code: '+32' },
    'suica': { flag: '🇨🇭', name: 'Suíça', code: '+41' },
    'austria': { flag: '🇦🇹', name: 'Áustria', code: '+43' },
    
    // Ásia
    'india': { flag: '🇮🇳', name: 'Índia', code: '+91' },
    'filipinas': { flag: '🇵🇭', name: 'Filipinas', code: '+63' },
    'malasia': { flag: '🇲🇾', name: 'Malásia', code: '+60' },
    'singapura': { flag: '🇸🇬', name: 'Singapura', code: '+65' },
    'tailandia': { flag: '🇹🇭', name: 'Tailândia', code: '+66' },
    'indonesia': { flag: '🇮🇩', name: 'Indonésia', code: '+62' },
    
    // Oceania
    'australia': { flag: '🇦🇺', name: 'Austrália', code: '+61' },
    'nova_zelandia': { flag: '🇳🇿', name: 'Nova Zelândia', code: '+64' },
    
    // África
    'africa_do_sul': { flag: '🇿🇦', name: 'África do Sul', code: '+27' },
    
    // Oriente Médio
    'israel': { flag: '🇮🇱', name: 'Israel', code: '+972' }
  };

  // Números de ejemplo por país
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
      setError('');
      console.log('🔄 Cargando países soportados...');
      
      const response = await api.get('/performance/cli-pattern/countries');
      console.log('📞 Respuesta del servidor:', response.data);
      
      // Verificar se há dados válidos, independente do success flag
      if (response.data && response.data.data && Array.isArray(response.data.data) && response.data.data.length > 0) {
        setCountries(response.data.data);
        console.log('✅ Países cargados:', response.data.data.length, 'países');
        
        // Mostrar informação sobre o tipo de serviço
        if (response.data.fallback) {
          setSuccess(`Países cargados en modo fallback (${response.data.data.length} países)`);
        } else if (!response.data.service_available) {
          setSuccess(`Países cargados con servicio básico (${response.data.data.length} países)`);
        } else {
          setSuccess(`Países cargados correctamente (${response.data.data.length} países)`);
        }
        
        return; // Sair da função aqui se tudo funcionou
      }
      
      // Se chegou aqui, algo deu errado
      console.warn('⚠️ Resposta inválida ou vazia do servidor');
      throw new Error('Resposta inválida do servidor');
      
    } catch (error) {
      console.error('❌ Error al cargar países:', error);
      setError('Error al cargar países del servidor. Usando configuración local.');
      
      // Fallback: cargar países por defecto
      useFallbackCountries();
    } finally {
      setLoading(false);
    }
  };

  const useFallbackCountries = () => {
    const fallbackCountries = Object.keys(countryInfo).map(code => ({
      country_code: code,
      country_name: countryInfo[code].name,
      phone_code: countryInfo[code].code,
      strategy: 'local_fallback',
      area_codes: ['default'],
      supported: true
    }));
    
    setCountries(fallbackCountries);
    console.log('🔄 Usando países por defecto:', fallbackCountries.length, 'países');
    setSuccess(`Configuração local carregada (${fallbackCountries.length} países disponíveis)`);
  };

  const loadCountryPatterns = async (country) => {
    try {
      console.log(`🔄 Cargando patrones para ${country}...`);
      const response = await api.get(`/performance/cli-pattern/patterns/${country}`);
      console.log('📞 Patrones recibidos:', response.data);
      
      if (response.data.success) {
        setAvailablePatterns(response.data.data);
        console.log('✅ Patrones cargados:', response.data.data);
      }
    } catch (error) {
      console.error('❌ Error al cargar patrones:', error);
    }
  };

  const generateCliPattern = async () => {
    if (!destinationNumber.trim()) {
      setError('Por favor, ingresá un número de destino válido');
      return;
    }

    try {
      setLoading(true);
      setError('');
      setSuccess('');
      
      console.log('🔄 Generando CLI patterns...', {
        destination_number: destinationNumber,
        quantity: quantity,
        country_override: selectedCountry,
        custom_pattern: customPattern,
        custom_area_code: selectedAreaCode
      });

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
      console.log('📞 Respuesta generación:', response.data);
      
      // Tratar diferentes formatos de resposta da API
      let clis = [];
      
      if (response.data && response.data.data && response.data.data.generated_clis) {
        // Formato: { success: true, data: { generated_clis: [...] } }
        clis = response.data.data.generated_clis;
      } else if (response.data && response.data.generated_clis) {
        // Formato: { success: true, generated_clis: [...] }
        clis = response.data.generated_clis;
      } else if (response.data && response.data.data && Array.isArray(response.data.data)) {
        // Formato: { success: true, data: [...] }
        clis = response.data.data;
      }
      
      console.log('📞 CLIs extraídos:', clis);
      
      if (clis && clis.length > 0) {
        setGeneratedClis(clis);
        setSuccess(`✅ Se generaron ${clis.length} CLIs correctamente`);
        loadStats();
      } else {
        // Verificar se há mensagem de erro específica
        const errorMsg = response.data?.error || response.data?.message || 'No se generaron CLIs. Verifica la configuración.';
        setError(errorMsg);
        console.warn('⚠️ No se generaron CLIs:', response.data);
      }
    } catch (error) {
      console.error('❌ Error al generar CLI:', error);
      setError('Error al generar patrones CLI. Revisa la consola para más detalles.');
    } finally {
      setLoading(false);
    }
  };

  const generateBulkPatterns = async () => {
    const numbers = bulkNumbers.split('\n').filter(num => num.trim());
    if (numbers.length === 0) {
      setError('Por favor, ingresá al menos un número para la generación masiva');
      return;
    }

    try {
      setLoading(true);
      setError('');
      setSuccess('');
      
      console.log('🔄 Generando CLIs masivos...', {
        destination_numbers: numbers,
        custom_pattern: customPattern
      });

      const payload = {
        destination_numbers: numbers
      };

      if (customPattern) {
        payload.custom_pattern = customPattern;
      }

      const response = await api.post('/performance/cli-pattern/bulk-generate', payload);
      console.log('📞 Respuesta generación masiva:', response.data);
      
      if (response.data.success) {
        // Tratar diferentes formatos de respuesta da API
        let results = [];
        
        if (response.data.data && response.data.data.results) {
          // Formato: { success: true, data: { results: [...] } }
          results = response.data.data.results;
        } else if (response.data.results) {
          // Formato: { success: true, results: [...] }
          results = response.data.results;
        } else {
          // Fallback: procurar no objeto completo
          results = response.data.data?.results || response.data.results || [];
        }
        
        console.log('📞 Resultados extraídos:', results);
        
        if (results && results.length > 0) {
          setBulkResults({ results });
          setSuccess(`✅ Se generaron CLIs masivos para ${numbers.length} números`);
          loadStats();
        } else {
          setError('No se generaron CLIs masivos. Verifica la configuración.');
        }
      } else {
        setError(response.data.error || 'Error en la generación masiva');
      }
    } catch (error) {
      console.error('❌ Error en la generación masiva:', error);
      setError('Error en la generación masiva. Revisa la consola para más detalles.');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await api.get('/performance/cli-pattern/stats');
      console.log('📊 Estadísticas:', response.data);
      
      if (response.data.success) {
        setStats(response.data.data);
      }
    } catch (error) {
      console.error('❌ Error al cargar estadísticas:', error);
    }
  };

  const fillExampleNumber = (country) => {
    const examples = exampleNumbers[country];
    if (examples && examples.length > 0) {
      const selectedExample = Array.isArray(examples) ? examples[0] : examples;
      setDestinationNumber(selectedExample);
      setSelectedCountry(country);
      setError('');
      setSuccess(`✅ Número de ejemplo para ${countryInfo[country].name}: ${selectedExample}`);
      console.log(`📱 Ejemplo seleccionado para ${country}:`, selectedExample);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text).then(() => {
      setSuccess(`✅ Copiado: ${text}`);
      setTimeout(() => setSuccess(''), 2000);
    });
  };

  const clearErrors = () => {
    setError('');
    setSuccess('');
  };

  const getPatternDescription = (pattern) => {
    const descriptions = {
      'area_code_prefix': 'Mantiene código de área + prefijo personalizado',
      'area_code_full': 'Código de área + aleatorización completa',
      'ddd_celular': 'DDD + indicador celular + aleatorización',
      'area_code_celular': 'Código de área + celular + aleatorización'
    };
    return descriptions[pattern] || pattern;
  };

  const renderPatternExamples = (country) => {
    const examples = {
      'usa': [
        { pattern: '2xx-xxxx', description: 'Prefijo 2 + 5 aleatorios', example: '305-221-4567' },
        { pattern: '25x-xxxx', description: 'Prefijo 25 + 4 aleatorios', example: '305-250-8901' },
        { pattern: '3xx-xxxx', description: 'Prefijo 3 + 5 aleatorios', example: '305-321-4567' }
      ],
      'mexico': [
        { pattern: 'xxxx-xxxx', description: '8 dígitos aleatorios', example: '55-1234-5678' },
        { pattern: 'xxx-xxxx', description: '7 dígitos aleatorios', example: '222-123-4567' }
      ],
      'brasil': [
        { pattern: '9xxxx-xxxx', description: 'Celular 9 + 8 aleatorios', example: '11-99123-4567' },
        { pattern: '8xxxx-xxxx', description: 'Celular 8 + 8 aleatorios', example: '11-88765-4321' }
      ],
      'argentina': [
        { pattern: 'xxxx-xxxx', description: '8 dígitos aleatorios', example: '11-1234-5678' },
        { pattern: '15xx-xxxx', description: 'Celular 15 + 6 aleatorios', example: '11-1534-5678' }
      ],
      'colombia': [
        { pattern: 'xxx-xxxx', description: '7 dígitos aleatorios', example: '1-234-5678' },
        { pattern: '3xx-xxxx', description: 'Celular 3 + 6 aleatorios', example: '4-321-5678' }
      ],
      'chile': [
        { pattern: 'xxxx-xxxx', description: '8 dígitos aleatorios', example: '2-1234-5678' },
        { pattern: '9xxx-xxxx', description: 'Celular 9 + 7 aleatorios', example: '2-9123-4567' }
      ],
      'peru': [
        { pattern: 'xxxx-xxxx', description: '8 dígitos aleatorios', example: '1-1234-5678' },
        { pattern: '9xx-xxxx', description: 'Celular 9 + 6 aleatorios', example: '1-912-3456' }
      ]
    };

    return examples[country] || [];
  };

  const renderGeneratorTab = () => (
    <div className="space-y-6">
      {/* Mensajes de Estado */}
      {error && (
        <Alert variant="destructive" className="mb-4">
          <div className="flex items-center justify-between">
            <span>{error}</span>
            <Button variant="ghost" size="sm" onClick={clearErrors}>✕</Button>
          </div>
        </Alert>
      )}
      
      {success && (
        <Alert variant="success" className="mb-4">
          <div className="flex items-center justify-between">
            <span>{success}</span>
            <Button variant="ghost" size="sm" onClick={clearErrors}>✕</Button>
          </div>
        </Alert>
      )}

      {/* Sección de Configuración */}
      <Card className="bg-gray-800 border-gray-700">
        <CardHeader>
          <CardTitle className="text-blue-400">🎯 Configuración de Patrones CLI</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Número de Destino */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-300">
              Número de Destino *
            </label>
            <div className="flex space-x-2">
              <Input
                value={destinationNumber}
                onChange={(e) => setDestinationNumber(e.target.value)}
                placeholder="Ej: +13055551234"
                className="flex-1"
                disabled={loading}
              />
              <Select
                value={selectedCountry}
                onValueChange={setSelectedCountry}
                placeholder="Detectar automáticamente"
                className="w-48"
                disabled={loading}
                options={countries.map(country => ({
                  value: country.country_code,
                  label: `${countryInfo[country.country_code]?.flag || '🌍'} ${country.country_name || countryInfo[country.country_code]?.name || country.country_code}`
                }))}
              />
            </div>
          </div>

          {/* Ejemplos por País */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-300">
              Ejemplos Rápidos
            </label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
              {Object.entries(countryInfo).map(([code, info]) => (
                <Button
                  key={code}
                  variant="outline"
                  size="sm"
                  onClick={() => fillExampleNumber(code)}
                  className="text-xs text-gray-300 hover:text-white"
                >
                  {info.flag} {info.name}
                </Button>
              ))}
            </div>
          </div>

          {/* Patrón Personalizado */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-300">
              Patrón Personalizado (Opcional)
            </label>
            <Input
              value={customPattern}
              onChange={(e) => setCustomPattern(e.target.value)}
              placeholder="Ej: 2xx-xxxx, 35x-xxxx, xxxx-xxxx"
            />
            <p className="text-xs text-gray-400">
              Usá 'x' para dígitos aleatorios. Ej: "2xx-xxxx" = 2 + 5 dígitos aleatorios
            </p>
          </div>

          {/* Código de Área Específico */}
          {selectedCountry && availablePatterns.area_codes && (
            <div className="space-y-2">
              <label className="text-sm font-medium text-gray-300">
                Código de Área Específico
              </label>
              <Select
                value={selectedAreaCode}
                onValueChange={setSelectedAreaCode}
              >
                <option value="">Detectar del número de destino</option>
                {Object.entries(availablePatterns.area_codes).map(([code, info]) => (
                  <option key={code} value={code}>
                    {code} - {info.name}
                  </option>
                ))}
              </Select>
            </div>
          )}

          {/* Cantidad */}
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-300">
              Cantidad de CLIs
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

          {/* Botón de Generación */}
          <Button
            onClick={generateCliPattern}
            disabled={loading || !destinationNumber.trim()}
            className="w-full"
            size="lg"
            variant="default"
          >
            {loading ? 'Generando...' : `🎯 Generar ${quantity} CLIs`}
          </Button>
        </CardContent>
      </Card>

      {/* Resultados */}
      {generatedClis.length > 0 && (
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader>
            <CardTitle className="text-green-400">✅ CLIs Generados</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {generatedClis.map((cli, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <Badge variant="outline" className="text-green-400">
                      CLI {index + 1}
                    </Badge>
                    <span className="font-mono text-lg text-white">{cli}</span>
                  </div>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => copyToClipboard(cli)}
                    className="text-blue-400 hover:text-blue-300"
                  >
                    📋 Copiar
                  </Button>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );

  const renderBulkTab = () => (
    <div className="space-y-6">
      {/* Mensajes de Estado */}
      {error && (
        <Alert variant="destructive" className="mb-4">
          <div className="flex items-center justify-between">
            <span>{error}</span>
            <Button variant="ghost" size="sm" onClick={clearErrors}>✕</Button>
          </div>
        </Alert>
      )}
      
      {success && (
        <Alert variant="success" className="mb-4">
          <div className="flex items-center justify-between">
            <span>{success}</span>
            <Button variant="ghost" size="sm" onClick={clearErrors}>✕</Button>
          </div>
        </Alert>
      )}

      <Card className="bg-gray-800 border-gray-700">
        <CardHeader>
          <CardTitle className="text-blue-400">📦 Generación Masiva</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-300">
              Números de Destino (uno por línea)
            </label>
            <textarea
              value={bulkNumbers}
              onChange={(e) => setBulkNumbers(e.target.value)}
              placeholder={`+13055551234\n+14255551234\n+12135551234`}
              className="w-full h-32 px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:border-blue-500 focus:outline-none"
            />
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-gray-300">
              Patrón Personalizado (Opcional)
            </label>
            <Input
              value={customPattern}
              onChange={(e) => setCustomPattern(e.target.value)}
              placeholder="Ej: 2xx-xxxx, 35x-xxxx"
            />
          </div>

          <Button
            onClick={generateBulkPatterns}
            disabled={loading || !bulkNumbers.trim()}
            className="w-full"
            size="lg"
            variant="default"
          >
            {loading ? 'Generando...' : '📦 Generar CLIs Masivos'}
          </Button>
        </CardContent>
      </Card>

      {/* Resultados Masivos */}
      {bulkResults && (
        <Card className="bg-gray-800 border-gray-700">
          <CardHeader>
            <CardTitle className="text-green-400">✅ Resultados Masivos</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {bulkResults.results && bulkResults.results.map((result, index) => (
                <div key={index} className="p-4 bg-gray-700 rounded-lg">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-gray-300">Para: {result.destination_number}</span>
                    <Badge variant="outline" className="text-green-400">
                      {result.country}
                    </Badge>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {result.generated_clis.map((cli, cliIndex) => (
                      <Button
                        key={cliIndex}
                        variant="ghost"
                        size="sm"
                        onClick={() => copyToClipboard(cli)}
                        className="font-mono text-white hover:text-blue-300"
                      >
                        {cli}
                      </Button>
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
      <Card className="bg-gray-800 border-gray-700">
        <CardHeader>
          <CardTitle className="text-blue-400">📚 Guía de Uso</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-white">¿Cómo Funciona?</h3>
            
            <div className="space-y-4">
              {Object.entries(countryInfo).map(([code, info]) => (
                <div key={code} className="p-4 bg-gray-700 rounded-lg">
                  <h4 className="font-semibold text-white mb-2">
                    {info.flag} {info.name} ({info.code})
                  </h4>
                  <p className="text-gray-300 mb-3">
                    {getPatternDescription(availablePatterns[code]?.pattern_type || 'area_code_prefix')}
                  </p>
                  
                  <div className="space-y-2">
                    <h5 className="font-medium text-gray-200">Ejemplos de Patrones:</h5>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                      {renderPatternExamples(code).map((example, index) => (
                        <div key={index} className="p-2 bg-gray-600 rounded text-sm">
                          <code className="text-green-400">{example.pattern}</code>
                          <div className="text-xs text-gray-400 mt-1">
                            {example.description}
                          </div>
                          <div className="text-xs text-blue-400 mt-1">
                            Ej: {example.example}
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
            <h3 className="text-lg font-semibold text-white">Consejos Avanzados</h3>
            
            <div className="space-y-3">
              <Alert variant="info">
                <div className="space-y-2">
                  <h4 className="font-semibold text-blue-200">🇺🇸 Estados Unidos</h4>
                  <p className="text-blue-100">
                    Para USA, el código de área son los 3 primeros dígitos (ej: 305 para Miami). 
                    Usá patrones como "2xx-xxxx" para que aparezca una llamada local. 
                    Los últimos 6 dígitos son aleatorios.
                  </p>
                </div>
              </Alert>

              <Alert variant="destructive">
                <div className="space-y-2">
                  <h4 className="font-semibold text-red-200">🇲🇽 México - MUY IMPORTANTE</h4>
                  <p className="text-red-100">
                    Para México es CRÍTICO usar CLIs locales. Si llamás a CDMX (55), 
                    el sistema genera "55 xxxx-xxxx" donde los últimos 8 dígitos son aleatorios.
                    Esto evita las contestadoras automáticas y aumenta la tasa de respuesta.
                  </p>
                </div>
              </Alert>

              <Alert variant="success">
                <div className="space-y-2">
                  <h4 className="font-semibold text-green-200">🇧🇷 Brasil</h4>
                  <p className="text-green-100">
                    Para Brasil, mantiene el DDD (11, 21, 31, etc.) y agrega el indicador 
                    de celular (9 o 8) seguido de aleatorización. 
                    Ej: "11 9xxxx-xxxx" para São Paulo.
                  </p>
                </div>
              </Alert>

              <Alert variant="warning">
                <div className="space-y-2">
                  <h4 className="font-semibold text-purple-200">🇦🇷 Argentina</h4>
                  <p className="text-purple-100">
                    Para Argentina, mantiene el código de área (11 para Buenos Aires) 
                    y aleatoriza los últimos 8 dígitos. Para celulares usa "15xx-xxxx".
                  </p>
                </div>
              </Alert>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  // Debug: Adicionar informações de debug no componente
  const renderDebugInfo = () => {
    return (
      <div className="mt-4 p-4 bg-gray-900 border border-gray-700 rounded-lg">
        <h4 className="text-sm font-medium text-gray-300 mb-2">🔍 Sistema CLI Pattern Generator</h4>
        <div className="text-xs text-gray-400 space-y-1">
          <div>📊 Países cargados: {countries.length}</div>
          <div>🌍 País seleccionado: {selectedCountry || 'Auto-detectar'}</div>
          <div>📱 Número de destino: {destinationNumber || 'Vacío'}</div>
          <div>🎯 Patrón personalizado: {customPattern || 'Ninguno'}</div>
          <div>🔢 Cantidad a generar: {quantity}</div>
          <div>⚡ Estado loading: {loading ? 'Sí' : 'No'}</div>
          <div>✅ CLIs generados: {generatedClis.length}</div>
          <div>📈 Patrones disponibles: {Object.keys(availablePatterns).length > 0 ? 'Sí' : 'No'}</div>
          <div className="mt-2 text-green-400">
            💡 Sistema funcionando - Error anterior corregido
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="p-6 bg-gray-900 min-h-screen">
      <div className="max-w-6xl mx-auto">
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-white mb-2">
            🎯 Generador de Patrones CLI
          </h1>
          <p className="text-gray-400">
            Genera identificadores de llamadas locales para mejorar las tasas de respuesta
          </p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="generator">🎯 Generador</TabsTrigger>
            <TabsTrigger value="bulk">📦 Masivo</TabsTrigger>
            <TabsTrigger value="guide">📋 Guía</TabsTrigger>
          </TabsList>

          <TabsContent value="generator" className="space-y-6">
            {renderGeneratorTab()}
            {process.env.NODE_ENV === 'development' && renderDebugInfo()}
          </TabsContent>

          <TabsContent value="bulk" className="space-y-6">
            {renderBulkTab()}
            {process.env.NODE_ENV === 'development' && renderDebugInfo()}
          </TabsContent>

          <TabsContent value="guide" className="space-y-6">
            {renderGuideTab()}
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default CliPatternGenerator; 