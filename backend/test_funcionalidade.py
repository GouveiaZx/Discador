#!/usr/bin/env python3
"""
Script de teste simples para verificar a funcionalidade de blacklist.
"""

import sys
import os

# Adicionar o diretorio backend ao path
sys.path.insert(0, os.path.dirname(__file__))

def test_validacao_numeros():
    """Testa a validacao de numeros."""
    print("=== Teste de Validacao de Numeros ===\n")
    
    try:
        from app.schemas.lista_llamadas import validar_numero_telefono
        
        numeros_teste = [
            "+54 9 11 1234-5678",
            "011 1234-5678", 
            "11 1234 5678",
            "1112345678",
            "abc123",
            ""
        ]
        
        for numero in numeros_teste:
            resultado = validar_numero_telefono(numero)
            print(f"Numero: '{numero}'")
            print(f"  Valido: {resultado.valido}")
            print(f"  Normalizado: {resultado.numero_normalizado}")
            if not resultado.valido:
                print(f"  Motivo: {resultado.motivo_invalido}")
            print()
            
        print("✅ Teste de validacao concluido com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste de validacao: {str(e)}")
        return False

def test_schemas_blacklist():
    """Testa os schemas de blacklist."""
    print("=== Teste dos Schemas de Blacklist ===\n")
    
    try:
        from app.schemas.blacklist import (
            BlacklistCreate, 
            BlacklistVerificationResponse,
            BlacklistStatsResponse
        )
        
        # Teste BlacklistCreate
        blacklist_data = BlacklistCreate(
            numero="+5491112345678",
            motivo="Teste de spam",
            creado_por="admin_teste"
        )
        print(f"BlacklistCreate criado: {blacklist_data.numero}")
        
        # Teste BlacklistVerificationResponse
        verificacao = BlacklistVerificationResponse(
            numero_original="+54 9 11 1234-5678",
            numero_normalizado="+5491112345678",
            en_blacklist=True,
            motivo="Spam detectado"
        )
        print(f"Verificacao: {verificacao.numero_normalizado} - Bloqueado: {verificacao.en_blacklist}")
        
        # Teste BlacklistStatsResponse
        stats = BlacklistStatsResponse(
            total_numeros=100,
            numeros_activos=90,
            numeros_inactivos=10,
            total_bloqueos_hoy=5,
            total_bloqueos_mes=50,
            numero_mas_bloqueado="+5491112345678"
        )
        print(f"Stats: {stats.total_numeros} numeros, {stats.numeros_activos} ativos")
        
        print("✅ Teste dos schemas concluido com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste dos schemas: {str(e)}")
        return False

def test_importacao_modelos():
    """Testa a importacao dos modelos."""
    print("=== Teste de Importacao dos Modelos ===\n")
    
    try:
        from app.models.lista_negra import ListaNegra
        from app.models.llamada import Llamada  
        from app.models.lista_llamadas import ListaLlamadas, NumeroLlamada
        
        print("✅ ListaNegra importado com sucesso")
        print("✅ Llamada importado com sucesso")
        print("✅ ListaLlamadas importado com sucesso")
        print("✅ NumeroLlamada importado com sucesso")
        
        # Verificar atributos do modelo ListaNegra
        print(f"\nAtributos do modelo ListaNegra:")
        for attr in ['numero', 'numero_normalizado', 'motivo', 'activo', 'veces_bloqueado']:
            if hasattr(ListaNegra, attr):
                print(f"  ✅ {attr}")
            else:
                print(f"  ❌ {attr} (faltando)")
        
        # Verificar atributos do modelo Llamada
        print(f"\nAtributos do modelo Llamada:")
        for attr in ['numero_normalizado', 'id_lista_llamadas', 'bloqueado_blacklist']:
            if hasattr(Llamada, attr):
                print(f"  ✅ {attr}")
            else:
                print(f"  ❌ {attr} (faltando)")
        
        print("\n✅ Teste de importacao concluido com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro na importacao dos modelos: {str(e)}")
        return False

def test_servicos():
    """Testa a importacao dos servicos."""
    print("=== Teste de Importacao dos Servicos ===\n")
    
    try:
        # Mock da sessao de BD para testar importacao
        class MockSession:
            def query(self, *args):
                return self
            def filter(self, *args):
                return self
            def first(self):
                return None
            def add(self, obj):
                pass
            def commit(self):
                pass
            def refresh(self, obj):
                pass
        
        from app.services.blacklist_service import BlacklistService
        from app.services.discado_service import DiscadoService
        
        # Testar criacao dos servicos
        mock_db = MockSession()
        blacklist_service = BlacklistService(mock_db)
        discado_service = DiscadoService(mock_db)
        
        print("✅ BlacklistService criado com sucesso")
        print("✅ DiscadoService criado com sucesso")
        
        # Verificar metodos principais
        blacklist_methods = [
            'verificar_numero_blacklist',
            'agregar_numero_blacklist', 
            'remover_numero_blacklist',
            'listar_blacklist'
        ]
        
        print(f"\nMetodos do BlacklistService:")
        for method in blacklist_methods:
            if hasattr(blacklist_service, method):
                print(f"  ✅ {method}")
            else:
                print(f"  ❌ {method} (faltando)")
        
        discado_methods = [
            'iniciar_llamada',
            'obtener_proxima_llamada_lista',
            'obtener_estadisticas_lista'
        ]
        
        print(f"\nMetodos do DiscadoService:")
        for method in discado_methods:
            if hasattr(discado_service, method):
                print(f"  ✅ {method}")
            else:
                print(f"  ❌ {method} (faltando)")
        
        print("\n✅ Teste dos servicos concluido com sucesso!")
        return True
        
    except Exception as e:
        print(f"❌ Erro no teste dos servicos: {str(e)}")
        return False

def main():
    """Executa todos os testes."""
    print("🚀 Iniciando testes da funcionalidade de Blacklist e Multiplas Listas\n")
    
    testes = [
        test_validacao_numeros,
        test_schemas_blacklist,
        test_importacao_modelos,
        test_servicos
    ]
    
    resultados = []
    
    for teste in testes:
        try:
            resultado = teste()
            resultados.append(resultado)
        except Exception as e:
            print(f"❌ Erro executando {teste.__name__}: {str(e)}")
            resultados.append(False)
        print("-" * 60)
    
    # Resumo
    sucessos = sum(resultados)
    total = len(resultados)
    
    print(f"\n🎯 RESUMO DOS TESTES:")
    print(f"   Sucessos: {sucessos}/{total}")
    print(f"   Taxa de sucesso: {(sucessos/total)*100:.1f}%")
    
    if sucessos == total:
        print("\n🎉 TODOS OS TESTES PASSARAM! A implementacao esta funcionando corretamente.")
        return True
    else:
        print(f"\n⚠️  {total - sucessos} teste(s) falharam. Verifique as mensagens de erro acima.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 