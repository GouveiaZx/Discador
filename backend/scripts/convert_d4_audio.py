#!/usr/bin/env python3
"""
Script de Conversão de Áudio D4
Converte arquivos G.729 do sistema D4 para WAV usando FFmpeg

Pré-requisitos:
- FFmpeg instalado no sistema
- Arquivos G.729 copiados para uploads/audio/

Uso:
    python scripts/convert_d4_audio.py
"""

import os
import sys
import subprocess
import logging
from pathlib import Path
from typing import List, Dict

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AudioConverter:
    """
    Conversor de áudio para arquivos DNC do sistema D4
    """
    
    def __init__(self):
        self.backend_path = Path(__file__).parent.parent
        self.audio_path = self.backend_path / "uploads" / "audio"
        
    def check_ffmpeg(self) -> bool:
        """
        Verifica se FFmpeg está disponível
        """
        try:
            result = subprocess.run(["ffmpeg", "-version"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                logger.info("✅ FFmpeg encontrado")
                return True
            else:
                logger.error("❌ FFmpeg não encontrado")
                return False
        except FileNotFoundError:
            logger.error("❌ FFmpeg não está instalado ou não está no PATH")
            return False
    
    def find_g729_files(self) -> List[Path]:
        """
        Encontra arquivos G.729 no diretório de áudio
        """
        g729_files = list(self.audio_path.glob("*.g729"))
        logger.info(f"Encontrados {len(g729_files)} arquivos G.729")
        return g729_files
    
    def convert_file(self, input_file: Path) -> bool:
        """
        Converte um arquivo G.729 para WAV
        """
        output_file = input_file.with_suffix('.wav')
        
        logger.info(f"Convertendo {input_file.name} -> {output_file.name}")
        
        cmd = [
            "ffmpeg", "-y",  # -y para sobrescrever
            "-i", str(input_file),
            "-ar", "8000",      # Sample rate 8kHz (padrão telefonia)
            "-ac", "1",         # Mono
            "-acodec", "pcm_s16le",  # PCM 16-bit
            str(output_file)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"✅ Conversão bem-sucedida: {output_file.name}")
                return True
            else:
                logger.error(f"❌ Erro na conversão: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Erro ao executar FFmpeg: {str(e)}")
            return False
    
    def convert_all(self) -> Dict[str, bool]:
        """
        Converte todos os arquivos G.729 encontrados
        """
        if not self.check_ffmpeg():
            logger.error("FFmpeg não disponível. Instale FFmpeg e tente novamente.")
            logger.info("Download: https://ffmpeg.org/download.html")
            return {}
        
        g729_files = self.find_g729_files()
        
        if not g729_files:
            logger.warning("Nenhum arquivo G.729 encontrado")
            return {}
        
        results = {}
        
        for file in g729_files:
            success = self.convert_file(file)
            results[file.name] = success
        
        # Resumo
        successful = sum(1 for success in results.values() if success)
        total = len(results)
        
        logger.info(f"\n📊 Resumo da conversão:")
        logger.info(f"   Total: {total} arquivos")
        logger.info(f"   Sucesso: {successful} arquivos")
        logger.info(f"   Falhas: {total - successful} arquivos")
        
        return results

def main():
    """
    Função principal
    """
    print("=" * 50)
    print("🎵 CONVERSOR DE ÁUDIO D4 (G.729 → WAV)")
    print("=" * 50)
    
    converter = AudioConverter()
    results = converter.convert_all()
    
    if results:
        successful = sum(1 for success in results.values() if success)
        if successful > 0:
            print(f"\n✅ {successful} arquivo(s) convertido(s) com sucesso!")
        else:
            print("\n❌ Nenhum arquivo foi convertido com sucesso.")
    else:
        print("\n⚠️ Nenhuma conversão realizada.")
        print("\n📋 Para instalar FFmpeg:")
        print("   Windows: https://ffmpeg.org/download.html")
        print("   Linux: sudo apt install ffmpeg")
        print("   macOS: brew install ffmpeg")

if __name__ == "__main__":
    main()