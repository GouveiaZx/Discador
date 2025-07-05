#!/usr/bin/env python3
"""
AGI Script para reproduzir áudio e capturar DTMF "Presione 1"
Compatible com Asterisk AGI interface
"""

import sys
import os
import logging
import time
import json
import requests
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/asterisk/presione1.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class AGIInterface:
    """
    Interface AGI para comunicação com Asterisk
    """
    
    def __init__(self):
        self.env = {}
        self.debug = True
        self.read_environment()
    
    def read_environment(self):
        """
        Ler variáveis de ambiente do AGI
        """
        try:
            while True:
                line = sys.stdin.readline().strip()
                if line == '':
                    break
                
                if ':' in line:
                    key, value = line.split(':', 1)
                    self.env[key.strip()] = value.strip()
                    
            logger.info(f"AGI Environment: {self.env}")
            
        except Exception as e:
            logger.error(f"Erro ao ler ambiente AGI: {e}")
    
    def execute(self, command):
        """
        Executar comando AGI
        """
        try:
            if self.debug:
                logger.info(f"AGI Command: {command}")
            
            print(command)
            sys.stdout.flush()
            
            result = sys.stdin.readline().strip()
            
            if self.debug:
                logger.info(f"AGI Response: {result}")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro ao executar comando AGI: {e}")
            return None
    
    def answer(self):
        """
        Atender chamada
        """
        return self.execute("ANSWER")
    
    def stream_file(self, filename, escape_digits=""):
        """
        Reproduzir arquivo de áudio
        """
        return self.execute(f"STREAM FILE {filename} \"{escape_digits}\"")
    
    def wait_for_digit(self, timeout=5000):
        """
        Aguardar dígito DTMF
        """
        return self.execute(f"WAIT FOR DIGIT {timeout}")
    
    def get_data(self, filename, timeout=5000, max_digits=1):
        """
        Reproduzir arquivo e capturar dados
        """
        return self.execute(f"GET DATA {filename} {timeout} {max_digits}")
    
    def set_variable(self, variable, value):
        """
        Definir variável
        """
        return self.execute(f"SET VARIABLE {variable} {value}")
    
    def get_variable(self, variable):
        """
        Obter variável
        """
        return self.execute(f"GET VARIABLE {variable}")
    
    def hangup(self):
        """
        Desligar chamada
        """
        return self.execute("HANGUP")
    
    def verbose(self, message, level=1):
        """
        Log verbose
        """
        return self.execute(f"VERBOSE \"{message}\" {level}")

