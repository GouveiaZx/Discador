#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para configurar dados iniciais do Sistema Discador Preditivo
"""

import os
import sys
import asyncio
from datetime import datetime, timedelta

# Adicionar o diretório raiz ao path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import get_db
from sqlalchemy.orm import Session

# Dados iniciais para popular o banco
INITIAL_DATA = {
    "roles": [
        {"id": 1, "name": "admin", "description": "Administrador do sistema", "permissions": "all"},
        {"id": 2, "name": "supervisor", "description": "Supervisor de campanhas", "permissions": "campaigns,monitoring,lists"},
        {"id": 3, "name": "operator", "description": "Operador básico", "permissions": "monitoring"}
    ],
    
    "trunks": [
        {
            "id": 1,
            "name": "Trunk Principal",
            "provider": "Provider1",
            "host": "sip.provider1.com",
            "port": 5060,
            "username": "trunk_user1",
            "password": "trunk_pass1",
            "max_channels": 30,
            "active": True
        },
        {
            "id": 2,
            "name": "Trunk Secundário",
            "provider": "Provider2", 
            "host": "sip.provider2.com",
            "port": 5060,
            "username": "trunk_user2",
            "password": "trunk_pass2",
            "max_channels": 20,
            "active": True
        }
    ],
    
    "audios": [
        {
            "id": 1,
            "name": "Áudio Principal",
            "description": "Áudio principal para campanhas",
            "file_path": "/audios/principal.wav",
            "duration_seconds": 30,
            "active": True
        },
        {
            "id": 2,
            "name": "Áudio Presione 1",
            "description": "Áudio para sistema Presione 1",
            "file_path": "/audios/presione1.wav", 
            "duration_seconds": 15,
            "active": True
        }
    ],
    
    "dnc_lists": [
        {
            "id": 1,
            "name": "DNC Brasil",
            "description": "Lista DNC nacional do Brasil",
            "country": "BR",
            "active": True
        }
    ],
    
    "contacts": [
        {
            "phone_number": "+5511999887766",
            "name": "Contato Teste 1",
            "campaign_id": 1,
            "status": "not_started"
        },
        {
            "phone_number": "+5511888776655", 
            "name": "Contato Teste 2",
            "campaign_id": 1,
            "status": "not_started"
        },
        {
            "phone_number": "+5511777665544",
            "name": "Contato Teste 3", 
            "campaign_id": 1,
            "status": "not_started"
        }
    ]
}

async def setup_initial_data():
    """Configurar dados iniciais no banco"""
    print("🚀 Iniciando configuração de dados iniciais...")
    
    try:
        # Obter sessão do banco
        db = next(get_db())
        
        # Popular roles
        print("📋 Configurando roles...")
        for role_data in INITIAL_DATA["roles"]:
            # Verificar se já existe
            existing = db.execute(
                "SELECT id FROM roles WHERE name = :name",
                {"name": role_data["name"]}
            ).fetchone()
            
            if not existing:
                db.execute(
                    """INSERT INTO roles (name, description, permissions, created_at) 
                       VALUES (:name, :description, :permissions, :created_at)""",
                    {
                        **role_data,
                        "created_at": datetime.now()
                    }
                )
                print(f"  ✅ Role criado: {role_data['name']}")
            else:
                print(f"  ⚠️ Role já existe: {role_data['name']}")
        
        # Popular trunks
        print("📞 Configurando trunks...")
        for trunk_data in INITIAL_DATA["trunks"]:
            existing = db.execute(
                "SELECT id FROM trunks WHERE name = :name",
                {"name": trunk_data["name"]}
            ).fetchone()
            
            if not existing:
                db.execute(
                    """INSERT INTO trunks (name, provider, host, port, username, password, 
                                         max_channels, active, created_at) 
                       VALUES (:name, :provider, :host, :port, :username, :password,
                               :max_channels, :active, :created_at)""",
                    {
                        **trunk_data,
                        "created_at": datetime.now()
                    }
                )
                print(f"  ✅ Trunk criado: {trunk_data['name']}")
            else:
                print(f"  ⚠️ Trunk já existe: {trunk_data['name']}")
        
        # Popular audios
        print("🔊 Configurando áudios...")
        for audio_data in INITIAL_DATA["audios"]:
            existing = db.execute(
                "SELECT id FROM audios WHERE name = :name",
                {"name": audio_data["name"]}
            ).fetchone()
            
            if not existing:
                db.execute(
                    """INSERT INTO audios (name, description, file_path, duration_seconds, 
                                         active, created_at) 
                       VALUES (:name, :description, :file_path, :duration_seconds,
                               :active, :created_at)""",
                    {
                        **audio_data,
                        "created_at": datetime.now()
                    }
                )
                print(f"  ✅ Áudio criado: {audio_data['name']}")
            else:
                print(f"  ⚠️ Áudio já existe: {audio_data['name']}")
        
        # Popular DNC lists
        print("🚫 Configurando listas DNC...")
        for dnc_data in INITIAL_DATA["dnc_lists"]:
            existing = db.execute(
                "SELECT id FROM dnc_lists WHERE name = :name",
                {"name": dnc_data["name"]}
            ).fetchone()
            
            if not existing:
                db.execute(
                    """INSERT INTO dnc_lists (name, description, country, active, created_at) 
                       VALUES (:name, :description, :country, :active, :created_at)""",
                    {
                        **dnc_data,
                        "created_at": datetime.now()
                    }
                )
                print(f"  ✅ Lista DNC criada: {dnc_data['name']}")
            else:
                print(f"  ⚠️ Lista DNC já existe: {dnc_data['name']}")
        
        # Popular contacts
        print("👥 Configurando contatos...")
        for contact_data in INITIAL_DATA["contacts"]:
            existing = db.execute(
                "SELECT id FROM contacts WHERE phone_number = :phone_number",
                {"phone_number": contact_data["phone_number"]}
            ).fetchone()
            
            if not existing:
                db.execute(
                    """INSERT INTO contacts (phone_number, name, campaign_id, status, created_at) 
                       VALUES (:phone_number, :name, :campaign_id, :status, :created_at)""",
                    {
                        **contact_data,
                        "created_at": datetime.now()
                    }
                )
                print(f"  ✅ Contato criado: {contact_data['name']}")
            else:
                print(f"  ⚠️ Contato já existe: {contact_data['name']}")
        
        # Commit das alterações
        db.commit()
        print("✅ Dados iniciais configurados com sucesso!")
        
    except Exception as e:
        print(f"❌ Erro ao configurar dados iniciais: {e}")
        db.rollback()
        raise
    finally:
        db.close()

async def verify_data():
    """Verificar se os dados foram inseridos corretamente"""
    print("\n🔍 Verificando dados inseridos...")
    
    try:
        db = next(get_db())
        
        # Verificar contagens
        tables = ["roles", "trunks", "audios", "dnc_lists", "contacts"]
        
        for table in tables:
            count = db.execute(f"SELECT COUNT(*) as total FROM {table}").fetchone()
            print(f"  📊 {table}: {count.total} registros")
        
        print("✅ Verificação concluída!")
        
    except Exception as e:
        print(f"❌ Erro na verificação: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("🎯 CONFIGURAÇÃO DE DADOS INICIAIS - SISTEMA DISCADOR PREDITIVO")
    print("=" * 60)
    
    # Executar setup
    asyncio.run(setup_initial_data())
    
    # Verificar dados
    asyncio.run(verify_data())
    
    print("\n🎉 Setup concluído! Sistema pronto para uso.") 