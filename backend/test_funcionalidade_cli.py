#!/usr/bin/env python3
"""
Script de teste funcional para verificar a implementacao completa do sistema CLI.
"""

import sys
import traceback
from datetime import datetime


def test_imports():
    """Teste 1: Verificar importacoes."""
    print("🔍 Teste 1: Verificando importacoes...")
    
    try:
        # Testar importacao dos modelos
        from app.models.cli import Cli
        print("✅ Modelo Cli importado com sucesso")
        
        # Testar importacao dos schemas
        from app.schemas.cli import (
            CliCreate, CliUpdate, CliResponse, 
            CliBulkAddRequest, CliBulkAddResponse,
            CliStatsResponse, CliRandomResponse
        )
        print("✅ Schemas de CLI importados com sucesso")
        
        # Testar importacao do servico
        from app.services.cli_service import CliService
        print("✅ CliService importado com sucesso")
        
        # Testar importacao das rotas
        from app.routes.cli import router
        print("✅ Router de CLI importado com sucesso")
        
        # Testar importacao no discado service
        from app.services.discado_service import DiscadoService
        print("✅ DiscadoService com integracao CLI importado com sucesso")
        
        return True
        
    except ImportError as e:
        print(f"❌ Erro de importacao: {e}")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")
        return False


def test_model_structure():
    """Teste 2: Verificar estrutura do modelo."""
    print("\n🔍 Teste 2: Verificando estrutura do modelo CLI...")
    
    try:
        from app.models.cli import Cli
        
        # Verificar campos obrigatorios
        campos_obrigatorios = [
            'id', 'numero', 'numero_normalizado', 'activo', 
            'veces_usado', 'fecha_creacion', 'fecha_actualizacion'
        ]
        
        for campo in campos_obrigatorios:
            if hasattr(Cli, campo):
                print(f"✅ Campo {campo} presente")
            else:
                print(f"❌ Campo {campo} ausente")
                return False
        
        # Verificar campos opcionais
        campos_opcionais = ['descripcion', 'notas', 'ultima_vez_usado']
        for campo in campos_opcionais:
            if hasattr(Cli, campo):
                print(f"✅ Campo opcional {campo} presente")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar modelo: {e}")
        return False


def test_schemas():
    """Teste 3: Verificar funcionalidade dos schemas."""
    print("\n🔍 Teste 3: Verificando schemas...")
    
    try:
        from app.schemas.cli import CliCreate, CliResponse, CliRandomResponse
        
        # Testar CliCreate
        cli_create = CliCreate(
            numero="+5491122334455",
            descripcion="CLI de teste"
        )
        print("✅ CliCreate criado com sucesso")
        
        # Verificar validacao
        assert cli_create.numero == "+5491122334455"
        print("✅ Validacao de CLI funcionando")
        
        # Testar CliRandomResponse
        random_response = CliRandomResponse(
            cli_seleccionado="+5491122334455",
            cli_id=1,
            veces_usado=5,
            mensaje="CLI selecionado"
        )
        print("✅ CliRandomResponse criado com sucesso")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao testar schemas: {e}")
        return False


def test_service_methods():
    """Teste 4: Verificar metodos do servico."""
    print("\n🔍 Teste 4: Verificando metodos do CliService...")
    
    try:
        from app.services.cli_service import CliService
        
        # Verificar metodos principais
        metodos_obrigatorios = [
            'generar_cli_aleatorio',
            'agregar_cli',
            'agregar_clis_bulk',
            'listar_clis',
            'atualizar_cli',
            'remover_cli',
            'obter_estatisticas'
        ]
        
        for metodo in metodos_obrigatorios:
            if hasattr(CliService, metodo):
                print(f"✅ Metodo {metodo} presente")
            else:
                print(f"❌ Metodo {metodo} ausente")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar service: {e}")
        return False


