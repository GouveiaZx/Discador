import asyncio
import logging
import time
import json
import os
from typing import Dict, Any, Optional, Tuple
from datetime import datetime

logger = logging.getLogger(__name__)

class AMDService:
    """
    Serviço de detecção de secretária eletrônica (Answering Machine Detection)
    """
    
    def __init__(self):
        self.config = {
            # Tempos em milissegundos
            "initial_silence": 2500,        # Silêncio inicial máximo
            "greeting_duration": 1500,      # Duração mínima de saudação
            "after_greeting_silence": 800,  # Silêncio após saudação
            "total_analysis_time": 5000,    # Tempo total de análise
            "maximum_number_of_words": 5,   # Máximo de palavras para humano
            "maximum_word_length": 5000,    # Duração máxima de palavra
            "between_words_silence": 50,    # Silêncio entre palavras
            "min_word_length": 100,         # Duração mínima de palavra
            "silence_threshold": 256,       # Threshold de silêncio
        }
        
        # Histórico de decisões para machine learning
        self.decision_history = []
        self.load_amd_history()
    
    def load_amd_history(self):
        """
        Carregar histórico de decisões AMD para aprendizado
        """
        try:
            history_file = "amd_history.json"
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    self.decision_history = json.load(f)
                logger.info(f"Carregado {len(self.decision_history)} registros de AMD")
        except Exception as e:
            logger.error(f"Erro ao carregar histórico AMD: {e}")
            self.decision_history = []
    
    def save_amd_decision(self, analysis_data: Dict[str, Any], decision: str, confidence: float):
        """
        Salvar decisão AMD para aprendizado futuro
        """
        try:
            record = {
                "timestamp": datetime.now().isoformat(),
                "decision": decision,
                "confidence": confidence,
                "analysis_data": analysis_data
            }
            
            self.decision_history.append(record)
            
            # Manter apenas os últimos 1000 registros
            if len(self.decision_history) > 1000:
                self.decision_history = self.decision_history[-1000:]
            
            # Salvar no arquivo
            with open("amd_history.json", 'w') as f:
                json.dump(self.decision_history, f, indent=2)
                
        except Exception as e:
            logger.error(f"Erro ao salvar decisão AMD: {e}")
    
    async def analyze_audio_stream(self, audio_data: bytes, call_id: str) -> Dict[str, Any]:
        """
        Analisar stream de áudio para detectar secretária eletrônica
        """
        try:
            analysis_start = time.time()
            
            # Converter bytes para análise (simulação)
            audio_length = len(audio_data)
            analysis_duration = min(audio_length / 8000, self.config["total_analysis_time"] / 1000)
            
            # Simular detecção de voz e silêncio
            voice_segments, silence_segments = await self._detect_voice_segments(audio_data)
            
            # Calcular estatísticas
            stats = self._calculate_audio_stats(voice_segments, silence_segments, analysis_duration)
            
            # Tomar decisão baseada nas estatísticas
            decision, confidence = self._make_amd_decision(stats)
            
            analysis_result = {
                "call_id": call_id,
                "decision": decision,  # "HUMAN", "MACHINE", "UNKNOWN"
                "confidence": confidence,
                "analysis_duration": analysis_duration,
                "stats": stats,
                "timestamp": datetime.now().isoformat()
            }
            
            # Salvar decisão para aprendizado
            self.save_amd_decision(stats, decision, confidence)
            
            logger.info(f"AMD Analysis - Call: {call_id}, Decision: {decision}, Confidence: {confidence:.2f}")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Erro na análise AMD: {e}")
            return {
                "call_id": call_id,
                "decision": "UNKNOWN",
                "confidence": 0.0,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    async def _detect_voice_segments(self, audio_data: bytes) -> Tuple[list, list]:
        """
        Detectar segmentos de voz e silêncio no áudio (simulação)
        """
        try:
            audio_length = len(audio_data)
            sample_rate = 8000  # 8kHz padrão para telefonia
            duration = audio_length / sample_rate
            
            voice_segments = []
            silence_segments = []
            
            # Padrão de secretária eletrônica: saudação longa + beep
            if duration > 3.0:  # Mais de 3 segundos
                voice_segments.append({"start": 0.5, "end": 2.8, "duration": 2.3})
                silence_segments.append({"start": 0.0, "end": 0.5, "duration": 0.5})
                silence_segments.append({"start": 2.8, "end": 3.0, "duration": 0.2})
            else:
                # Resposta humana típica: silêncio curto + fala breve
                voice_segments.append({"start": 0.2, "end": 1.5, "duration": 1.3})
                silence_segments.append({"start": 0.0, "end": 0.2, "duration": 0.2})
                silence_segments.append({"start": 1.5, "end": duration, "duration": duration - 1.5})
            
            return voice_segments, silence_segments
            
        except Exception as e:
            logger.error(f"Erro na detecção de segmentos: {e}")
            return [], []
    
    def _calculate_audio_stats(self, voice_segments: list, silence_segments: list, total_duration: float) -> Dict[str, Any]:
        """
        Calcular estatísticas do áudio
        """
        try:
            total_voice_time = sum(seg["duration"] for seg in voice_segments)
            total_silence_time = sum(seg["duration"] for seg in silence_segments)
            
            longest_voice = max((seg["duration"] for seg in voice_segments), default=0)
            longest_silence = max((seg["duration"] for seg in silence_segments), default=0)
            
            # Calcular ratio de voz/silêncio
            voice_ratio = total_voice_time / total_duration if total_duration > 0 else 0
            silence_ratio = total_silence_time / total_duration if total_duration > 0 else 0
            
            # Detectar padrões típicos
            initial_silence = silence_segments[0]["duration"] if silence_segments else 0
            
            stats = {
                "total_duration": total_duration,
                "total_voice_time": total_voice_time,
                "total_silence_time": total_silence_time,
                "voice_ratio": voice_ratio,
                "silence_ratio": silence_ratio,
                "longest_voice_segment": longest_voice,
                "longest_silence_segment": longest_silence,
                "initial_silence": initial_silence,
                "voice_segments_count": len(voice_segments),
                "silence_segments_count": len(silence_segments),
                "average_voice_segment": total_voice_time / len(voice_segments) if voice_segments else 0,
                "average_silence_segment": total_silence_time / len(silence_segments) if silence_segments else 0
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Erro no cálculo de estatísticas: {e}")
            return {}
    
    def _make_amd_decision(self, stats: Dict[str, Any]) -> Tuple[str, float]:
        """
        Tomar decisão de AMD baseada nas estatísticas
        """
        try:
            confidence = 0.5
            decision = "UNKNOWN"
            
            # Regras para detecção de secretária eletrônica
            machine_indicators = 0
            human_indicators = 0
            
            # Indicador 1: Silêncio inicial muito longo
            if stats.get("initial_silence", 0) > 1.0:  # Mais de 1 segundo
                machine_indicators += 1
            elif stats.get("initial_silence", 0) < 0.5:  # Menos de 0.5 segundos
                human_indicators += 1
            
            # Indicador 2: Segmento de voz muito longo (saudação de secretária)
            if stats.get("longest_voice_segment", 0) > 2.0:  # Mais de 2 segundos
                machine_indicators += 2
            elif stats.get("longest_voice_segment", 0) < 1.0:  # Menos de 1 segundo
                human_indicators += 1
            
            # Indicador 3: Poucos segmentos de voz (secretária fala de uma vez)
            if stats.get("voice_segments_count", 0) <= 2:
                machine_indicators += 1
            elif stats.get("voice_segments_count", 0) >= 4:
                human_indicators += 1
            
            # Indicador 4: Ratio de voz muito alto (secretária fala muito)
            if stats.get("voice_ratio", 0) > 0.7:  # Mais de 70% do tempo falando
                machine_indicators += 1
            elif stats.get("voice_ratio", 0) < 0.4:  # Menos de 40% do tempo falando
                human_indicators += 1
            
            # Indicador 5: Duração total longa (secretárias têm saudações longas)
            if stats.get("total_duration", 0) > 4.0:  # Mais de 4 segundos
                machine_indicators += 1
            elif stats.get("total_duration", 0) < 2.0:  # Menos de 2 segundos
                human_indicators += 1
            
            # Tomar decisão baseada nos indicadores
            total_indicators = machine_indicators + human_indicators
            
            if total_indicators > 0:
                machine_confidence = machine_indicators / total_indicators
                human_confidence = human_indicators / total_indicators
                
                if machine_confidence > 0.6:
                    decision = "MACHINE"
                    confidence = machine_confidence
                elif human_confidence > 0.6:
                    decision = "HUMAN"
                    confidence = human_confidence
                else:
                    decision = "UNKNOWN"
                    confidence = 0.5
            
            return decision, confidence
            
        except Exception as e:
            logger.error(f"Erro na decisão AMD: {e}")
            return "UNKNOWN", 0.0
    
    async def get_amd_stats(self) -> Dict[str, Any]:
        """
        Obter estatísticas do sistema AMD
        """
        try:
            total_decisions = len(self.decision_history)
            
            if total_decisions == 0:
                return {
                    "total_decisions": 0,
                    "human_count": 0,
                    "machine_count": 0,
                    "unknown_count": 0,
                    "accuracy_estimate": 0.0
                }
            
            human_count = len([d for d in self.decision_history if d["decision"] == "HUMAN"])
            machine_count = len([d for d in self.decision_history if d["decision"] == "MACHINE"])
            unknown_count = len([d for d in self.decision_history if d["decision"] == "UNKNOWN"])
            
            # Calcular confiança média
            avg_confidence = sum(d["confidence"] for d in self.decision_history) / total_decisions
            
            return {
                "total_decisions": total_decisions,
                "human_count": human_count,
                "machine_count": machine_count,
                "unknown_count": unknown_count,
                "human_percentage": (human_count / total_decisions) * 100,
                "machine_percentage": (machine_count / total_decisions) * 100,
                "unknown_percentage": (unknown_count / total_decisions) * 100,
                "average_confidence": avg_confidence,
                "accuracy_estimate": avg_confidence * 100
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas AMD: {e}")
            return {}
    
    def update_config(self, new_config: Dict[str, Any]):
        """
        Atualizar configurações do AMD
        """
        try:
            self.config.update(new_config)
            logger.info(f"Configuração AMD atualizada: {new_config}")
        except Exception as e:
            logger.error(f"Erro ao atualizar configuração AMD: {e}")
    
    def get_config(self) -> Dict[str, Any]:
        """
        Obter configurações atuais do AMD
        """
        return self.config.copy()
