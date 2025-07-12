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
    'usa': { flag: '🇺🇸', name: 'Estados Unidos', code: '+1' },
    'canada': { flag: '🇨🇦', name: 'Canadá', code: '+1' },
    'mexico': { flag: '🇲🇽', name: 'México', code: '+52' },
    'brasil': { flag: '🇧🇷', name: 'Brasil', code: '+55' },
    'colombia': { flag: '🇨🇴', name: 'Colombia', code: '+57' },
    'argentina': { flag: '🇦🇷', name: 'Argentina', code: '+54' },
    'chile': { flag: '🇨🇱', name: 'Chile', code: '+56' },
    'peru': { flag: '🇵🇪', name: 'Perú', code: '+51' }
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
      console.log('🔄 Cargando países soportados...');
      
      const response = await api.get('/performance/cli-pattern/countries');
      console.log('📞 Respuesta del servidor:', response.data);
      
      if (response.data.success) {
        setCountries(response.data.data);
        console.log('✅ Países cargados:', response.data.data);
        setSuccess('Países cargados correctamente');
      } else {
        console.error('❌ Error en la respuesta:', response.data.error);
        setError('Error al cargar países: ' + response.data.error);
      }
    } catch (error) {
      console.error('❌ Error al cargar países:', error);
      setError('Error al cargar países soportados. Revisa la consola para más detalles.');
      
      // Fallback: cargar países por defecto
      const fallbackCountries = Object.keys(countryInfo).map(code => ({
        country_code: code,
        name: countryInfo[code].name,
        supported: true
      }));
      setCountries(fallbackCountries);
      console.log('🔄 Usando países por defecto:', fallbackCountries);
    } finally {
      setLoading(false);
    }
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
      
      if (response.data.success) {
        setGeneratedClis(response.data.data.generated_clis);
        setSuccess(`✅ Se generaron ${response.data.data.generated_clis.length} CLIs correctamente`);
        loadStats();
      } else {
        setError(response.data.error || 'Error al generar CLIs');
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
        setBulkResults(response.data.data);
        setSuccess(`✅ Se generaron CLIs masivos para ${numbers.length} números`);
        loadStats();
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
              />
              <Select
                value={selectedCountry}
                onValueChange={setSelectedCountry}
                className="w-48"
              >
                <option value="">Detectar automáticamente</option>
                {countries.map(country => (
                  <option key={country.country_code} value={country.country_code}>
                    {countryInfo[country.country_code]?.flag} {countryInfo[country.country_code]?.name}
                  </option>
                ))}
              </Select>
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
              {bulkResults.generated_clis && bulkResults.generated_clis.map((result, index) => (
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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-900/50 to-gray-900/50 p-6 rounded-xl border border-blue-500/20">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-3xl font-bold text-white mb-2">
              🎯 Generador de CLIs Aleatorios Locales
            </h2>
            <p className="text-gray-300 text-lg">
              Sistema avanzado para generar CLIs locales con patrones personalizados por país
            </p>
            <p className="text-blue-300 text-sm mt-2">
              <strong>Funciona para TODOS los países:</strong> USA, Canadá, México, Brasil, Colombia, Argentina, Chile, Perú
            </p>
          </div>
          <div className="text-right">
            <div className="text-2xl font-bold text-blue-400">
              {Object.keys(countryInfo).length}
            </div>
            <div className="text-sm text-gray-400">
              Países Soportados
            </div>
          </div>
        </div>
      </div>

      {/* Alerta Importante */}
      <Alert className="bg-gradient-to-r from-yellow-900/40 to-orange-900/40 border-2 border-yellow-500/50">
        <div className="flex items-start space-x-4">
          <span className="text-4xl">🚀</span>
          <div>
            <h4 className="font-semibold text-yellow-200 text-lg mb-2">
              Sistema de CLIs Locales - Como funciona
            </h4>
            <p className="text-yellow-100 leading-relaxed">
              <strong>Para USA:</strong> Si llamás a 305 300 9005, el cliente ve "305 2xx-xxxx" (últimos 6 aleatorios)<br/>
              <strong>Para México:</strong> Si llamás a CDMX (55), el cliente ve "55 xxxx-xxxx" (últimos 8 aleatorios)<br/>
              <strong>Para Brasil:</strong> Si llamás a SP (11), el cliente ve "11 9xxxx-xxxx" (últimos 8 aleatorios)<br/>
              <strong>¡Funciona para todos los países!</strong> El cliente siempre recibe una llamada que parece local.
            </p>
          </div>
        </div>
      </Alert>

      {/* Debug Info */}
      <div className="bg-gray-800 p-4 rounded-lg text-xs text-gray-400">
        <details>
          <summary className="cursor-pointer mb-2">🔍 Debug Info</summary>
          <div className="space-y-2">
            <p>Países cargados: {countries.length}</p>
            <p>País seleccionado: {selectedCountry || 'Ninguno'}</p>
            <p>Número de destino: {destinationNumber || 'Vacío'}</p>
            <p>CLIs generados: {generatedClis.length}</p>
            <p>Estado de carga: {loading ? 'Cargando...' : 'Listo'}</p>
          </div>
        </details>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList className="grid w-full grid-cols-3">
          <TabsTrigger value="generator">🎯 Generador</TabsTrigger>
          <TabsTrigger value="bulk">📦 Masivo</TabsTrigger>
          <TabsTrigger value="guide">📚 Guía</TabsTrigger>
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