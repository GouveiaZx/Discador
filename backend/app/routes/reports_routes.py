from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from fastapi.responses import FileResponse
from typing import List, Optional, Dict, Any
import os
import json
import csv
import asyncio
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.lineplots import LinePlot
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
import base64

router = APIRouter()

# Configurações
REPORTS_DIR = "reports"
os.makedirs(REPORTS_DIR, exist_ok=True)

class ReportsService:
    """
    Serviço para gerar relatórios
    """
    
    @staticmethod
    async def get_campaign_stats(campaign_id: int = None, start_date: str = None, end_date: str = None):
        """
        Obter estatísticas de campanhas
        """
        try:
            # Simular dados de campanha (substituir por dados reais)
            stats = {
                "total_calls": 15420,
                "answered_calls": 8950,
                "transferred_calls": 2140,
                "success_rate": 58.1,
                "transfer_rate": 13.9,
                "average_call_duration": 45.2,
                "campaigns": [
                    {
                        "id": 1,
                        "name": "Campanha Principal",
                        "total_calls": 8500,
                        "answered": 4950,
                        "transferred": 1200,
                        "success_rate": 58.2
                    },
                    {
                        "id": 2,
                        "name": "Campanha Secundária",
                        "total_calls": 6920,
                        "answered": 4000,
                        "transferred": 940,
                        "success_rate": 57.8
                    }
                ],
                "daily_stats": [
                    {"date": "2024-01-01", "calls": 1200, "answered": 720, "transferred": 180},
                    {"date": "2024-01-02", "calls": 1350, "answered": 810, "transferred": 200},
                    {"date": "2024-01-03", "calls": 1100, "answered": 640, "transferred": 160},
                    {"date": "2024-01-04", "calls": 1450, "answered": 870, "transferred": 210},
                    {"date": "2024-01-05", "calls": 1320, "answered": 780, "transferred": 195}
                ],
                "hourly_stats": [
                    {"hour": "09:00", "calls": 120, "answered": 72},
                    {"hour": "10:00", "calls": 180, "answered": 108},
                    {"hour": "11:00", "calls": 220, "answered": 132},
                    {"hour": "12:00", "calls": 200, "answered": 120},
                    {"hour": "13:00", "calls": 160, "answered": 96},
                    {"hour": "14:00", "calls": 240, "answered": 144},
                    {"hour": "15:00", "calls": 280, "answered": 168},
                    {"hour": "16:00", "calls": 320, "answered": 192},
                    {"hour": "17:00", "calls": 290, "answered": 174},
                    {"hour": "18:00", "calls": 250, "answered": 150}
                ]
            }
            
            return stats
            
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return {}
    
    @staticmethod
    async def generate_pdf_report(data: Dict[str, Any], report_type: str = "campaign") -> str:
        """
        Gerar relatório PDF
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"relatorio_{report_type}_{timestamp}.pdf"
            filepath = os.path.join(REPORTS_DIR, filename)
            
            # Criar documento PDF
            doc = SimpleDocTemplate(filepath, pagesize=A4)
            styles = getSampleStyleSheet()
            story = []
            
            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.darkblue
            )
            
            story.append(Paragraph(f"Relatório de {report_type.title()}", title_style))
            story.append(Spacer(1, 20))
            
            # Informações gerais
            info_data = [
                ["Data de Geração:", datetime.now().strftime("%d/%m/%Y %H:%M:%S")],
                ["Período:", "Últimos 30 dias"],
                ["Total de Chamadas:", f"{data.get('total_calls', 0):,}"],
                ["Chamadas Atendidas:", f"{data.get('answered_calls', 0):,}"],
                ["Taxa de Sucesso:", f"{data.get('success_rate', 0):.1f}%"],
                ["Taxa de Transferência:", f"{data.get('transfer_rate', 0):.1f}%"]
            ]
            
            info_table = Table(info_data, colWidths=[2*inch, 2*inch])
            info_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(info_table)
            story.append(Spacer(1, 20))
            
            # Estatísticas por campanha
            if 'campaigns' in data:
                story.append(Paragraph("Estatísticas por Campanha", styles['Heading2']))
                story.append(Spacer(1, 10))
                
                campaign_data = [["Campanha", "Chamadas", "Atendidas", "Transferidas", "Taxa Sucesso"]]
                for campaign in data['campaigns']:
                    campaign_data.append([
                        campaign['name'],
                        f"{campaign['total_calls']:,}",
                        f"{campaign['answered']:,}",
                        f"{campaign['transferred']:,}",
                        f"{campaign['success_rate']:.1f}%"
                    ])
                
                campaign_table = Table(campaign_data, colWidths=[2*inch, 1*inch, 1*inch, 1*inch, 1*inch])
                campaign_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightblue),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(campaign_table)
                story.append(Spacer(1, 20))
            
            # Estatísticas diárias
            if 'daily_stats' in data:
                story.append(Paragraph("Estatísticas Diárias", styles['Heading2']))
                story.append(Spacer(1, 10))
                
                daily_data = [["Data", "Chamadas", "Atendidas", "Transferidas", "Taxa Sucesso"]]
                for daily in data['daily_stats']:
                    success_rate = (daily['answered'] / daily['calls'] * 100) if daily['calls'] > 0 else 0
                    daily_data.append([
                        daily['date'],
                        f"{daily['calls']:,}",
                        f"{daily['answered']:,}",
                        f"{daily['transferred']:,}",
                        f"{success_rate:.1f}%"
                    ])
                
                daily_table = Table(daily_data, colWidths=[1.5*inch, 1*inch, 1*inch, 1*inch, 1*inch])
                daily_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.lightgreen),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(daily_table)
            
            # Gerar PDF
            doc.build(story)
            
            return filepath
            
        except Exception as e:
            print(f"Erro ao gerar PDF: {e}")
            raise e
    
    @staticmethod
    async def generate_csv_report(data: Dict[str, Any], report_type: str = "campaign") -> str:
        """
        Gerar relatório CSV
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"relatorio_{report_type}_{timestamp}.csv"
            filepath = os.path.join(REPORTS_DIR, filename)
            
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                
                # Cabeçalho
                writer.writerow([f"Relatório de {report_type.title()} - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"])
                writer.writerow([])
                
                # Informações gerais
                writer.writerow(["INFORMAÇÕES GERAIS"])
                writer.writerow(["Total de Chamadas", data.get('total_calls', 0)])
                writer.writerow(["Chamadas Atendidas", data.get('answered_calls', 0)])
                writer.writerow(["Chamadas Transferidas", data.get('transferred_calls', 0)])
                writer.writerow(["Taxa de Sucesso (%)", data.get('success_rate', 0)])
                writer.writerow(["Taxa de Transferência (%)", data.get('transfer_rate', 0)])
                writer.writerow(["Duração Média (seg)", data.get('average_call_duration', 0)])
                writer.writerow([])
                
                # Estatísticas por campanha
                if 'campaigns' in data:
                    writer.writerow(["ESTATÍSTICAS POR CAMPANHA"])
                    writer.writerow(["Campanha", "Total Chamadas", "Atendidas", "Transferidas", "Taxa Sucesso (%)"])
                    
                    for campaign in data['campaigns']:
                        writer.writerow([
                            campaign['name'],
                            campaign['total_calls'],
                            campaign['answered'],
                            campaign['transferred'],
                            campaign['success_rate']
                        ])
                    writer.writerow([])
                
                # Estatísticas diárias
                if 'daily_stats' in data:
                    writer.writerow(["ESTATÍSTICAS DIÁRIAS"])
                    writer.writerow(["Data", "Chamadas", "Atendidas", "Transferidas", "Taxa Sucesso (%)"])
                    
                    for daily in data['daily_stats']:
                        success_rate = (daily['answered'] / daily['calls'] * 100) if daily['calls'] > 0 else 0
                        writer.writerow([
                            daily['date'],
                            daily['calls'],
                            daily['answered'],
                            daily['transferred'],
                            round(success_rate, 1)
                        ])
                    writer.writerow([])
                
                # Estatísticas horárias
                if 'hourly_stats' in data:
                    writer.writerow(["ESTATÍSTICAS HORÁRIAS"])
                    writer.writerow(["Hora", "Chamadas", "Atendidas", "Taxa Sucesso (%)"])
                    
                    for hourly in data['hourly_stats']:
                        success_rate = (hourly['answered'] / hourly['calls'] * 100) if hourly['calls'] > 0 else 0
                        writer.writerow([
                            hourly['hour'],
                            hourly['calls'],
                            hourly['answered'],
                            round(success_rate, 1)
                        ])
            
            return filepath
            
        except Exception as e:
            print(f"Erro ao gerar CSV: {e}")
            raise e

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
        stats = await ReportsService.get_campaign_stats(campaign_id, start_date, end_date)
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao obter estatísticas: {str(e)}")

