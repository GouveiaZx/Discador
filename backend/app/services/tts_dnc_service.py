"""
Serviço de TTS (Text-to-Speech) para DNC
Sistema de vozes automáticas para listas DNC em espanhol e inglês.
"""

import os
import logging
import asyncio
from typing import Optional, Dict, List, Any
from enum import Enum
from dataclasses import dataclass
from datetime import datetime
import hashlib
import tempfile
import base64

# Configurar logging
logger = logging.getLogger(__name__)

class IdiomaVoz(Enum):
    """Idiomas suportados para TTS"""
    ESPANOL = "es"
    ENGLISH = "en"
    PORTUGUES = "pt"

class TipoVoz(Enum):
    """Tipos de voz disponíveis"""
    MASCULINA = "male"
    FEMININA = "female"
    NEUTRA = "neutral"

@dataclass
class ConfiguracionVoz:
    """Configuração da voz TTS"""
    idioma: IdiomaVoz
    tipo: TipoVoz
    velocidad: float = 1.0  # 0.5 - 2.0
    tono: float = 1.0      # 0.5 - 2.0
    volumen: float = 1.0   # 0.0 - 1.0
    pausa_entre_frases: float = 0.5  # segundos
    calidad: str = "high"   # low, medium, high
    formato_audio: str = "wav"  # wav, mp3

@dataclass
class MensajeDNC:
    """Mensagem DNC para ser convertida em áudio"""
    texto: str
    idioma: IdiomaVoz
    tipo_mensaje: str  # "opt_out", "confirmacao", "despedida"
    personalizaciones: Optional[Dict[str, str]] = None

