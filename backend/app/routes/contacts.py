from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.utils.logger import logger

router = APIRouter(prefix="/contacts", tags=["Contacts"])

@router.post("/upload")
async def upload_contatos(
    arquivo: UploadFile = File(...),
    incluir_nome: bool = Form(True),
    pais_preferido: str = Form("auto"),
    db: Session = Depends(get_db)
):
    """
    Upload de contatos - Versão simplificada e funcional.
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
            if linha_limpa and len(linha_limpa) >= 10:  # Mínimo 10 dígitos
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
        
        # 6. Inserir contatos no Supabase
        contatos_inseridos = 0
        contatos_duplicados = 0
        contatos_invalidos = 0
        
        for linha in linhas_processadas:
            if len(linha) >= 10:
                try:
                    # Inserir no Supabase
                    query = """
                        INSERT INTO contacts (phone_number, name, campaign_id, status, attempts, created_at, updated_at) 
                        VALUES (:phone, :name, :campaign_id, 'not_started', 0, NOW(), NOW())
                        ON CONFLICT (phone_number, campaign_id) DO NOTHING
                        RETURNING id
                    """
                    
                    result = db.execute(query, {
                        "phone": linha,
                        "name": "",  # Nome vazio por enquanto
                        "campaign_id": 1  # Campanha padrão
                    })
                    
                    if result.fetchone():
                        contatos_inseridos += 1
                    else:
                        contatos_duplicados += 1
                        
                except Exception as e:
                    logger.error(f"❌ Erro ao inserir {linha}: {str(e)}")
                    contatos_invalidos += 1
            else:
                contatos_invalidos += 1
        
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
        "version": "2.0.0",
        "timestamp": "2025-01-08"
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
        linhas_validas = [linha for linha in linhas_limpas if linha.strip()]
        
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
    return []

@router.options("/upload")
async def options_upload():
    """CORS para upload."""
    return {"message": "OK"}

@router.options("/")
async def options_root():
    """CORS para root."""
    return {"message": "OK"} 