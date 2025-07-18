import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Grid,
  Card,
  CardContent,
  CardActions,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  LinearProgress,
  Alert,
  IconButton,
  Divider,
  Tabs,
  Tab,
  Badge,
  Tooltip
} from '@mui/material';
import {
  PictureAsPdf as PdfIcon,
  TableChart as CsvIcon,
  Download as DownloadIcon,
  Delete as DeleteIcon,
  Assessment as ReportIcon,
  DateRange as DateRangeIcon,
  Campaign as CampaignIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
  Phone as PhoneIcon,
  CallMade as CallMadeIcon,
  Group as GroupIcon,
  Block as BlockIcon,
  TrendingUp as TrendingUpIcon,
  Warning as WarningIcon
} from '@mui/icons-material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { ptBR } from 'date-fns/locale';
import api from '../config/api';

const ReportsManager = () => {
  const [reports, setReports] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [openGenerateDialog, setOpenGenerateDialog] = useState(false);
  const [openStatsDialog, setOpenStatsDialog] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  
  const [generateForm, setGenerateForm] = useState({
    report_type: 'campaign',
    format: 'pdf',
    campaign_id: '',
    start_date: null,
    end_date: null
  });

  const [dateRange, setDateRange] = useState({
    start_date: new Date(new Date().setDate(new Date().getDate() - 7)),
    end_date: new Date()
  });

  const [filters, setFilters] = useState({
    campaign: '',
    agent: '',
    status: '',
    cli_type: ''
  });

  const [detailedReports, setDetailedReports] = useState({
    campaigns: [],
    cli_usage: [],
    transfers: [],
    calls: [],
    agents: [],
    dnc: []
  });

  const [summary, setSummary] = useState({
    total_calls: 0,
    connected_calls: 0,
    transferred_calls: 0,
    eliminated_calls: 0,
    total_talk_time: 0,
    cli_used: 0,
    active_campaigns: 0
  });

  const [availableCampaigns, setAvailableCampaigns] = useState([]);
  const [availableAgents, setAvailableAgents] = useState([]);

  useEffect(() => {
    loadReports();
    loadStats();
    loadAvailableFilters();
    loadDetailedReports();
  }, []);

  useEffect(() => {
    loadDetailedReports();
  }, [dateRange, filters]);

  const loadReports = async () => {
    try {
      setLoading(true);
      const response = await api.get('/reports/list');
      if (response.data.success) {
        setReports(response.data.reports);
      }
    } catch (error) {
      setError('Erro ao carregar relatórios');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    try {
      const response = await api.get('/reports/campaigns/stats');
      if (response.data.success) {
        setStats(response.data.data);
      }
    } catch (error) {
    }
  };

  const loadAvailableFilters = async () => {
    try {
      // Carregar campanhas disponíveis
      const campaignsResponse = await api.get('/campaigns');
      if (campaignsResponse.data.success) {
        setAvailableCampaigns(campaignsResponse.data.campaigns);
      }

      // Carregar agentes disponíveis
      const agentsResponse = await api.get('/agents');
      if (agentsResponse.data.success) {
        setAvailableAgents(agentsResponse.data.agents);
      }
    } catch (error) {
      console.error('Erro ao carregar filtros:', error);
    }
  };

  const loadDetailedReports = async () => {
    try {
      setLoading(true);
      const params = new URLSearchParams({
        start_date: dateRange.start_date.toISOString().split('T')[0],
        end_date: dateRange.end_date.toISOString().split('T')[0],
        ...filters
      });

      const response = await api.get(`/reports/detailed?${params}`);
      if (response.data.success) {
        setDetailedReports(response.data.reports);
        setSummary(response.data.summary);
      }
    } catch (error) {
      console.error('Erro ao carregar relatórios detalhados:', error);
      setError('Erro ao carregar relatórios detalhados');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateReport = async () => {
    try {
      setGenerating(true);
      
      const params = {
        report_type: generateForm.report_type,
        campaign_id: generateForm.campaign_id || null,
        start_date: generateForm.start_date?.toISOString().split('T')[0] || null,
        end_date: generateForm.end_date?.toISOString().split('T')[0] || null
      };

      const endpoint = generateForm.format === 'pdf' ? '/reports/generate/pdf' : '/reports/generate/csv';
      const response = await api.post(endpoint, null, { params });

      if (response.data.success) {
        setSuccess(`Relatório ${generateForm.format.toUpperCase()} gerado com sucesso!`);
        setOpenGenerateDialog(false);
        setGenerateForm({
          report_type: 'campaign',
          format: 'pdf',
          campaign_id: '',
          start_date: null,
          end_date: null
        });
        loadReports();
      } else {
        setError(response.data.message || 'Erro ao gerar relatório');
      }

    } catch (error) {
      setError(error.response?.data?.detail || 'Erro ao gerar relatório');
    } finally {
      setGenerating(false);
    }
  };

  const handleDownloadReport = async (report) => {
    try {
      const response = await api.get(`/reports/download/${report.filename}`, {
        responseType: 'blob'
      });

      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = report.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

    } catch (error) {
      setError('Erro ao baixar relatório');
    }
  };

  const handleDeleteReport = async (report) => {
    if (!window.confirm('Tem certeza que deseja deletar este relatório?')) {
      return;
    }

    try {
      await api.delete(`/reports/delete/${report.filename}`);
      setSuccess('Relatório deletado com sucesso!');
      loadReports();
    } catch (error) {
      setError('Erro ao deletar relatório');
    }
  };

  const exportDetailedReport = async (type, format = 'csv') => {
    try {
      const params = new URLSearchParams({
        type: type,
        format: format,
        start_date: dateRange.start_date.toISOString().split('T')[0],
        end_date: dateRange.end_date.toISOString().split('T')[0],
        ...filters
      });

      const response = await api.get(`/reports/export?${params}`, {
        responseType: 'blob'
      });

      const blob = new Blob([response.data]);
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `relatorio_${type}_${dateRange.start_date.toISOString().split('T')[0]}_${dateRange.end_date.toISOString().split('T')[0]}.${format}`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
      setSuccess('Relatório exportado com sucesso!');
    } catch (error) {
      console.error('Erro ao exportar relatório:', error);
      setError('Erro ao exportar relatório');
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('es-AR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getReportIcon = (type) => {
    return type === 'PDF' ? <PdfIcon color="error" /> : <CsvIcon color="success" />;
  };

  const getReportColor = (type) => {
    return type === 'PDF' ? 'error' : 'success';
  };

  const formatDuration = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    return `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  const formatPercentage = (value, total) => {
    if (total === 0) return '0%';
    return `${((value / total) * 100).toFixed(1)}%`;
  };

  const getStatusColor = (status) => {
    const colors = {
      'conectada': 'success',
      'transferida': 'info',
      'eliminada': 'error',
      'ocupado': 'warning',
      'nao_atende': 'default',
      'secretaria': 'secondary'
    };
    return colors[status] || 'default';
  };

  const getCliTypeColor = (type) => {
    const colors = {
      'MXN': 'success',
      'ALEATORIO': 'info',
      'ALEATORIO1': 'primary',
      'DID': 'secondary',
      'DID1': 'warning'
    };
    return colors[type] || 'default';
  };

  const tabs = [
    { label: 'Relatórios Gerados', icon: <ReportIcon /> },
    { label: 'Campanhas', icon: <CampaignIcon /> },
    { label: 'Uso de CLI', icon: <PhoneIcon /> },
    { label: 'Transferências', icon: <CallMadeIcon /> },
    { label: 'Chamadas', icon: <TrendingUpIcon /> },
    { label: 'Agentes', icon: <GroupIcon /> },
    { label: 'Lista DNC', icon: <BlockIcon /> }
  ];

  return (
    <LocalizationProvider dateAdapter={AdapterDateFns} adapterLocale={ptBR}>
      <Box sx={{ p: 3 }}>
        {/* Header */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            Relatórios
          </Typography>
          
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setOpenGenerateDialog(true)}
            >
              Gerar Relatório
            </Button>
            
            <Button
              variant="outlined"
              startIcon={<ReportIcon />}
              onClick={() => {
                loadStats();
                setOpenStatsDialog(true);
              }}
            >
              Estatísticas
            </Button>
            
            <Button
              variant="outlined"
              startIcon={<RefreshIcon />}
              onClick={loadReports}
            >
              Atualizar
            </Button>
          </Box>
        </Box>

        {/* Alerts */}
        {error && (
          <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError('')}>
            {error}
          </Alert>
        )}
        
        {success && (
          <Alert severity="success" sx={{ mb: 2 }} onClose={() => setSuccess('')}>
            {success}
          </Alert>
        )}

        {/* Filtros */}
        {activeTab > 0 && (
          <Paper sx={{ p: 2, mb: 3 }}>
            <Typography variant="h6" gutterBottom>
              Filtros
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={3}>
                <DatePicker
                  label="Data Início"
                  value={dateRange.start_date}
                  onChange={(date) => setDateRange(prev => ({ ...prev, start_date: date }))}
                  renderInput={(params) => <TextField {...params} fullWidth size="small" />}
                />
              </Grid>
              <Grid item xs={12} md={3}>
                <DatePicker
                  label="Data Fim"
                  value={dateRange.end_date}
                  onChange={(date) => setDateRange(prev => ({ ...prev, end_date: date }))}
                  renderInput={(params) => <TextField {...params} fullWidth size="small" />}
                />
              </Grid>
              <Grid item xs={12} md={2}>
                <FormControl fullWidth size="small">
                  <InputLabel>Campanha</InputLabel>
                  <Select
                    value={filters.campaign}
                    onChange={(e) => setFilters(prev => ({ ...prev, campaign: e.target.value }))}
                  >
                    <MenuItem value="">Todas</MenuItem>
                    {availableCampaigns.map(campaign => (
                      <MenuItem key={campaign.id} value={campaign.id}>{campaign.name}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={2}>
                <FormControl fullWidth size="small">
                  <InputLabel>Agente</InputLabel>
                  <Select
                    value={filters.agent}
                    onChange={(e) => setFilters(prev => ({ ...prev, agent: e.target.value }))}
                  >
                    <MenuItem value="">Todos</MenuItem>
                    {availableAgents.map(agent => (
                      <MenuItem key={agent.id} value={agent.id}>{agent.name}</MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={2}>
                <Button
                  variant="contained"
                  onClick={loadDetailedReports}
                  fullWidth
                  startIcon={<RefreshIcon />}
                >
                  Atualizar
                </Button>
              </Grid>
            </Grid>
          </Paper>
        )}

        {/* Estatísticas Resumidas */}
        {activeTab > 0 && (
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid item xs={12} md={12/7}>
              <Card>
                <CardContent>
                  <Typography variant="h4" color="primary">
                    {summary.total_calls?.toLocaleString() || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total de Chamadas
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={12/7}>
              <Card>
                <CardContent>
                  <Typography variant="h4" color="success.main">
                    {summary.connected_calls?.toLocaleString() || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Conectadas
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {formatPercentage(summary.connected_calls, summary.total_calls)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={12/7}>
              <Card>
                <CardContent>
                  <Typography variant="h4" color="info.main">
                    {summary.transferred_calls?.toLocaleString() || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Transferidas
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {formatPercentage(summary.transferred_calls, summary.total_calls)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={12/7}>
              <Card>
                <CardContent>
                  <Typography variant="h4" color="error.main">
                    {summary.eliminated_calls?.toLocaleString() || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Eliminadas
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {formatPercentage(summary.eliminated_calls, summary.total_calls)}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={12/7}>
              <Card>
                <CardContent>
                  <Typography variant="h4" color="secondary.main">
                    {formatDuration(summary.total_talk_time || 0)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Tempo Total
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={12/7}>
              <Card>
                <CardContent>
                  <Typography variant="h4" color="warning.main">
                    {summary.cli_used?.toLocaleString() || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    CLIs Utilizados
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={12/7}>
              <Card>
                <CardContent>
                  <Typography variant="h4" color="primary.main">
                    {summary.active_campaigns?.toLocaleString() || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Campanhas Ativas
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        )}

        {/* Tabs */}
        <Paper sx={{ mb: 2 }}>
          <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)} variant="scrollable" scrollButtons="auto">
            {tabs.map((tab, index) => (
              <Tab key={index} label={tab.label} icon={tab.icon} />
            ))}
          </Tabs>
        </Paper>

        {/* Conteúdo das Tabs */}
        <Paper sx={{ p: 2 }}>
          {activeTab === 0 && (
            <Box>
          <Typography variant="h6" gutterBottom>
            Relatórios Gerados ({reports.length})
          </Typography>
          
          {loading && <LinearProgress sx={{ mb: 2 }} />}
          
          {reports.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <ReportIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
              <Typography variant="h6" color="text.secondary">
                Nenhum relatório encontrado
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Gere seu primeiro relatório para começar
              </Typography>
            </Box>
          ) : (
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Tipo</TableCell>
                    <TableCell>Nome do Arquivo</TableCell>
                    <TableCell>Tamanho</TableCell>
                    <TableCell>Criado em</TableCell>
                    <TableCell>Formato</TableCell>
                    <TableCell>Ações</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {reports.map((report, index) => (
                    <TableRow key={index}>
                      <TableCell>
                        {getReportIcon(report.type)}
                      </TableCell>
                      <TableCell>
                        <Typography variant="body2">
                          {report.filename}
                        </Typography>
                      </TableCell>
                      <TableCell>
                        {formatFileSize(report.size)}
                      </TableCell>
                      <TableCell>
                        {formatDate(report.created)}
                      </TableCell>
                      <TableCell>
                        <Chip 
                          label={report.type}
                          color={getReportColor(report.type)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <IconButton
                          onClick={() => handleDownloadReport(report)}
                          color="primary"
                          title="Download"
                        >
                          <DownloadIcon />
                        </IconButton>
                        <IconButton
                          onClick={() => handleDeleteReport(report)}
                          color="error"
                          title="Deletar"
                        >
                          <DeleteIcon />
                        </IconButton>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          )}
            </Box>
          )}

          {/* Aba Campanhas */}
          {activeTab === 1 && (
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Relatório de Campanhas
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<DownloadIcon />}
                  onClick={() => exportDetailedReport('campaigns')}
                >
                  Exportar CSV
                </Button>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Campanha</TableCell>
                      <TableCell align="right">Total Chamadas</TableCell>
                      <TableCell align="right">Conectadas</TableCell>
                      <TableCell align="right">Transferidas</TableCell>
                      <TableCell align="right">Eliminadas</TableCell>
                      <TableCell align="right">Taxa Sucesso</TableCell>
                      <TableCell align="right">Tempo Total</TableCell>
                      <TableCell align="right">CLIs Usados</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {detailedReports.campaigns?.map((campaign) => (
                      <TableRow key={campaign.id}>
                        <TableCell>
                          <Box>
                            <Typography variant="body2" fontWeight="bold">
                              {campaign.name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {campaign.description}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell align="right">{campaign.total_calls?.toLocaleString()}</TableCell>
                        <TableCell align="right">
                          <Chip
                            label={campaign.connected_calls?.toLocaleString()}
                            color="success"
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="right">
                          <Chip
                            label={campaign.transferred_calls?.toLocaleString()}
                            color="info"
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="right">
                          <Chip
                            label={campaign.eliminated_calls?.toLocaleString()}
                            color="error"
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="right">
                          <Typography variant="body2" color={campaign.success_rate > 50 ? 'success.main' : 'error.main'}>
                            {campaign.success_rate?.toFixed(1)}%
                          </Typography>
                        </TableCell>
                        <TableCell align="right">{formatDuration(campaign.total_talk_time)}</TableCell>
                        <TableCell align="right">{campaign.cli_used?.toLocaleString()}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {/* Aba Uso de CLI */}
          {activeTab === 2 && (
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Relatório de Uso de CLI
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<DownloadIcon />}
                  onClick={() => exportDetailedReport('cli_usage')}
                >
                  Exportar CSV
                </Button>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>CLI</TableCell>
                      <TableCell>Tipo</TableCell>
                      <TableCell align="right">Uso Hoje</TableCell>
                      <TableCell align="right">Limite Diário</TableCell>
                      <TableCell align="right">Total Chamadas</TableCell>
                      <TableCell align="right">Conectadas</TableCell>
                      <TableCell align="right">Status</TableCell>
                      <TableCell align="center">Ações</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {detailedReports.cli_usage?.map((cli) => (
                      <TableRow key={cli.cli}>
                        <TableCell>
                          <Typography variant="body2" fontWeight="bold">
                            {cli.cli}
                          </Typography>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={cli.type}
                            color={getCliTypeColor(cli.type)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="right">
                          <Box>
                            <Typography variant="body2">
                              {cli.daily_usage?.toLocaleString()}
                            </Typography>
                            {cli.daily_limit && (
                              <LinearProgress
                                variant="determinate"
                                value={(cli.daily_usage / cli.daily_limit) * 100}
                                color={cli.daily_usage >= cli.daily_limit ? 'error' : 'primary'}
                                sx={{ mt: 0.5 }}
                              />
                            )}
                          </Box>
                        </TableCell>
                        <TableCell align="right">{cli.daily_limit?.toLocaleString() || 'Ilimitado'}</TableCell>
                        <TableCell align="right">{cli.total_calls?.toLocaleString()}</TableCell>
                        <TableCell align="right">{cli.connected_calls?.toLocaleString()}</TableCell>
                        <TableCell align="right">
                          <Chip
                            label={cli.status}
                            color={cli.status === 'ativo' ? 'success' : 'error'}
                            size="small"
                          />
                        </TableCell>
                        <TableCell align="center">
                          {cli.daily_usage >= cli.daily_limit && (
                            <Tooltip title="CLI atingiu limite diário">
                              <IconButton color="warning" size="small">
                                <WarningIcon />
                              </IconButton>
                            </Tooltip>
                          )}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {/* Aba Transferências */}
          {activeTab === 3 && (
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Relatório de Transferências
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<DownloadIcon />}
                  onClick={() => exportDetailedReport('transfers')}
                >
                  Exportar CSV
                </Button>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Número</TableCell>
                      <TableCell>Campanha</TableCell>
                      <TableCell>CLI Usado</TableCell>
                      <TableCell>Áudio</TableCell>
                      <TableCell>Data/Hora</TableCell>
                      <TableCell align="right">Duração</TableCell>
                      <TableCell>Agente</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {detailedReports.transfers?.map((transfer, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Typography variant="body2" fontWeight="bold">
                            {transfer.phone_number}
                          </Typography>
                        </TableCell>
                        <TableCell>{transfer.campaign_name}</TableCell>
                        <TableCell>{transfer.cli_used}</TableCell>
                        <TableCell>{transfer.audio_name}</TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {new Date(transfer.transfer_time).toLocaleString()}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">{formatDuration(transfer.call_duration)}</TableCell>
                        <TableCell>{transfer.agent_name || 'N/A'}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {/* Aba Chamadas */}
          {activeTab === 4 && (
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Relatório de Chamadas
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<DownloadIcon />}
                  onClick={() => exportDetailedReport('calls')}
                >
                  Exportar CSV
                </Button>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Número</TableCell>
                      <TableCell>CLI</TableCell>
                      <TableCell>Campanha</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Data/Hora</TableCell>
                      <TableCell align="right">Duração</TableCell>
                      <TableCell align="right">Tentativas</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {detailedReports.calls?.map((call, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Typography variant="body2" fontWeight="bold">
                            {call.phone_number}
                          </Typography>
                        </TableCell>
                        <TableCell>{call.cli_used}</TableCell>
                        <TableCell>{call.campaign_name}</TableCell>
                        <TableCell>
                          <Chip
                            label={call.status}
                            color={getStatusColor(call.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {new Date(call.call_time).toLocaleString()}
                          </Typography>
                        </TableCell>
                        <TableCell align="right">{formatDuration(call.duration)}</TableCell>
                        <TableCell align="right">{call.attempts}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {/* Aba Agentes */}
          {activeTab === 5 && (
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Relatório de Agentes
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<DownloadIcon />}
                  onClick={() => exportDetailedReport('agents')}
                >
                  Exportar CSV
                </Button>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Agente</TableCell>
                      <TableCell align="right">Chamadas Recebidas</TableCell>
                      <TableCell align="right">Tempo Total</TableCell>
                      <TableCell align="right">Tempo Médio</TableCell>
                      <TableCell align="right">Transferências</TableCell>
                      <TableCell>Status</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {detailedReports.agents?.map((agent) => (
                      <TableRow key={agent.id}>
                        <TableCell>
                          <Box>
                            <Typography variant="body2" fontWeight="bold">
                              {agent.name}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {agent.extension}
                            </Typography>
                          </Box>
                        </TableCell>
                        <TableCell align="right">{agent.calls_received?.toLocaleString()}</TableCell>
                        <TableCell align="right">{formatDuration(agent.total_talk_time)}</TableCell>
                        <TableCell align="right">{formatDuration(agent.average_talk_time)}</TableCell>
                        <TableCell align="right">{agent.transfers?.toLocaleString()}</TableCell>
                        <TableCell>
                          <Chip
                            label={agent.status}
                            color={agent.status === 'online' ? 'success' : 'default'}
                            size="small"
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}

          {/* Aba Lista DNC */}
          {activeTab === 6 && (
            <Box>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  Relatório de Lista DNC
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<DownloadIcon />}
                  onClick={() => exportDetailedReport('dnc')}
                >
                  Exportar CSV
                </Button>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Número</TableCell>
                      <TableCell>Campanha</TableCell>
                      <TableCell>Data Eliminação</TableCell>
                      <TableCell>Motivo</TableCell>
                      <TableCell>CLI Usado</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {detailedReports.dnc?.map((dnc, index) => (
                      <TableRow key={index}>
                        <TableCell>
                          <Typography variant="body2" fontWeight="bold">
                            {dnc.phone_number}
                          </Typography>
                        </TableCell>
                        <TableCell>{dnc.campaign_name}</TableCell>
                        <TableCell>
                          <Typography variant="body2">
                            {new Date(dnc.elimination_date).toLocaleString()}
                          </Typography>
                        </TableCell>
                        <TableCell>{dnc.reason}</TableCell>
                        <TableCell>{dnc.cli_used}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Box>
          )}
        </Paper>

        {/* Dialog de Geração */}
        <Dialog open={openGenerateDialog} onClose={() => setOpenGenerateDialog(false)} maxWidth="md" fullWidth>
          <DialogTitle>Gerar Novo Relatório</DialogTitle>
          <DialogContent>
            <Box sx={{ pt: 2 }}>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Tipo de Relatório</InputLabel>
                    <Select
                      value={generateForm.report_type}
                      onChange={(e) => setGenerateForm({...generateForm, report_type: e.target.value})}
                    >
                      <MenuItem value="campaign">Performance de Campanhas</MenuItem>
                      <MenuItem value="daily">Atividade Diária</MenuItem>
                      <MenuItem value="agents">Performance de Agentes</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <FormControl fullWidth>
                    <InputLabel>Formato</InputLabel>
                    <Select
                      value={generateForm.format}
                      onChange={(e) => setGenerateForm({...generateForm, format: e.target.value})}
                    >
                      <MenuItem value="pdf">PDF</MenuItem>
                      <MenuItem value="csv">CSV</MenuItem>
                    </Select>
                  </FormControl>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <DatePicker
                    label="Data Início"
                    value={generateForm.start_date}
                    onChange={(date) => setGenerateForm({...generateForm, start_date: date})}
                    renderInput={(params) => <TextField {...params} fullWidth />}
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <DatePicker
                    label="Data Fim"
                    value={generateForm.end_date}
                    onChange={(date) => setGenerateForm({...generateForm, end_date: date})}
                    renderInput={(params) => <TextField {...params} fullWidth />}
                  />
                </Grid>
              </Grid>
            </Box>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenGenerateDialog(false)}>Cancelar</Button>
            <Button onClick={handleGenerateReport} variant="contained" disabled={generating}>
              {generating ? 'Gerando...' : 'Gerar Relatório'}
            </Button>
          </DialogActions>
        </Dialog>

        {/* Dialog de Estatísticas */}
        <Dialog open={openStatsDialog} onClose={() => setOpenStatsDialog(false)} maxWidth="lg" fullWidth>
          <DialogTitle>Estatísticas Detalhadas</DialogTitle>
          <DialogContent>
            <Grid container spacing={3} sx={{ pt: 2 }}>
              {/* Campanhas */}
              {stats.campaigns && (
                <Grid item xs={12}>
                  <Typography variant="h6" gutterBottom>
                    Performance por Campanha
                  </Typography>
                  <TableContainer>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Campanha</TableCell>
                          <TableCell>Chamadas</TableCell>
                          <TableCell>Atendidas</TableCell>
                          <TableCell>Transferidas</TableCell>
                          <TableCell>Taxa Sucesso</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {stats.campaigns.map((campaign, index) => (
                          <TableRow key={index}>
                            <TableCell>{campaign.name}</TableCell>
                            <TableCell>{campaign.total_calls.toLocaleString()}</TableCell>
                            <TableCell>{campaign.answered.toLocaleString()}</TableCell>
                            <TableCell>{campaign.transferred.toLocaleString()}</TableCell>
                            <TableCell>{campaign.success_rate.toFixed(1)}%</TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                </Grid>
              )}
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenStatsDialog(false)}>Fechar</Button>
          </DialogActions>
        </Dialog>
      </Box>
    </LocalizationProvider>
  );
};

export default ReportsManager;