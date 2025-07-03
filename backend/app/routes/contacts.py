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
    logger.info(f"Iniciando upload de contatos: {arquivo.filename}")
    
    # Validar tamanho do arquivo (máximo 100MB)
    max_size = 100 * 1024 * 1024
    if arquivo.size and arquivo.size > max_size:
        raise HTTPException(
            status_code=413,
            detail="Arquivo muito grande. Tamanho máximo: 100MB"
        )
    
    try:
        service = ContactsService(db)
        resultado = await service.procesar_archivo_contatos(
            archivo, 
            incluir_nome, 
            pais_preferido
        )
        
        # Preparar mensagem de resultado
        mensaje = (
            f"Arquivo processado com sucesso! "
            f"{resultado['contatos_validos']} contatos válidos salvos "
            f"de {resultado['total_lineas_archivo']} linhas processadas."
        )
        
        if resultado['contatos_invalidos'] > 0:
            mensaje += f" {resultado['contatos_invalidos']} contatos inválidos encontrados."
        
        if resultado['contatos_duplicados'] > 0:
            mensaje += f" {resultado['contatos_duplicados']} contatos duplicados removidos."
        
        return ContactsUploadResponse(
            mensaje=mensaje,
            archivo_original=resultado['archivo_original'],
            total_lineas_archivo=resultado['total_lineas_archivo'],
            contatos_validos=resultado['contatos_validos'],
            contatos_invalidos=resultado['contatos_invalidos'],
            contatos_duplicados=resultado['contatos_duplicados'],
            errores=resultado['errores']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro inesperado no upload de contatos: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erro interno do servidor ao processar o arquivo"
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