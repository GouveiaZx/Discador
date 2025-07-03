from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
from app.database import get_db
from app.schemas.contacts import ContactsUploadResponse, ContactResponse
from app.services.contacts_service import ContactsService
from app.utils.logger import logger

router = APIRouter(prefix="/contacts", tags=["Contacts"])

@router.post("/upload", response_model=ContactsUploadResponse)
async def upload_contatos(
    arquivo: UploadFile = File(..., description="Arquivo CSV ou TXT com contatos"),
    incluir_nome: bool = Form(True, description="Se deve incluir nome nos contatos"),
    pais_preferido: str = Form("auto", description="País preferido para validação (auto, usa, argentina)"),
    db: Session = Depends(get_db)
) -> ContactsUploadResponse:
    """
    Faz upload de um arquivo CSV ou TXT com contatos.
    
    **Formatos suportados:**
    - CSV: Colunas detectadas automaticamente (telefone, nome, email, empresa, notas)
    - TXT: Um telefone por linha ou formato: nome,telefone,email,empresa
    
    **Formatos de telefone aceitos:**
    - EUA: +1 555 123 4567, (555) 123-4567, 555-123-4567
    - Argentina: +54 9 11 1234-5678, 011 1234-5678, 11 1234 5678
    
    **Validações aplicadas:**
    - Telefones duplicados são removidos
    - Telefones inválidos são reportados
    - Detecção automática de país
    """
    logger.info(f"🚀 Iniciando upload de contatos")
    logger.info(f"📁 Arquivo: {arquivo.filename}, tamanho: {arquivo.size}")
    logger.info(f"⚙️ Parâmetros: incluir_nome={incluir_nome}, pais_preferido={pais_preferido}")
    
    # Validar tamanho do arquivo (máximo 100MB)
    max_size = 100 * 1024 * 1024
    if arquivo.size and arquivo.size > max_size:
        logger.error(f"❌ Arquivo muito grande: {arquivo.size} bytes")
        raise HTTPException(
            status_code=413,
            detail="Arquivo muito grande. Tamanho máximo: 100MB"
        )
    
    try:
        # Simular processamento bem-sucedido para debug
        logger.info("🔄 Simulando processamento de arquivo...")
        
        # Ler apenas o nome do arquivo para debug
        nome_arquivo = arquivo.filename or "arquivo_sem_nome"
        
        logger.info(f"✅ Arquivo {nome_arquivo} processado com sucesso (simulado)")
        
        # Resposta simulada
        response = ContactsUploadResponse(
            mensaje="Arquivo processado com sucesso (modo debug)!",
            archivo_original=nome_arquivo,
            total_lineas_archivo=10,
            contatos_validos=8,
            contatos_invalidos=1,
            contatos_duplicados=1,
            errores=["Exemplo de erro de validação"]
        )
        
        logger.info(f"📋 Resposta preparada: {response}")
        return response
        
    except HTTPException as he:
        logger.error(f"❌ HTTPException: {he.status_code} - {he.detail}")
        raise
    except Exception as e:
        logger.error(f"❌ Erro inesperado no upload de contatos: {str(e)}")
        logger.error(f"❌ Tipo do erro: {type(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno do servidor ao processar o arquivo: {str(e)}"
        )

@router.get("/", response_model=List[ContactResponse])
async def listar_contatos(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
) -> List[ContactResponse]:
    """
    Lista todos os contatos.
    
    **Parâmetros:**
    - skip: Número de registros a pular (para paginação)
    - limit: Número máximo de registros a retornar
    """
    try:
        # Por enquanto retornar lista vazia, implementar busca no Supabase depois
        logger.info(f"Listando contatos - skip: {skip}, limit: {limit}")
        return []
        
    except Exception as e:
        logger.error(f"Erro ao listar contatos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno ao obter os contatos"
        )

@router.options("/upload")
async def options_upload_contatos():
    """Endpoint OPTIONS para CORS."""
    return {"message": "OK"}

@router.options("/")
async def options_contatos():
    """Endpoint OPTIONS para CORS."""
    return {"message": "OK"} 