#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGI Script para Integracao Multi-SIP com Asterisk
Selecao dinamica de provedores SIP para chamadas de saida
"""

import sys
import os
import requests
import json
import logging
from typing import Dict, Any, Optional

# Configuracao de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/asterisk/multi_sip_agi.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('MultiSipAGI')

class AsteriskAGI:
    """Classe para comunicacao AGI com Asterisk"""
    
    def __init__(self):
        self.variables = {}
        self._read_variables()
    
    def _read_variables(self):
        """Le variaveis do ambiente AGI"""
        while True:
            line = sys.stdin.readline().strip()
            if line == '':
                break
            
            if ':' in line:
                key, value = line.split(':', 1)
                self.variables[key.strip()] = value.strip()
        
        logger.info(f"Variaveis AGI carregadas: {self.variables}")
    
    def get_variable(self, var_name: str) -> Optional[str]:
        """Obtem valor de uma variavel do Asterisk"""
        sys.stdout.write(f'GET VARIABLE {var_name}\n')
        sys.stdout.flush()
        
        response = sys.stdin.readline().strip()
        if response.startswith('200 result=1'):
            # Extrair valor entre parenteses
            start = response.find('(') + 1
            end = response.find(')')
            if start > 0 and end > start:
                return response[start:end]
        
        return None
    
    def set_variable(self, var_name: str, value: str):
        """Define valor de uma variavel no Asterisk"""
        sys.stdout.write(f'SET VARIABLE {var_name} "{value}"\n')
        sys.stdout.flush()
        sys.stdin.readline()  # Ler resposta
    
    def verbose(self, message: str, level: int = 1):
        """Envia mensagem verbose para Asterisk"""
        sys.stdout.write(f'VERBOSE "{message}" {level}\n')
        sys.stdout.flush()
        sys.stdin.readline()  # Ler resposta
    
    def hangup(self):
        """Desliga a chamada"""
        sys.stdout.write('HANGUP\n')
        sys.stdout.flush()
        sys.stdin.readline()

class MultiSipSelector:
    """Seletor inteligente de provedores SIP"""
    
    def __init__(self, api_base_url: str = "http://localhost:8000"):
        self.api_base_url = api_base_url
        self.timeout = 10
    
    def selecionar_provedor(self, numero_destino: str, campanha_id: Optional[int] = None,
                          metodo_selecao: str = "inteligente") -> Optional[Dict[str, Any]]:
        """Seleciona provedor via API do sistema"""
        try:
            url = f"{self.api_base_url}/api/multi-sip/selecionar-provedor"
            
            payload = {
                "numero_destino": numero_destino,
                "campanha_id": campanha_id,
                "metodo_selecao": metodo_selecao,
                "duracao_estimada_segundos": 60
            }
            
            logger.info(f"Solicitando selecao de provedor para {numero_destino}")
            
            response = requests.post(
                url, 
                json=payload, 
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                resultado = response.json()
                logger.info(f"Provedor selecionado: {resultado['provedor_selecionado']['nome']}")
                return resultado
            else:
                logger.error(f"Erro na API: {response.status_code} - {response.text}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro de conexao com API: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Erro inesperado: {str(e)}")
            return None
    
    def registrar_resultado(self, uuid_selecao: str, resultado: Dict[str, Any]):
        """Registra resultado da chamada na API"""
        try:
            url = f"{self.api_base_url}/api/multi-sip/selecionar-provedor/resultado"
            
            params = {"uuid_selecao": uuid_selecao}
            
            response = requests.post(
                url,
                params=params,
                json=resultado,
                timeout=self.timeout
            )
            
            if response.status_code == 204:
                logger.info(f"Resultado registrado para selecao {uuid_selecao}")
            else:
                logger.warning(f"Falha ao registrar resultado: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Erro ao registrar resultado: {str(e)}")

def construir_dial_string(provedor: Dict[str, Any], numero_destino: str) -> str:
    """Constroi string de discagem para Asterisk"""
    provedor_data = provedor['provedor_selecionado']
    
    # Formato basico: SIP/numero@provedor
    # Pode ser personalizado conforme configuracao do Asterisk
    
    if provedor_data['tipo_provedor'] == 'twilio':
        # Para Twilio, formato especial
        return f"SIP/{numero_destino}@twilio-trunk"
    
    elif provedor_data['tipo_provedor'] == 'gottrunk':
        # Para GoTrunk
        return f"SIP/{numero_destino}@gottrunk-{provedor_data['codigo']}"
    
    elif provedor_data['tipo_provedor'] == 'asterisk_peer':
        # Para peer Asterisk local
        return f"SIP/{numero_destino}@{provedor_data['codigo']}"
    
    else:
        # Formato generico
        codigo = provedor_data['codigo'].lower()
        return f"SIP/{numero_destino}@{codigo}"

def aplicar_configuracoes_canal(agi: AsteriskAGI, provedor: Dict[str, Any]):
    """Aplica configuracoes especificas do provedor ao canal"""
    provedor_data = provedor['provedor_selecionado']
    
    # Definir timeout baseado no provedor
    timeout_segundos = provedor_data.get('timeout_conexao', 30)
    agi.set_variable('TIMEOUT_DIAL', str(timeout_segundos))
    
    # Configurar codec preferido se especificado
    if 'configuracoes_extras' in provedor_data:
        configuracoes = provedor_data['configuracoes_extras']
        if isinstance(configuracoes, dict):
            if 'codec_preferido' in configuracoes:
                agi.set_variable('SIP_CODEC', configuracoes['codec_preferido'])
    
    # Definir variaveis de contexto para logs
    agi.set_variable('MULTISIP_PROVEDOR_ID', str(provedor_data['id']))
    agi.set_variable('MULTISIP_PROVEDOR_NOME', provedor_data['nome'])
    agi.set_variable('MULTISIP_UUID_SELECAO', str(provedor['uuid_selecao']))
    agi.set_variable('MULTISIP_CUSTO_ESTIMADO', str(provedor['custo_estimado']))

def main():
    """Funcao principal do AGI"""
    agi = AsteriskAGI()
    selector = MultiSipSelector()
    
    try:
        # Obter dados da chamada
        numero_destino = agi.get_variable('EXTEN') or agi.variables.get('agi_extension', '')
        caller_id = agi.get_variable('CALLERID(num)') or agi.variables.get('agi_callerid', '')
        campanha_id = agi.get_variable('CAMPANHA_ID')
        metodo_selecao = agi.get_variable('METODO_SELECAO') or 'inteligente'
        
        if not numero_destino:
            agi.verbose("ERRO: Numero de destino nao fornecido", 1)
            agi.hangup()
            return
        
        agi.verbose(f"Iniciando selecao de provedor para {numero_destino}", 2)
        
        # Converter campanha_id se fornecido
        campanha_id_int = None
        if campanha_id and campanha_id.isdigit():
            campanha_id_int = int(campanha_id)
        
        # Selecionar provedor
        resultado_selecao = selector.selecionar_provedor(
            numero_destino=numero_destino,
            campanha_id=campanha_id_int,
            metodo_selecao=metodo_selecao
        )
        
        if not resultado_selecao:
            agi.verbose("ERRO: Nao foi possivel selecionar provedor", 1)
            agi.set_variable('MULTISIP_ERROR', 'SELECTION_FAILED')
            agi.hangup()
            return
        
        # Aplicar configuracoes do provedor
        aplicar_configuracoes_canal(agi, resultado_selecao)
        
        # Construir string de discagem
        dial_string = construir_dial_string(resultado_selecao, numero_destino)
        
        agi.verbose(f"Provedor selecionado: {resultado_selecao['provedor_selecionado']['nome']}", 2)
        agi.verbose(f"String de discagem: {dial_string}", 2)
        agi.verbose(f"Custo estimado: {resultado_selecao['custo_estimado']}", 2)
        
        # Definir variavel com string de discagem para uso no dialplan
        agi.set_variable('MULTISIP_DIAL_STRING', dial_string)
        agi.set_variable('MULTISIP_SUCCESS', '1')
        
        logger.info(f"Selecao concluida: {resultado_selecao['provedor_selecionado']['nome']} para {numero_destino}")
        
    except Exception as e:
        error_msg = f"Erro no AGI Multi-SIP: {str(e)}"
        logger.error(error_msg)
        agi.verbose(error_msg, 1)
        agi.set_variable('MULTISIP_ERROR', 'INTERNAL_ERROR')
        agi.hangup()

if __name__ == '__main__':
    main() 