@router.post("/generate/pdf")
async def generate_pdf_report(
    background_tasks: BackgroundTasks,
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
        data = await ReportsService.get_campaign_stats(campaign_id, start_date, end_date)
        
        # Gerar PDF
        filepath = await ReportsService.generate_pdf_report(data, report_type)
        
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
    background_tasks: BackgroundTasks,
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
        data = await ReportsService.get_campaign_stats(campaign_id, start_date, end_date)
        
        # Gerar CSV
        filepath = await ReportsService.generate_csv_report(data, report_type)
        
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
        filepath = os.path.join(REPORTS_DIR, filename)
        
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
        reports = []
        
        if os.path.exists(REPORTS_DIR):
            for filename in os.listdir(REPORTS_DIR):
                if filename.endswith(('.pdf', '.csv')):
                    filepath = os.path.join(REPORTS_DIR, filename)
                    file_size = os.path.getsize(filepath)
                    created_time = os.path.getctime(filepath)
                    
                    reports.append({
                        "filename": filename,
                        "size": file_size,
                        "created": datetime.fromtimestamp(created_time).isoformat(),
                        "type": "PDF" if filename.endswith('.pdf') else "CSV",
                        "download_url": f"/api/reports/download/{filename}"
                    })
        
        # Ordenar por data de criação (mais recente primeiro)
        reports.sort(key=lambda x: x['created'], reverse=True)
        
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
        filepath = os.path.join(REPORTS_DIR, filename)
        
        if not os.path.exists(filepath):
            raise HTTPException(status_code=404, detail="Arquivo não encontrado")
        
        os.remove(filepath)
        
        return {
            "success": True,
            "message": "Relatório deletado com sucesso"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao deletar relatório: {str(e)}")

@router.get("/templates")
async def get_report_templates():
    """
    Obter templates de relatórios disponíveis
    """
    templates = [
        {
            "id": "campaign_performance",
            "name": "Performance de Campanhas",
            "description": "Relatório completo de performance das campanhas",
            "fields": ["total_calls", "answered_calls", "success_rate", "transfer_rate"]
        },
        {
            "id": "daily_activity",
            "name": "Atividade Diária",
            "description": "Relatório de atividades por dia",
            "fields": ["daily_stats", "hourly_stats"]
        },
        {
            "id": "agent_performance",
            "name": "Performance de Agentes",
            "description": "Relatório de performance dos agentes",
            "fields": ["agent_stats", "call_duration", "transfer_rate"]
        }
    ]
    
    return {
        "success": True,
        "templates": templates
    } 