class TTSDNCService:
    """Serviço principal de TTS para DNC"""
    
    def __init__(self):
        self.configuraciones_por_idioma = {
            IdiomaVoz.ESPANOL: ConfiguracionVoz(
                idioma=IdiomaVoz.ESPANOL,
                tipo=TipoVoz.FEMININA,
                velocidad=0.9,
                tono=1.1,
                volumen=1.0,
                pausa_entre_frases=0.7
            ),
            IdiomaVoz.ENGLISH: ConfiguracionVoz(
                idioma=IdiomaVoz.ENGLISH,
                tipo=TipoVoz.MASCULINA,
                velocidad=1.0,
                tono=1.0,
                volumen=1.0,
                pausa_entre_frases=0.5
            ),
            IdiomaVoz.PORTUGUES: ConfiguracionVoz(
                idioma=IdiomaVoz.PORTUGUES,
                tipo=TipoVoz.FEMININA,
                velocidad=0.95,
                tono=1.05,
                volumen=1.0,
                pausa_entre_frases=0.6
            )
        }
        
        self.cache_audios = {}
        self.directorio_audios = os.path.join(os.path.dirname(__file__), "../../audios/tts_dnc")
        self._crear_directorio_audios()
    
    def _crear_directorio_audios(self):
        """Cria diretório para armazenar áudios TTS"""
        try:
            os.makedirs(self.directorio_audios, exist_ok=True)
            logger.info(f"✅ Diretório TTS criado: {self.directorio_audios}")
        except Exception as e:
            logger.error(f"❌ Erro ao criar diretório TTS: {e}")
    
    def obtener_mensajes_predefinidos(self) -> Dict[IdiomaVoz, Dict[str, str]]:
        """Obtém mensagens predefinidas para DNC em todos os idiomas"""
        return {
            IdiomaVoz.ESPANOL: {
                "opt_out": "Si no desea recibir más llamadas de nuestra empresa, presione 9 ahora o diga 'STOP'. Su número será removido de nuestra lista de contactos inmediatamente.",
                "confirmacao": "Perfecto. Su número ha sido agregado a nuestra lista de No Llamar. No recibirá más llamadas nuestras. Que tenga un buen día.",
                "despedida": "Gracias por su atención. Si cambió de opinión, puede contactarnos directamente. Hasta luego.",
                "error": "Lo sentimos, no pudimos procesar su solicitud. Por favor, intente nuevamente presionando 9 para ser removido de nuestra lista.",
                "timeout": "No detectamos respuesta. Su número permanecerá en nuestra lista de contactos. Para ser removido, presione 9 en cualquier momento."
            },
            IdiomaVoz.ENGLISH: {
                "opt_out": "If you do not wish to receive more calls from our company, please press 9 now or say 'STOP'. Your number will be removed from our contact list immediately.",
                "confirmacao": "Perfect. Your number has been added to our Do Not Call list. You will not receive any more calls from us. Have a great day.",
                "despedida": "Thank you for your attention. If you change your mind, you can contact us directly. Goodbye.",
                "error": "We're sorry, we couldn't process your request. Please try again by pressing 9 to be removed from our list.",
                "timeout": "We didn't detect a response. Your number will remain on our contact list. To be removed, press 9 at any time."
            },
            IdiomaVoz.PORTUGUES: {
                "opt_out": "Se não deseja receber mais ligações da nossa empresa, pressione 9 agora ou diga 'PARAR'. Seu número será removido da nossa lista de contatos imediatamente.",
                "confirmacao": "Perfeito. Seu número foi adicionado à nossa lista de Não Ligar. Você não receberá mais ligações nossas. Tenha um bom dia.",
                "despedida": "Obrigado pela sua atenção. Se mudar de ideia, pode entrar em contato conosco diretamente. Até logo.",
                "error": "Desculpe, não conseguimos processar sua solicitação. Por favor, tente novamente pressionando 9 para ser removido da nossa lista.",
                "timeout": "Não detectamos resposta. Seu número permanecerá na nossa lista de contatos. Para ser removido, pressione 9 a qualquer momento."
            }
        }
    
    def _generar_hash_audio(self, texto: str, configuracion: ConfiguracionVoz) -> str:
        """Gera hash único para o áudio baseado no texto e configuração"""
        contenido = f"{texto}_{configuracion.idioma.value}_{configuracion.tipo.value}_{configuracion.velocidad}_{configuracion.tono}"
        return hashlib.md5(contenido.encode()).hexdigest()
    
    async def generar_audio_tts(self, mensaje: MensajeDNC, configuracion: Optional[ConfiguracionVoz] = None) -> Dict[str, Any]:
        """Gera áudio TTS para mensagem DNC"""
        try:
            # Usar configuração por idioma se não especificada
            if configuracion is None:
                configuracion = self.configuraciones_por_idioma.get(
                    mensaje.idioma, 
                    self.configuraciones_por_idioma[IdiomaVoz.ESPANOL]
                )
            
            # Verificar cache
            hash_audio = self._generar_hash_audio(mensaje.texto, configuracion)
            if hash_audio in self.cache_audios:
                logger.info(f"✅ Áudio TTS recuperado do cache: {hash_audio}")
                return self.cache_audios[hash_audio]
            
            # Gerar novo áudio
            resultado = await self._procesar_tts(mensaje, configuracion, hash_audio)
            
            # Armazenar no cache
            self.cache_audios[hash_audio] = resultado
            
            logger.info(f"✅ Áudio TTS gerado: {resultado['archivo']}")
            return resultado
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar áudio TTS: {e}")
            return {
                "success": False,
                "error": str(e),
                "archivo": None,
                "duracion": 0
            }
    
    async def _procesar_tts(self, mensaje: MensajeDNC, configuracion: ConfiguracionVoz, hash_audio: str) -> Dict[str, Any]:
        """Processa TTS usando diferentes engines disponíveis"""
        
        # Tentar gTTS primeiro (Google TTS)
        try:
            return await self._generar_con_gtts(mensaje, configuracion, hash_audio)
        except Exception as e:
            logger.warning(f"⚠️ gTTS falhou: {e}")
        
        # Tentar pyttsx3 como fallback
        try:
            return await self._generar_con_pyttsx3(mensaje, configuracion, hash_audio)
        except Exception as e:
            logger.warning(f"⚠️ pyttsx3 falhou: {e}")
        
        # Usar TTS simulado como último recurso
        return await self._generar_tts_simulado(mensaje, configuracion, hash_audio)
    
    async def _generar_con_gtts(self, mensaje: MensajeDNC, configuracion: ConfiguracionVoz, hash_audio: str) -> Dict[str, Any]:
        """Gera TTS usando Google TTS"""
        try:
            from gtts import gTTS
            import pygame
            
            # Mapear idiomas para gTTS
            idioma_gtts = {
                IdiomaVoz.ESPANOL: "es",
                IdiomaVoz.ENGLISH: "en",
                IdiomaVoz.PORTUGUES: "pt"
            }
            
            # Processar texto com pausas
            texto_processado = self._processar_texto_com_pausas(mensaje.texto, configuracion)
            
            # Gerar TTS
            tts = gTTS(
                text=texto_processado,
                lang=idioma_gtts[configuracion.idioma],
                slow=configuracion.velocidad < 1.0
            )
            
            # Salvar arquivo
            nome_arquivo = f"tts_dnc_{hash_audio}.{configuracion.formato_audio}"
            caminho_arquivo = os.path.join(self.directorio_audios, nome_arquivo)
            
            tts.save(caminho_arquivo)
            
            # Aplicar processamento de áudio (velocidade, tom, volume)
            caminho_processado = await self._processar_audio_avancado(
                caminho_arquivo, configuracion, hash_audio
            )
            
            # Calcular duração
            duracao = await self._calcular_duracao_audio(caminho_processado)
            
            return {
                "success": True,
                "archivo": caminho_processado,
                "duracion": duracion,
                "engine": "gtts",
                "idioma": configuracion.idioma.value,
                "tipo": configuracion.tipo.value,
                "hash": hash_audio,
                "url": f"/api/v1/audios/tts-dnc/{nome_arquivo}",
                "metadata": {
                    "texto_original": mensaje.texto,
                    "tipo_mensaje": mensaje.tipo_mensaje,
                    "fecha_creacion": datetime.now().isoformat(),
                    "configuracion": {
                        "velocidad": configuracion.velocidad,
                        "tono": configuracion.tono,
                        "volumen": configuracion.volumen,
                        "calidad": configuracion.calidad
                    }
                }
            }
            
        except ImportError:
            logger.warning("⚠️ gTTS não está instalado")
            raise Exception("gTTS não disponível")
        except Exception as e:
            logger.error(f"❌ Erro no gTTS: {e}")
            raise
    
    async def _generar_con_pyttsx3(self, mensaje: MensajeDNC, configuracion: ConfiguracionVoz, hash_audio: str) -> Dict[str, Any]:
        """Gera TTS usando pyttsx3"""
        try:
            import pyttsx3
            
            # Configurar engine
            engine = pyttsx3.init()
            
            # Configurar voz
            voices = engine.getProperty('voices')
            for voice in voices:
                # Selecionar voz por idioma e tipo
                if configuracion.idioma.value in voice.id.lower():
                    if configuracion.tipo == TipoVoz.FEMININA and 'female' in voice.id.lower():
                        engine.setProperty('voice', voice.id)
                        break
                    elif configuracion.tipo == TipoVoz.MASCULINA and 'male' in voice.id.lower():
                        engine.setProperty('voice', voice.id)
                        break
            
            # Configurar propriedades
            engine.setProperty('rate', int(200 * configuracion.velocidad))
            engine.setProperty('volume', configuracion.volumen)
            
            # Salvar arquivo
            nome_arquivo = f"tts_dnc_{hash_audio}.{configuracion.formato_audio}"
            caminho_arquivo = os.path.join(self.directorio_audios, nome_arquivo)
            
            engine.save_to_file(mensaje.texto, caminho_arquivo)
            engine.runAndWait()
            
            # Calcular duração
            duracao = await self._calcular_duracao_audio(caminho_arquivo)
            
            return {
                "success": True,
                "archivo": caminho_arquivo,
                "duracion": duracao,
                "engine": "pyttsx3",
                "idioma": configuracion.idioma.value,
                "tipo": configuracion.tipo.value,
                "hash": hash_audio,
                "url": f"/api/v1/audios/tts-dnc/{nome_arquivo}",
                "metadata": {
                    "texto_original": mensaje.texto,
                    "tipo_mensaje": mensaje.tipo_mensaje,
                    "fecha_creacion": datetime.now().isoformat(),
                    "configuracion": {
                        "velocidad": configuracion.velocidad,
                        "tono": configuracion.tono,
                        "volumen": configuracion.volumen,
                        "calidad": configuracion.calidad
                    }
                }
            }
            
        except ImportError:
            logger.warning("⚠️ pyttsx3 não está instalado")
            raise Exception("pyttsx3 não disponível")
        except Exception as e:
            logger.error(f"❌ Erro no pyttsx3: {e}")
            raise
    
    async def _generar_tts_simulado(self, mensaje: MensajeDNC, configuracion: ConfiguracionVoz, hash_audio: str) -> Dict[str, Any]:
        """Gera TTS simulado quando engines reais não estão disponíveis"""
        try:
            # Simular tempo de processamento
            await asyncio.sleep(0.5)
            
            # Criar arquivo de áudio vazio ou com tom de teste
            nome_arquivo = f"tts_dnc_simulado_{hash_audio}.{configuracion.formato_audio}"
            caminho_arquivo = os.path.join(self.directorio_audios, nome_arquivo)
            
            # Gerar áudio simulado (tom simples)
            duracao_estimada = len(mensaje.texto) * 0.1  # 0.1 segundos por caractere
            
            # Criar arquivo de áudio simples
            try:
                import numpy as np
                from scipy.io import wavfile
                
                # Gerar tom simples
                sample_rate = 44100
                duration = duracao_estimada
                frequency = 440  # La4
                
                t = np.linspace(0, duration, int(sample_rate * duration))
                wave = np.sin(2 * np.pi * frequency * t) * 0.3
                
                wavfile.write(caminho_arquivo, sample_rate, wave.astype(np.float32))
                
            except ImportError:
                # Criar arquivo vazio se scipy não estiver disponível
                with open(caminho_arquivo, 'wb') as f:
                    f.write(b'')
            
            return {
                "success": True,
                "archivo": caminho_arquivo,
                "duracion": duracao_estimada,
                "engine": "simulado",
                "idioma": configuracion.idioma.value,
                "tipo": configuracion.tipo.value,
                "hash": hash_audio,
                "url": f"/api/v1/audios/tts-dnc/{nome_arquivo}",
                "metadata": {
                    "texto_original": mensaje.texto,
                    "tipo_mensaje": mensaje.tipo_mensaje,
                    "fecha_creacion": datetime.now().isoformat(),
                    "configuracion": {
                        "velocidad": configuracion.velocidad,
                        "tono": configuracion.tono,
                        "volumen": configuracion.volumen,
                        "calidad": configuracion.calidad
                    },
                    "simulado": True
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Erro no TTS simulado: {e}")
            raise
    
    def _processar_texto_com_pausas(self, texto: str, configuracion: ConfiguracionVoz) -> str:
        """Processa texto adicionando pausas adequadas"""
        # Adicionar pausas após pontuação
        texto_processado = texto.replace('.', f'. <break time="{configuracion.pausa_entre_frases}s"/>')
        texto_processado = texto_processado.replace(',', f', <break time="{configuracion.pausa_entre_frases/2}s"/>')
        texto_processado = texto_processado.replace('?', f'? <break time="{configuracion.pausa_entre_frases}s"/>')
        texto_processado = texto_processado.replace('!', f'! <break time="{configuracion.pausa_entre_frases}s"/>')
        
        return texto_processado
    
    async def _processar_audio_avancado(self, caminho_arquivo: str, configuracion: ConfiguracionVoz, hash_audio: str) -> str:
        """Processa áudio com configurações avançadas"""
        try:
            # Se não houver processamento necessário, retornar arquivo original
            if (configuracion.velocidad == 1.0 and 
                configuracion.tono == 1.0 and 
                configuracion.volumen == 1.0):
                return caminho_arquivo
            
            # Tentar usar pydub para processamento
            try:
                from pydub import AudioSegment
                from pydub.effects import speedup
                
                # Carregar áudio
                audio = AudioSegment.from_wav(caminho_arquivo)
                
                # Aplicar mudanças
                if configuracion.velocidad != 1.0:
                    audio = speedup(audio, playback_speed=configuracion.velocidad)
                
                if configuracion.volumen != 1.0:
                    audio = audio + (20 * np.log10(configuracion.volumen))
                
                # Salvar arquivo processado
                nome_processado = f"tts_dnc_processado_{hash_audio}.{configuracion.formato_audio}"
                caminho_processado = os.path.join(self.directorio_audios, nome_processado)
                
                audio.export(caminho_processado, format=configuracion.formato_audio)
                
                return caminho_processado
                
            except ImportError:
                logger.warning("⚠️ pydub não está instalado - retornando áudio original")
                return caminho_arquivo
            
        except Exception as e:
            logger.error(f"❌ Erro no processamento de áudio: {e}")
            return caminho_arquivo
    
    async def _calcular_duracao_audio(self, caminho_arquivo: str) -> float:
        """Calcula duração do arquivo de áudio"""
        try:
            # Tentar usar mutagen para obter duração
            try:
                from mutagen import File
                audio_file = File(caminho_arquivo)
                if audio_file and audio_file.info:
                    return float(audio_file.info.length)
            except ImportError:
                pass
            
            # Fallback: estimativa baseada no tamanho do arquivo
            tamanho_arquivo = os.path.getsize(caminho_arquivo)
            # Estimativa aproximada para WAV 16-bit 44.1kHz
            duracao_estimada = tamanho_arquivo / (44100 * 2)  # 2 bytes por amostra
            return max(duracao_estimada, 1.0)  # Mínimo 1 segundo
            
        except Exception as e:
            logger.error(f"❌ Erro ao calcular duração: {e}")
            return 10.0  # Duração padrão
    
    async def generar_mensajes_dnc_completos(self, idioma: IdiomaVoz, personalizaciones: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Gera conjunto completo de mensagens DNC para um idioma"""
        try:
            mensajes_predefinidos = self.obtener_mensajes_predefinidos()[idioma]
            resultados = {}
            
            for tipo_mensaje, texto in mensajes_predefinidos.items():
                # Aplicar personalizações se fornecidas
                if personalizaciones:
                    for placeholder, valor in personalizaciones.items():
                        texto = texto.replace(f"{{{placeholder}}}", valor)
                
                # Criar mensagem DNC
                mensaje = MensajeDNC(
                    texto=texto,
                    idioma=idioma,
                    tipo_mensaje=tipo_mensaje,
                    personalizaciones=personalizaciones
                )
                
                # Gerar áudio
                resultado_audio = await self.generar_audio_tts(mensaje)
                resultados[tipo_mensaje] = resultado_audio
            
            return {
                "success": True,
                "idioma": idioma.value,
                "total_mensajes": len(resultados),
                "mensajes": resultados,
                "fecha_generacion": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao gerar mensagens DNC completas: {e}")
            return {
                "success": False,
                "error": str(e),
                "idioma": idioma.value,
                "mensajes": {}
            }
    
    def listar_audios_dnc(self) -> List[Dict[str, Any]]:
        """Lista todos os áudios DNC gerados"""
        try:
            audios = []
            
            if os.path.exists(self.directorio_audios):
                for arquivo in os.listdir(self.directorio_audios):
                    if arquivo.startswith("tts_dnc_"):
                        caminho_completo = os.path.join(self.directorio_audios, arquivo)
                        stat = os.stat(caminho_completo)
                        
                        audios.append({
                            "archivo": arquivo,
                            "caminho": caminho_completo,
                            "tamanho": stat.st_size,
                            "fecha_creacion": datetime.fromtimestamp(stat.st_ctime).isoformat(),
                            "fecha_modificacion": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                            "url": f"/api/v1/audios/tts-dnc/{arquivo}"
                        })
            
            return audios
            
        except Exception as e:
            logger.error(f"❌ Erro ao listar áudios DNC: {e}")
            return []
    
    def limpiar_cache_audios(self) -> Dict[str, Any]:
        """Limpa cache de áudios TTS"""
        try:
            audios_removidos = 0
            
            # Limpar cache em memória
            self.cache_audios.clear()
            
            # Remover arquivos antigos (mais de 7 dias)
            if os.path.exists(self.directorio_audios):
                agora = datetime.now()
                
                for arquivo in os.listdir(self.directorio_audios):
                    caminho_completo = os.path.join(self.directorio_audios, arquivo)
                    stat = os.stat(caminho_completo)
                    idade = agora - datetime.fromtimestamp(stat.st_mtime)
                    
                    if idade.days > 7:
                        os.remove(caminho_completo)
                        audios_removidos += 1
            
            logger.info(f"✅ Cache TTS limpo: {audios_removidos} arquivos removidos")
            
            return {
                "success": True,
                "audios_removidos": audios_removidos,
                "fecha_limpieza": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Erro ao limpar cache TTS: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# Instância global do serviço
tts_dnc_service = TTSDNCService() 