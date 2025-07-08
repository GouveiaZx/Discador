#!/usr/bin/env python3
"""
Script para popular o banco de dados com dados de exemplo.

Este script cria:
- Lista de números de exemplo
- Campanhas de exemplo
- Configurações básicas

Uso:
    python scripts/populate_sample_data.py
"""

import sys
import os
from datetime import datetime

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import configuracao
from app.models.lista_llamadas import ListaLlamadas, NumeroLlamada
from app.models.campana_presione1 import CampanaPresione1

def popular_dados_exemplo():
    """Popula o banco com dados de exemplo."""
    
    # Criar engine e sessão
    engine = create_engine(configuracao.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        print("🔄 Populando banco de dados com dados de exemplo...")
        
        # 1. Criar lista de números de exemplo
        print("\n📞 Criando lista de números de exemplo...")
        
        # Verificar se já existe
        lista_existente = db.query(ListaLlamadas).filter(
            ListaLlamadas.nombre == "Lista Exemplo Sistema"
        ).first()
        
        if not lista_existente:
            nova_lista = ListaLlamadas(
                nombre="Lista Exemplo Sistema",
                descripcion="Lista com números de exemplo para testes do sistema",
                activa=True,
                notas="Criada automaticamente pelo script de inicialização"
            )
            
            db.add(nova_lista)
            db.commit()
            db.refresh(nova_lista)
            
            print(f"✅ Lista criada com ID: {nova_lista.id}")
            
            # Adicionar números de exemplo
            numeros_exemplo = [
                "+5511999999001",  # Número que atende e pressiona 1
                "+5511999999002",  # Número que atende mas não pressiona
                "+5511999999003",  # Número que vai para voicemail
                "+5511999999004",  # Número que não atende
                "+5511999999005",  # Número que atende e pressiona 1
                "+5511888888001",  # Número para teste de voicemail
                "+5511888888002",  # Número para teste de voicemail
                "+5511777777001",  # Número que desliga durante áudio
                "+5511777777002",  # Número que pressiona outras teclas
                "+5511666666001",  # Número para teste de transferência
            ]
            
            for numero in numeros_exemplo:
                numero_obj = NumeroLlamada(
                    id_lista=nova_lista.id,
                    numero=numero,
                    numero_normalizado=numero,
                    valido=True,
                    observaciones=f"Número de exemplo criado em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                )
                db.add(numero_obj)
            
            db.commit()
            print(f"✅ Adicionados {len(numeros_exemplo)} números de exemplo")
            
        else:
            print(f"⚠️  Lista já existe com ID: {lista_existente.id}")
            nova_lista = lista_existente
        
        # 2. Criar campanha de exemplo
        print("\n🎯 Criando campanha de exemplo...")
        
        campana_existente = db.query(CampanaPresione1).filter(
            CampanaPresione1.nombre == "Campanha Demo Sistema"
        ).first()
        
        if not campana_existente:
            nova_campana = CampanaPresione1(
                nombre="Campanha Demo Sistema",
                descripcion="Campanha de demonstração com detecção de voicemail",
                lista_llamadas_id=nova_lista.id,
                mensaje_audio_url="/var/lib/asterisk/sounds/custom/presione1_demo.wav",
                timeout_presione1=10,
                
                # Configuração de voicemail
                detectar_voicemail=True,
                mensaje_voicemail_url="/var/lib/asterisk/sounds/custom/voicemail_demo.wav",
                duracion_minima_voicemail=3,
                duracion_maxima_voicemail=30,
                
                # Configuração de transferência
                extension_transferencia="100",
                
                # Configuração de discado
                llamadas_simultaneas=2,
                tiempo_entre_llamadas=5,
                
                # Estado inicial
                activa=False,
                pausada=False,
                
                notas="Campanha criada automaticamente para demonstração do sistema"
            )
            
            db.add(nova_campana)
            db.commit()
            db.refresh(nova_campana)
            
            print(f"✅ Campanha criada com ID: {nova_campana.id}")
            
        else:
            print(f"⚠️  Campanha já existe com ID: {campana_existente.id}")
        
        # 3. Criar campanha apenas com pessoa (sem voicemail)
        print("\n👤 Criando campanha sem voicemail...")
        
        campana_sem_vm = db.query(CampanaPresione1).filter(
            CampanaPresione1.nombre == "Campanha Apenas Pessoas"
        ).first()
        
        if not campana_sem_vm:
            campana_pessoas = CampanaPresione1(
                nombre="Campanha Apenas Pessoas",
                descripcion="Campanha tradicional sem detecção de voicemail",
                lista_llamadas_id=nova_lista.id,
                mensaje_audio_url="/var/lib/asterisk/sounds/custom/presione1_demo.wav",
                timeout_presione1=15,
                
                # Voicemail desabilitado
                detectar_voicemail=False,
                mensaje_voicemail_url=None,
                duracion_minima_voicemail=3,
                duracion_maxima_voicemail=30,
                
                # Transferência para fila
                extension_transferencia=None,
                cola_transferencia="vendas",
                
                # Configuração conservadora
                llamadas_simultaneas=1,
                tiempo_entre_llamadas=8,
                
                activa=False,
                pausada=False,
                
                notas="Campanha sem voicemail para comparação de resultados"
            )
            
            db.add(campana_pessoas)
            db.commit()
            
            print(f"✅ Campanha sem voicemail criada")
            
        else:
            print(f"⚠️  Campanha sem voicemail já existe")
        
        print("\n🎉 Dados de exemplo populados com sucesso!")
        print("\n📋 Resumo do que foi criado:")
        print(f"  📞 Lista: {nova_lista.nombre} (ID: {nova_lista.id})")
        print(f"  📊 Números: {len(numeros_exemplo)} números de teste")
        print(f"  🎯 Campanhas: 2 campanhas de exemplo")
        print("\n🔗 Próximos passos:")
        print("  1. Iniciar o sistema: ./start.sh")
        print("  2. Acessar documentação: http://localhost:8000/docs")
        print("  3. Executar testes: python scripts/teste_voicemail.py")
        
    except Exception as e:
        print(f"❌ Erro ao popular dados: {str(e)}")
        db.rollback()
        return False
        
    finally:
        db.close()
    
    return True


def verificar_dados():
    """Verifica se os dados foram criados corretamente."""
    
    engine = create_engine(configuracao.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Verificar listas
        listas = db.query(ListaLlamadas).count()
        numeros = db.query(NumeroLlamada).count()
        campanhas = db.query(CampanaPresione1).count()
        
        print(f"\n📊 Status do banco de dados:")
        print(f"  📞 Listas de chamadas: {listas}")
        print(f"  🔢 Números cadastrados: {numeros}")
        print(f"  🎯 Campanhas criadas: {campanhas}")
        
        if listas > 0 and numeros > 0 and campanhas > 0:
            print("✅ Banco de dados configurado corretamente!")
            return True
        else:
            print("⚠️  Banco de dados pode estar incompleto")
            return False
            
    except Exception as e:
        print(f"❌ Erro ao verificar dados: {str(e)}")
        return False
        
    finally:
        db.close()


def limpar_dados_exemplo():
    """Remove todos os dados de exemplo (use com cuidado!)."""
    
    print("⚠️  ATENÇÃO: Esta operação removerá TODOS os dados de exemplo!")
    confirmacao = input("Digite 'CONFIRMAR' para continuar: ")
    
    if confirmacao != "CONFIRMAR":
        print("❌ Operação cancelada")
        return False
    
    engine = create_engine(configuracao.DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Remover campanhas de exemplo
        campanhas_removidas = db.query(CampanaPresione1).filter(
            CampanaPresione1.nombre.in_([
                "Campanha Demo Sistema",
                "Campanha Apenas Pessoas"
            ])
        ).delete(synchronize_session=False)
        
        # Remover lista e números de exemplo
        lista_exemplo = db.query(ListaLlamadas).filter(
            ListaLlamadas.nombre == "Lista Exemplo Sistema"
        ).first()
        
        numeros_removidos = 0
        if lista_exemplo:
            numeros_removidos = db.query(NumeroLlamada).filter(
                NumeroLlamada.id_lista == lista_exemplo.id
            ).delete(synchronize_session=False)
            
            db.delete(lista_exemplo)
        
        db.commit()
        
        print(f"✅ Dados removidos com sucesso:")
        print(f"  🗑️  Campanhas: {campanhas_removidas}")
        print(f"  🗑️  Números: {numeros_removidos}")
        print(f"  🗑️  Listas: {1 if lista_exemplo else 0}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao limpar dados: {str(e)}")
        db.rollback()
        return False
        
    finally:
        db.close()


def main():
    """Função principal."""
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--verificar":
            return verificar_dados()
        elif sys.argv[1] == "--limpar":
            return limpar_dados_exemplo()
        elif sys.argv[1] == "--help":
            print("Uso:")
            print("  python scripts/populate_sample_data.py           # Popular dados")
            print("  python scripts/populate_sample_data.py --verificar # Verificar dados")
            print("  python scripts/populate_sample_data.py --limpar    # Limpar dados")
            return True
    
    # Comportamento padrão: popular dados
    return popular_dados_exemplo()


if __name__ == "__main__":
    sucesso = main()
    sys.exit(0 if sucesso else 1) 