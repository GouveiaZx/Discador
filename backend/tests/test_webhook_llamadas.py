import pytest
import os
import uuid
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from app.main import app
from app.models.llamada import Llamada
from app.services.llamadas import LlamadasService

# Cliente de prueba
client = TestClient(app)

# Simular API Key para pruebas
API_KEY_TEST = "test_api_key_for_webhook"

# Patch para ambiente de variable
@pytest.fixture(autouse=True)
def mock_env_api_key():
    """Configura una API Key de prueba en la variable de entorno"""
    with patch.dict(os.environ, {"WEBHOOK_API_KEY": API_KEY_TEST}):
        yield

# Mock para llamada existente
@pytest.fixture
def mock_llamada_en_progreso():
    """Crea un mock para una llamada en estado 'en_progreso'"""
    return Llamada(
        id=123,
        numero_destino="+5491112345678",
        usuario_id=uuid.uuid4(),
        fecha_inicio=datetime.now() - timedelta(minutes=5),
        fecha_asignacion=datetime.now() - timedelta(minutes=4),
        estado="en_progreso"
    )

# Mock para llamada conectada
@pytest.fixture
def mock_llamada_conectada():
    """Crea un mock para una llamada en estado 'conectada'"""
    return Llamada(
        id=456,
        numero_destino="+5491187654321",
        usuario_id=uuid.uuid4(),
        fecha_inicio=datetime.now() - timedelta(minutes=5),
        fecha_asignacion=datetime.now() - timedelta(minutes=4),
        fecha_conexion=datetime.now() - timedelta(minutes=3),
        estado="conectada"
    )

# Mock para llamada finalizada
@pytest.fixture
def mock_llamada_finalizada():
    """Crea un mock para una llamada en estado 'finalizada'"""
    ahora = datetime.now()
    return Llamada(
        id=789,
        numero_destino="+5491165432198",
        usuario_id=uuid.uuid4(),
        fecha_inicio=ahora - timedelta(minutes=10),
        fecha_asignacion=ahora - timedelta(minutes=9),
        fecha_conexion=ahora - timedelta(minutes=8),
        fecha_finalizacion=ahora - timedelta(minutes=5),
        estado="finalizada",
        resultado="contestada",
        duracion=300  # 5 minutos
    )

# Patch para actualizacion de llamada exitosa
@pytest.fixture
def patch_actualizar_estado_exitoso(mock_llamada_en_progreso):
    """Patch para el metodo de actualizacion de estado exitoso"""
    # Clonar la llamada y actualizar su estado
    llamada_actualizada = Llamada(
        id=mock_llamada_en_progreso.id,
        numero_destino=mock_llamada_en_progreso.numero_destino,
        usuario_id=mock_llamada_en_progreso.usuario_id,
        fecha_inicio=mock_llamada_en_progreso.fecha_inicio,
        fecha_asignacion=mock_llamada_en_progreso.fecha_asignacion,
        fecha_conexion=datetime.now(),
        estado="conectada"  # Estado actualizado
    )
    
    with patch.object(
        LlamadasService, 
        "actualizar_estado_llamada_desde_webhook", 
        return_value=llamada_actualizada
    ):
        yield

# Patch para llamada no encontrada
@pytest.fixture
def patch_llamada_no_encontrada():
    """Patch para simular llamada no encontrada"""
    with patch.object(
        LlamadasService, 
        "actualizar_estado_llamada_desde_webhook", 
        side_effect=HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La llamada con ID 999 no existe"
        )
    ):
        yield

# Patch para estado invalido
@pytest.fixture
def patch_estado_invalido():
    """Patch para simular estado invalido"""
    with patch.object(
        LlamadasService, 
        "actualizar_estado_llamada_desde_webhook", 
        side_effect=HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="El estado 'inexistente' no es valido para webhook"
        )
    ):
        yield

# Patch para transicion invalida
@pytest.fixture
def patch_transicion_invalida():
    """Patch para simular transicion de estado invalida"""
    with patch.object(
        LlamadasService, 
        "actualizar_estado_llamada_desde_webhook", 
        side_effect=HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="No se puede cambiar el estado de 'finalizada' a 'en_progreso'"
        )
    ):
        yield

