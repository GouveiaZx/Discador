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
  Divider
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
  Add as AddIcon
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
  
  const [generateForm, setGenerateForm] = useState({
    report_type: 'campaign',
    format: 'pdf',
    campaign_id: '',
    start_date: null,
    end_date: null
  });

  useEffect(() => {
    loadReports();
    loadStats();
  }, []);

  const loadReports = async () => {
    try {
      setLoading(true);
      const response = await api.get('/reports/list');
      if (response.data.success) {
        setReports(response.data.reports);
      }
    } catch (error) {
      setError('Erro ao carregar relatórios');
      console.error('Erro ao carregar relatórios:', error);
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
      console.error('Erro ao carregar estatísticas:', error);
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
      console.error('Erro ao baixar relatório:', error);
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
      console.error('Erro ao deletar relatório:', error);
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
    return new Date(dateString).toLocaleDateString('pt-BR', {
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

        {/* Estatísticas Resumidas */}
        <Grid container spacing={3} sx={{ mb: 3 }}>
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h4" color="primary">
                  {stats.total_calls?.toLocaleString() || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Total de Chamadas
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h4" color="secondary">
                  {stats.answered_calls?.toLocaleString() || 0}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Chamadas Atendidas
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h4" color="success.main">
                  {stats.success_rate?.toFixed(1) || 0}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Taxa de Sucesso
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          
          <Grid item xs={12} md={3}>
            <Card>
              <CardContent>
                <Typography variant="h4" color="warning.main">
                  {stats.transfer_rate?.toFixed(1) || 0}%
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Taxa de Transferência
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Lista de Relatórios */}
        <Paper sx={{ p: 2 }}>
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