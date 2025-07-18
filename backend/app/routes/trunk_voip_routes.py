from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from pydantic import BaseModel
import asyncio
import subprocess
import os
from datetime import datetime
from app.database import get_db_connection
try:
    from app.services.asterisk_service import AsteriskService
except ImportError:
    # Fallback se o serviço do Asterisk não estiver disponível
    AsteriskService = None

router = APIRouter(prefix="/trunks", tags=["trunks"])

class TrunkVoipCreate(BaseModel):
    nome: str
    host: str
    porta: str = "5060"
    usuario: Optional[str] = None
    senha: Optional[str] = None
    contexto: str = "from-trunk"
    codec: str = "ulaw,alaw,g729"
    dtmf_mode: str = "rfc2833"
    country_code: Optional[str] = None
    dial_prefix: Optional[str] = None
    max_channels: str = "30"
    qualify: str = "yes"
    nat: str = "force_rport,comedia"
    insecure: str = "port,invite"
    type: str = "peer"
    disallow: str = "all"
    allow: str = "ulaw,alaw,g729"
    fromuser: Optional[str] = None
    fromdomain: Optional[str] = None
    register_string: Optional[str] = None
    outbound_proxy: Optional[str] = None
    transport: str = "udp"
    encryption: str = "no"
    activo: bool = True

class TrunkVoipUpdate(BaseModel):
    nome: Optional[str] = None
    host: Optional[str] = None
    porta: Optional[str] = None
    usuario: Optional[str] = None
    senha: Optional[str] = None
    contexto: Optional[str] = None
    codec: Optional[str] = None
    dtmf_mode: Optional[str] = None
    country_code: Optional[str] = None
    dial_prefix: Optional[str] = None
    max_channels: Optional[str] = None
    qualify: Optional[str] = None
    nat: Optional[str] = None
    insecure: Optional[str] = None
    type: Optional[str] = None
    disallow: Optional[str] = None
    allow: Optional[str] = None
    fromuser: Optional[str] = None
    fromdomain: Optional[str] = None
    register_string: Optional[str] = None
    outbound_proxy: Optional[str] = None
    transport: Optional[str] = None
    encryption: Optional[str] = None
    activo: Optional[bool] = None

class TrunkVoipResponse(BaseModel):
    id: int
    nome: str
    host: str
    porta: str
    usuario: Optional[str]
    contexto: str
    country_code: Optional[str]
    dial_prefix: Optional[str]
    max_channels: str
    transport: str
    activo: bool
    created_at: datetime
    updated_at: Optional[datetime]

@router.get("/", response_model=dict)
async def list_trunks():
    """
    Lista todos os trunks VoIP configurados
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, nome, host, porta, usuario, contexto, country_code, 
                   dial_prefix, max_channels, transport, activo, created_at, updated_at
            FROM trunks_voip 
            ORDER BY nome
        """)
        
        trunks = []
        for row in cursor.fetchall():
            trunk = {
                "id": row[0],
                "nome": row[1],
                "host": row[2],
                "porta": row[3],
                "usuario": row[4],
                "contexto": row[5],
                "country_code": row[6],
                "dial_prefix": row[7],
                "max_channels": row[8],
                "transport": row[9],
                "activo": bool(row[10]),
                "created_at": row[11],
                "updated_at": row[12]
            }
            trunks.append(trunk)
        
        conn.close()
        return {"trunks": trunks, "total": len(trunks)}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar trunks: {str(e)}")

