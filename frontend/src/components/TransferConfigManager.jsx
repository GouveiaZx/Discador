import React, { useState, useEffect } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  FormControl,
  FormControlLabel,
  Grid,
  IconButton,
  InputLabel,
  MenuItem,
  Select,
  Switch,
  TextField,
  Typography,
  Chip,
  Alert,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  LinearProgress,
  Tooltip
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  ExpandMore as ExpandMoreIcon,
  Phone as PhoneIcon,
  Schedule as ScheduleIcon,
  Analytics as AnalyticsIcon,
  PlayArrow as TestIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { toast } from 'react-toastify';

const TransferConfigManager = () => {
  const [configs, setConfigs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingConfig, setEditingConfig] = useState(null);
  const [statsDialogOpen, setStatsDialogOpen] = useState(false);
  const [selectedConfigStats, setSelectedConfigStats] = useState(null);
  const [testDialogOpen, setTestDialogOpen] = useState(false);
  const [testResults, setTestResults] = useState(null);

  // Form state
  const [formData, setFormData] = useState({
    campanha_id: '',
    nome: '',
    numeros_transferencia: [],
    estrategia_selecao: 'round-robin',
    ativo: true,
    horario_funcionamento: {
      inicio: '08:00',
      fim: '18:00',
      dias_semana: [0, 1, 2, 3, 4], // Segunda a Sexta
      fuso_horario: 'America/Sao_Paulo'
    },
    prioridades: {}
  });

  const [newNumber, setNewNumber] = useState('');

  const estrategias = [
    { value: 'round-robin', label: 'Round Robin (Sequencial)' },
    { value: 'aleatoria', label: 'Aleatória' },
    { value: 'prioridade', label: 'Por Prioridade' }
  ];

  const diasSemana = [
    { value: 0, label: 'Segunda' },
    { value: 1, label: 'Terça' },
    { value: 2, label: 'Quarta' },
    { value: 3, label: 'Quinta' },
    { value: 4, label: 'Sexta' },
    { value: 5, label: 'Sábado' },
    { value: 6, label: 'Domingo' }
  ];

  useEffect(() => {
    loadConfigs();
  }, []);

  const loadConfigs = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/transfer-config/');
      if (response.ok) {
        const data = await response.json();
        setConfigs(data);
      } else {
        toast.error('Erro ao carregar configurações');
      }
    } catch (error) {
      console.error('Erro ao carregar configurações:', error);
      toast.error('Erro de conexão');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      const url = editingConfig 
        ? `/api/transfer-config/${editingConfig.id}`
        : '/api/transfer-config/';
      
      const method = editingConfig ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        toast.success(editingConfig ? 'Configuração atualizada!' : 'Configuração criada!');
        setDialogOpen(false);
        resetForm();
        loadConfigs();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Erro ao salvar configuração');
      }
    } catch (error) {
      console.error('Erro ao salvar:', error);
      toast.error('Erro de conexão');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Tem certeza que deseja deletar esta configuração?')) {
      return;
    }

    try {
      const response = await fetch(`/api/transfer-config/${id}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        toast.success('Configuração deletada!');
        loadConfigs();
      } else {
        toast.error('Erro ao deletar configuração');
      }
    } catch (error) {
      console.error('Erro ao deletar:', error);
      toast.error('Erro de conexão');
    }
  };

  const handleEdit = (config) => {
    setEditingConfig(config);
    setFormData({
      campanha_id: config.campanha_id,
      nome: config.nome,
      numeros_transferencia: config.numeros_transferencia,
      estrategia_selecao: config.estrategia_selecao,
      ativo: config.ativo,
      horario_funcionamento: config.horario_funcionamento || {
        inicio: '08:00',
        fim: '18:00',
        dias_semana: [0, 1, 2, 3, 4],
        fuso_horario: 'America/Sao_Paulo'
      },
      prioridades: config.prioridades || {}
    });
    setDialogOpen(true);
  };

  const resetForm = () => {
    setEditingConfig(null);
    setFormData({
      campanha_id: '',
      nome: '',
      numeros_transferencia: [],
      estrategia_selecao: 'round-robin',
      ativo: true,
      horario_funcionamento: {
        inicio: '08:00',
        fim: '18:00',
        dias_semana: [0, 1, 2, 3, 4],
        fuso_horario: 'America/Sao_Paulo'
      },
      prioridades: {}
    });
    setNewNumber('');
  };

  const addNumber = () => {
    if (newNumber.trim() && !formData.numeros_transferencia.includes(newNumber.trim())) {
      setFormData(prev => ({
        ...prev,
        numeros_transferencia: [...prev.numeros_transferencia, newNumber.trim()]
      }));
      setNewNumber('');
    }
  };

  const removeNumber = (numberToRemove) => {
    setFormData(prev => ({
      ...prev,
      numeros_transferencia: prev.numeros_transferencia.filter(num => num !== numberToRemove)
    }));
    
    // Remover das prioridades também
    if (formData.prioridades[numberToRemove]) {
      const newPrioridades = { ...formData.prioridades };
      delete newPrioridades[numberToRemove];
      setFormData(prev => ({ ...prev, prioridades: newPrioridades }));
    }
  };

  const updatePriority = (number, priority) => {
    setFormData(prev => ({
      ...prev,
      prioridades: {
        ...prev.prioridades,
        [number]: parseInt(priority)
      }
    }));
  };

  const loadStats = async (configId) => {
    try {
      const response = await fetch(`/api/transfer-config/${configId}/stats`);
      if (response.ok) {
        const stats = await response.json();
        setSelectedConfigStats(stats);
        setStatsDialogOpen(true);
      } else {
        toast.error('Erro ao carregar estatísticas');
      }
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
      toast.error('Erro de conexão');
    }
  };

  const testStrategy = async () => {
    try {
      const response = await fetch('/api/transfer-config/test-strategy', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          numeros: formData.numeros_transferencia,
          estrategia: formData.estrategia_selecao,
          prioridades: formData.estrategia_selecao === 'prioridade' ? formData.prioridades : null,
          quantidade_testes: 20
        })
      });

      if (response.ok) {
        const results = await response.json();
        setTestResults(results);
        setTestDialogOpen(true);
      } else {
        toast.error('Erro ao testar estratégia');
      }
    } catch (error) {
      console.error('Erro ao testar estratégia:', error);
      toast.error('Erro de conexão');
    }
  };

  const getStatusColor = (ativo) => {
    return ativo ? 'success' : 'default';
  };

  const getEstrategiaLabel = (estrategia) => {
    const found = estrategias.find(e => e.value === estrategia);
    return found ? found.label : estrategia;
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Configurações de Transferência
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadConfigs}
            sx={{ mr: 2 }}
          >
            Atualizar
          </Button>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => {
              resetForm();
              setDialogOpen(true);
            }}
          >
            Nova Configuração
          </Button>
        </Box>
      </Box>

      {loading && <LinearProgress sx={{ mb: 2 }} />}

      <Grid container spacing={3}>
        {configs.map((config) => (
          <Grid item xs={12} md={6} lg={4} key={config.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
                  <Typography variant="h6" component="h2">
                    {config.nome}
                  </Typography>
                  <Chip
                    label={config.ativo ? 'Ativo' : 'Inativo'}
                    color={getStatusColor(config.ativo)}
                    size="small"
                  />
                </Box>

                <Typography color="text.secondary" gutterBottom>
                  Campanha: {config.campanha_id}
                </Typography>

                <Typography variant="body2" sx={{ mb: 1 }}>
                  <strong>Estratégia:</strong> {getEstrategiaLabel(config.estrategia_selecao)}
                </Typography>

                <Typography variant="body2" sx={{ mb: 2 }}>
                  <strong>Números:</strong> {config.numeros_transferencia.length}
                </Typography>

                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mb: 2 }}>
                  {config.numeros_transferencia.slice(0, 3).map((numero, index) => (
                    <Chip
                      key={index}
                      label={numero}
                      size="small"
                      icon={<PhoneIcon />}
                    />
                  ))}
                  {config.numeros_transferencia.length > 3 && (
                    <Chip
                      label={`+${config.numeros_transferencia.length - 3} mais`}
                      size="small"
                      variant="outlined"
                    />
                  )}
                </Box>

                <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                  <Box>
                    <Tooltip title="Editar">
                      <IconButton
                        size="small"
                        onClick={() => handleEdit(config)}
                      >
                        <EditIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Estatísticas">
                      <IconButton
                        size="small"
                        onClick={() => loadStats(config.id)}
                      >
                        <AnalyticsIcon />
                      </IconButton>
                    </Tooltip>
                    <Tooltip title="Deletar">
                      <IconButton
                        size="small"
                        color="error"
                        onClick={() => handleDelete(config.id)}
                      >
                        <DeleteIcon />
                      </IconButton>
                    </Tooltip>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Dialog para criar/editar configuração */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingConfig ? 'Editar Configuração' : 'Nova Configuração'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="ID da Campanha"
                type="number"
                value={formData.campanha_id}
                onChange={(e) => setFormData(prev => ({ ...prev, campanha_id: parseInt(e.target.value) || '' }))}
                required
              />
            </Grid>
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Nome da Configuração"
                value={formData.nome}
                onChange={(e) => setFormData(prev => ({ ...prev, nome: e.target.value }))}
                required
              />
            </Grid>
            
            <Grid item xs={12} sm={8}>
              <FormControl fullWidth>
                <InputLabel>Estratégia de Seleção</InputLabel>
                <Select
                  value={formData.estrategia_selecao}
                  onChange={(e) => setFormData(prev => ({ ...prev, estrategia_selecao: e.target.value }))}
                  label="Estratégia de Seleção"
                >
                  {estrategias.map((estrategia) => (
                    <MenuItem key={estrategia.value} value={estrategia.value}>
                      {estrategia.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={4}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.ativo}
                    onChange={(e) => setFormData(prev => ({ ...prev, ativo: e.target.checked }))}
                  />
                }
                label="Ativo"
              />
            </Grid>

            {/* Seção de números */}
            <Grid item xs={12}>
              <Typography variant="h6" sx={{ mb: 2 }}>
                Números de Transferência
              </Typography>
              
              <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
                <TextField
                  label="Novo número"
                  value={newNumber}
                  onChange={(e) => setNewNumber(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && addNumber()}
                  placeholder="Ex: 1140001234"
                  sx={{ flexGrow: 1 }}
                />
                <Button variant="outlined" onClick={addNumber}>
                  Adicionar
                </Button>
              </Box>

              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                {formData.numeros_transferencia.map((numero, index) => (
                  <Chip
                    key={index}
                    label={numero}
                    onDelete={() => removeNumber(numero)}
                    color="primary"
                    variant="outlined"
                  />
                ))}
              </Box>

              {formData.estrategia_selecao === 'prioridade' && formData.numeros_transferencia.length > 0 && (
                <Accordion>
                  <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography>Configurar Prioridades</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <Grid container spacing={2}>
                      {formData.numeros_transferencia.map((numero) => (
                        <Grid item xs={12} sm={6} key={numero}>
                          <TextField
                            fullWidth
                            label={`Prioridade - ${numero}`}
                            type="number"
                            value={formData.prioridades[numero] || 1}
                            onChange={(e) => updatePriority(numero, e.target.value)}
                            inputProps={{ min: 1, max: 10 }}
                            helperText="1 = maior prioridade, 10 = menor prioridade"
                          />
                        </Grid>
                      ))}
                    </Grid>
                  </AccordionDetails>
                </Accordion>
              )}
            </Grid>

            {/* Seção de horário de funcionamento */}
            <Grid item xs={12}>
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography>Horário de Funcionamento (Opcional)</Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Horário de Início"
                        type="time"
                        value={formData.horario_funcionamento.inicio}
                        onChange={(e) => setFormData(prev => ({
                          ...prev,
                          horario_funcionamento: {
                            ...prev.horario_funcionamento,
                            inicio: e.target.value
                          }
                        }))}
                        InputLabelProps={{ shrink: true }}
                      />
                    </Grid>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Horário de Fim"
                        type="time"
                        value={formData.horario_funcionamento.fim}
                        onChange={(e) => setFormData(prev => ({
                          ...prev,
                          horario_funcionamento: {
                            ...prev.horario_funcionamento,
                            fim: e.target.value
                          }
                        }))}
                        InputLabelProps={{ shrink: true }}
                      />
                    </Grid>
                    <Grid item xs={12}>
                      <Typography variant="subtitle2" sx={{ mb: 1 }}>
                        Dias da Semana
                      </Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                        {diasSemana.map((dia) => (
                          <FormControlLabel
                            key={dia.value}
                            control={
                              <Switch
                                checked={formData.horario_funcionamento.dias_semana.includes(dia.value)}
                                onChange={(e) => {
                                  const dias = formData.horario_funcionamento.dias_semana;
                                  if (e.target.checked) {
                                    setFormData(prev => ({
                                      ...prev,
                                      horario_funcionamento: {
                                        ...prev.horario_funcionamento,
                                        dias_semana: [...dias, dia.value]
                                      }
                                    }));
                                  } else {
                                    setFormData(prev => ({
                                      ...prev,
                                      horario_funcionamento: {
                                        ...prev.horario_funcionamento,
                                        dias_semana: dias.filter(d => d !== dia.value)
                                      }
                                    }));
                                  }
                                }}
                                size="small"
                              />
                            }
                            label={dia.label}
                          />
                        ))}
                      </Box>
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>Cancelar</Button>
          {formData.numeros_transferencia.length > 0 && (
            <Button
              startIcon={<TestIcon />}
              onClick={testStrategy}
              variant="outlined"
            >
              Testar Estratégia
            </Button>
          )}
          <Button onClick={handleSave} variant="contained">
            {editingConfig ? 'Atualizar' : 'Criar'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog de estatísticas */}
      <Dialog open={statsDialogOpen} onClose={() => setStatsDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Estatísticas de Transferência</DialogTitle>
        <DialogContent>
          {selectedConfigStats && (
            <Box>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="h6">{selectedConfigStats.total_transferencias}</Typography>
                  <Typography color="text.secondary">Total de Transferências</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="h6" color="success.main">
                    {selectedConfigStats.taxa_sucesso}%
                  </Typography>
                  <Typography color="text.secondary">Taxa de Sucesso</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="h6" color="success.main">
                    {selectedConfigStats.transferencias_sucesso}
                  </Typography>
                  <Typography color="text.secondary">Sucessos</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="h6" color="error.main">
                    {selectedConfigStats.transferencias_falha}
                  </Typography>
                  <Typography color="text.secondary">Falhas</Typography>
                </Grid>
                {selectedConfigStats.numero_mais_usado && (
                  <Grid item xs={12}>
                    <Typography variant="body1">
                      <strong>Número mais usado:</strong> {selectedConfigStats.numero_mais_usado}
                    </Typography>
                  </Grid>
                )}
                {selectedConfigStats.ultimo_uso && (
                  <Grid item xs={12}>
                    <Typography variant="body2" color="text.secondary">
                      Último uso: {new Date(selectedConfigStats.ultimo_uso).toLocaleString()}
                    </Typography>
                  </Grid>
                )}
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setStatsDialogOpen(false)}>Fechar</Button>
        </DialogActions>
      </Dialog>

      {/* Dialog de teste de estratégia */}
      <Dialog open={testDialogOpen} onClose={() => setTestDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Resultado do Teste de Estratégia</DialogTitle>
        <DialogContent>
          {testResults && (
            <Box>
              <Alert severity="info" sx={{ mb: 2 }}>
                Estratégia: <strong>{getEstrategiaLabel(testResults.estrategia)}</strong> | 
                Testes realizados: <strong>{testResults.quantidade_testes}</strong>
              </Alert>
              
              <Typography variant="h6" sx={{ mb: 2 }}>Distribuição dos Resultados</Typography>
              
              <TableContainer component={Paper}>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Número</TableCell>
                      <TableCell align="right">Vezes Selecionado</TableCell>
                      <TableCell align="right">Percentual</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {Object.entries(testResults.distribuicao_percentual).map(([numero, percentual]) => (
                      <TableRow key={numero}>
                        <TableCell>{numero}</TableCell>
                        <TableCell align="right">{testResults.distribuicao[numero]}</TableCell>
                        <TableCell align="right">{percentual}%</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setTestDialogOpen(false)}>Fechar</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default TransferConfigManager;