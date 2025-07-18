"""Rotas para upload otimizado de listas grandes."""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional
import logging
import uuid

from ..database import get_db
from ..services.optimized_list_loader import OptimizedListLoader

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/optimized-upload", tags=["Upload Otimizado"])

# Cache global para loaders
loaders_cache = {}

def get_loader(db: Session) -> OptimizedListLoader:
    """Obtém ou cria um loader otimizado."""
    db_id = id(db)
    if db_id not in loaders_cache:
        loaders_cache[db_id] = OptimizedListLoader(db)
    return loaders_cache[db_id]

@router.post("/upload-large-list")
async def upload_large_list(
    background_tasks: BackgroundTasks,
    arquivo: UploadFile = File(...),
    nome_lista: str = None,
    campanha_id: Optional[int] = None,
    max_records: int = 50000,
    db: Session = Depends(get_db)
):
    """Upload otimizado para listas grandes."""
    try:
        # Validações básicas
        if not arquivo.filename:
            raise HTTPException(status_code=400, detail="Nome do arquivo é obrigatório")
        
        if not nome_lista:
            nome_lista = arquivo.filename.split('.')[0]
        
        # Verificar tipo de arquivo
        allowed_extensions = ['.csv', '.txt', '.tsv']
        file_extension = '.' + arquivo.filename.split('.')[-1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Tipo de arquivo não suportado. Use: {', '.join(allowed_extensions)}"
            )
        
        # Verificar tamanho do arquivo (máximo 100MB)
        arquivo.file.seek(0, 2)  # Ir para o final
        file_size = arquivo.file.tell()
        arquivo.file.seek(0)  # Voltar ao início
        
        max_size = 100 * 1024 * 1024  # 100MB
        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"Arquivo muito grande. Máximo: {max_size // (1024*1024)}MB"
            )
        
        # Gerar ID único para acompanhar progresso
        task_id = str(uuid.uuid4())
        
        # Obter loader
        loader = get_loader(db)
        
        # Processar arquivo em background
        background_tasks.add_task(
            process_file_background,
            loader,
            arquivo,
            nome_lista,
            campanha_id,
            task_id,
            max_records
        )
        
        return JSONResponse({
            "success": True,
            "message": "Upload iniciado com sucesso",
            "task_id": task_id,
            "status_url": f"/api/optimized-upload/status/{task_id}",
            "file_info": {
                "filename": arquivo.filename,
                "size_mb": round(file_size / (1024*1024), 2),
                "max_records": max_records
            }
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no upload otimizado: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

async def process_file_background(
    loader: OptimizedListLoader,
    arquivo: UploadFile,
    nome_lista: str,
    campanha_id: Optional[int],
    task_id: str,
    max_records: int
):
    """Processa arquivo em background."""
    try:
        result = await loader.process_large_file(
            arquivo=arquivo,
            nome_lista=nome_lista,
            campanha_id=campanha_id,
            progress_callback_id=task_id,
            max_records=max_records
        )
        logger.info(f"✅ Processamento concluído para task {task_id}: {result}")
    except Exception as e:
        logger.error(f"❌ Erro no processamento background {task_id}: {e}")

@router.get("/status/{task_id}")
async def get_upload_status(
    task_id: str,
    db: Session = Depends(get_db)
):
    """Obtém status do upload em progresso."""
    try:
        loader = get_loader(db)
        status = loader.get_processing_status(task_id)
        
        if status.get("status") == "nao_encontrado":
            raise HTTPException(status_code=404, detail="Task não encontrada")
        
        # Calcular estatísticas adicionais
        if status.get("status") == "processando":
            elapsed_time = status.get("processing_time", 0)
            processed = status.get("processed_records", 0)
            total = status.get("total_records", 1)
            
            if processed > 0 and elapsed_time > 0:
                records_per_second = processed / elapsed_time
                estimated_remaining = (total - processed) / records_per_second if records_per_second > 0 else 0
                status["estimated_remaining_seconds"] = round(estimated_remaining, 1)
                status["records_per_second"] = round(records_per_second, 1)
        
        return JSONResponse({
            "success": True,
            "task_id": task_id,
            "status": status
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro ao obter status: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.post("/upload-sync")
async def upload_sync(
    arquivo: UploadFile = File(...),
    nome_lista: str = None,
    campanha_id: Optional[int] = None,
    max_records: int = 10000,
    db: Session = Depends(get_db)
):
    """Upload síncrono para listas menores (até 10k registros)."""
    try:
        # Validações básicas
        if not arquivo.filename:
            raise HTTPException(status_code=400, detail="Nome do arquivo é obrigatório")
        
        if not nome_lista:
            nome_lista = arquivo.filename.split('.')[0]
        
        # Verificar tamanho do arquivo (máximo 10MB para sync)
        arquivo.file.seek(0, 2)
        file_size = arquivo.file.tell()
        arquivo.file.seek(0)
        
        max_size = 10 * 1024 * 1024  # 10MB
        if file_size > max_size:
            raise HTTPException(
                status_code=400,
                detail=f"Para arquivos maiores que {max_size // (1024*1024)}MB, use o upload assíncrono"
            )
        
        # Processar diretamente
        loader = get_loader(db)
        result = await loader.process_large_file(
            arquivo=arquivo,
            nome_lista=nome_lista,
            campanha_id=campanha_id,
            max_records=max_records
        )
        
        if result["success"]:
            return JSONResponse({
                "success": True,
                "message": "Lista processada com sucesso",
                "result": {
                    "lista_id": result["lista_id"],
                    "total_processed": result["total_processed"],
                    "total_errors": result["total_errors"],
                    "processing_time": result["processing_time"],
                    "records_per_second": result["records_per_second"]
                }
            })
        else:
            raise HTTPException(status_code=400, detail=result.get("error", "Erro no processamento"))
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erro no upload síncrono: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/cleanup-old-tasks")
async def cleanup_old_tasks(
    max_age_hours: int = 24,
    db: Session = Depends(get_db)
):
    """Remove tasks antigas do cache."""
    try:
        loader = get_loader(db)
        loader.cleanup_old_tasks(max_age_hours)
        
        return JSONResponse({
            "success": True,
            "message": f"Tasks antigas removidas (mais de {max_age_hours}h)"
        })
        
    except Exception as e:
        logger.error(f"Erro na limpeza: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")

@router.get("/performance-stats")
async def get_performance_stats(
    db: Session = Depends(get_db)
):
    """Obtém estatísticas de performance do sistema."""
    try:
        loader = get_loader(db)
        
        # Contar tasks ativas
        active_tasks = sum(1 for status in loader.processing_status.values() 
                          if status.get("status") == "processando")
        
        completed_tasks = sum(1 for status in loader.processing_status.values() 
                             if status.get("status") == "concluido")
        
        error_tasks = sum(1 for status in loader.processing_status.values() 
                         if status.get("status") == "erro")
        
        # Calcular média de performance
        completed_stats = [status for status in loader.processing_status.values() 
                          if status.get("status") == "concluido" and "records_per_second" in status]
        
        avg_records_per_second = 0
        if completed_stats:
            avg_records_per_second = sum(s.get("records_per_second", 0) for s in completed_stats) / len(completed_stats)
        
        return JSONResponse({
            "success": True,
            "stats": {
                "active_tasks": active_tasks,
                "completed_tasks": completed_tasks,
                "error_tasks": error_tasks,
                "total_tasks": len(loader.processing_status),
                "avg_records_per_second": round(avg_records_per_second, 2),
                "batch_size": loader.batch_size,
                "max_workers": loader.max_workers
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {str(e)}")