# Tests para el servicio de webhook
class TestServicioWebhook:
    """Tests para el servicio de actualizacion de estado via webhook"""
    
    def test_actualizar_estado_exitoso(self, mock_llamada_en_progreso):
        """Test para actualizar estado correctamente"""
        # Crear mock de db y configurarlo para encontrar la llamada
        db = MagicMock()
        db.query().filter().first.return_value = mock_llamada_en_progreso
        
        # Ejecutar el metodo
        llamada_actualizada = LlamadasService.actualizar_estado_llamada_desde_webhook(
            db=db,
            llamada_id=mock_llamada_en_progreso.id,
            nuevo_estado="conectada"
        )
        
        # Verificar que se actualizo el estado
        assert llamada_actualizada.estado == "conectada"
        # Verificar que se hizo commit a la base de datos
        db.commit.assert_called_once()
    
    def test_llamada_no_encontrada(self):
        """Test para llamada no encontrada"""
        # Crear mock de db y configurarlo para no encontrar la llamada
        db = MagicMock()
        db.query().filter().first.return_value = None
        
        # Verificar que se lance la excepcion HTTP
        with pytest.raises(HTTPException) as excinfo:
            LlamadasService.actualizar_estado_llamada_desde_webhook(
                db=db,
                llamada_id=999,
                nuevo_estado="conectada"
            )
        
        # Verificar codigo de estado y mensaje
        assert excinfo.value.status_code == 404
        assert "no existe" in excinfo.value.detail
    
    def test_estado_invalido(self, mock_llamada_en_progreso):
        """Test para estado invalido"""
        # Crear mock de db y configurarlo para encontrar la llamada
        db = MagicMock()
        db.query().filter().first.return_value = mock_llamada_en_progreso
        
        # Verificar que se lance la excepcion HTTP
        with pytest.raises(HTTPException) as excinfo:
            LlamadasService.actualizar_estado_llamada_desde_webhook(
                db=db,
                llamada_id=mock_llamada_en_progreso.id,
                nuevo_estado="estado_invalido"
            )
        
        # Verificar codigo de estado y mensaje
        assert excinfo.value.status_code == 422
        assert "no es valido" in excinfo.value.detail
    
    def test_transicion_invalida(self, mock_llamada_finalizada):
        """Test para transicion de estado invalida"""
        # Crear mock de db y configurarlo para encontrar la llamada finalizada
        db = MagicMock()
        db.query().filter().first.return_value = mock_llamada_finalizada
        
        # Verificar que se lance la excepcion HTTP
        with pytest.raises(HTTPException) as excinfo:
            LlamadasService.actualizar_estado_llamada_desde_webhook(
                db=db,
                llamada_id=mock_llamada_finalizada.id,
                nuevo_estado="en_progreso"
            )
        
        # Verificar codigo de estado y mensaje
        assert excinfo.value.status_code == 422
        assert "No se puede cambiar" in excinfo.value.detail

# Tests para la ruta de webhook
class TestRutaWebhook:
    """Tests para la ruta de webhook"""
    
    def test_actualizar_estado_exitoso(self, patch_actualizar_estado_exitoso):
        """Test para actualizar estado con API Key valida"""
        response = client.post(
            "/api/v1/llamadas/webhook",
            headers={"X-API-Key": API_KEY_TEST},
            json={"llamada_id": 123, "nuevo_estado": "conectada"}
        )
        
        # Verificar respuesta exitosa
        assert response.status_code == 200
        data = response.json()
        assert data["mensaje"] == "Estado de llamada actualizado"
        assert data["estado_actual"] == "conectada"
    
    def test_api_key_invalida(self):
        """Test para API Key invalida"""
        response = client.post(
            "/api/v1/llamadas/webhook",
            headers={"X-API-Key": "clave_incorrecta"},
            json={"llamada_id": 123, "nuevo_estado": "conectada"}
        )
        
        # Verificar error de autenticacion
        assert response.status_code == 403
        assert "API Key invalida" in response.json()["error"]
    
    def test_llamada_no_encontrada(self, patch_llamada_no_encontrada):
        """Test para llamada no encontrada"""
        response = client.post(
            "/api/v1/llamadas/webhook",
            headers={"X-API-Key": API_KEY_TEST},
            json={"llamada_id": 999, "nuevo_estado": "conectada"}
        )
        
        # Verificar error de llamada no encontrada
        assert response.status_code == 404
        assert "no existe" in response.json()["error"]
    
    def test_estado_invalido(self, patch_estado_invalido):
        """Test para estado invalido"""
        response = client.post(
            "/api/v1/llamadas/webhook",
            headers={"X-API-Key": API_KEY_TEST},
            json={"llamada_id": 123, "nuevo_estado": "inexistente"}
        )
        
        # Verificar error de estado invalido
        assert response.status_code == 422
        assert "no es valido" in response.json()["error"]
    
    def test_transicion_invalida(self, patch_transicion_invalida):
        """Test para transicion de estado invalida"""
        response = client.post(
            "/api/v1/llamadas/webhook",
            headers={"X-API-Key": API_KEY_TEST},
            json={"llamada_id": 789, "nuevo_estado": "en_progreso"}
        )
        
        # Verificar error de transicion invalida
        assert response.status_code == 422
        assert "No se puede cambiar" in response.json()["error"] 