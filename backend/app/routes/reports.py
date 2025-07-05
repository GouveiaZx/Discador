from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from typing import Optional
import os
from ..services.reports_service import ReportsService

router = APIRouter()
reports_service = ReportsService()

@router.get("/campaigns/stats")
async def get_campaign_stats(
    campaign_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Obter estatísticas de campanhas
    """
    try:
        stats = await reports_service.get_campaign_stats(campaign_id, start_date, end_date)
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}")

@router.post("/generate/pdf")
async def generate_pdf_report(
    report_type: str = "campaign",
    campaign_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Gerar relatório em PDF
    """
    try:
        # Obter dados
        data = await reports_service.get_campaign_stats(campaign_id, start_date, end_date)
        
        # Gerar PDF
        filepath = await reports_service.generate_pdf_report(data, report_type)
        
        return {
            "success": True,
            "message": "Relatório PDF gerado com sucesso",
            "filename": os.path.basename(filepath),
            "download_url": f"/api/reports/download/{os.path.basename(filepath)}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório PDF: {str(e)}")

@router.post("/generate/csv")
async def generate_csv_report(
    report_type: str = "campaign",
    campaign_id: Optional[int] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
):
    """
    Gerar relatório em CSV
    """
    try:
        # Obter dados
        data = await reports_service.get_campaign_stats(campaign_id, start_date, end_date)
        
        # Gerar CSV
        filepath = await reports_service.generate_csv_report(data, report_type)
        
        return {
            "success": True,
            "message": "Relatório CSV gerado com sucesso",
            "filename": os.path.basename(filepath),
            "download_url": f"/api/reports/download/{os.path.basename(filepath)}"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar relatório CSV: {str(e)}")

@router.get("/download/{filename}")
async def download_report(filename: str):
    """
    Download de relatório
    """
    try:
        filepath = os.path.join(reports_service.reports_dir, filename)
        
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        
        return FileResponse(
            path=filepath,
            filename=filename,
            media_type='application/octet-stream'
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao baixar relatório: {str(e)}")

@router.get("/list")
async def list_reports():
    """
    Listar relatórios disponíveis
    """
    try:
        reports = await reports_service.list_reports()
        
        return {
            "success": True,
            "reports": reports
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao listar relatórios: {str(e)}")

@router.delete("/delete/{filename}")
async def delete_report(filename: str):
    """
    Deletar relatório
    """
    try:
        success = await reports_service.delete_report(filename)
        
        if success:
            return {
                "success": True,
                "message": "Relatório deletado com sucesso"
            }
        else:
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar relatório: {str(e)}") 