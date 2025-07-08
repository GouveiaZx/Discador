import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  Input,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  LinearProgress,
  Alert,
  Grid,
  Card,
  CardContent,
  CardActions,
  Avatar,
  Divider
} from '@mui/material';
import {
  Upload as UploadIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Delete as DeleteIcon,
  Download as DownloadIcon,
  AudioFile as AudioFileIcon,
  Campaign as CampaignIcon,
  Statistics as StatsIcon,
  CloudUpload as CloudUploadIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import api from '../config/api';

const VisuallyHiddenInput = styled('input')({
  clip: 'rect(0 0 0 0)',
  clipPath: 'inset(50%)',
  height: 1,
  overflow: 'hidden',
  position: 'absolute',
  bottom: 0,
  left: 0,
  whiteSpace: 'nowrap',
  width: 1,
});

const AudioManager = () => {
  const [audioFiles, setAudioFiles] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [loading, setLoading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [currentlyPlaying, setCurrentlyPlaying] = useState(null);
  const [openUploadDialog, setOpenUploadDialog] = useState(false);
  const [openStatsDialog, setOpenStatsDialog] = useState(false);
  const [stats, setStats] = useState({});
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Upload form state
  const [uploadForm, setUploadForm] = useState({
    file: null,
    name: '',
    description: '',
    campaign_id: '',
    audio_type: 'greeting'
  });

  const audioRef = useRef(null);

  useEffect(() => {
    loadAudioFiles();
    loadCampaigns();
  }, []);

  const loadAudioFiles = async () => {
    try {
      setLoading(true);
      const response = await api.get('/audio/list');
      setAudioFiles(response.data.files || response.data || []);
    } catch (error) {
      setError('Erro ao carregar arquivos de áudio');
      console.error('Erro ao carregar áudios:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadCampaigns = async () => {
    try {
      const response = await api.get('/campaigns');
      setCampaigns(response.data);
    } catch (error) {
      console.error('Erro ao carregar campanhas:', error);
    }
  };

  const loadStats = async () => {
    try {
      const response = await api.get('/audio/stats');
      setStats(response.data);
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error);
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validar formato
      const allowedFormats = ['audio/wav', 'audio/mp3', 'audio/m4a', 'audio/aac', 'audio/flac'];
      if (!allowedFormats.includes(file.type)) {
        setError('Formato no soportado. Use: WAV, MP3, M4A, AAC, FLAC');
        return;
      }

      // Validar tamanho (50MB)
      if (file.size > 50 * 1024 * 1024) {
        setError('Archivo muy grande. Máximo: 50MB');
        return;
      }

      setUploadForm({
        ...uploadForm,
        file: file,
        name: uploadForm.name || file.name.split('.')[0]
      });
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!uploadForm.file) {
      setError('Seleccione un archivo');
      return;
    }

    try {
      setLoading(true);
      setUploadProgress(0);
      
      const formData = new FormData();
      formData.append('file', uploadForm.file);
      formData.append('name', uploadForm.name);
      formData.append('description', uploadForm.description);
      formData.append('campaign_id', uploadForm.campaign_id);
      formData.append('audio_type', uploadForm.audio_type);

      const response = await api.post('/audio/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(progress);
        }
      });

      if (response.data.success) {
        setSuccess('¡Archivo enviado con éxito!');
        setOpenUploadDialog(false);
        setUploadForm({
          file: null,
          name: '',
          description: '',
          campaign_id: '',
          audio_type: 'greeting'
        });
        loadAudioFiles();
      } else {
        setError(response.data.message || 'Erro ao enviar arquivo');
      }

    } catch (error) {
      setError(error.response?.data?.detail || 'Erro ao enviar arquivo');
    } finally {
      setLoading(false);
      setUploadProgress(0);
    }
  };

  const handlePlay = async (audioFile) => {
    try {
      if (currentlyPlaying === audioFile.filename) {
        // Parar reprodução
        if (audioRef.current) {
          audioRef.current.pause();
          audioRef.current.currentTime = 0;
        }
        setCurrentlyPlaying(null);
        return;
      }

      // Parar reprodução atual
      if (audioRef.current) {
        audioRef.current.pause();
      }

      // Iniciar nova reprodução
      const response = await api.get(`/audio/play/${audioFile.id || audioFile.filename}`, {
        responseType: 'blob'
      });

      const audioBlob = new Blob([response.data], { type: 'audio/wav' });
      const audioUrl = URL.createObjectURL(audioBlob);

      if (audioRef.current) {
        audioRef.current.src = audioUrl;
        audioRef.current.play();
        setCurrentlyPlaying(audioFile.filename);

        audioRef.current.onended = () => {
          setCurrentlyPlaying(null);
          URL.revokeObjectURL(audioUrl);
        };
      }

    } catch (error) {
      setError('Erro ao reproduzir áudio');
      console.error('Erro ao reproduzir:', error);
    }
  };

  const handleDelete = async (audioFile) => {
    if (!window.confirm('Tem certeza que deseja deletar este arquivo?')) {
      return;
    }

    try {
      await api.delete(`/audio/delete/${audioFile.id || audioFile.filename}`);
      setSuccess('¡Archivo eliminado con éxito!');
      loadAudioFiles();
    } catch (error) {
      setError('Erro ao deletar arquivo');
      console.error('Erro ao deletar:', error);
    }
  };

  const handleDownload = async (audioFile) => {
    try {
      const response = await api.get(`/audio/play/${audioFile.id || audioFile.filename}`, {
        responseType: 'blob'
      });

      const blob = new Blob([response.data], { type: 'audio/wav' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = audioFile.filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

    } catch (error) {
      setError('Erro ao baixar arquivo');
      console.error('Erro ao baixar:', error);
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
    if (!seconds) return '0:00';
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.floor(seconds % 60);
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  const getAudioTypeColor = (type) => {
    const colors = {
      'greeting': 'primary',
      'ivr': 'secondary',
      'hold_music': 'success',
      'transfer': 'warning',
      'goodbye': 'error'
    };
    return colors[type] || 'default';
  };

  const AudioTypeIcon = ({ type }) => {
    const icons = {
      'greeting': <AudioFileIcon />,
      'ivr': <CampaignIcon />,
      'hold_music': <PlayIcon />,
      'transfer': <DownloadIcon />,
      'goodbye': <StopIcon />
    };
    return icons[type] || <AudioFileIcon />;
  };

  return (
    <Box sx={{ p: 3 }}>
      <audio ref={audioRef} style={{ display: 'none' }} />
      
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" component="h1">
          Gerenciador de Áudios
        </Typography>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Button
            variant="contained"
            startIcon={<CloudUploadIcon />}
            onClick={() => setOpenUploadDialog(true)}
          >
            Upload Áudio
          </Button>
          
          <Button
            variant="outlined"
            startIcon={<StatsIcon />}
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
            onClick={loadAudioFiles}
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

      {/* Lista de Arquivos */}
      <Paper sx={{ p: 2 }}>
        <Typography variant="h6" gutterBottom>
          Arquivos de Áudio ({audioFiles.length})
        </Typography>
        
        {loading && <LinearProgress sx={{ mb: 2 }} />}
        
        {audioFiles.length === 0 ? (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <AudioFileIcon sx={{ fontSize: 64, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary">
              Nenhum arquivo de áudio encontrado
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Faça upload de arquivos para começar
            </Typography>
          </Box>
        ) : (
          <Grid container spacing={2}>
            {audioFiles.map((audioFile, index) => (
              <Grid item xs={12} md={6} lg={4} key={index}>
                <Card>
                  <CardContent>
                    <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                      <Avatar sx={{ mr: 2 }}>
                        <AudioTypeIcon type={audioFile.type} />
                      </Avatar>
                      <Box sx={{ flexGrow: 1 }}>
                        <Typography variant="h6" noWrap>
                          {audioFile.display_name || audioFile.filename}
                        </Typography>
                        <Chip 
                          label={audioFile.type || 'greeting'}
                          color={getAudioTypeColor(audioFile.type)}
                          size="small"
                        />
                      </Box>
                    </Box>
                    
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      {audioFile.description || 'Sem descrição'}
                    </Typography>
                    
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
                      <Typography variant="caption">
                        {formatFileSize(audioFile.size)}
                      </Typography>
                      <Typography variant="caption">
                        {formatDuration(audioFile.duration)}
                      </Typography>
                    </Box>
                  </CardContent>
                  
                  <CardActions>
                    <IconButton
                      onClick={() => handlePlay(audioFile)}
                      color={currentlyPlaying === audioFile.filename ? 'secondary' : 'primary'}
                      title={currentlyPlaying === audioFile.filename ? 'Parar' : 'Reproduzir'}
                    >
                      {currentlyPlaying === audioFile.filename ? <StopIcon /> : <PlayIcon />}
                    </IconButton>
                    
                    <IconButton
                      onClick={() => handleDownload(audioFile)}
                      color="primary"
                      title="Download"
                    >
                      <DownloadIcon />
                    </IconButton>
                    
                    <IconButton
                      onClick={() => handleDelete(audioFile)}
                      color="error"
                      title="Deletar"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </CardActions>
                </Card>
              </Grid>
            ))}
          </Grid>
        )}
      </Paper>

      {/* Dialog de Upload */}
      <Dialog open={openUploadDialog} onClose={() => setOpenUploadDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Upload de Arquivo de Áudio</DialogTitle>
        <DialogContent>
          <Box sx={{ pt: 2 }}>
            <Button
              component="label"
              variant="outlined"
              startIcon={<UploadIcon />}
              fullWidth
              sx={{ mb: 3, p: 3 }}
            >
              {uploadForm.file ? uploadForm.file.name : 'Selecionar Arquivo'}
              <VisuallyHiddenInput
                type="file"
                accept=".wav,.mp3,.m4a,.aac,.flac"
                onChange={handleFileSelect}
              />
            </Button>
            
            {uploadProgress > 0 && (
              <Box sx={{ mb: 3 }}>
                <LinearProgress variant="determinate" value={uploadProgress} />
                <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                  {uploadProgress}% enviado
                </Typography>
              </Box>
            )}
            
            <Grid container spacing={2}>
              <Grid item xs={12} md={6}>
                <TextField
                  fullWidth
                  label="Nome"
                  value={uploadForm.name}
                  onChange={(e) => setUploadForm({...uploadForm, name: e.target.value})}
                  required
                />
              </Grid>
              
              <Grid item xs={12} md={6}>
                <FormControl fullWidth>
                  <InputLabel>Tipo de Áudio</InputLabel>
                  <Select
                    value={uploadForm.audio_type}
                    onChange={(e) => setUploadForm({...uploadForm, audio_type: e.target.value})}
                  >
                    <MenuItem value="greeting">Saudação</MenuItem>
                    <MenuItem value="ivr">IVR</MenuItem>
                    <MenuItem value="hold_music">Música de Espera</MenuItem>
                    <MenuItem value="transfer">Transferência</MenuItem>
                    <MenuItem value="goodbye">Despedida</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12}>
                <FormControl fullWidth>
                  <InputLabel>Campanha</InputLabel>
                  <Select
                    value={uploadForm.campaign_id}
                    onChange={(e) => setUploadForm({...uploadForm, campaign_id: e.target.value})}
                  >
                    <MenuItem value="">Nenhuma</MenuItem>
                    {campaigns.map((campaign) => (
                      <MenuItem key={campaign.id} value={campaign.id}>
                        {campaign.name}
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>
              </Grid>
              
              <Grid item xs={12}>
                <TextField
                  fullWidth
                  label="Descrição"
                  multiline
                  rows={3}
                  value={uploadForm.description}
                  onChange={(e) => setUploadForm({...uploadForm, description: e.target.value})}
                />
              </Grid>
            </Grid>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenUploadDialog(false)}>Cancelar</Button>
          <Button onClick={handleUpload} variant="contained" disabled={!uploadForm.file || loading}>
            {loading ? 'Enviando...' : 'Enviar'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Dialog de Estatísticas */}
      <Dialog open={openStatsDialog} onClose={() => setOpenStatsDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Estatísticas dos Arquivos de Áudio</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ pt: 2 }}>
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h4" color="primary">
                    {stats.total_files || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total de Arquivos
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h4" color="secondary">
                    {formatFileSize(stats.total_size || 0)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Tamanho Total
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
            
            <Grid item xs={12} md={4}>
              <Card>
                <CardContent>
                  <Typography variant="h4" color="success.main">
                    {formatDuration(stats.total_duration || 0)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Duração Total
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenStatsDialog(false)}>Fechar</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AudioManager; 