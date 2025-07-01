import pytest
import uuid
import csv
import io
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.main import app
from app.models.llamada import Llamada
from app.models.usuario import Usuario
from app.services.llamadas import LlamadasService

# Cliente de prueba
client = TestClient(app)

# Mock para usuario administrador
@pytest.fixture
def mock_usuario_admin():
    """Crea un mock para un usuario administrador"""
    return Usuario(
        id=uuid.uuid4(),
        email="admin@test.com",
        nombre="Admin Test",
        es_administrador=True,
        tiene_permiso_llamadas=True
    )

# Mock para usuario regular (no administrador)
@pytest.fixture
def mock_usuario_regular():
    """Crea un mock para un usuario regular (no administrador)"""
    return Usuario(
        id=uuid.uuid4(),
        email="usuario@test.com",
        nombre="Usuario Test",
        es_administrador=False,
        tiene_permiso_llamadas=True
    )

# Mock para llamadas finalizadas
@pytest.fixture
def mock_llamadas_finalizadas():
    """Crea mocks para llamadas finalizadas"""
    usuario_id = uuid.uuid4()
    ahora = datetime.now()
    
    # Crear varias llamadas con diferentes resultados
    llamada1 = Llamada(
        id=1,
        numero_destino="+5491112345678",
        usuario_id=usuario_id,
        fecha_inicio=ahora - timedelta(minutes=10),
        fecha_asignacion=ahora - timedelta(minutes=9),
        fecha_conexion=ahora - timedelta(minutes=8),
        fecha_finalizacion=ahora - timedelta(minutes=5),
        estado="finalizada",
        resultado="contestada",
        duracion=300  # 5 minutos
    )
    
    llamada2 = Llamada(
        id=2,
        numero_destino="+5491187654321",
        usuario_id=usuario_id,
        fecha_inicio=ahora - timedelta(minutes=20),
        fecha_asignacion=ahora - timedelta(minutes=19),
        fecha_conexion=None,
        fecha_finalizacion=ahora - timedelta(minutes=18),
        estado="finalizada",
        resultado="no_contesta",
        duracion=120  # 2 minutos
    )
    
    return [
        (llamada1, "usuario@test.com"),
        (llamada2, "usuario@test.com")
    ]

# Mock para ninguna llamada finalizada
@pytest.fixture
def mock_llamadas_vacias():
    """Crea un mock para ninguna llamada finalizada"""
    return []

# Patch para autenticacion con usuario administrador
@pytest.fixture
def patch_auth_admin(mock_usuario_admin):
    """Patch para autenticacion con usuario administrador"""
    with patch("app.routes.llamadas.get_current_user_simulado", return_value=mock_usuario_admin):
        yield

# Patch para autenticacion con usuario regular
@pytest.fixture
def patch_auth_regular(mock_usuario_regular):
    """Patch para autenticacion con usuario regular"""
    with patch("app.routes.llamadas.get_current_user_simulado", return_value=mock_usuario_regular):
        yield

# Patch para exportar CSV con llamadas
@pytest.fixture
def patch_exportar_csv(mock_llamadas_finalizadas):
    """Patch para el metodo exportar_llamadas_finalizadas_csv del servicio"""
    # Crear un CSV real con los datos mock
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "llamada_id", "numero_destino", "estado", "resultado", 
        "fecha_asignacion", "fecha_conexion", "fecha_finalizacion", 
        "duracion_segundos", "usuario_email"
    ])
    writer.writeheader()
    
    formato_fecha = "%Y-%m-%dT%H:%M:%S"
    
    for llamada, email in mock_llamadas_finalizadas:
        fecha_asignacion = llamada.fecha_asignacion.strftime(formato_fecha) if llamada.fecha_asignacion else ""
        fecha_conexion = llamada.fecha_conexion.strftime(formato_fecha) if llamada.fecha_conexion else ""
        fecha_finalizacion = llamada.fecha_finalizacion.strftime(formato_fecha) if llamada.fecha_finalizacion else ""
        
        writer.writerow({
            "llamada_id": llamada.id,
            "numero_destino": llamada.numero_destino,
            "estado": llamada.estado,
            "resultado": llamada.resultado,
            "fecha_asignacion": fecha_asignacion,
            "fecha_conexion": fecha_conexion,
            "fecha_finalizacion": fecha_finalizacion,
            "duracion_segundos": llamada.duracion,
            "usuario_email": email
        })
    
    csv_content = output.getvalue()
    output.close()
    
    with patch.object(LlamadasService, "exportar_llamadas_finalizadas_csv", return_value=csv_content):
        yield

# Patch para exportar CSV vacio
@pytest.fixture
def patch_exportar_csv_vacio(mock_llamadas_vacias):
    """Patch para el metodo exportar_llamadas_finalizadas_csv que devuelve un CSV vacio"""
    # Crear un CSV vacio con solo la cabecera
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=[
        "llamada_id", "numero_destino", "estado", "resultado", 
        "fecha_asignacion", "fecha_conexion", "fecha_finalizacion", 
        "duracion_segundos", "usuario_email"
    ])
    writer.writeheader()
    
    csv_content = output.getvalue()
    output.close()
    
    with patch.object(LlamadasService, "exportar_llamadas_finalizadas_csv", return_value=csv_content):
        yield

