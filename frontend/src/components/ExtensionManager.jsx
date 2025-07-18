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
  InputLabel,
  MenuItem,
  Select,
  Switch,
  TextField,
  Typography,
  Alert,
  Chip,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Phone as PhoneIcon,
  Settings as SettingsIcon,
  ExpandMore as ExpandMoreIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  CheckCircle as ActiveIcon,
  Cancel as InactiveIcon,
  Warning as WarningIcon
} from '@mui/icons-material';
import { toast } from 'react-toastify';

const ExtensionManager = () => {
  const [extensions, setExtensions] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingExtension, setEditingExtension] = useState(null);
  const [extensionStats, setExtensionStats] = useState({});

  // Form state
  const [formData, setFormData] = useState({
    numero: '',
    nome: '',
    campanha_id: null,
    ativo: true,
    configuracoes: {
      max_chamadas_simultaneas: 5,
      timeout_chamada: 30,
      retry_attempts: 3,
      retry_interval: 60,
      codec_preferido: 'ulaw',
      dtmf_mode: 'rfc2833',
      nat: 'yes',
      qualify: 'yes',
      canreinvite: 'no',
      context: 'default',
      type: 'friend',
      host: 'dynamic',
      disallow: 'all',
      allow: 'ulaw,alaw,gsm'
    },
    horario_funcionamento: {
      segunda: { ativo: true, inicio: '08:00', fim: '18:00' },
      terca: { ativo: true, inicio: '08:00', fim: '18:00' },
      quarta: { ativo: true, inicio: '08:00', fim: '18:00' },
      quinta: { ativo: true, inicio: '08:00', fim: '18:00' },
      sexta: { ativo: true, inicio: '08:00', fim: '18:00' },
      sabado: { ativo: false, inicio: '08:00', fim: '18:00' },
      domingo: { ativo: false, inicio: '08:00', fim: '18:00' }
    }
  });

  const diasSemana = [
    { key: 'segunda', label: 'Segunda-feira' },
    { key: 'terca', label: 'Terça-feira' },
    { key: 'quarta', label: 'Quarta-feira' },
    { key: 'quinta', label: 'Quinta-feira' },
    { key: 'sexta', label: 'Sexta-feira' },
    { key: 'sabado', label: 'Sábado' },
    { key: 'domingo', label: 'Domingo' }
  ];

  const codecOptions = [
    { value: 'ulaw', label: 'μ-law (G.711)' },
    { value: 'alaw', label: 'A-law (G.711)' },
    { value: 'gsm', label: 'GSM' },
    { value: 'g729', label: 'G.729' },
    { value: 'g722', label: 'G.722' },
    { value: 'opus', label: 'Opus' }
  ];

  const dtmfModes = [
    { value: 'rfc2833', label: 'RFC2833' },
    { value: 'inband', label: 'In-band' },
    { value: 'info', label: 'SIP INFO' },
    { value: 'auto', label: 'Automático' }
  ];

  useEffect(() => {
    loadExtensions();
    loadCampaigns();
    loadExtensionStats();
    
    // Atualizar estatísticas a cada 30 segundos
    const interval = setInterval(() => {
      loadExtensionStats();
    }, 30000);

    return () => clearInterval(interval);
  }, []);

  const loadExtensions = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/extensions');
      if (response.ok) {
        const data = await response.json();
        setExtensions(data);
      } else {
        toast.error('Erro ao carregar extensões');
      }
    } catch (error) {
      console.error('Erro ao carregar extensões:', error);
      toast.error('Erro de conexão');
    } finally {
      setLoading(false);
    }
  };

  const loadCampaigns = async () => {
    try {
      const response = await fetch('/api/campaigns');
      if (response.ok) {
        const data = await response.json();
        setCampaigns(data);
      }
    } catch (error) {
      console.error('Erro ao carregar campanhas:', error);
    }
  };

  const loadExtensionStats = async () => {
    try {
      const response = await fetch('/api/extensions/stats');
      if (response.ok) {
        const data = await response.json();
        setExtensionStats(data);
      }
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
    }
  };

  const handleSave = async () => {
    try {
      const url = editingExtension 
        ? `/api/extensions/${editingExtension.id}`
        : '/api/extensions';
      
      const method = editingExtension ? 'PUT' : 'POST';
      
      const response = await fetch(url, {
        method,
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
      });

      if (response.ok) {
        toast.success(editingExtension ? 'Extensão atualizada!' : 'Extensão criada!');
        setDialogOpen(false);
        resetForm();
        loadExtensions();
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Erro ao salvar extensão');
      }
    } catch (error) {
      console.error('Erro ao salvar extensão:', error);
      toast.error('Erro de conexão');
    }
  };

  const handleEdit = (extension) => {
    setEditingExtension(extension);
    setFormData({
      numero: extension.numero,
      nome: extension.nome,
      campanha_id: extension.campanha_id,
      ativo: extension.ativo,
      configuracoes: extension.configuracoes || formData.configuracoes,
      horario_funcionamento: extension.horario_funcionamento || formData.horario_funcionamento
    });
    setDialogOpen(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Tem certeza que deseja deletar esta extensão?')) {
      return;
    }

    try {
      const response = await fetch(`/api/extensions/${id}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        toast.success('Extensão deletada!');
        loadExtensions();
      } else {
        toast.error('Erro ao deletar extensão');
      }
    } catch (error) {
      console.error('Erro ao deletar extensão:', error);
      toast.error('Erro de conexão');
    }
  };

  const handleToggleStatus = async (id, currentStatus) => {
    try {
      const response = await fetch(`/api/extensions/${id}/toggle`, {
        method: 'POST'
      });

      if (response.ok) {
        toast.success(`Extensão ${currentStatus ? 'desativada' : 'ativada'}!`);
        loadExtensions();
      } else {
        toast.error('Erro ao alterar status');
      }
    } catch (error) {
      console.error('Erro ao alterar status:', error);
      toast.error('Erro de conexão');
    }
  };

  const handleTestExtension = async (id) => {
    try {
      const response = await fetch(`/api/extensions/${id}/test`, {
        method: 'POST'
      });

      if (response.ok) {
        const result = await response.json();
        if (result.success) {
          toast.success('Teste realizado com sucesso!');
        } else {
          toast.warning(`Teste falhou: ${result.message}`);
        }
      } else {
        toast.error('Erro no teste');
      }
    } catch (error) {
      console.error('Erro no teste:', error);
      toast.error('Erro de conexão');
    }
  };

  const resetForm = () => {
    setEditingExtension(null);
    setFormData({
      numero: '',
      nome: '',
      campanha_id: null,
      ativo: true,
      configuracoes: {
        max_chamadas_simultaneas: 5,
        timeout_chamada: 30,
        retry_attempts: 3,
        retry_interval: 60,
        codec_preferido: 'ulaw',
        dtmf_mode: 'rfc2833',
        nat: 'yes',
        qualify: 'yes',
        canreinvite: 'no',
        context: 'default',
        type: 'friend',
        host: 'dynamic',
        disallow: 'all',
        allow: 'ulaw,alaw,gsm'
      },
      horario_funcionamento: {
        segunda: { ativo: true, inicio: '08:00', fim: '18:00' },
        terca: { ativo: true, inicio: '08:00', fim: '18:00' },
        quarta: { ativo: true, inicio: '08:00', fim: '18:00' },
        quinta: { ativo: true, inicio: '08:00', fim: '18:00' },
        sexta: { ativo: true, inicio: '08:00', fim: '18:00' },
        sabado: { ativo: false, inicio: '08:00', fim: '18:00' },
        domingo: { ativo: false, inicio: '08:00', fim: '18:00' }
      }
    });
  };

  const getStatusIcon = (extension) => {
    const stats = extensionStats[extension.id];
    if (!extension.ativo) {
      return <InactiveIcon color="disabled" />;
    }
    if (stats?.online) {
      return <ActiveIcon color="success" />;
    }
    return <WarningIcon color="warning" />;
  };

  const getStatusText = (extension) => {
    const stats = extensionStats[extension.id];
    if (!extension.ativo) return 'Inativo';
    if (stats?.online) return 'Online';
    return 'Offline';
  };

  const getStatusColor = (extension) => {
    const stats = extensionStats[extension.id];
    if (!extension.ativo) return 'default';
    if (stats?.online) return 'success';
    return 'warning';
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Gerenciador de Extensões
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadExtensions}
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
            Nova Extensão
          </Button>
        </Box>
      </Box>

      {/* Estatísticas Gerais */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Total de Extensões
              </Typography>
              <Typography variant="h5">
                {extensions.length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Extensões Ativas
              </Typography>
              <Typography variant="h5" color="success.main">
                {extensions.filter(ext => ext.ativo).length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Online
              </Typography>
              <Typography variant="h5" color="primary.main">
                {Object.values(extensionStats).filter(stat => stat.online).length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="text.secondary" gutterBottom>
                Chamadas Ativas
              </Typography>
              <Typography variant="h5">
                {Object.values(extensionStats).reduce((total, stat) => total + (stat.active_calls || 0), 0)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Lista de Extensões */}
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Extensões Configuradas
          </Typography>
          
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Status</TableCell>
                  <TableCell>Número</TableCell>
                  <TableCell>Nome</TableCell>
                  <TableCell>Campanha</TableCell>
                  <TableCell>Chamadas</TableCell>
                  <TableCell>Última Atividade</TableCell>
                  <TableCell>Ações</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {extensions.map((extension) => {
                  const stats = extensionStats[extension.id] || {};
                  return (
                    <TableRow key={extension.id}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {getStatusIcon(extension)}
                          <Chip
                            label={getStatusText(extension)}
                            color={getStatusColor(extension)}
                            size="small"
                          />
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                          {extension.numero}
                        </Typography>
                      </TableCell>
                      <TableCell>{extension.nome}</TableCell>
                      <TableCell>
                        {extension.campanha_id ? (
                          <Chip
                            label={campaigns.find(c => c.id === extension.campanha_id)?.nome || `ID: ${extension.campanha_id}`}
                            size="small"
                            variant="outlined"
                          />
                        ) : (
                          <Typography color="text.secondary">-</Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {stats.active_calls || 0} / {extension.configuracoes?.max_chamadas_simultaneas || 5}
                        </Typography>
                        {stats.total_calls > 0 && (
                          <Typography variant="caption" color="text.secondary">
                            Total: {stats.total_calls}
                          </Typography>
                        )}
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {stats.last_activity ? new Date(stats.last_activity).toLocaleString() : '-'}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        <Tooltip title="Testar">
                          <IconButton
                            size="small"
                            onClick={() => handleTestExtension(extension.id)}
                          >
                            <PlayIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title={extension.ativo ? 'Desativar' : 'Ativar'}>
                          <IconButton
                            size="small"
                            color={extension.ativo ? 'warning' : 'success'}
                            onClick={() => handleToggleStatus(extension.id, extension.ativo)}
                          >
                            {extension.ativo ? <StopIcon /> : <PlayIcon />}
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Editar">
                          <IconButton
                            size="small"
                            onClick={() => handleEdit(extension)}
                          >
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Deletar">
                          <IconButton
                            size="small"
                            color="error"
                            onClick={() => handleDelete(extension.id)}
                          >
                            <DeleteIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  );
                })}
                {extensions.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={7} align="center">
                      <Typography color="text.secondary">
                        Nenhuma extensão encontrada
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Dialog de Criação/Edição */}
      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {editingExtension ? 'Editar Extensão' : 'Nova Extensão'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {/* Informações Básicas */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Informações Básicas
              </Typography>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Número da Extensão"
                value={formData.numero}
                onChange={(e) => setFormData(prev => ({ ...prev, numero: e.target.value }))}
                required
                helperText="Ex: 1001, 2000, etc."
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Nome/Descrição"
                value={formData.nome}
                onChange={(e) => setFormData(prev => ({ ...prev, nome: e.target.value }))}
                required
              />
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>Campanha</InputLabel>
                <Select
                  value={formData.campanha_id || ''}
                  onChange={(e) => setFormData(prev => ({ ...prev, campanha_id: e.target.value || null }))}
                  label="Campanha"
                >
                  <MenuItem value="">Nenhuma</MenuItem>
                  {campaigns.map((campaign) => (
                    <MenuItem key={campaign.id} value={campaign.id}>
                      {campaign.nome}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            
            <Grid item xs={12} sm={6}>
              <FormControlLabel
                control={
                  <Switch
                    checked={formData.ativo}
                    onChange={(e) => setFormData(prev => ({ ...prev, ativo: e.target.checked }))}
                  />
                }
                label="Extensão Ativa"
              />
            </Grid>

            {/* Configurações Técnicas */}
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="h6">
                    <SettingsIcon sx={{ mr: 1, verticalAlign: 'middle' }} />
                    Configurações Técnicas
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Máx. Chamadas Simultâneas"
                        type="number"
                        value={formData.configuracoes.max_chamadas_simultaneas}
                        onChange={(e) => setFormData(prev => ({
                          ...prev,
                          configuracoes: {
                            ...prev.configuracoes,
                            max_chamadas_simultaneas: parseInt(e.target.value) || 1
                          }
                        }))}
                        inputProps={{ min: 1, max: 50 }}
                      />
                    </Grid>
                    
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Timeout de Chamada (s)"
                        type="number"
                        value={formData.configuracoes.timeout_chamada}
                        onChange={(e) => setFormData(prev => ({
                          ...prev,
                          configuracoes: {
                            ...prev.configuracoes,
                            timeout_chamada: parseInt(e.target.value) || 30
                          }
                        }))}
                        inputProps={{ min: 10, max: 300 }}
                      />
                    </Grid>
                    
                    <Grid item xs={12} sm={6}>
                      <FormControl fullWidth>
                        <InputLabel>Codec Preferido</InputLabel>
                        <Select
                          value={formData.configuracoes.codec_preferido}
                          onChange={(e) => setFormData(prev => ({
                            ...prev,
                            configuracoes: {
                              ...prev.configuracoes,
                              codec_preferido: e.target.value
                            }
                          }))}
                          label="Codec Preferido"
                        >
                          {codecOptions.map((codec) => (
                            <MenuItem key={codec.value} value={codec.value}>
                              {codec.label}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>
                    
                    <Grid item xs={12} sm={6}>
                      <FormControl fullWidth>
                        <InputLabel>Modo DTMF</InputLabel>
                        <Select
                          value={formData.configuracoes.dtmf_mode}
                          onChange={(e) => setFormData(prev => ({
                            ...prev,
                            configuracoes: {
                              ...prev.configuracoes,
                              dtmf_mode: e.target.value
                            }
                          }))}
                          label="Modo DTMF"
                        >
                          {dtmfModes.map((mode) => (
                            <MenuItem key={mode.value} value={mode.value}>
                              {mode.label}
                            </MenuItem>
                          ))}
                        </Select>
                      </FormControl>
                    </Grid>
                    
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Context"
                        value={formData.configuracoes.context}
                        onChange={(e) => setFormData(prev => ({
                          ...prev,
                          configuracoes: {
                            ...prev.configuracoes,
                            context: e.target.value
                          }
                        }))}
                      />
                    </Grid>
                    
                    <Grid item xs={12} sm={6}>
                      <TextField
                        fullWidth
                        label="Codecs Permitidos"
                        value={formData.configuracoes.allow}
                        onChange={(e) => setFormData(prev => ({
                          ...prev,
                          configuracoes: {
                            ...prev.configuracoes,
                            allow: e.target.value
                          }
                        }))}
                        helperText="Ex: ulaw,alaw,gsm"
                      />
                    </Grid>
                  </Grid>
                </AccordionDetails>
              </Accordion>
            </Grid>

            {/* Horário de Funcionamento */}
            <Grid item xs={12}>
              <Accordion>
                <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                  <Typography variant="h6">
                    Horário de Funcionamento
                  </Typography>
                </AccordionSummary>
                <AccordionDetails>
                  <Grid container spacing={2}>
                    {diasSemana.map((dia) => (
                      <Grid item xs={12} key={dia.key}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                          <FormControlLabel
                            control={
                              <Switch
                                checked={formData.horario_funcionamento[dia.key].ativo}
                                onChange={(e) => setFormData(prev => ({
                                  ...prev,
                                  horario_funcionamento: {
                                    ...prev.horario_funcionamento,
                                    [dia.key]: {
                                      ...prev.horario_funcionamento[dia.key],
                                      ativo: e.target.checked
                                    }
                                  }
                                }))}
                              />
                            }
                            label={dia.label}
                            sx={{ minWidth: 150 }}
                          />
                          
                          {formData.horario_funcionamento[dia.key].ativo && (
                            <>
                              <TextField
                                type="time"
                                label="Início"
                                value={formData.horario_funcionamento[dia.key].inicio}
                                onChange={(e) => setFormData(prev => ({
                                  ...prev,
                                  horario_funcionamento: {
                                    ...prev.horario_funcionamento,
                                    [dia.key]: {
                                      ...prev.horario_funcionamento[dia.key],
                                      inicio: e.target.value
                                    }
                                  }
                                }))}
                                InputLabelProps={{ shrink: true }}
                                size="small"
                              />
                              
                              <TextField
                                type="time"
                                label="Fim"
                                value={formData.horario_funcionamento[dia.key].fim}
                                onChange={(e) => setFormData(prev => ({
                                  ...prev,
                                  horario_funcionamento: {
                                    ...prev.horario_funcionamento,
                                    [dia.key]: {
                                      ...prev.horario_funcionamento[dia.key],
                                      fim: e.target.value
                                    }
                                  }
                                }))}
                                InputLabelProps={{ shrink: true }}
                                size="small"
                              />
                            </>
                          )}
                        </Box>
                      </Grid>
                    ))}
                  </Grid>
                </AccordionDetails>
              </Accordion>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)}>
            Cancelar
          </Button>
          <Button
            onClick={handleSave}
            variant="contained"
            disabled={!formData.numero || !formData.nome}
          >
            {editingExtension ? 'Atualizar' : 'Criar'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ExtensionManager;