class PresioneUno:
    """
    Classe principal para processar "Presione 1"
    """
    
    def __init__(self):
        self.agi = AGIInterface()
        self.api_base_url = "http://localhost:8000/api"
        self.audio_path = "/var/lib/asterisk/sounds/custom"
        self.max_attempts = 3
        self.digit_timeout = 5000  # 5 segundos
        
    def get_campaign_audio(self, campaign_id):
        """
        Buscar áudio da campanha via API
        """
        try:
            url = f"{self.api_base_url}/audio/list"
            params = {"campaign_id": campaign_id, "audio_type": "greeting"}
            
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data and len(data) > 0:
                    audio_file = data[0]
                    
                    # Converter caminho para formato Asterisk
                    audio_filename = audio_file["filename"].replace(".wav", "")
                    audio_path = f"{self.audio_path}/{audio_filename}"
                    
                    return {
                        "id": audio_file["id"],
                        "filename": audio_filename,
                        "path": audio_path,
                        "duration": audio_file.get("duration", 0)
                    }
            
            return None
            
        except Exception as e:
            logger.error(f"Erro ao buscar áudio da campanha: {e}")
            return None
    
    def log_call_result(self, call_id, campaign_id, result, dtmf_digit=None):
        """
        Registrar resultado da chamada via API
        """
        try:
            url = f"{self.api_base_url}/dialer/call-result"
            data = {
                "call_id": call_id,
                "campaign_id": campaign_id,
                "result": result,
                "dtmf_digit": dtmf_digit,
                "timestamp": datetime.now().isoformat()
            }
            
            response = requests.post(url, json=data, timeout=5)
            
            if response.status_code == 200:
                logger.info(f"Resultado da chamada registrado: {result}")
            else:
                logger.error(f"Erro ao registrar resultado: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Erro ao registrar resultado da chamada: {e}")
    
    def process_dtmf_1(self, call_id, campaign_id):
        """
        Processar quando usuário pressiona 1
        """
        try:
            # Reproduzir mensagem de confirmação
            self.agi.stream_file("custom/transfer-message")
            
            # Aguardar um momento
            time.sleep(1)
            
            # Transferir para operador/fila
            transfer_extension = self.agi.get_variable("TRANSFER_EXTENSION")
            
            if transfer_extension and "200" in transfer_extension:
                # Extrair extensão
                extension = transfer_extension.split()[1]
                
                # Transferir chamada
                self.agi.execute(f"TRANSFER {extension}")
                
                # Registrar sucesso
                self.log_call_result(call_id, campaign_id, "TRANSFER_SUCCESS", "1")
                
                logger.info(f"Chamada transferida para extensão: {extension}")
                
            else:
                # Fallback: reproduzir mensagem de erro
                self.agi.stream_file("custom/transfer-error")
                self.log_call_result(call_id, campaign_id, "TRANSFER_ERROR", "1")
                
        except Exception as e:
            logger.error(f"Erro ao processar DTMF 1: {e}")
            self.log_call_result(call_id, campaign_id, "TRANSFER_ERROR", "1")
    
    def run(self):
        """
        Executar script principal
        """
        try:
            # Obter parâmetros da chamada
            call_id = self.agi.env.get("agi_uniqueid", "unknown")
            campaign_id = self.agi.env.get("agi_arg_1", "1")  # Primeiro argumento
            phone_number = self.agi.env.get("agi_callerid", "unknown")
            
            logger.info(f"Iniciando Presione 1 - Call ID: {call_id}, Campaign: {campaign_id}")
            
            # Atender chamada
            self.agi.answer()
            
            # Aguardar 2 segundos para estabilizar
            time.sleep(2)
            
            # Buscar áudio da campanha
            audio_info = self.get_campaign_audio(campaign_id)
            
            if not audio_info:
                # Usar áudio padrão
                audio_filename = "custom/default-greeting"
                logger.warning(f"Usando áudio padrão: {audio_filename}")
            else:
                audio_filename = audio_info["filename"]
                logger.info(f"Usando áudio da campanha: {audio_filename}")
            
            # Tentar capturar DTMF
            attempts = 0
            dtmf_received = None
            
            while attempts < self.max_attempts and not dtmf_received:
                attempts += 1
                
                logger.info(f"Tentativa {attempts}/{self.max_attempts}")
                
                # Reproduzir áudio e aguardar DTMF
                result = self.agi.get_data(audio_filename, self.digit_timeout, 1)
                
                if result and "200" in result:
                    # Extrair dígito da resposta
                    parts = result.split()
                    if len(parts) >= 2:
                        dtmf_digit = parts[1]
                        
                        if dtmf_digit == "1":
                            logger.info("DTMF '1' recebido com sucesso!")
                            dtmf_received = "1"
                            
                            # Processar presione 1
                            self.process_dtmf_1(call_id, campaign_id)
                            break
                            
                        elif dtmf_digit and dtmf_digit != "":
                            logger.info(f"DTMF '{dtmf_digit}' recebido (não é 1)")
                            
                            # Reproduzir mensagem de opção inválida
                            self.agi.stream_file("custom/invalid-option")
                            
                        else:
                            logger.info("Nenhum DTMF recebido")
                
                # Aguardar antes da próxima tentativa
                if attempts < self.max_attempts:
                    time.sleep(1)
            
            # Verificar resultado final
            if dtmf_received == "1":
                logger.info("Chamada processada com sucesso - DTMF 1 recebido")
            else:
                logger.info("Chamada finalizada - Nenhum DTMF válido recebido")
                
                # Reproduzir mensagem de despedida
                self.agi.stream_file("custom/goodbye")
                
                # Registrar resultado
                self.log_call_result(call_id, campaign_id, "NO_DTMF", None)
            
            # Aguardar 2 segundos antes de finalizar
            time.sleep(2)
            
            # Finalizar chamada
            self.agi.hangup()
            
        except Exception as e:
            logger.error(f"Erro crítico no AGI: {e}")
            
            # Tentar finalizar graciosamente
            try:
                self.agi.stream_file("custom/error")
                self.agi.hangup()
            except:
                pass

def main():
    """
    Função principal
    """
    try:
        presione1 = PresioneUno()
        presione1.run()
        
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 