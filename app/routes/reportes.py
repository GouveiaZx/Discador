from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import date, datetime, timedelta
import io
import csv

from app.database import obtener_sesion
# Importar servicios y modelos necesarios

router = APIRouter(tags=["Reportes"])

@router.get("/exportar", summary="Exportar llamadas del día en CSV")
async def exportar_llamadas(
    fecha: date = Query(None, description="Fecha de las llamadas (formato YYYY-MM-DD). Por defecto es hoy."),
    db: Session = Depends(obtener_sesion)
):
    """
    Exporta las llamadas del día especificado en un archivo CSV.
    
    Parámetros:
        fecha: Fecha de las llamadas a exportar (formato YYYY-MM-DD)
        
    Retorna:
        StreamingResponse: Archivo CSV con las llamadas
    """
    try:
        # Si no se especifica fecha, usar hoy
        if fecha is None:
            fecha = date.today()
            
        # En una implementación real, aquí se consultarían las llamadas de la base de datos
        # Por ahora, generamos datos de ejemplo
        llamadas = [
            {
                "id": 1,
                "numero_destino": "3051234567",
                "cli": "3052345678",
                "fecha_hora": datetime.combine(fecha, datetime.min.time()) + timedelta(hours=9, minutes=30),
                "duracion": 45,
                "estado": "completada",
                "presiono_1": True,
                "transcripcion": "Sí, me interesa el producto. Pueden llamarme más tarde."
            },
            {
                "id": 2,
                "numero_destino": "3059876543",
                "cli": "3058765432",
                "fecha_hora": datetime.combine(fecha, datetime.min.time()) + timedelta(hours=10, minutes=15),
                "duracion": 30,
                "estado": "completada",
                "presiono_1": False,
                "transcripcion": None
            }
        ]
        
        # Crear archivo CSV en memoria
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=llamadas[0].keys())
        writer.writeheader()
        writer.writerows(llamadas)
        
        # Preparar respuesta
        output.seek(0)
        fecha_str = fecha.strftime("%Y-%m-%d")
        filename = f"llamadas_{fecha_str}.csv"
        
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al exportar llamadas: {str(e)}") 