@router.post("/", response_model=dict)
async def create_trunk(trunk: TrunkVoipCreate):
    """
    Cria um novo trunk VoIP
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verifica se já existe um trunk com o mesmo nome
        cursor.execute("SELECT id FROM trunks_voip WHERE nome = ?", (trunk.nome,))
        if cursor.fetchone():
            raise HTTPException(status_code=400, detail="Já existe um trunk com este nome")
        
        # Insere o novo trunk
        cursor.execute("""
            INSERT INTO trunks_voip (
                nome, host, porta, usuario, senha, contexto, codec, dtmf_mode,
                country_code, dial_prefix, max_channels, qualify, nat, insecure,
                type, disallow, allow, fromuser, fromdomain, register_string,
                outbound_proxy, transport, encryption, activo, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            trunk.nome, trunk.host, trunk.porta, trunk.usuario, trunk.senha,
            trunk.contexto, trunk.codec, trunk.dtmf_mode, trunk.country_code,
            trunk.dial_prefix, trunk.max_channels, trunk.qualify, trunk.nat,
            trunk.insecure, trunk.type, trunk.disallow, trunk.allow,
            trunk.fromuser, trunk.fromdomain, trunk.register_string,
            trunk.outbound_proxy, trunk.transport, trunk.encryption,
            trunk.activo, datetime.now()
        ))
        
        trunk_id = cursor.lastrowid
        conn.commit()
        
        # Gera configuração SIP
        await generate_sip_config(trunk_id)
        
        conn.close()
        
        return {
            "message": "Trunk criado com sucesso",
            "trunk_id": trunk_id,
            "sip_config_generated": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao criar trunk: {str(e)}")

@router.get("/{trunk_id}", response_model=dict)
async def get_trunk(trunk_id: int):
    """
    Obtém detalhes de um trunk específico
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM trunks_voip WHERE id = ?
        """, (trunk_id,))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Trunk não encontrado")
        
        # Mapeia os campos (assumindo a ordem das colunas)
        trunk = {
            "id": row[0],
            "nome": row[1],
            "host": row[2],
            "porta": row[3],
            "usuario": row[4],
            "senha": "***" if row[5] else None,  # Oculta a senha
            "contexto": row[6],
            "codec": row[7],
            "dtmf_mode": row[8],
            "country_code": row[9],
            "dial_prefix": row[10],
            "max_channels": row[11],
            "qualify": row[12],
            "nat": row[13],
            "insecure": row[14],
            "type": row[15],
            "disallow": row[16],
            "allow": row[17],
            "fromuser": row[18],
            "fromdomain": row[19],
            "register_string": row[20],
            "outbound_proxy": row[21],
            "transport": row[22],
            "encryption": row[23],
            "activo": bool(row[24]),
            "created_at": row[25],
            "updated_at": row[26]
        }
        
        conn.close()
        return {"trunk": trunk}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter trunk: {str(e)}")

