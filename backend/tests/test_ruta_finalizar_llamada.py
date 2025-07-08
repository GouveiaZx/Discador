import pytest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException, status
from fastapi.testclient import TestClient
import uuid

from app.main import app
from app.models.llamada import Llamada
from app.models.usuario import Usuario
from app.services.llamadas import LlamadasService

# Cliente de prueba
client = TestClient(app)

# Mock para usuario autenticado
@pytest.fixture
def mock_usuario_autenticado():
    """Crea un mock para el usuario autenticado"""
    usuario = Usuario(
        id=uuid.uuid4(),
        email="usuario@test.com",
        nombre="Usuario Test",
        es_administrador=False,
        tiene_permiso_llamadas=True
    )
    return usuario

# Mock para llamada finalizada
@pytest.fixture
def mock_llamada_finalizada():
    """Crea un mock para una llamada finalizada"""
    return Llamada(
        id=123,
        numero_destino="+5491112345678",
        fecha_inicio="2023-07-01T10:00:00",
        fecha_finalizacion="2023-07-01T10:05:30",
        estado="finalizada",
        resultado="contestada"
    )

# Patch para get_current_user_simulado
@pytest.fixture
def patch_get_current_user(mock_usuario_autenticado):
    """Patch para la funcion get_current_user_simulado"""
    with patch("app.routes.llamadas.get_current_user_simulado", return_value=mock_usuario_autenticado):
        yield

# Patch para finalizar_llamada del servicio
@pytest.fixture
def patch_finalizar_llamada(mock_llamada_finalizada):
    """Patch para el metodo finalizar_llamada del servicio"""
    with patch.object(LlamadasService, "finalizar_llamada", return_value=mock_llamada_finalizada):
        yield

# Patch para finalizar_llamada con error 404
@pytest.fixture
def patch_finalizar_llamada_404():
    """Patch para el metodo finalizar_llamada que devuelve error 404"""
    with patch.object(
        LlamadasService, 
        "finalizar_llamada", 
        side_effect=HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="La llamada no existe")
    ):
        yield

# Patch para finalizar_llamada con error 403
@pytest.fixture
def patch_finalizar_llamada_403():
    """Patch para el metodo finalizar_llamada que devuelve error 403"""
    with patch.object(
        LlamadasService, 
        "finalizar_llamada", 
        side_effect=HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No tienes permiso")
    ):
        yield

# Patch para finalizar_llamada con error 400
@pytest.fixture
def patch_finalizar_llamada_400():
    """Patch para el metodo finalizar_llamada que devuelve error 400"""
    with patch.object(
        LlamadasService, 
        "finalizar_llamada", 
        side_effect=HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Resultado invalido")
    ):
        yield

# Patch para finalizar_llamada con error 500
@pytest.fixture
def patch_finalizar_llamada_500():
    """Patch para el metodo finalizar_llamada que devuelve error 500"""
    with patch.object(
        LlamadasService, 
        "finalizar_llamada", 
        side_effect=HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno")
    ):
        yield

# Tests para la ruta /finalizar
def test_finalizar_llamada_exitoso(patch_get_current_user, patch_finalizar_llamada):
    """Test para finalizar una llamada correctamente desde la ruta"""
    datos = {
        "llamada_id": 123,
        "resultado": "contestada"
    }
    
    response = client.post("/api/v1/llamadas/finalizar", json=datos)
    
    assert response.status_code == 200
    assert response.json()["mensaje"] == "Llamada finalizada correctamente"
    assert response.json()["llamada_id"] == 123
    assert response.json()["estado"] == "finalizada"
    assert response.json()["resultado"] == "contestada"

def test_finalizar_llamada_404(patch_get_current_user, patch_finalizar_llamada_404):
    """Test para finalizar una llamada que no existe desde la ruta"""
    datos = {
        "llamada_id": 999,
        "resultado": "contestada"
    }
    
    response = client.post("/api/v1/llamadas/finalizar", json=datos)
    
    assert response.status_code == 404
    assert "La llamada no existe" in response.json()["error"]

def test_finalizar_llamada_403(patch_get_current_user, patch_finalizar_llamada_403):
    """Test para finalizar una llamada sin permiso desde la ruta"""
    datos = {
        "llamada_id": 123,
        "resultado": "contestada"
    }
    
    response = client.post("/api/v1/llamadas/finalizar", json=datos)
    
    assert response.status_code == 403
    assert "No tienes permiso" in response.json()["error"]

def test_finalizar_llamada_400(patch_get_current_user, patch_finalizar_llamada_400):
    """Test para finalizar una llamada con resultado invalido desde la ruta"""
    datos = {
        "llamada_id": 123,
        "resultado": "resultado_invalido"
    }
    
    response = client.post("/api/v1/llamadas/finalizar", json=datos)
    
    assert response.status_code == 400
    assert "Resultado invalido" in response.json()["error"]

def test_finalizar_llamada_500(patch_get_current_user, patch_finalizar_llamada_500):
    """Test para finalizar una llamada con error interno desde la ruta"""
    datos = {
        "llamada_id": 123,
        "resultado": "contestada"
    }
    
    response = client.post("/api/v1/llamadas/finalizar", json=datos)
    
    assert response.status_code == 500
    assert "Error interno" in response.json()["error"]

def test_finalizar_llamada_schema_invalido(patch_get_current_user):
    """Test para finalizar una llamada con esquema invalido desde la ruta"""
    # Llamada sin resultado
    datos = {
        "llamada_id": 123
    }
    
    response = client.post("/api/v1/llamadas/finalizar", json=datos)
    assert response.status_code == 422
    
    # Resultado fuera de los valores permitidos
    datos = {
        "llamada_id": 123,
        "resultado": "valor_no_permitido"
    }
    
    response = client.post("/api/v1/llamadas/finalizar", json=datos)
    assert response.status_code == 422 