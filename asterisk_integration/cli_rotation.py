#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AGI Script para Rotação Inteligente de CLIs
Sistema Discador Preditivo
"""

import sys
import requests
import json
import random
from datetime import datetime

class AsteriskAGI:
    """Classe para interação com Asterisk via AGI"""
    
    def __init__(self):
        self.variables = {}
        self.read_variables()
    
    def read_variables(self):
        """Ler variáveis do Asterisk"""
        while True:
            line = sys.stdin.readline().strip()
            if line == '':
                break
            if ':' in line:
                key, value = line.split(':', 1)
                self.variables[key.strip()] = value.strip()
    
    def set_variable(self, name, value):
        """Definir variável no Asterisk"""
        print(f'SET VARIABLE {name} "{value}"')
        sys.stdout.flush()
        return sys.stdin.readline().strip()
    
    def verbose(self, message, level=1):
        """Enviar mensagem verbose para Asterisk"""
        print(f'VERBOSE "{message}" {level}')
        sys.stdout.flush()
        return sys.stdin.readline().strip()

class CLIRotation:
    """Sistema de rotação de CLIs"""
    
    def __init__(self):
        self.api_url = "https://discador.onrender.com/api/v1"
        self.clis_disponiveis = [
            {
                "cli": "+5511999887766",
                "trunk": "trunk_principal",
                "prioridade": 1,
                "ativo": True,
                "max_chamadas_simultaneas": 10,
                "chamadas_ativas": 0
            },
            {
                "cli": "+5511888776655", 
                "trunk": "trunk_secundario",
                "prioridade": 2,
                "ativo": True,
                "max_chamadas_simultaneas": 8,
                "chamadas_ativas": 0
            },
            {
                "cli": "+5511777665544",
                "trunk": "trunk_principal",
                "prioridade": 3,
                "ativo": True,
                "max_chamadas_simultaneas": 5,
                "chamadas_ativas": 0
            }
        ]
    
    def obter_clis_disponiveis(self):
        """Obter CLIs disponíveis da API"""
        try:
            response = requests.get(f"{self.api_url}/code2base/clis", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'clis' in data:
                    return data['clis']
        except Exception as e:
            self.log_error(f"Erro ao obter CLIs da API: {e}")
        
        # Fallback para CLIs locais
        return self.clis_disponiveis
    
    def selecionar_cli_inteligente(self, numero_destino):
        """Selecionar CLI baseado em algoritmo inteligente"""
        clis = self.obter_clis_disponiveis()
        
        # Filtrar CLIs ativos e disponíveis
        clis_disponiveis = [
            cli for cli in clis 
            if cli.get('ativo', True) and 
               cli.get('chamadas_ativas', 0) < cli.get('max_chamadas_simultaneas', 10)
        ]
        
        if not clis_disponiveis:
            # Se nenhum CLI disponível, usar o primeiro ativo
            clis_disponiveis = [cli for cli in clis if cli.get('ativo', True)]
        
        if not clis_disponiveis:
            raise Exception("Nenhum CLI disponível")
        
        # Algoritmo de seleção:
        # 1. Prioridade por menor uso
        # 2. Balanceamento de carga
        # 3. Rotação circular como fallback
        
        # Ordenar por prioridade e uso
        clis_ordenados = sorted(
            clis_disponiveis,
            key=lambda x: (
                x.get('chamadas_ativas', 0) / max(x.get('max_chamadas_simultaneas', 1), 1),
                x.get('prioridade', 999)
            )
        )
        
        cli_selecionado = clis_ordenados[0]
        
        # Log da seleção
        self.log_selection(cli_selecionado, numero_destino)
        
        return cli_selecionado
    
    def log_selection(self, cli, numero_destino):
        """Registrar seleção de CLI"""
        log_data = {
            "timestamp": datetime.now().isoformat(),
            "numero_destino": numero_destino,
            "cli_selecionado": cli.get('numero', cli.get('cli')),
            "trunk_selecionado": cli.get('trunk', 'trunk_principal'),
            "prioridade": cli.get('prioridade', 1),
            "chamadas_ativas": cli.get('chamadas_ativas', 0)
        }
        
        try:
            # Tentar enviar log para API
            requests.post(
                f"{self.api_url}/logs/cli-rotation",
                json=log_data,
                timeout=2
            )
        except:
            # Se falhar, continuar sem logging
            pass
    
    def log_error(self, message):
        """Registrar erro"""
        error_data = {
            "timestamp": datetime.now().isoformat(),
            "error": message,
            "script": "cli_rotation.py"
        }
        
        try:
            requests.post(
                f"{self.api_url}/logs/errors",
                json=error_data,
                timeout=2
            )
        except:
            pass

def main():
    """Função principal do AGI"""
    try:
        # Inicializar AGI
        agi = AsteriskAGI()
        
        # Obter número de destino
        numero_destino = sys.argv[1] if len(sys.argv) > 1 else agi.variables.get('agi_extension', '')
        
        if not numero_destino:
            raise Exception("Número de destino não fornecido")
        
        # Inicializar sistema de rotação
        rotacao = CLIRotation()
        
        # Selecionar CLI
        agi.verbose(f"Selecionando CLI para {numero_destino}")
        cli_selecionado = rotacao.selecionar_cli_inteligente(numero_destino)
        
        # Definir variáveis no Asterisk
        cli_numero = cli_selecionado.get('numero', cli_selecionado.get('cli', '+5511999887766'))
        trunk_nome = cli_selecionado.get('trunk', 'trunk_principal')
        
        agi.set_variable('CLI_SELECTED', cli_numero)
        agi.set_variable('TRUNK_SELECTED', trunk_nome)
        
        agi.verbose(f"CLI selecionado: {cli_numero} via {trunk_nome}")
        
        # Incrementar contador de chamadas ativas (seria feito na API em produção)
        
    except Exception as e:
        # Em caso de erro, usar CLI padrão
        agi = AsteriskAGI()
        agi.verbose(f"Erro na rotação de CLI: {e}")
        agi.set_variable('CLI_SELECTED', '+5511999887766')
        agi.set_variable('TRUNK_SELECTED', 'trunk_principal')

if __name__ == "__main__":
    main() 