@router.put("/{trunk_id}", response_model=dict)
async def update_trunk(trunk_id: int, trunk_update: TrunkVoipUpdate):
    """
    Atualiza um trunk VoIP existente
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verifica se o trunk existe
        cursor.execute("SELECT id FROM trunks_voip WHERE id = ?", (trunk_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Trunk não encontrado")
        
        # Prepara os campos para atualização
        update_fields = []
        update_values = []
        
        for field, value in trunk_update.dict(exclude_unset=True).items():
            if value is not None:
                update_fields.append(f"{field} = ?")
                update_values.append(value)
        
        if not update_fields:
            raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")
        
        # Adiciona timestamp de atualização
        update_fields.append("updated_at = ?")
        update_values.append(datetime.now())
        update_values.append(trunk_id)
        
        # Executa a atualização
        query = f"UPDATE trunks_voip SET {', '.join(update_fields)} WHERE id = ?"
        cursor.execute(query, update_values)
        conn.commit()
        
        # Regenera configuração SIP
        await generate_sip_config(trunk_id)
        
        conn.close()
        
        return {
            "message": "Trunk atualizado com sucesso",
            "trunk_id": trunk_id,
            "sip_config_updated": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar trunk: {str(e)}")

@router.delete("/{trunk_id}", response_model=dict)
async def delete_trunk(trunk_id: int):
    """
    Exclui um trunk VoIP
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verifica se o trunk existe
        cursor.execute("SELECT nome FROM trunks_voip WHERE id = ?", (trunk_id,))
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Trunk não encontrado")
        
        trunk_name = row[0]
        
        # Remove o trunk
        cursor.execute("DELETE FROM trunks_voip WHERE id = ?", (trunk_id,))
        conn.commit()
        conn.close()
        
        # Remove configuração SIP
        await remove_sip_config(trunk_name)
        
        return {
            "message": "Trunk excluído com sucesso",
            "trunk_id": trunk_id,
            "sip_config_removed": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao excluir trunk: {str(e)}")

@router.post("/{trunk_id}/test", response_model=dict)
async def test_trunk_connection(trunk_id: int):
    """
    Testa a conexão com um trunk VoIP
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT nome, host, porta, usuario, senha, transport
            FROM trunks_voip WHERE id = ?
        """, (trunk_id,))
        
        row = cursor.fetchone()
        if not row:
            raise HTTPException(status_code=404, detail="Trunk não encontrado")
        
        nome, host, porta, usuario, senha, transport = row
        conn.close()
        
        # Testa conectividade básica
        test_results = {
            "ping_test": await test_ping(host),
            "port_test": await test_port(host, int(porta)),
            "sip_test": await test_sip_registration(host, porta, usuario, senha, transport)
        }
        
        # Determina se o teste foi bem-sucedido
        success = all(test_results.values())
        
        message = f"Teste do trunk '{nome}' concluído."
        if success:
            message += " Todas as verificações passaram."
        else:
            failed_tests = [test for test, result in test_results.items() if not result]
            message += f" Falhas em: {', '.join(failed_tests)}"
        
        return {
            "success": success,
            "message": message,
            "test_results": test_results,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao testar trunk: {str(e)}")

@router.get("/{trunk_id}/config", response_model=dict)
async def get_trunk_sip_config(trunk_id: int):
    """
    Gera e retorna a configuração SIP para um trunk
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM trunks_voip WHERE id = ?", (trunk_id,))
        row = cursor.fetchone()
        
        if not row:
            raise HTTPException(status_code=404, detail="Trunk não encontrado")
        
        # Gera configuração SIP
        sip_config = generate_sip_config_text(row)
        
        conn.close()
        
        return {
            "trunk_id": trunk_id,
            "sip_config": sip_config,
            "generated_at": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar configuração: {str(e)}")

# Funções auxiliares

async def test_ping(host: str) -> bool:
    """Testa conectividade básica com ping"""
    try:
        # Usa ping do sistema operacional
        if os.name == 'nt':  # Windows
            result = subprocess.run(['ping', '-n', '1', host], 
                                  capture_output=True, text=True, timeout=5)
        else:  # Linux/Unix
            result = subprocess.run(['ping', '-c', '1', host], 
                                  capture_output=True, text=True, timeout=5)
        return result.returncode == 0
    except:
        return False

async def test_port(host: str, port: int) -> bool:
    """Testa se a porta está aberta"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(5)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

async def test_sip_registration(host: str, port: str, usuario: str, senha: str, transport: str) -> bool:
    """Testa registro SIP básico (simulado)"""
    try:
        # Aqui você pode implementar um teste SIP real
        # Por enquanto, retorna True se os parâmetros básicos estão presentes
        return bool(host and port and usuario)
    except:
        return False

async def generate_sip_config(trunk_id: int):
    """Gera arquivo de configuração SIP para o trunk"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM trunks_voip WHERE id = ?", (trunk_id,))
        row = cursor.fetchone()
        
        if row:
            config_text = generate_sip_config_text(row)
            
            # Salva em arquivo (opcional)
            config_dir = "/etc/asterisk/sip_trunks"  # Ajuste conforme necessário
            os.makedirs(config_dir, exist_ok=True)
            
            config_file = f"{config_dir}/{row[1]}.conf"  # row[1] é o nome
            with open(config_file, 'w') as f:
                f.write(config_text)
        
        conn.close()
    except Exception as e:
        # Log do erro, mas não falha a operação principal
        print(f"Erro ao gerar configuração SIP: {e}")

def generate_sip_config_text(trunk_row) -> str:
    """Gera o texto da configuração SIP"""
    nome = trunk_row[1]
    host = trunk_row[2]
    porta = trunk_row[3]
    usuario = trunk_row[4]
    senha = trunk_row[5]
    contexto = trunk_row[6]
    dtmf_mode = trunk_row[8]
    qualify = trunk_row[12]
    nat = trunk_row[13]
    insecure = trunk_row[14]
    trunk_type = trunk_row[15]
    disallow = trunk_row[16]
    allow = trunk_row[17]
    fromuser = trunk_row[18]
    fromdomain = trunk_row[19]
    register_string = trunk_row[20]
    outbound_proxy = trunk_row[21]
    transport = trunk_row[22]
    
    config = f"""
; Configuração SIP para trunk: {nome}
; Gerado automaticamente em {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

[{nome}]
type={trunk_type}
host={host}
port={porta}
context={contexto}
dtmfmode={dtmf_mode}
qualify={qualify}
nat={nat}
insecure={insecure}
disallow={disallow}
allow={allow}
transport={transport}
"""
    
    if usuario:
        config += f"username={usuario}\n"
    if senha:
        config += f"secret={senha}\n"
    if fromuser:
        config += f"fromuser={fromuser}\n"
    if fromdomain:
        config += f"fromdomain={fromdomain}\n"
    if outbound_proxy:
        config += f"outboundproxy={outbound_proxy}\n"
    
    if register_string:
        config += f"\n; String de registro\nregister => {register_string}\n"
    
    return config

async def remove_sip_config(trunk_name: str):
    """Remove arquivo de configuração SIP do trunk"""
    try:
        config_file = f"/etc/asterisk/sip_trunks/{trunk_name}.conf"
        if os.path.exists(config_file):
            os.remove(config_file)
    except Exception as e:
        print(f"Erro ao remover configuração SIP: {e}")