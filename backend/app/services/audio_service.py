from sqlalchemy.orm import Session
from app.models.audio import Audio
from app.schemas.audio import AudioCreate, AudioUpdate
import os
import wave
import asyncio
from typing import List, Optional, Dict, Any
from pydub import AudioSegment
from datetime import datetime
import json
import subprocess

class AudioService:
    def __init__(self, db: Session):
        self.db = db

    def create_audio(self, audio_in: AudioCreate) -> Audio:
        audio = Audio(**audio_in.dict())
        self.db.add(audio)
        self.db.commit()
        self.db.refresh(audio)
        return audio

    def get_audio(self, audio_id: int) -> Audio:
        return self.db.query(Audio).filter(Audio.id == audio_id).first()

    def list_audios(self, campaign_id: int = None):
        query = self.db.query(Audio)
        if campaign_id:
            query = query.filter(Audio.campaign_id == campaign_id)
        return query.all()

    def update_audio(self, audio_id: int, audio_in: AudioUpdate) -> Audio:
        audio = self.get_audio(audio_id)
        if not audio:
            return None
        for field, value in audio_in.dict(exclude_unset=True).items():
            setattr(audio, field, value)
        self.db.commit()
        self.db.refresh(audio)
        return audio

    def delete_audio(self, audio_id: int) -> bool:
        audio = self.get_audio(audio_id)
        if not audio:
            return False
        self.db.delete(audio)
        self.db.commit()
        return True

    @staticmethod
    async def analyze_audio(file_path: str) -> Dict[str, Any]:
        """
        Analisar propriedades do arquivo de áudio
        """
        try:
            # Usar pydub para análise
            audio = AudioSegment.from_file(file_path)
            
            return {
                "duration": len(audio) / 1000.0,  # Duração em segundos
                "sample_rate": audio.frame_rate,
                "channels": audio.channels,
                "format": "wav",
                "bit_depth": audio.sample_width * 8,
                "size": os.path.getsize(file_path)
            }
        except Exception as e:
            print(f"Erro ao analisar áudio: {e}")
            return {
                "duration": 0,
                "sample_rate": 8000,
                "channels": 1,
                "format": "wav",
                "bit_depth": 16,
                "size": os.path.getsize(file_path) if os.path.exists(file_path) else 0
            }
    
    @staticmethod
    async def create_audio_file(db, audio_data) -> Dict[str, Any]:
        """
        Criar registro de arquivo de áudio no banco
        """
        try:
            # Simulação de criação no banco (substituir por implementação real)
            audio_file = {
                "id": len(str(datetime.now().timestamp()).replace('.', '')),
                "filename": audio_data.filename,
                "original_name": audio_data.original_name,
                "display_name": audio_data.display_name,
                "description": audio_data.description,
                "file_path": audio_data.file_path,
                "file_size": audio_data.file_size,
                "duration": audio_data.duration,
                "sample_rate": audio_data.sample_rate,
                "channels": audio_data.channels,
                "format": audio_data.format,
                "campaign_id": audio_data.campaign_id,
                "audio_type": audio_data.audio_type,
                "created_at": datetime.now()
            }
            
            # Salvar metadados em JSON (temporário)
            metadata_path = "uploads/audio/metadata.json"
            os.makedirs(os.path.dirname(metadata_path), exist_ok=True)
            
            metadata = []
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
            
            metadata.append(audio_file)
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
            
            return type('AudioFile', (), audio_file)
            
        except Exception as e:
            print(f"Erro ao criar arquivo de áudio: {e}")
            raise e
    
    @staticmethod
    async def get_audio_files(db, campaign_id: Optional[int] = None, audio_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Buscar arquivos de áudio com filtros
        """
        try:
            metadata_path = "uploads/audio/metadata.json"
            
            if not os.path.exists(metadata_path):
                return []
            
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            # Aplicar filtros
            filtered_files = []
            for audio in metadata:
                if campaign_id and audio.get("campaign_id") != campaign_id:
                    continue
                if audio_type and audio.get("audio_type") != audio_type:
                    continue
                
                # Verificar se arquivo ainda existe
                if os.path.exists(audio.get("file_path", "")):
                    filtered_files.append(type('AudioFile', (), audio))
            
            return filtered_files
            
        except Exception as e:
            print(f"Erro ao buscar arquivos de áudio: {e}")
            return []
    
    @staticmethod
    async def get_audio_file(db, audio_id: int) -> Optional[Dict[str, Any]]:
        """
        Buscar arquivo de áudio por ID
        """
        try:
            metadata_path = "uploads/audio/metadata.json"
            
            if not os.path.exists(metadata_path):
                return None
            
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            for audio in metadata:
                if audio.get("id") == audio_id:
                    return type('AudioFile', (), audio)
            
            return None
            
        except Exception as e:
            print(f"Erro ao buscar arquivo de áudio: {e}")
            return None
    
    @staticmethod
    async def delete_audio_file(db, audio_id: int) -> bool:
        """
        Deletar arquivo de áudio do banco
        """
        try:
            metadata_path = "uploads/audio/metadata.json"
            
            if not os.path.exists(metadata_path):
                return False
            
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            # Remover arquivo dos metadados
            metadata = [audio for audio in metadata if audio.get("id") != audio_id]
            
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2, default=str)
            
            return True
            
        except Exception as e:
            print(f"Erro ao deletar arquivo de áudio: {e}")
            return False
    
    @staticmethod
    async def convert_audio(
        input_path: str,
        target_format: str = "wav",
        sample_rate: int = 8000,
        channels: int = 1
    ) -> str:
        """
        Converter arquivo de áudio para formato específico
        """
        try:
            # Gerar nome do arquivo convertido
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            output_path = os.path.join(
                os.path.dirname(input_path),
                f"{base_name}_converted.{target_format}"
            )
            
            # Converter usando pydub
            audio = AudioSegment.from_file(input_path)
            audio = audio.set_channels(channels)
            audio = audio.set_frame_rate(sample_rate)
            audio.export(output_path, format=target_format)
            
            return output_path
            
        except Exception as e:
            print(f"Erro ao converter áudio: {e}")
            raise e
    
    @staticmethod
    async def get_audio_stats(db) -> Dict[str, Any]:
        """
        Obter estatísticas dos arquivos de áudio
        """
        try:
            metadata_path = "uploads/audio/metadata.json"
            
            if not os.path.exists(metadata_path):
                return {
                    "total_files": 0,
                    "total_size": 0,
                    "total_duration": 0,
                    "by_type": {},
                    "by_campaign": {},
                    "disk_usage": 0
                }
            
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            stats = {
                "total_files": len(metadata),
                "total_size": sum(audio.get("file_size", 0) for audio in metadata),
                "total_duration": sum(audio.get("duration", 0) for audio in metadata),
                "by_type": {},
                "by_campaign": {},
                "disk_usage": 0
            }
            
            # Estatísticas por tipo
            for audio in metadata:
                audio_type = audio.get("audio_type", "unknown")
                if audio_type not in stats["by_type"]:
                    stats["by_type"][audio_type] = 0
                stats["by_type"][audio_type] += 1
            
            # Estatísticas por campanha
            for audio in metadata:
                campaign_id = audio.get("campaign_id", "none")
                if campaign_id not in stats["by_campaign"]:
                    stats["by_campaign"][campaign_id] = 0
                stats["by_campaign"][campaign_id] += 1
            
            # Uso do disco
            audio_dir = "uploads/audio"
            if os.path.exists(audio_dir):
                total_size = 0
                for root, dirs, files in os.walk(audio_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        total_size += os.path.getsize(file_path)
                stats["disk_usage"] = total_size
            
            return stats
            
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return {
                "total_files": 0,
                "total_size": 0,
                "total_duration": 0,
                "by_type": {},
                "by_campaign": {},
                "disk_usage": 0
            } 