# Patch para exportar CSV con error
@pytest.fixture
def patch_exportar_csv_error():
    """Patch para el metodo exportar_llamadas_finalizadas_csv que devuelve un error"""
    with patch.object(
        LlamadasService, 
        "exportar_llamadas_finalizadas_csv", 
        side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Error al exportar llamadas a CSV"
        )
    ):
        yield

# Tests para el servicio de exportacion
class TestServicioExportacion:
    """Tests para el servicio de exportacion a CSV"""
    
    def test_exportar_llamadas_csv(self, mock_llamadas_finalizadas):
        """Test para exportar llamadas a CSV correctamente"""
        # Crear mock de db
        db = MagicMock()
        
        # Configurar mock para devolver llamadas finalizadas
        db.query().outerjoin().filter().order_by().all.return_value = mock_llamadas_finalizadas
        
        # Ejecutar el metodo
        resultado = LlamadasService.exportar_llamadas_finalizadas_csv(db)
        
        # Verificar que es un string (contenido CSV)
        assert isinstance(resultado, str)
        
        # Verificar que contiene las cabeceras esperadas
        assert "llamada_id,numero_destino,estado,resultado" in resultado
        
        # Verificar que contiene datos de las llamadas
        assert "+5491112345678" in resultado
        assert "+5491187654321" in resultado
        assert "contestada" in resultado
        assert "no_contesta" in resultado
    
    def test_exportar_llamadas_csv_vacio(self):
        """Test para exportar llamadas a CSV cuando no hay llamadas finalizadas"""
        # Crear mock de db
        db = MagicMock()
        
        # Configurar mock para devolver lista vacia
        db.query().outerjoin().filter().order_by().all.return_value = []
        
        # Ejecutar el metodo
        resultado = LlamadasService.exportar_llamadas_finalizadas_csv(db)
        
        # Verificar que es un string (contenido CSV)
        assert isinstance(resultado, str)
        
        # Verificar que contiene solo las cabeceras
        assert "llamada_id,numero_destino,estado,resultado" in resultado
        
        # Verificar que no contiene datos de llamadas (solo la cabecera)
        lineas = resultado.strip().split("\n")
        assert len(lineas) == 1  # Solo la linea de cabecera
    
    def test_exportar_llamadas_csv_error(self):
        """Test para manejo de errores al exportar llamadas a CSV"""
        # Crear mock de db
        db = MagicMock()
        
        # Configurar mock para lanzar excepcion
        db.query().outerjoin().filter().order_by().all.side_effect = Exception("Error de base de datos")
        
        # Verificar que se lance la excepcion HTTP
        with pytest.raises(HTTPException) as excinfo:
            LlamadasService.exportar_llamadas_finalizadas_csv(db)
        
        # Verificar el codigo de estado y el mensaje
        assert excinfo.value.status_code == 500
        assert "Error al exportar llamadas a CSV" in excinfo.value.detail

# Tests para la ruta de exportacion
class TestRutaExportacion:
    """Tests para la ruta de exportacion a CSV"""
    
    def test_exportar_llamadas_admin(self, patch_auth_admin, patch_exportar_csv):
        """Test para exportar llamadas con usuario administrador"""
        response = client.get("/api/v1/llamadas/exportar")
        
        # Verificar respuesta exitosa
        assert response.status_code == 200
        
        # Verificar headers de archivo descargable
        assert response.headers["Content-Type"] == "text/csv"
        assert "attachment; filename=llamadas_finalizadas_" in response.headers["Content-Disposition"]
        
        # Verificar contenido CSV
        content = response.content.decode("utf-8")
        assert "llamada_id,numero_destino,estado,resultado" in content
        assert "+5491112345678" in content
        assert "+5491187654321" in content
    
    def test_exportar_llamadas_csv_vacio(self, patch_auth_admin, patch_exportar_csv_vacio):
        """Test para exportar cuando no hay llamadas finalizadas"""
        response = client.get("/api/v1/llamadas/exportar")
        
        # Verificar respuesta exitosa (aunque no haya datos)
        assert response.status_code == 200
        
        # Verificar headers de archivo descargable
        assert response.headers["Content-Type"] == "text/csv"
        
        # Verificar contenido CSV (solo cabecera)
        content = response.content.decode("utf-8")
        assert "llamada_id,numero_destino,estado,resultado" in content
        
        # Verificar que no hay datos adicionales
        lineas = content.strip().split("\n")
        assert len(lineas) == 1  # Solo la linea de cabecera
    
    def test_exportar_llamadas_no_admin(self, patch_auth_regular):
        """Test para exportar llamadas con usuario no administrador"""
        response = client.get("/api/v1/llamadas/exportar")
        
        # Verificar denegacion de acceso
        assert response.status_code == 403
        assert "Solo los administradores pueden exportar" in response.json()["error"]
    
    def test_exportar_llamadas_error(self, patch_auth_admin, patch_exportar_csv_error):
        """Test para exportar llamadas con error"""
        response = client.get("/api/v1/llamadas/exportar")
        
        # Verificar error interno
        assert response.status_code == 500
        assert "Error al exportar llamadas" in response.json()["error"] 