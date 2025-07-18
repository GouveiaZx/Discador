import React, { useState, useEffect } from 'react';
import { makeApiRequest } from '../services/api';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select } from './ui/select';
import { Badge } from './ui/badge';
import { Alert } from './ui/alert';
import { Switch } from './ui/switch';

const ScheduleManager = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Estados para configuração de horários
  const [scheduleConfig, setScheduleConfig] = useState({
    ativo: false,
    horario_inicio: '08:00',
    horario_fim: '18:00',
    horario_almoco_inicio: '12:00',
    horario_almoco_fim: '13:00',
    dias_semana: {
      segunda: true,
      terca: true,
      quarta: true,
      quinta: true,
      sexta: true,
      sabado: false,
      domingo: false
    },
    fuso_horario: 'America/Sao_Paulo',
    pausar_durante_almoco: true,
    pausar_fora_horario: true,
    retomar_automaticamente: true
  });
  
  // Estados para status atual
  const [currentStatus, setCurrentStatus] = useState({
    sistema_ativo: false,
    em_horario_funcionamento: false,
    em_pausa_almoco: false,
    proximo_evento: null,
    tempo_restante: null,
    campanhas_pausadas: 0,
    campanhas_ativas: 0
  });
  
  // Estados para histórico de eventos
  const [scheduleHistory, setScheduleHistory] = useState([]);
  
  // Estados para configurações de feriados
  const [holidays, setHolidays] = useState([]);
  const [showHolidayForm, setShowHolidayForm] = useState(false);
  const [holidayForm, setHolidayForm] = useState({
    nome: '',
    data: '',
    recorrente: false,
    pausar_sistema: true,
    descricao: ''
  });
  
  // Estados para timer em tempo real
  const [currentTime, setCurrentTime] = useState(new Date());
  const [timeUntilNext, setTimeUntilNext] = useState('');

  useEffect(() => {
    fetchScheduleData();
    
    // Atualizar tempo a cada segundo
    const timeInterval = setInterval(() => {
      setCurrentTime(new Date());
      calculateTimeUntilNext();
    }, 1000);
    
    // Verificar status a cada minuto
    const statusInterval = setInterval(() => {
      fetchCurrentStatus();
    }, 60000);
    
    return () => {
      clearInterval(timeInterval);
      clearInterval(statusInterval);
    };
  }, []);

  const fetchScheduleData = async () => {
    try {
      setLoading(true);
      await Promise.all([
        fetchScheduleConfig(),
        fetchCurrentStatus(),
        fetchScheduleHistory(),
        fetchHolidays()
      ]);
    } catch (err) {
      setError('Erro ao carregar dados de horário: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchScheduleConfig = async () => {
    try {
      const response = await makeApiRequest('/schedule/config');
      if (response.config) {
        setScheduleConfig(response.config);
      }
    } catch (err) {
      console.error('Erro ao buscar configuração de horário:', err);
    }
  };

  const fetchCurrentStatus = async () => {
    try {
      const response = await makeApiRequest('/schedule/status');
      if (response.status) {
        setCurrentStatus(response.status);
      }
    } catch (err) {
      console.error('Erro ao buscar status atual:', err);
    }
  };

  const fetchScheduleHistory = async () => {
    try {
      const response = await makeApiRequest('/schedule/history');
      setScheduleHistory(response.history || []);
    } catch (err) {
      console.error('Erro ao buscar histórico:', err);
    }
  };

  const fetchHolidays = async () => {
    try {
      const response = await makeApiRequest('/schedule/holidays');
      setHolidays(response.holidays || []);
    } catch (err) {
      console.error('Erro ao buscar feriados:', err);
    }
  };

  const saveScheduleConfig = async () => {
    try {
      setLoading(true);
      await makeApiRequest('/schedule/config', 'PUT', scheduleConfig);
      await fetchCurrentStatus();
      setSuccess('Configuração de horário salva com sucesso!');
    } catch (err) {
      setError('Erro ao salvar configuração: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleSystemStatus = async () => {
    try {
      setLoading(true);
      const action = currentStatus.sistema_ativo ? 'pause' : 'resume';
      await makeApiRequest(`/schedule/${action}`, 'POST');
      await fetchCurrentStatus();
      setSuccess(`Sistema ${action === 'pause' ? 'pausado' : 'retomado'} manualmente!`);
    } catch (err) {
      setError('Erro ao alterar status do sistema: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const forceStart = async () => {
    if (!confirm('Forçar início do sistema fora do horário configurado?')) return;
    
    try {
      setLoading(true);
      await makeApiRequest('/schedule/force-start', 'POST');
      await fetchCurrentStatus();
      setSuccess('Sistema iniciado forçadamente!');
    } catch (err) {
      setError('Erro ao forçar início: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const forceStop = async () => {
    if (!confirm('Forçar parada do sistema?')) return;
    
    try {
      setLoading(true);
      await makeApiRequest('/schedule/force-stop', 'POST');
      await fetchCurrentStatus();
      setSuccess('Sistema parado forçadamente!');
    } catch (err) {
      setError('Erro ao forçar parada: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const addHoliday = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      await makeApiRequest('/schedule/holidays', 'POST', holidayForm);
      await fetchHolidays();
      resetHolidayForm();
      setSuccess('Feriado adicionado com sucesso!');
    } catch (err) {
      setError('Erro ao adicionar feriado: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const deleteHoliday = async (holidayId) => {
    if (!confirm('Excluir este feriado?')) return;
    
    try {
      setLoading(true);
      await makeApiRequest(`/schedule/holidays/${holidayId}`, 'DELETE');
      await fetchHolidays();
      setSuccess('Feriado excluído com sucesso!');
    } catch (err) {
      setError('Erro ao excluir feriado: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const resetHolidayForm = () => {
    setHolidayForm({
      nome: '',
      data: '',
      recorrente: false,
      pausar_sistema: true,
      descricao: ''
    });
    setShowHolidayForm(false);
  };

  const calculateTimeUntilNext = () => {
    if (!scheduleConfig.ativo || !currentStatus.proximo_evento) {
      setTimeUntilNext('');
      return;
    }
    
    const now = new Date();
    const nextEvent = new Date(currentStatus.proximo_evento);
    const diff = nextEvent - now;
    
    if (diff <= 0) {
      setTimeUntilNext('Evento em andamento');
      return;
    }
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    const seconds = Math.floor((diff % (1000 * 60)) / 1000);
    
    if (hours > 0) {
      setTimeUntilNext(`${hours}h ${minutes}m ${seconds}s`);
    } else if (minutes > 0) {
      setTimeUntilNext(`${minutes}m ${seconds}s`);
    } else {
      setTimeUntilNext(`${seconds}s`);
    }
  };

  const formatTime = (time) => {
    return new Date(time).toLocaleString('pt-BR');
  };

  const getStatusColor = (status) => {
    if (status) return 'bg-green-100 text-green-800';
    return 'bg-red-100 text-red-800';
  };

  const getDayName = (day) => {
    const days = {
      segunda: 'Segunda',
      terca: 'Terça',
      quarta: 'Quarta',
      quinta: 'Quinta',
      sexta: 'Sexta',
      sabado: 'Sábado',
      domingo: 'Domingo'
    };
    return days[day] || day;
  };

  return (
    <div className="p-6 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">Gestão de Horários</h1>
        <div className="text-lg font-mono text-gray-600">
          {currentTime.toLocaleString('pt-BR')}
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

      {/* Status Atual */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm text-gray-600">Sistema</div>
              <Badge className={getStatusColor(currentStatus.sistema_ativo)}>
                {currentStatus.sistema_ativo ? 'Ativo' : 'Inativo'}
              </Badge>
            </div>
            <Button
              size="sm"
              onClick={toggleSystemStatus}
              className={currentStatus.sistema_ativo ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'}
            >
              {currentStatus.sistema_ativo ? 'Pausar' : 'Iniciar'}
            </Button>
          </div>
        </Card>
        
        <Card className="p-4">
          <div className="text-sm text-gray-600">Horário de Funcionamento</div>
          <Badge className={getStatusColor(currentStatus.em_horario_funcionamento)}>
            {currentStatus.em_horario_funcionamento ? 'Em funcionamento' : 'Fora do horário'}
          </Badge>
        </Card>
        
        <Card className="p-4">
          <div className="text-sm text-gray-600">Pausa Almoço</div>
          <Badge className={getStatusColor(!currentStatus.em_pausa_almoco)}>
            {currentStatus.em_pausa_almoco ? 'Em pausa' : 'Ativo'}
          </Badge>
        </Card>
        
        <Card className="p-4">
          <div className="text-sm text-gray-600">Campanhas</div>
          <div className="text-lg font-semibold">
            {currentStatus.campanhas_ativas} ativas / {currentStatus.campanhas_pausadas} pausadas
          </div>
        </Card>
      </div>

      {/* Próximo Evento */}
      {currentStatus.proximo_evento && (
        <Card className="p-4">
          <div className="flex justify-between items-center">
            <div>
              <h3 className="font-semibold text-gray-900">Próximo Evento</h3>
              <p className="text-sm text-gray-600">{formatTime(currentStatus.proximo_evento)}</p>
            </div>
            <div className="text-right">
              <div className="text-lg font-mono font-semibold text-blue-600">{timeUntilNext}</div>
              <div className="text-xs text-gray-500">tempo restante</div>
            </div>
          </div>
        </Card>
      )}

      {/* Configuração de Horários */}
      <Card className="p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Configuração de Horários</h2>
          <div className="flex space-x-2">
            <Button onClick={forceStart} variant="outline" className="border-green-300 text-green-600">
              Forçar Início
            </Button>
            <Button onClick={forceStop} variant="outline" className="border-red-300 text-red-600">
              Forçar Parada
            </Button>
          </div>
        </div>
        
        <div className="space-y-6">
          <div className="flex items-center space-x-2">
            <Switch
              checked={scheduleConfig.ativo}
              onCheckedChange={(checked) => setScheduleConfig({...scheduleConfig, ativo: checked})}
            />
            <Label>Ativar controle automático de horários</Label>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div>
              <Label htmlFor="horario_inicio">Horário de Início</Label>
              <Input
                id="horario_inicio"
                type="time"
                value={scheduleConfig.horario_inicio}
                onChange={(e) => setScheduleConfig({...scheduleConfig, horario_inicio: e.target.value})}
              />
            </div>
            
            <div>
              <Label htmlFor="horario_fim">Horário de Fim</Label>
              <Input
                id="horario_fim"
                type="time"
                value={scheduleConfig.horario_fim}
                onChange={(e) => setScheduleConfig({...scheduleConfig, horario_fim: e.target.value})}
              />
            </div>
            
            <div>
              <Label htmlFor="horario_almoco_inicio">Início do Almoço</Label>
              <Input
                id="horario_almoco_inicio"
                type="time"
                value={scheduleConfig.horario_almoco_inicio}
                onChange={(e) => setScheduleConfig({...scheduleConfig, horario_almoco_inicio: e.target.value})}
              />
            </div>
            
            <div>
              <Label htmlFor="horario_almoco_fim">Fim do Almoço</Label>
              <Input
                id="horario_almoco_fim"
                type="time"
                value={scheduleConfig.horario_almoco_fim}
                onChange={(e) => setScheduleConfig({...scheduleConfig, horario_almoco_fim: e.target.value})}
              />
            </div>
          </div>
          
          <div>
            <Label>Dias da Semana</Label>
            <div className="grid grid-cols-7 gap-2 mt-2">
              {Object.keys(scheduleConfig.dias_semana).map((day) => (
                <div key={day} className="flex items-center space-x-1">
                  <input
                    type="checkbox"
                    id={day}
                    checked={scheduleConfig.dias_semana[day]}
                    onChange={(e) => setScheduleConfig({
                      ...scheduleConfig,
                      dias_semana: {
                        ...scheduleConfig.dias_semana,
                        [day]: e.target.checked
                      }
                    })}
                    className="rounded"
                  />
                  <Label htmlFor={day} className="text-xs">{getDayName(day)}</Label>
                </div>
              ))}
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="pausar_durante_almoco"
                checked={scheduleConfig.pausar_durante_almoco}
                onChange={(e) => setScheduleConfig({...scheduleConfig, pausar_durante_almoco: e.target.checked})}
                className="rounded"
              />
              <Label htmlFor="pausar_durante_almoco">Pausar durante almoço</Label>
            </div>
            
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="pausar_fora_horario"
                checked={scheduleConfig.pausar_fora_horario}
                onChange={(e) => setScheduleConfig({...scheduleConfig, pausar_fora_horario: e.target.checked})}
                className="rounded"
              />
              <Label htmlFor="pausar_fora_horario">Pausar fora do horário</Label>
            </div>
            
            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="retomar_automaticamente"
                checked={scheduleConfig.retomar_automaticamente}
                onChange={(e) => setScheduleConfig({...scheduleConfig, retomar_automaticamente: e.target.checked})}
                className="rounded"
              />
              <Label htmlFor="retomar_automaticamente">Retomar automaticamente</Label>
            </div>
          </div>
          
          <div>
            <Label htmlFor="fuso_horario">Fuso Horário</Label>
            <Select
              value={scheduleConfig.fuso_horario}
              onValueChange={(value) => setScheduleConfig({...scheduleConfig, fuso_horario: value})}
            >
              <option value="America/Sao_Paulo">Brasília (GMT-3)</option>
              <option value="America/New_York">Nova York (GMT-5)</option>
              <option value="America/Los_Angeles">Los Angeles (GMT-8)</option>
              <option value="America/Mexico_City">Cidade do México (GMT-6)</option>
              <option value="America/Toronto">Toronto (GMT-5)</option>
            </Select>
          </div>
          
          <Button onClick={saveScheduleConfig} disabled={loading}>
            {loading ? 'Salvando...' : 'Salvar Configuração'}
          </Button>
        </div>
      </Card>

      {/* Gestão de Feriados */}
      <Card className="p-6">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-semibold">Feriados e Datas Especiais</h2>
          <Button 
            onClick={() => setShowHolidayForm(!showHolidayForm)}
            className="bg-purple-600 hover:bg-purple-700"
          >
            {showHolidayForm ? 'Cancelar' : 'Adicionar Feriado'}
          </Button>
        </div>
        
        {showHolidayForm && (
          <form onSubmit={addHoliday} className="mb-6 p-4 border rounded-lg bg-gray-50">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <Label htmlFor="holiday_nome">Nome do Feriado</Label>
                <Input
                  id="holiday_nome"
                  value={holidayForm.nome}
                  onChange={(e) => setHolidayForm({...holidayForm, nome: e.target.value})}
                  placeholder="Ex: Natal"
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="holiday_data">Data</Label>
                <Input
                  id="holiday_data"
                  type="date"
                  value={holidayForm.data}
                  onChange={(e) => setHolidayForm({...holidayForm, data: e.target.value})}
                  required
                />
              </div>
              
              <div>
                <Label htmlFor="holiday_descricao">Descrição</Label>
                <Input
                  id="holiday_descricao"
                  value={holidayForm.descricao}
                  onChange={(e) => setHolidayForm({...holidayForm, descricao: e.target.value})}
                  placeholder="Descrição opcional"
                />
              </div>
              
              <div className="space-y-2">
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="holiday_recorrente"
                    checked={holidayForm.recorrente}
                    onChange={(e) => setHolidayForm({...holidayForm, recorrente: e.target.checked})}
                    className="rounded"
                  />
                  <Label htmlFor="holiday_recorrente">Recorrente (todo ano)</Label>
                </div>
                
                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="holiday_pausar"
                    checked={holidayForm.pausar_sistema}
                    onChange={(e) => setHolidayForm({...holidayForm, pausar_sistema: e.target.checked})}
                    className="rounded"
                  />
                  <Label htmlFor="holiday_pausar">Pausar sistema</Label>
                </div>
              </div>
            </div>
            
            <div className="flex space-x-2 mt-4">
              <Button type="submit" disabled={loading}>
                {loading ? 'Adicionando...' : 'Adicionar Feriado'}
              </Button>
              <Button type="button" variant="outline" onClick={resetHolidayForm}>
                Cancelar
              </Button>
            </div>
          </form>
        )}
        
        <div className="space-y-2">
          {holidays.map((holiday) => (
            <div key={holiday.id} className="flex justify-between items-center p-3 border rounded hover:bg-gray-50">
              <div>
                <div className="font-medium">{holiday.nome}</div>
                <div className="text-sm text-gray-600">
                  {new Date(holiday.data).toLocaleDateString('pt-BR')}
                  {holiday.recorrente && ' (Anual)'}
                  {holiday.pausar_sistema && ' • Pausa sistema'}
                </div>
                {holiday.descricao && (
                  <div className="text-xs text-gray-500">{holiday.descricao}</div>
                )}
              </div>
              <Button
                size="sm"
                variant="outline"
                className="border-red-300 text-red-600 hover:bg-red-50"
                onClick={() => deleteHoliday(holiday.id)}
              >
                Excluir
              </Button>
            </div>
          ))}
          
          {holidays.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              Nenhum feriado configurado.
            </div>
          )}
        </div>
      </Card>

      {/* Histórico de Eventos */}
      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4">Histórico de Eventos</h2>
        
        <div className="space-y-2">
          {scheduleHistory.slice(0, 10).map((event, index) => (
            <div key={index} className="flex justify-between items-center p-3 border rounded hover:bg-gray-50">
              <div>
                <div className="font-medium">{event.evento}</div>
                <div className="text-sm text-gray-600">{event.descricao}</div>
              </div>
              <div className="text-sm text-gray-500">
                {formatTime(event.timestamp)}
              </div>
            </div>
          ))}
          
          {scheduleHistory.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              Nenhum evento registrado.
            </div>
          )}
          
          {scheduleHistory.length > 10 && (
            <div className="text-center text-sm text-gray-500">
              Mostrando 10 eventos mais recentes de {scheduleHistory.length} total.
            </div>
          )}
        </div>
      </Card>
    </div>
  );
};

export default ScheduleManager;