def test_discado_integration():
    """Teste 5: Verificar integracao com discado."""
    print("\n🔍 Teste 5: Verificando integracao com discado...")
    
    try:
        from app.services.discado_service import DiscadoService
        
        # Verificar se DiscadoService tem CliService
        import inspect
        init_signature = inspect.signature(DiscadoService.__init__)
        
        # Verificar se iniciar_llamada aceita cli_personalizado
        metodo_llamada = getattr(DiscadoService, 'iniciar_llamada')
        llamada_signature = inspect.signature(metodo_llamada)
        
        if 'cli_personalizado' in llamada_signature.parameters:
            print("✅ Metodo iniciar_llamada aceita cli_personalizado")
        else:
            print("❌ Metodo iniciar_llamada nao aceita cli_personalizado")
            return False
        
        # Verificar metodo llamar_siguiente_de_lista
        metodo_siguiente = getattr(DiscadoService, 'llamar_siguiente_de_lista')
        siguiente_signature = inspect.signature(metodo_siguiente)
        
        if 'cli_personalizado' in siguiente_signature.parameters:
            print("✅ Metodo llamar_siguiente_de_lista aceita cli_personalizado")
        else:
            print("❌ Metodo llamar_siguiente_de_lista nao aceita cli_personalizado")
            return False
        
        print("✅ Integracao com discado verificada")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar integracao: {e}")
        traceback.print_exc()
        return False


def test_routes():
    """Teste 6: Verificar endpoints das rotas."""
    print("\n🔍 Teste 6: Verificando endpoints de CLI...")
    
    try:
        from app.routes.cli import router
        
        # Obter todas as rotas
        routes = [route for route in router.routes if hasattr(route, 'path')]
        
        # Endpoints esperados
        endpoints_esperados = [
            '/generar-aleatorio',
            '/agregar',
            '/agregar-bulk',
            '/',
            '/estadisticas'
        ]
        
        for endpoint in endpoints_esperados:
            encontrado = any(route.path == endpoint for route in routes)
            if encontrado:
                print(f"✅ Endpoint {endpoint} presente")
            else:
                print(f"❌ Endpoint {endpoint} ausente")
                return False
        
        print(f"✅ Total de {len(routes)} rotas configuradas")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar rotas: {e}")
        return False


def test_file_structure():
    """Teste 7: Verificar estrutura de arquivos."""
    print("\n🔍 Teste 7: Verificando estrutura de arquivos...")
    
    import os
    
    arquivos_esperados = [
        'app/models/cli.py',
        'app/schemas/cli.py', 
        'app/services/cli_service.py',
        'app/routes/cli.py',
        'migrations/create_cli_table.sql',
        'tests/test_cli.py'
    ]
    
    for arquivo in arquivos_esperados:
        if os.path.exists(arquivo):
            print(f"✅ Arquivo {arquivo} existe")
        else:
            print(f"❌ Arquivo {arquivo} nao encontrado")
            return False
    
    return True


def test_main_integration():
    """Teste 8: Verificar integracao no main.py."""
    print("\n🔍 Teste 8: Verificando integracao no main.py...")
    
    try:
        # Verificar se main.py importa as rotas CLI
        with open('main.py', 'r', encoding='utf-8') as f:
            conteudo = f.read()
        
        if 'from app.routes import' in conteudo and 'cli' in conteudo:
            print("✅ Importacao das rotas CLI presente no main.py")
        else:
            print("❌ Importacao das rotas CLI ausente no main.py")
            return False
        
        if 'cli.router' in conteudo:
            print("✅ Router CLI incluido no main.py")
        else:
            print("❌ Router CLI nao incluido no main.py")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao verificar main.py: {e}")
        return False


def main():
    """Funcao principal para executar todos os testes."""
    print("🚀 INICIANDO TESTES DE FUNCIONALIDADE CLI")
    print("=" * 60)
    
    testes = [
        test_imports,
        test_model_structure,
        test_schemas,
        test_service_methods,
        test_discado_integration,
        test_routes,
        test_file_structure,
        test_main_integration
    ]
    
    sucessos = 0
    total = len(testes)
    
    for i, teste in enumerate(testes, 1):
        try:
            resultado = teste()
            if resultado:
                sucessos += 1
            print(f"\n{'✅' if resultado else '❌'} Teste {i}/{total} {'PASSOU' if resultado else 'FALHOU'}")
        except Exception as e:
            print(f"\n❌ Teste {i}/{total} FALHOU com erro: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print(f"📊 RESUMO DOS TESTES:")
    print(f"   Sucessos: {sucessos}/{total}")
    print(f"   Taxa de sucesso: {(sucessos/total)*100:.1f}%")
    
    if sucessos == total:
        print("🎉 TODOS OS TESTES PASSARAM! Sistema CLI implementado com sucesso!")
        return 0
    else:
        print("⚠️  Alguns testes falharam. Verificar implementacao.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⏹️  Testes interrompidos pelo usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Erro fatal durante os testes: {e}")
        traceback.print_exc()
        sys.exit(1) 