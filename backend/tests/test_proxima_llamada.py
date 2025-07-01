import pytest
from fastapi.testclient import TestClient
import json
from datetime import datetime
from unittest.mock import patch, MagicMock
import uuid

from backend.main import app
from app.models.llamada import Llamada
from app.models.usuario import Usuario
from app.database import obtener_sesion_context
from app.auth.dependencies import USUARIOS_SIMULADOS

# Cliente de teste
client = TestClient(app)

# Constantes
API_URL = "/api/v1/llamadas/proxima"  # URL completa segun la configuracion en main.py

@pytest.fixture
def crear_llamada_pendiente():
    """Fixture para crear una llamada en estado 'pendiente' para las pruebas"""
    with obtener_sesion_context() as db:
        # Crear una llamada de prueba
        llamada = Llamada(
            numero_destino="666123456",
            cli="912345678",
            id_campana=1,
            fecha_inicio=datetime.now(),
            estado="pendiente"
        )
        db.add(llamada)
        db.commit()
        db.refresh(llamada)
        
        # Devolver el ID para usar en las pruebas
        llamada_id = llamada.id
        
    # Despues de la prueba, se limpia automaticamente con el context manager
    return llamada_id

@pytest.fixture
def crear_llamada_en_progreso():
    """Fixture para crear una llamada en estado 'en_progreso' asignada a un usuario"""
    with obtener_sesion_context() as db:
        # ID de usuario administrador (simulado)
        usuario_id = list(USUARIOS_SIMULADOS.values())[0]["id"]
        
        # Crear una llamada de prueba ya asignada
        llamada = Llamada(
            numero_destino="666123456",
            cli="912345678",
            id_campana=1,
            fecha_inicio=datetime.now(),
            fecha_asignacion=datetime.now(),
            estado="en_progreso",
            usuario_id=usuario_id
        )
        db.add(llamada)
        db.commit()
        db.refresh(llamada)
        
        # Devolver el ID y el ID del usuario para usar en las pruebas
        return {
            "llamada_id": llamada.id,
            "usuario_id": usuario_id
        }

def test_proxima_llamada_usuario_cliente():
    """Test para verificar que un usuario cliente no puede acceder a la ruta"""
    
    # Headers con usuario cliente
    headers = {
        "Authorization": "cliente@example.com"
    }
    
    # Realizar la solicitud GET
    response = client.get(API_URL, headers=headers)
    
    # Verificar que devuelve un error 403
    assert response.status_code == 403
    
    # Verificar que el mensaje de error es adecuado
    datos_respuesta = response.json()
    assert "error" in datos_respuesta
    assert "permiso" in datos_respuesta["error"].lower()

def test_proxima_llamada_sin_llamadas_disponibles():
    """Test para verificar el comportamiento cuando no hay llamadas pendientes"""
    
    # Headers con usuario administrador
    headers = {
        "Authorization": "admin@example.com"
    }
    
    # Realizar la solicitud GET
    response = client.get(API_URL, headers=headers)
    
    # Verificar codigo de estado
    assert response.status_code == 200
    
    # Verificar que el mensaje indica que no hay llamadas
    datos_respuesta = response.json()
    assert "mensaje" in datos_respuesta
    assert "no hay llamadas" in datos_respuesta["mensaje"].lower()

def test_proxima_llamada_con_llamada_en_progreso(crear_llamada_en_progreso):
    """Test para verificar que si el usuario ya tiene una llamada, devuelve esa misma"""
    
    # Obtener datos de la llamada en progreso
    datos_llamada = crear_llamada_en_progreso
    
    # Headers con el usuario que ya tiene una llamada
    headers = {
        "Authorization": "admin@example.com"
    }
    
    # Realizar la solicitud GET
    response = client.get(API_URL, headers=headers)
    
    # Verificar codigo de estado
    assert response.status_code == 200
    
    # Verificar que devuelve la llamada existente
    datos_respuesta = response.json()
    assert "llamada_id" in datos_respuesta
    assert datos_respuesta["llamada_id"] == datos_llamada["llamada_id"]
    assert datos_respuesta["estado"] == "en_progreso"

def test_proxima_llamada_asignar_nueva(crear_llamada_pendiente):
    """Test para verificar la asignacion de una nueva llamada pendiente"""
    
    # Obtener ID de la llamada pendiente
    llamada_id = crear_llamada_pendiente
    
    # Headers con usuario integrador (que no tiene llamadas asignadas)
    headers = {
        "Authorization": "integrador@example.com"
    }
    
    # Realizar la solicitud GET
    response = client.get(API_URL, headers=headers)
    
    # Verificar codigo de estado
    assert response.status_code == 200
    
    # Verificar que se asigno la llamada correctamente
    datos_respuesta = response.json()
    assert "llamada_id" in datos_respuesta
    assert datos_respuesta["llamada_id"] == llamada_id
    assert datos_respuesta["estado"] == "en_progreso"
    
    # Verificar que se actualizo en la base de datos
    with obtener_sesion_context() as db:
        llamada = db.query(Llamada).filter(Llamada.id == llamada_id).first()
        assert llamada is not None
        assert llamada.estado == "en_progreso"
        assert llamada.fecha_asignacion is not None
        assert llamada.usuario_id is not None

def test_proxima_llamada_error_db():
    """Test para verificar el manejo de errores de base de datos"""
    
    # Headers con usuario administrador
    headers = {
        "Authorization": "admin@example.com"
    }
    
    # Simular un error en la base de datos
    with patch('sqlalchemy.orm.Session.commit') as mock_commit:
        # Hacer que commit lance una excepcion
        mock_commit.side_effect = Exception("Error simulado de base de datos")
        
        # Realizar la solicitud GET
        response = client.get(API_URL, headers=headers)
    
    # Verificar que devuelve un error 500
    assert response.status_code == 500
    
    # Verificar que el mensaje de error es adecuado
    datos_respuesta = response.json()
    assert "error" in datos_respuesta
    assert "error" in datos_respuesta["error"].lower() 