#!/usr/bin/env python3
# Teste direto da funcionalidade de pausar sem servidor

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    print("🔍 Testando funcionalidade de pausar diretamente...")
    
    # Importar o serviço diretamente
    from app.services.presione1_service import PresionE1Service
    print("✅ PresionE1Service importado com sucesso")
    
    # Criar instância do serviço
    service = PresionE1Service()
    print("✅ Instância do serviço criada")
    
    # Testar se o método existe
    if hasattr(service, 'pausar_campana'):
        print("✅ Método pausar_campana existe")
        
        # Simular uma chamada de pausar
        print("\n🔧 Simulando pausar campanha ID 1...")
        
        # Verificar se a campanha existe primeiro
        try:
            campanha = service.obter_campana(1)
            if campanha:
                print(f"✅ Campanha encontrada: {campanha.get('nome', 'N/A')}")
                
                # Tentar pausar (assinatura correta: campana_id, pausar, motivo)
                import asyncio
                resultado = asyncio.run(service.pausar_campana(1, True, 'Teste direto'))
                print(f"✅ Resultado de pausar: {resultado}")
                
                # Verificar status após pausar
                campanha_atualizada = service.obter_campana(1)
                if campanha_atualizada:
                    print(f"📊 Status após pausar: pausada={campanha_atualizada.get('pausada', 'N/A')}")
                
            else:
                print("⚠️ Campanha ID 1 não encontrada")
                
        except Exception as e:
            print(f"❌ Erro ao testar pausar: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ Método pausar_campana não encontrado")
        
except ImportError as e:
    print(f"❌ Erro de importação: {e}")
except Exception as e:
    print(f"❌ Erro geral: {e}")
    import traceback
    traceback.print_exc()