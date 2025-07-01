import pytest
import uuid
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.main import app
from app.models.llamada import Llamada
from app.models.usuario import Usuario
from app.services.llamadas import LlamadasService
from app.schemas.estadisticas import EstadisticasLlamadasResponse

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

# Mock para estadisticas de llamadas
@pytest.fixture
def mock_estadisticas():
    """Crea un mock para las estadisticas de llamadas"""
    return {
        "total_llamadas": 132,
        "por_estado": {
            "pendiente": 12,
            "en_progreso": 15,
            "conectada": 20,
            "finalizada": 85
        },
        "por_resultado": {
            "contestada": 40,
            "no_contesta": 30,
            "buzon": 10,
            "numero_invalido": 5,
            "otro": 0
        },
        "en_progreso_por_usuario": {
            "integrador1@example.com": 2,
            "integrador2@example.com": 3
        }
    }

# Mock para estadisticas vacias
@pytest.fixture
def mock_estadisticas_vacias():
    """Crea un mock para estadisticas vacias"""
    return {
        "total_llamadas": 0,
        "por_estado": {
            "pendiente": 0,
            "en_progreso": 0,
            "conectada": 0,
            "finalizada": 0
        },
        "por_resultado": {
            "contestada": 0,
            "no_contesta": 0,
            "buzon": 0,
            "numero_invalido": 0,
            "otro": 0
        },
        "en_progreso_por_usuario": {}
    }

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

# Patch para obtener estadisticas
@pytest.fixture
def patch_obtener_estadisticas(mock_estadisticas):
    """Patch para el metodo obtener_estadisticas del servicio"""
    with patch.object(LlamadasService, "obtener_estadisticas", return_value=mock_estadisticas):
        yield

# Patch para obtener estadisticas vacias
@pytest.fixture
def patch_obtener_estadisticas_vacias(mock_estadisticas_vacias):
    """Patch para el metodo obtener_estadisticas del servicio con datos vacios"""
    with patch.object(LlamadasService, "obtener_estadisticas", return_value=mock_estadisticas_vacias):
        yield

# Patch para obtener estadisticas con error
@pytest.fixture
def patch_obtener_estadisticas_error():
    """Patch para el metodo obtener_estadisticas del servicio que devuelve error"""
    with patch.object(
        LlamadasService, 
        "obtener_estadisticas", 
        side_effect=HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Error al obtener estadisticas"
        )
    ):
        yield

# Tests para el servicio de estadisticas
class TestServicioEstadisticas:
    """Tests para el servicio de estadisticas"""
    
    def test_obtener_estadisticas(self):
        """Test para obtener estadisticas correctamente"""
        # Crear mock de db
        db = MagicMock()
        
        # Configurar mock para total de llamadas
        db.query().scalar.return_value = 132
        
        # Configurar mock para llamadas por estado
        estados_mock = [
            ("pendiente", 12),
            ("en_progreso", 15),
            ("conectada", 20),
            ("finalizada", 85)
        ]
        db.query().group_by().all.return_value = estados_mock
        
        # Configurar mock para llamadas por resultado
        resultados_mock = [
            ("contestada", 40),
            ("no_contesta", 30),
            ("buzon", 10),
            ("numero_invalido", 5)
        ]
        db.query().filter().group_by().all.return_value = resultados_mock
        
        # Configurar mock para llamadas en progreso por usuario
        en_progreso_mock = [
            ("integrador1@example.com", 2),
            ("integrador2@example.com", 3)
        ]
        db.query().join().filter().group_by().order_by().all.return_value = en_progreso_mock
        
        # Ejecutar el metodo
        resultado = LlamadasService.obtener_estadisticas(db)
        
        # Verificar resultado
        assert resultado["total_llamadas"] == 132
        assert resultado["por_estado"]["pendiente"] == 12
        assert resultado["por_estado"]["en_progreso"] == 15
        assert resultado["por_estado"]["conectada"] == 20
        assert resultado["por_estado"]["finalizada"] == 85
        assert resultado["por_resultado"]["contestada"] == 40
        assert resultado["por_resultado"]["no_contesta"] == 30
        assert resultado["por_resultado"]["buzon"] == 10
        assert resultado["por_resultado"]["numero_invalido"] == 5
        assert resultado["por_resultado"]["otro"] == 0
        assert resultado["en_progreso_por_usuario"]["integrador1@example.com"] == 2
        assert resultado["en_progreso_por_usuario"]["integrador2@example.com"] == 3
    
    def test_obtener_estadisticas_error(self):
        """Test para manejo de errores al obtener estadisticas"""
        # Crear mock de db
        db = MagicMock()
        
        # Configurar mock para lanzar excepcion
        db.query().scalar.side_effect = Exception("Error de base de datos")
        
        # Verificar que se lance la excepcion HTTP
        with pytest.raises(HTTPException) as excinfo:
            LlamadasService.obtener_estadisticas(db)
        
        # Verificar el codigo de estado y el mensaje
        assert excinfo.value.status_code == 500
        assert "Error al obtener estadisticas" in excinfo.value.detail

# Tests para la ruta de estadisticas
class TestRutaEstadisticas:
    """Tests para la ruta de estadisticas"""
    
    def test_obtener_estadisticas_admin(self, patch_auth_admin, patch_obtener_estadisticas):
        """Test para obtener estadisticas con usuario administrador"""
        response = client.get("/api/v1/llamadas/estadisticas")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_llamadas"] == 132
        assert data["por_estado"]["pendiente"] == 12
        assert data["por_estado"]["en_progreso"] == 15
        assert data["por_estado"]["conectada"] == 20
        assert data["por_estado"]["finalizada"] == 85
        assert data["por_resultado"]["contestada"] == 40
        assert data["por_resultado"]["no_contesta"] == 30
        assert data["por_resultado"]["buzon"] == 10
        assert data["por_resultado"]["numero_invalido"] == 5
        assert data["por_resultado"]["otro"] == 0
        assert data["en_progreso_por_usuario"]["integrador1@example.com"] == 2
        assert data["en_progreso_por_usuario"]["integrador2@example.com"] == 3
    
    def test_obtener_estadisticas_no_admin(self, patch_auth_regular, patch_obtener_estadisticas):
        """Test para obtener estadisticas con usuario no administrador"""
        response = client.get("/api/v1/llamadas/estadisticas")
        
        assert response.status_code == 403
        assert "Solo los administradores pueden acceder" in response.json()["error"]
    
    def test_obtener_estadisticas_vacias(self, patch_auth_admin, patch_obtener_estadisticas_vacias):
        """Test para obtener estadisticas vacias"""
        response = client.get("/api/v1/llamadas/estadisticas")
        
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_llamadas"] == 0
        assert data["por_estado"]["pendiente"] == 0
        assert data["por_estado"]["en_progreso"] == 0
        assert data["por_estado"]["conectada"] == 0
        assert data["por_estado"]["finalizada"] == 0
        assert data["por_resultado"]["contestada"] == 0
        assert data["por_resultado"]["no_contesta"] == 0
        assert data["por_resultado"]["buzon"] == 0
        assert data["por_resultado"]["numero_invalido"] == 0
        assert data["por_resultado"]["otro"] == 0
        assert data["en_progreso_por_usuario"] == {}
    
    def test_obtener_estadisticas_error(self, patch_auth_admin, patch_obtener_estadisticas_error):
        """Test para obtener estadisticas con error"""
        response = client.get("/api/v1/llamadas/estadisticas")
        
        assert response.status_code == 500
        assert "Error al obtener estadisticas" in response.json()["error"] 