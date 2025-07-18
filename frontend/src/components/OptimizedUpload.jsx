import React, { useState, useEffect, useCallback } from 'react';
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
  LinearProgress,
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
  Divider
} from '@mui/material';
import {
  CloudUpload as UploadIcon,
  Refresh as RefreshIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
  Info as InfoIcon,
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Schedule as PendingIcon,
  PlayArrow as ProcessingIcon
} from '@mui/icons-material';
import { toast } from 'react-toastify';
import { useDropzone } from 'react-dropzone';

const OptimizedUpload = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploadDialogOpen, setUploadDialogOpen] = useState(false);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState(null);
  const [performanceStats, setPerformanceStats] = useState(null);

  // Upload form state
  const [uploadConfig, setUploadConfig] = useState({
    country: 'BR',
    batch_size: 1000,
    validate_numbers: true,
    clean_numbers: true,
    detect_format: true,
    skip_duplicates: true,
    campaign_id: null
  });

  const [selectedFile, setSelectedFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [isUploading, setIsUploading] = useState(false);

  const countries = [
    { code: 'BR', name: 'Brasil', flag: '🇧🇷' },
    { code: 'AR', name: 'Argentina', flag: '🇦🇷' },
    { code: 'CL', name: 'Chile', flag: '🇨🇱' },
    { code: 'CO', name: 'Colômbia', flag: '🇨🇴' },
    { code: 'MX', name: 'México', flag: '🇲🇽' },
    { code: 'US', name: 'Estados Unidos', flag: '🇺🇸' }
  ];

  const statusIcons = {
    pending: <PendingIcon color="warning" />,
    processing: <ProcessingIcon color="info" />,
    completed: <SuccessIcon color="success" />,
    failed: <ErrorIcon color="error" />,
    cancelled: <ErrorIcon color="disabled" />
  };

  const statusColors = {
    pending: 'warning',
    processing: 'info',
    completed: 'success',
    failed: 'error',
    cancelled: 'default'
  };

  const statusLabels = {
    pending: 'Pendente',
    processing: 'Processando',
    completed: 'Concluído',
    failed: 'Falhou',
    cancelled: 'Cancelado'
  };

  useEffect(() => {
    loadTasks();
    loadPerformanceStats();
    
    // Atualizar tarefas a cada 5 segundos
    const interval = setInterval(() => {
      loadTasks();
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const loadTasks = async () => {
    try {
      const response = await fetch('/api/optimized-upload/tasks');
      if (response.ok) {
        const data = await response.json();
        setTasks(data);
      }
    } catch (error) {
      console.error('Erro ao carregar tarefas:', error);
    }
  };

  const loadPerformanceStats = async () => {
    try {
      const response = await fetch('/api/optimized-upload/performance-stats');
      if (response.ok) {
        const data = await response.json();
        setPerformanceStats(data);
      }
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
    }
  };

  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      setSelectedFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv'],
      'text/plain': ['.txt'],
      'application/vnd.ms-excel': ['.xls'],
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx']
    },
    multiple: false,
    maxSize: 100 * 1024 * 1024 // 100MB
  });

  const handleUpload = async () => {
    if (!selectedFile) {
      toast.error('Selecione um arquivo para upload');
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('config', JSON.stringify(uploadConfig));

      const response = await fetch('/api/optimized-upload/upload-large-list', {
        method: 'POST',
        body: formData
      });

      if (response.ok) {
        const result = await response.json();
        toast.success('Upload iniciado com sucesso!');
        setUploadDialogOpen(false);
        setSelectedFile(null);
        loadTasks();
        
        // Monitorar progresso
        monitorTask(result.task_id);
      } else {
        const error = await response.json();
        toast.error(error.detail || 'Erro no upload');
      }
    } catch (error) {
      console.error('Erro no upload:', error);
      toast.error('Erro de conexão');
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  };

  const monitorTask = async (taskId) => {
    const checkStatus = async () => {
      try {
        const response = await fetch(`/api/optimized-upload/status/${taskId}`);
        if (response.ok) {
          const status = await response.json();
          
          if (status.status === 'processing') {
            setUploadProgress(status.progress_percentage || 0);
            setTimeout(checkStatus, 2000);
          } else if (status.status === 'completed') {
            setUploadProgress(100);
            toast.success('Upload concluído com sucesso!');
            loadTasks();
          } else if (status.status === 'failed') {
            toast.error(`Upload falhou: ${status.error_message}`);
            loadTasks();
          }
        }
      } catch (error) {
        console.error('Erro ao monitorar tarefa:', error);
      }
    };

    checkStatus();
  };

  const handleTaskDetails = async (task) => {
    setSelectedTask(task);
    setDetailsDialogOpen(true);
  };

  const handleDeleteTask = async (taskId) => {
    if (!window.confirm('Tem certeza que deseja deletar esta tarefa?')) {
      return;
    }

    try {
      const response = await fetch(`/api/optimized-upload/tasks/${taskId}`, {
        method: 'DELETE'
      });

      if (response.ok) {
        toast.success('Tarefa deletada!');
        loadTasks();
      } else {
        toast.error('Erro ao deletar tarefa');
      }
    } catch (error) {
      console.error('Erro ao deletar tarefa:', error);
      toast.error('Erro de conexão');
    }
  };

  const handleCleanupOldTasks = async () => {
    try {
      const response = await fetch('/api/optimized-upload/cleanup-old-tasks', {
        method: 'POST'
      });

      if (response.ok) {
        const result = await response.json();
        toast.success(`${result.deleted_count} tarefas antigas removidas`);
        loadTasks();
      } else {
        toast.error('Erro na limpeza');
      }
    } catch (error) {
      console.error('Erro na limpeza:', error);
      toast.error('Erro de conexão');
    }
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDuration = (seconds) => {
    if (!seconds) return '-';
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `${hours}h ${minutes}m ${secs}s`;
    } else if (minutes > 0) {
      return `${minutes}m ${secs}s`;
    } else {
      return `${secs}s`;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Upload Otimizado de Listas
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={loadTasks}
            sx={{ mr: 2 }}
          >
            Atualizar
          </Button>
          <Button
            variant="outlined"
            onClick={handleCleanupOldTasks}
            sx={{ mr: 2 }}
          >
            Limpar Antigas
          </Button>
          <Button
            variant="contained"
            startIcon={<UploadIcon />}
            onClick={() => setUploadDialogOpen(true)}
          >
            Novo Upload
          </Button>
        </Box>
      </Box>

      {/* Estatísticas de Performance */}
      {performanceStats && (
        <Grid container spacing={2} sx={{ mb: 3 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Total de Uploads
                </Typography>
                <Typography variant="h5">
                  {performanceStats.total_uploads}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Taxa de Sucesso
                </Typography>
                <Typography variant="h5" color="success.main">
                  {performanceStats.success_rate}%
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Registros Processados
                </Typography>
                <Typography variant="h5">
                  {performanceStats.total_records?.toLocaleString()}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Card>
              <CardContent>
                <Typography color="text.secondary" gutterBottom>
                  Tempo Médio
                </Typography>
                <Typography variant="h5">
                  {formatDuration(performanceStats.avg_processing_time)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Lista de Tarefas */}
      <Card>
        <CardContent>
          <Typography variant="h6" sx={{ mb: 2 }}>
            Tarefas de Upload
          </Typography>
          
          {loading && <LinearProgress sx={{ mb: 2 }} />}
          
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Status</TableCell>
                  <TableCell>Arquivo</TableCell>
                  <TableCell>Tamanho</TableCell>
                  <TableCell>Progresso</TableCell>
                  <TableCell>Registros</TableCell>
                  <TableCell>Criado em</TableCell>
                  <TableCell>Ações</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {tasks.map((task) => (
                  <TableRow key={task.id}>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {statusIcons[task.status]}
                        <Chip
                          label={statusLabels[task.status]}
                          color={statusColors[task.status]}
                          size="small"
                        />
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2" sx={{ fontWeight: 'medium' }}>
                        {task.original_filename}
                      </Typography>
                      {task.detected_format && (
                        <Typography variant="caption" color="text.secondary">
                          {task.detected_format.separator} | {task.detected_format.encoding}
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>{formatFileSize(task.file_size)}</TableCell>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={task.progress_percentage || 0}
                          sx={{ width: 60 }}
                        />
                        <Typography variant="caption">
                          {Math.round(task.progress_percentage || 0)}%
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {task.processed_records}/{task.total_records}
                      </Typography>
                      {task.valid_records > 0 && (
                        <Typography variant="caption" color="success.main">
                          ✓ {task.valid_records} válidos
                        </Typography>
                      )}
                      {task.invalid_records > 0 && (
                        <Typography variant="caption" color="error.main" sx={{ display: 'block' }}>
                          ✗ {task.invalid_records} inválidos
                        </Typography>
                      )}
                    </TableCell>
                    <TableCell>
                      <Typography variant="body2">
                        {new Date(task.created_at).toLocaleString()}
                      </Typography>
                    </TableCell>
                    <TableCell>
                      <Tooltip title="Detalhes">
                        <IconButton
                          size="small"
                          onClick={() => handleTaskDetails(task)}
                        >
                          <InfoIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Deletar">
                        <IconButton
                          size="small"
                          color="error"
                          onClick={() => handleDeleteTask(task.id)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
                {tasks.length === 0 && (
                  <TableRow>
                    <TableCell colSpan={7} align="center">
                      <Typography color="text.secondary">
                        Nenhuma tarefa encontrada
                      </Typography>
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Dialog de Upload */}
      <Dialog open={uploadDialogOpen} onClose={() => setUploadDialogOpen(false)} maxWidth="md" fullWidth>
        <DialogTitle>Novo Upload de Lista</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {/* Área de Drop */}
            <Grid item xs={12}>
              <Box
                {...getRootProps()}
                sx={{
                  border: '2px dashed',
                  borderColor: isDragActive ? 'primary.main' : 'grey.300',
                  borderRadius: 2,
                  p: 3,
                  textAlign: 'center',
                  cursor: 'pointer',
                  bgcolor: isDragActive ? 'action.hover' : 'background.paper',
                  transition: 'all 0.2s ease'
                }}
              >
                <input {...getInputProps()} />
                <UploadIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
                <Typography variant="h6" gutterBottom>
                  {isDragActive ? 'Solte o arquivo aqui' : 'Arraste um arquivo ou clique para selecionar'}
                </Typography>
                <Typography color="text.secondary">
                  Suporta: CSV, TXT, XLS, XLSX (máx. 100MB)
                </Typography>
                {selectedFile && (
                  <Alert severity="success" sx={{ mt: 2 }}>
                    Arquivo selecionado: {selectedFile.name} ({formatFileSize(selectedFile.size)})
                  </Alert>
                )}
              </Box>
            </Grid>

            {/* Configurações */}
            <Grid item xs={12}>
              <Divider sx={{ my: 2 }} />
              <Typography variant="h6" gutterBottom>
                Configurações de Processamento
              </Typography>
            </Grid>

            <Grid item xs={12} sm={6}>
              <FormControl fullWidth>
                <InputLabel>País</InputLabel>
                <Select
                  value={uploadConfig.country}
                  onChange={(e) => setUploadConfig(prev => ({ ...prev, country: e.target.value }))}
                  label="País"
                >
                  {countries.map((country) => (
                    <MenuItem key={country.code} value={country.code}>
                      {country.flag} {country.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="Tamanho do Lote"
                type="number"
                value={uploadConfig.batch_size}
                onChange={(e) => setUploadConfig(prev => ({ ...prev, batch_size: parseInt(e.target.value) || 1000 }))}
                inputProps={{ min: 100, max: 10000 }}
                helperText="Registros processados por vez"
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <TextField
                fullWidth
                label="ID da Campanha (Opcional)"
                type="number"
                value={uploadConfig.campaign_id || ''}
                onChange={(e) => setUploadConfig(prev => ({ ...prev, campaign_id: parseInt(e.target.value) || null }))}
                helperText="Associar lista a uma campanha"
              />
            </Grid>

            <Grid item xs={12} sm={6}>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <FormControlLabel
                  control={
                    <Switch
                      checked={uploadConfig.validate_numbers}
                      onChange={(e) => setUploadConfig(prev => ({ ...prev, validate_numbers: e.target.checked }))}
                    />
                  }
                  label="Validar números"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={uploadConfig.clean_numbers}
                      onChange={(e) => setUploadConfig(prev => ({ ...prev, clean_numbers: e.target.checked }))}
                    />
                  }
                  label="Limpar formatação"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={uploadConfig.detect_format}
                      onChange={(e) => setUploadConfig(prev => ({ ...prev, detect_format: e.target.checked }))}
                    />
                  }
                  label="Detectar formato automaticamente"
                />
                <FormControlLabel
                  control={
                    <Switch
                      checked={uploadConfig.skip_duplicates}
                      onChange={(e) => setUploadConfig(prev => ({ ...prev, skip_duplicates: e.target.checked }))}
                    />
                  }
                  label="Pular duplicatas"
                />
              </Box>
            </Grid>

            {/* Progresso do Upload */}
            {isUploading && (
              <Grid item xs={12}>
                <Alert severity="info">
                  Upload em progresso...
                </Alert>
                <LinearProgress
                  variant="determinate"
                  value={uploadProgress}
                  sx={{ mt: 1 }}
                />
                <Typography variant="caption" sx={{ mt: 1, display: 'block' }}>
                  {Math.round(uploadProgress)}% concluído
                </Typography>
              </Grid>
            )}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setUploadDialogOpen(false)} disabled={isUploading}>
            Cancelar
          </Button>
          <Button
            onClick={handleUpload}
            variant="contained"
            disabled={!selectedFile || isUploading}
            startIcon={<UploadIcon />}
          >
            {isUploading ? 'Enviando...' : 'Iniciar Upload'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog de Detalhes da Tarefa */}
      <Dialog open={detailsDialogOpen} onClose={() => setDetailsDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Detalhes da Tarefa</DialogTitle>
        <DialogContent>
          {selectedTask && (
            <Box>
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Typography variant="h6">{selectedTask.original_filename}</Typography>
                  <Typography color="text.secondary">
                    ID: {selectedTask.id}
                  </Typography>
                </Grid>
                
                <Grid item xs={6}>
                  <Typography variant="body2">
                    <strong>Status:</strong> {statusLabels[selectedTask.status]}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2">
                    <strong>Progresso:</strong> {Math.round(selectedTask.progress_percentage || 0)}%
                  </Typography>
                </Grid>
                
                <Grid item xs={6}>
                  <Typography variant="body2">
                    <strong>Total:</strong> {selectedTask.total_records}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2">
                    <strong>Processados:</strong> {selectedTask.processed_records}
                  </Typography>
                </Grid>
                
                <Grid item xs={6}>
                  <Typography variant="body2" color="success.main">
                    <strong>Válidos:</strong> {selectedTask.valid_records}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="error.main">
                    <strong>Inválidos:</strong> {selectedTask.invalid_records}
                  </Typography>
                </Grid>
                
                <Grid item xs={12}>
                  <Typography variant="body2">
                    <strong>Tamanho:</strong> {formatFileSize(selectedTask.file_size)}
                  </Typography>
                </Grid>
                
                {selectedTask.detected_format && (
                  <Grid item xs={12}>
                    <Typography variant="body2">
                      <strong>Formato detectado:</strong>
                    </Typography>
                    <Typography variant="caption" component="div">
                      Separador: {selectedTask.detected_format.separator}<br/>
                      Codificação: {selectedTask.detected_format.encoding}<br/>
                      Cabeçalho: {selectedTask.detected_format.has_header ? 'Sim' : 'Não'}
                    </Typography>
                  </Grid>
                )}
                
                {selectedTask.error_message && (
                  <Grid item xs={12}>
                    <Alert severity="error">
                      <strong>Erro:</strong> {selectedTask.error_message}
                    </Alert>
                  </Grid>
                )}
                
                <Grid item xs={12}>
                  <Typography variant="caption" color="text.secondary">
                    Criado em: {new Date(selectedTask.created_at).toLocaleString()}
                  </Typography>
                  {selectedTask.completed_at && (
                    <Typography variant="caption" color="text.secondary" sx={{ display: 'block' }}>
                      Concluído em: {new Date(selectedTask.completed_at).toLocaleString()}
                    </Typography>
                  )}
                </Grid>
              </Grid>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDetailsDialogOpen(false)}>Fechar</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default OptimizedUpload;