import os
import csv
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors

class ReportsService:
    """
    Serviço para gerar relatórios
    """
    
    def __init__(self):
        self.reports_dir = "reports"
        os.makedirs(self.reports_dir, exist_ok=True)
    
    async def get_campaign_stats(self, campaign_id: int = None, start_date: str = None, end_date: str = None):
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
                ]
            }
            
            return stats
            
        except Exception as e:
            print(f"Erro ao obter estatísticas: {e}")
            return {}
    
    async def generate_pdf_report(self, data: Dict[str, Any], report_type: str = "campaign") -> str:
        """
        Gerar relatório PDF
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"relatorio_{report_type}_{timestamp}.pdf"
            filepath = os.path.join(self.reports_dir, filename)
            
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
            
            # Gerar PDF
            doc.build(story)
            
            return filepath
            
        except Exception as e:
            print(f"Erro ao gerar PDF: {e}")
            raise e
    
    async def generate_csv_report(self, data: Dict[str, Any], report_type: str = "campaign") -> str:
        """
        Gerar relatório CSV
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"relatorio_{report_type}_{timestamp}.csv"
            filepath = os.path.join(self.reports_dir, filename)
            
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
            
            return filepath
            
        except Exception as e:
            print(f"Erro ao gerar CSV: {e}")
            raise e
    
    async def list_reports(self):
        """
        Listar relatórios disponíveis
        """
        try:
            reports = []
            
            if os.path.exists(self.reports_dir):
                for filename in os.listdir(self.reports_dir):
                    if filename.endswith(('.pdf', '.csv')):
                        filepath = os.path.join(self.reports_dir, filename)
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
            
            return reports
            
        except Exception as e:
            print(f"Erro ao listar relatórios: {e}")
            return []
    
    async def delete_report(self, filename: str):
        """
        Deletar relatório
        """
        try:
            filepath = os.path.join(self.reports_dir, filename)
            
            if not os.path.exists(filepath):
                return False
            
            os.remove(filepath)
            return True
            
        except Exception as e:
            print(f"Erro ao deletar relatório: {e}")
            return False 