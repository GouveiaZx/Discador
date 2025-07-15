import React, { useState, useEffect } from 'react';
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from './ui/card';
import {
  Tabs,
  TabsContent,
  TabsList,
  TabsTrigger,
} from './ui/tabs';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select } from './ui/select';
import { Badge } from './ui/badge';
import { Alert, AlertDescription } from './ui/alert';
import { Progress } from './ui/progress';
import {
  CalculatorIcon,
  Cog6ToothIcon as Settings,
  ArrowTrendingUpIcon as TrendingUp,
  ExclamationTriangleIcon as AlertTriangle,
  CheckCircleIcon as CheckCircle,
  InformationCircleIcon as Info,
  PhoneIcon as Phone,
  ClockIcon as Clock,
  UsersIcon as Users,
  ChartBarIcon as BarChart3,
  BoltIcon as Zap,
  ShieldCheckIcon as Shield
} from '@heroicons/react/24/outline';
import { toast } from './ui/toast';

const CliAutoCalculator = () => {
  const [activeTab, setActiveTab] = useState('calculator');
  const [loading, setLoading] = useState(false);
  const [calculation, setCalculation] = useState(null);
  const [configs, setConfigs] = useState([]);
  const [areaCodes, setAreaCodes] = useState([]);
  
  // Estados do formulário de cálculo
  const [calcForm, setCalcForm] = useState({
    total_numbers: 10000,
    calls_per_hour: 500,
    daily_call_limit: 100,
    work_hours: 8,
    country: 'usa'
  });
  
  // Estados do formulário de configuração
  const [configForm, setConfigForm] = useState({
    campaign_id: '',
    total_numbers: 10000,
    calls_per_hour: 500,
    daily_call_limit: 100,
    work_hours: 8,
    country: 'usa',
    auto_generate: true
  });
  
  // Estados para estatísticas
  const [selectedConfig, setSelectedConfig] = useState(null);
  const [configStats, setConfigStats] = useState(null);

  useEffect(() => {
    loadAreaCodes();
    loadConfigs();
  }, []);

  const loadAreaCodes = async () => {
    try {
      const response = await fetch('/api/v1/cli-auto/area-codes?country=usa');
      const data = await response.json();
      if (data.success) {
        setAreaCodes(data.data.area_codes);
      }
    } catch (error) {
      console.error('Erro ao carregar códigos de área:', error);
    }
  };

  const loadConfigs = async () => {
    try {
      // Implementar endpoint para listar configurações
      setConfigs([]);
    } catch (error) {
      console.error('Erro ao carregar configurações:', error);
    }
  };

  const calculateClis = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/cli-auto/calculate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(calcForm),
      });
      
      const data = await response.json();
      if (data.success) {
        setCalculation(data.data);
        toast.success(data.message);
      } else {
        toast.error('Erro no cálculo');
      }
    } catch (error) {
      console.error('Erro ao calcular CLIs:', error);
      toast.error('Erro ao calcular CLIs');
    } finally {
      setLoading(false);
    }
  };

  const createConfig = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/v1/cli-auto/config', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(configForm),
      });
      
      const data = await response.json();
      if (data.success) {
        toast.success(data.message);
        loadConfigs();
        setActiveTab('management');
      } else {
        toast.error('Erro ao criar configuração');
      }
    } catch (error) {
      console.error('Erro ao criar configuração:', error);
      toast.error('Erro ao criar configuração');
    } finally {
      setLoading(false);
    }
  };

  const loadConfigStats = async (configId) => {
    try {
      const response = await fetch(`/api/v1/cli-auto/config/${configId}/stats`);
      const data = await response.json();
      if (data.success) {
        setConfigStats(data.data.stats);
      }
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
    }
  };

  const resetDailyUsage = async (configId = null) => {
    try {
      const url = configId 
        ? `/api/v1/cli-auto/reset-usage?config_id=${configId}`
        : '/api/v1/cli-auto/reset-usage';
      
      const response = await fetch(url, { method: 'POST' });
      const data = await response.json();
      
      if (data.success) {
        toast.success(data.message);
        if (selectedConfig) {
          loadConfigStats(selectedConfig.id);
        }
      }
    } catch (error) {
      console.error('Erro ao resetar uso:', error);
      toast.error('Erro ao resetar uso diário');
    }
  };

  const formatNumber = (num) => {
    return new Intl.NumberFormat('pt-BR').format(num);
  };

  const getEfficiencyColor = (ratio) => {
    if (ratio >= 80) return 'text-green-600';
    if (ratio >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getEfficiencyBadge = (ratio) => {
    if (ratio >= 80) return <Badge className="bg-green-100 text-green-800">Excelente</Badge>;
    if (ratio >= 60) return <Badge className="bg-yellow-100 text-yellow-800">Bom</Badge>;
    return <Badge className="bg-red-100 text-red-800">Baixa</Badge>;
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Calculadora Automática de CLIs</h1>
          <p className="text-muted-foreground">
            Sistema inteligente para cálculo e geração automática de CLIs baseado no volume de números
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Shield className="h-5 w-5 text-green-600" />
          <span className="text-sm text-green-600 font-medium">Prevenção de Blacklisting</span>
        </div>
      </div>

      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="calculator" className="flex items-center space-x-2">
            <Calculator className="h-4 w-4" />
            <span>Calculadora</span>
          </TabsTrigger>
          <TabsTrigger value="config" className="flex items-center space-x-2">
            <Settings className="h-4 w-4" />
            <span>Configuração</span>
          </TabsTrigger>
          <TabsTrigger value="management" className="flex items-center space-x-2">
            <BarChart3 className="h-4 w-4" />
            <span>Gerenciamento</span>
          </TabsTrigger>
          <TabsTrigger value="examples" className="flex items-center space-x-2">
            <Info className="h-4 w-4" />
            <span>Exemplos</span>
          </TabsTrigger>
        </TabsList>

        <TabsContent value="calculator" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <CalculatorIcon className="h-5 w-5" />
                <span>Cálculo de CLIs Necessários</span>
              </CardTitle>
              <div className="text-sm text-gray-600">
                Calcule quantos CLIs são necessários para sua campanha baseado no volume e velocidade de discagem
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="total_numbers" className="flex items-center space-x-2">
                    <Users className="h-4 w-4" />
                    <span>Total de Números</span>
                  </Label>
                  <Input
                    id="total_numbers"
                    type="number"
                    value={calcForm.total_numbers}
                    onChange={(e) => setCalcForm({...calcForm, total_numbers: parseInt(e.target.value) || 0})}
                    placeholder="10000"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="calls_per_hour" className="flex items-center space-x-2">
                    <Zap className="h-4 w-4" />
                    <span>Chamadas/Hora</span>
                  </Label>
                  <Input
                    id="calls_per_hour"
                    type="number"
                    value={calcForm.calls_per_hour}
                    onChange={(e) => setCalcForm({...calcForm, calls_per_hour: parseInt(e.target.value) || 0})}
                    placeholder="500"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="daily_call_limit" className="flex items-center space-x-2">
                    <Phone className="h-4 w-4" />
                    <span>Limite Diário/CLI</span>
                  </Label>
                  <Input
                    id="daily_call_limit"
                    type="number"
                    value={calcForm.daily_call_limit}
                    onChange={(e) => setCalcForm({...calcForm, daily_call_limit: parseInt(e.target.value) || 0})}
                    placeholder="100"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="work_hours" className="flex items-center space-x-2">
                    <Clock className="h-4 w-4" />
                    <span>Horas de Trabalho</span>
                  </Label>
                  <Input
                    id="work_hours"
                    type="number"
                    value={calcForm.work_hours}
                    onChange={(e) => setCalcForm({...calcForm, work_hours: parseInt(e.target.value) || 0})}
                    placeholder="8"
                  />
                </div>
              </div>
              
              <div className="flex justify-center">
                <Button 
                  onClick={calculateClis} 
                  disabled={loading}
                  className="w-full md:w-auto"
                  size="lg"
                >
                  {loading ? 'Calculando...' : 'Calcular CLIs Necessários'}
                </Button>
              </div>
              
              {calculation && (
                <div className="mt-6 space-y-4">
                  <Alert>
                    <CheckCircle className="h-4 w-4" />
                    <AlertDescription>
                      <strong>Resultado do Cálculo:</strong> {formatNumber(calculation.recommended_clis)} CLIs recomendados
                      para {formatNumber(calculation.total_numbers)} números
                    </AlertDescription>
                  </Alert>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-2xl font-bold text-blue-600">
                          {formatNumber(calculation.min_clis_needed)}
                        </div>
                        <p className="text-sm text-muted-foreground">CLIs Mínimos</p>
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-2xl font-bold text-orange-600">
                          {formatNumber(calculation.velocity_based_clis)}
                        </div>
                        <p className="text-sm text-muted-foreground">Por Velocidade</p>
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-2xl font-bold text-green-600">
                          {formatNumber(calculation.recommended_clis)}
                        </div>
                        <p className="text-sm text-muted-foreground">Recomendados</p>
                        <div className="mt-1">
                          <Badge className="bg-green-100 text-green-800">
                            +{calculation.safety_margin_percent}% segurança
                          </Badge>
                        </div>
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardContent className="pt-6">
                        <div className="text-2xl font-bold text-purple-600">
                          {calculation.estimated_completion_days}
                        </div>
                        <p className="text-sm text-muted-foreground">Dias para Completar</p>
                      </CardContent>
                    </Card>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Eficiência da Configuração</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          <div className="flex justify-between items-center">
                            <span>Eficiência:</span>
                            <div className="flex items-center space-x-2">
                              <span className={`font-bold ${getEfficiencyColor(calculation.efficiency_ratio)}`}>
                                {calculation.efficiency_ratio}%
                              </span>
                              {getEfficiencyBadge(calculation.efficiency_ratio)}
                            </div>
                          </div>
                          <Progress value={calculation.efficiency_ratio} className="w-full" />
                          <div className="text-sm text-muted-foreground">
                            Capacidade diária total: {formatNumber(calculation.total_daily_capacity)} chamadas
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                    
                    <Card>
                      <CardHeader>
                        <CardTitle className="text-lg">Detalhes Técnicos</CardTitle>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-2 text-sm">
                          <div className="flex justify-between">
                            <span>Chamadas por CLI/hora:</span>
                            <span className="font-medium">{calculation.calls_per_cli_per_hour}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>País:</span>
                            <span className="font-medium uppercase">{calculation.country}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Limite diário aplicado:</span>
                            <span className="font-medium">{calculation.daily_call_limit}</span>
                          </div>
                          <div className="flex justify-between">
                            <span>Horas de trabalho:</span>
                            <span className="font-medium">{calculation.work_hours}h</span>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="config" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Settings className="h-5 w-5" />
                <span>Criar Configuração Automática</span>
              </CardTitle>
              <div className="text-sm text-gray-600">
                Crie uma configuração completa com geração automática de CLIs
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="config_campaign_id">ID da Campanha (opcional)</Label>
                  <Input
                    id="config_campaign_id"
                    type="number"
                    value={configForm.campaign_id}
                    onChange={(e) => setConfigForm({...configForm, campaign_id: e.target.value})}
                    placeholder="Deixe vazio se não aplicável"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="config_total_numbers">Total de Números</Label>
                  <Input
                    id="config_total_numbers"
                    type="number"
                    value={configForm.total_numbers}
                    onChange={(e) => setConfigForm({...configForm, total_numbers: parseInt(e.target.value) || 0})}
                    placeholder="10000"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="config_calls_per_hour">Chamadas por Hora</Label>
                  <Input
                    id="config_calls_per_hour"
                    type="number"
                    value={configForm.calls_per_hour}
                    onChange={(e) => setConfigForm({...configForm, calls_per_hour: parseInt(e.target.value) || 0})}
                    placeholder="500"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="config_daily_limit">Limite Diário por CLI</Label>
                  <Input
                    id="config_daily_limit"
                    type="number"
                    value={configForm.daily_call_limit}
                    onChange={(e) => setConfigForm({...configForm, daily_call_limit: parseInt(e.target.value) || 0})}
                    placeholder="100"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="config_work_hours">Horas de Trabalho</Label>
                  <Input
                    id="config_work_hours"
                    type="number"
                    value={configForm.work_hours}
                    onChange={(e) => setConfigForm({...configForm, work_hours: parseInt(e.target.value) || 0})}
                    placeholder="8"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="config_country">País</Label>
                  <Select 
                    value={configForm.country} 
                    onChange={(e) => setConfigForm({...configForm, country: e.target.value})}
                    options={[
                      { value: 'usa', label: 'Estados Unidos' },
                      { value: 'canada', label: 'Canadá' },
                      { value: 'mexico', label: 'México' },
                      { value: 'brazil', label: 'Brasil' }
                    ]}
                  />
                </div>
              </div>
              
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  id="auto_generate"
                  checked={configForm.auto_generate}
                  onChange={(e) => setConfigForm({...configForm, auto_generate: e.target.checked})}
                  className="rounded"
                />
                <Label htmlFor="auto_generate">Gerar CLIs automaticamente</Label>
              </div>
              
              <Alert>
                <Info className="h-4 w-4" />
                <AlertDescription>
                  <strong>Benefícios da configuração automática:</strong>
                  <ul className="mt-2 list-disc list-inside space-y-1">
                    <li>Remove o limite de 20 CLIs do sistema atual</li>
                    <li>Cálculo baseado no volume real de números</li>
                    <li>Geração automática com códigos de área reais dos EUA</li>
                    <li>Prevenção automática de blacklisting</li>
                    <li>Distribuição inteligente de carga entre CLIs</li>
                  </ul>
                </AlertDescription>
              </Alert>
              
              <div className="flex justify-center">
                <Button 
                  onClick={createConfig} 
                  disabled={loading}
                  className="w-full md:w-auto"
                  size="lg"
                >
                  {loading ? 'Criando...' : 'Criar Configuração Automática'}
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="management" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <BarChart3 className="h-5 w-5" />
                <span>Gerenciamento de Configurações</span>
              </CardTitle>
              <div className="text-sm text-gray-600">
                Monitore e gerencie suas configurações automáticas de CLIs
              </div>
            </CardHeader>
            <CardContent>
              {configs.length === 0 ? (
                <div className="text-center py-8">
                  <Settings className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
                  <h3 className="text-lg font-medium mb-2">Nenhuma configuração encontrada</h3>
                  <p className="text-muted-foreground mb-4">
                    Crie sua primeira configuração automática na aba "Configuração"
                  </p>
                  <Button onClick={() => setActiveTab('config')}>
                    Criar Configuração
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  {/* Lista de configurações será implementada aqui */}
                  <p className="text-muted-foreground">Configurações carregadas: {configs.length}</p>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="examples" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Info className="h-5 w-5" />
                <span>Exemplos Práticos</span>
              </CardTitle>
              <div className="text-sm text-gray-600">
                Entenda como o sistema calcula CLIs para diferentes cenários
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <Card className="border-blue-200">
                  <CardHeader>
                    <CardTitle className="text-lg text-blue-700">Campanha Pequena</CardTitle>
                    <div className="text-sm text-gray-600">Volume baixo, operação local</div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Números:</span>
                        <span className="font-medium">1.000</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Chamadas/hora:</span>
                        <span className="font-medium">200</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Limite diário:</span>
                        <span className="font-medium">100</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Horas trabalho:</span>
                        <span className="font-medium">8h</span>
                      </div>
                      <hr className="my-2" />
                      <div className="flex justify-between font-bold text-blue-700">
                        <span>CLIs necessários:</span>
                        <span>~3</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                <Card className="border-green-200">
                  <CardHeader>
                    <CardTitle className="text-lg text-green-700">Campanha Média</CardTitle>
                    <div className="text-sm text-gray-600">Volume moderado, operação regional</div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Números:</span>
                        <span className="font-medium">10.000</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Chamadas/hora:</span>
                        <span className="font-medium">500</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Limite diário:</span>
                        <span className="font-medium">100</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Horas trabalho:</span>
                        <span className="font-medium">8h</span>
                      </div>
                      <hr className="my-2" />
                      <div className="flex justify-between font-bold text-green-700">
                        <span>CLIs necessários:</span>
                        <span>~63</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                <Card className="border-orange-200">
                  <CardHeader>
                    <CardTitle className="text-lg text-orange-700">Campanha Grande</CardTitle>
                    <div className="text-sm text-gray-600">Alto volume, operação nacional</div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Números:</span>
                        <span className="font-medium">100.000</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Chamadas/hora:</span>
                        <span className="font-medium">1.000</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Limite diário:</span>
                        <span className="font-medium">100</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Horas trabalho:</span>
                        <span className="font-medium">8h</span>
                      </div>
                      <hr className="my-2" />
                      <div className="flex justify-between font-bold text-orange-700">
                        <span>CLIs necessários:</span>
                        <span>~1.500</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
                
                <Card className="border-red-200">
                  <CardHeader>
                    <CardTitle className="text-lg text-red-700">Campanha Intensiva</CardTitle>
                    <div className="text-sm text-gray-600">Discagem muito agressiva</div>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span>Números:</span>
                        <span className="font-medium">50.000</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Chamadas/hora:</span>
                        <span className="font-medium">2.000</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Limite diário:</span>
                        <span className="font-medium">100</span>
                      </div>
                      <div className="flex justify-between">
                        <span>Horas trabalho:</span>
                        <span className="font-medium">8h</span>
                      </div>
                      <hr className="my-2" />
                      <div className="flex justify-between font-bold text-red-700">
                        <span>CLIs necessários:</span>
                        <span>~3.000</span>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </div>
              
              <Alert>
                <TrendingUp className="h-4 w-4" />
                <AlertDescription>
                  <strong>Fórmula de Cálculo:</strong>
                  <div className="mt-2 space-y-1 text-sm">
                    <p><strong>Básica:</strong> CLIs = (Total números × Chamadas/hora) ÷ (Limite diário × Horas trabalho)</p>
                    <p><strong>Margem de Segurança:</strong> Resultado × 1.2 (20% adicional)</p>
                    <p><strong>Regra Mínima:</strong> Nunca menos que Total números ÷ Limite diário</p>
                  </div>
                </AlertDescription>
              </Alert>
              
              <Card>
                <CardHeader>
                  <CardTitle className="text-lg">Melhores Práticas</CardTitle>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2 text-sm">
                    <li className="flex items-start space-x-2">
                      <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                      <span>Sempre usar margem de segurança de pelo menos 20%</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                      <span>Considerar fuso horário do público-alvo</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                      <span>Monitorar uso diário para ajustar limites</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                      <span>Resetar contadores diariamente</span>
                    </li>
                    <li className="flex items-start space-x-2">
                      <CheckCircle className="h-4 w-4 text-green-600 mt-0.5" />
                      <span>Usar códigos de área locais quando possível</span>
                    </li>
                  </ul>
                </CardContent>
              </Card>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default CliAutoCalculator;