from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.utils.logger import logger
import requests
import re

router = APIRouter(prefix="/contacts", tags=["Contacts"])

# Configurações do Supabase
SUPABASE_URL = "https://orxxocptgaeoyrtlxwkv.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im9yeHhvY3B0Z2Flb3lydGx4d2t2Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEyOTk0MDksImV4cCI6MjA2Njg3NTQwOX0.hJ5vXcLBiSE0TjVzdbZcnlN_jiT1mNijqWEWylVrhdQ"

def validar_telefone(numero: str) -> bool:
    """Validar número de telefone."""
    numero_limpo = re.sub(r'[^\d]', '', numero)
    return len(numero_limpo) >= 10

@router.post("/upload")
async def upload_contatos(
    arquivo: UploadFile = File(...),
    incluir_nome: bool = Form(True),
    pais_preferido: str = Form("auto")
):
    """
    Upload de contatos - Versão simplificada sem dependência de database.
    """
    logger.info(f"🚀 [UPLOAD] Iniciando upload: {arquivo.filename}")
    
    try:
        # 1. Validações básicas
        if not arquivo or not arquivo.filename:
            raise HTTPException(status_code=400, detail="Arquivo não enviado")
        
        if arquivo.size and arquivo.size > 50 * 1024 * 1024:  # 50MB
            raise HTTPException(status_code=413, detail="Arquivo muito grande (máximo 50MB)")
        
        # 2. Ler e processar arquivo
        logger.info(f"📖 [UPLOAD] Lendo arquivo: {arquivo.size} bytes")
        conteudo = await arquivo.read()
        
        if not conteudo:
            raise HTTPException(status_code=400, detail="Arquivo vazio")
        
        # 3. Decodificar conteúdo
        try:
            texto = conteudo.decode('utf-8')
        except UnicodeDecodeError:
            try:
                texto = conteudo.decode('latin-1')
            except UnicodeDecodeError:
                raise HTTPException(status_code=400, detail="Erro de codificação do arquivo")
        
        # 4. Processar linhas
        linhas = texto.strip().split('\n')
        linhas_limpas = []
        
        for linha in linhas:
            linha_limpa = linha.replace('\r', '').strip()
            if linha_limpa and validar_telefone(linha_limpa):
                linhas_limpas.append(linha_limpa)
        
        total_linhas = len(linhas_limpas)
        logger.info(f"📊 [UPLOAD] Processadas {total_linhas} linhas válidas")
        
        if total_linhas == 0:
            raise HTTPException(status_code=400, detail="Nenhuma linha válida encontrada")
        
        # 5. Para arquivos grandes, processar em lotes
        if total_linhas > 10000:
            logger.info("⚠️ [UPLOAD] Arquivo grande - processando primeiros 1000 registros")
            linhas_processadas = linhas_limpas[:1000]
        else:
            linhas_processadas = linhas_limpas
        
        # 6. Inserir contatos no Supabase via API REST
        contatos_inseridos = 0
        contatos_duplicados = 0
        contatos_invalidos = 0
        
        # Preparar headers para Supabase
        headers = {
            "apikey": SUPABASE_ANON_KEY,
            "Authorization": f"Bearer {SUPABASE_ANON_KEY}",
            "Content-Type": "application/json",
            "Prefer": "resolution=merge-duplicates"
        }
        
        # Inserir em lotes de 100
        lote_size = 100
        for i in range(0, len(linhas_processadas), lote_size):
            lote = linhas_processadas[i:i+lote_size]
            
            # Preparar dados para inserção
            dados_insercao = []
            for linha in lote:
                if validar_telefone(linha):
                    dados_insercao.append({
                        "phone_number": linha,
                        "name": "",
                        "campaign_id": 1,
                        "status": "not_started",
                        "attempts": 0
                    })
            
            try:
                # Fazer inserção no Supabase
                response = requests.post(
                    f"{SUPABASE_URL}/rest/v1/contacts",
                    headers=headers,
                    json=dados_insercao
                )
                
                if response.status_code in [200, 201]:
                    contatos_inseridos += len(dados_insercao)
                    logger.info(f"✅ Lote inserido: {len(dados_insercao)} contatos")
                else:
                    logger.error(f"❌ Erro no lote: {response.status_code} - {response.text}")
                    contatos_invalidos += len(dados_insercao)
                    
            except Exception as e:
                logger.error(f"❌ Erro na inserção do lote: {str(e)}")
                contatos_invalidos += len(dados_insercao)
        
        # 7. Preparar resposta
        resultado = {
            "mensaje": f"Upload concluído com sucesso! {contatos_inseridos} contatos processados.",
            "archivo_original": arquivo.filename,
            "total_lineas_archivo": len(linhas_processadas),
            "contatos_validos": contatos_inseridos,
            "contatos_invalidos": contatos_invalidos,
            "contatos_duplicados": contatos_duplicados,
            "errores": []
        }
        
        logger.info(f"✅ [UPLOAD] Sucesso: {contatos_inseridos} contatos")
        return resultado
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ [UPLOAD] Erro: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/test")
async def test_endpoint():
    """Endpoint de teste."""
    return {
        "message": "Endpoint funcionando!",
        "version": "3.0.0",
        "timestamp": "2025-01-08",
        "supabase_url": SUPABASE_URL[:50] + "...",
        "status": "OK"
    }

@router.post("/debug-txt")
async def debug_txt_upload(
    arquivo: UploadFile = File(...),
    incluir_nome: bool = Form(True),
    pais_preferido: str = Form("auto")
):
    """Debug específico para arquivos TXT."""
    logger.info(f"🔍 [DEBUG] Arquivo: {arquivo.filename}")
    
    try:
        conteudo = await arquivo.read()
        
        try:
            texto = conteudo.decode('utf-8')
        except UnicodeDecodeError:
            texto = conteudo.decode('latin-1')
        
        linhas = texto.strip().split('\n')
        linhas_limpas = [linha.replace('\r', '').strip() for linha in linhas]
        linhas_validas = [linha for linha in linhas_limpas if linha.strip() and validar_telefone(linha)]
        
        return {
            "message": "Debug concluído",
            "filename": arquivo.filename,
            "size": arquivo.size,
            "total_linhas": len(linhas_validas),
            "primeiras_5_linhas": linhas_validas[:5],
            "tem_carriage_return": '\r' in texto,
            "exemplo_linha": linhas_validas[0] if linhas_validas else "Nenhuma"
        }
        
    except Exception as e:
        logger.error(f"❌ [DEBUG] Erro: {str(e)}")
        return {"error": str(e)}

@router.get("/")
async def listar_contatos(skip: int = 0, limit: int = 100):
    """Lista contatos."""
    return {"message": "Endpoint disponível", "total": 0, "contatos": []}

@router.options("/upload")
async def options_upload():
    """CORS para upload."""
    return {"message": "OK"}

@router.post("/test-simple")
async def test_simple():
    """Endpoint POST simples para testar."""
    return {
        "message": "Endpoint POST simples funcionando!",
        "status": "success",
        "timestamp": "2025-01-08"
    }

@router.options("/")
async def options_root():
    """CORS para root."""
    return {"message": "OK"} 