import pytest
from fastapi.testclient import TestClient
import json
from datetime import datetime
from unittest.mock import patch

from backend.main import app
from app.models.llamada import Llamada
from app.database import obtener_sesion_context

# Cliente de teste
client = TestClient(app)

# Constantes
API_URL = "/api/v1/llamadas/presione1"  # URL completa segun la configuracion en main.py

@pytest.fixture
def crear_llamada_en_progreso():
    """Fixture para crear una llamada en estado 'en_progreso' para las pruebas"""
    with obtener_sesion_context() as db:
        # Crear una llamada de prueba
        llamada = Llamada(
            numero_destino="666123456",
            cli="912345678",
            id_campana=1,
            fecha_inicio=datetime.now(),
            estado="en_progreso"
        )
        db.add(llamada)
        db.commit()
        db.refresh(llamada)
        
        # Devolver el ID para usar en las pruebas
        llamada_id = llamada.id
        
    # Despues de la prueba, se limpia automaticamente con el context manager
    return llamada_id

@pytest.fixture
def crear_llamada_conectada():
    """Fixture para crear una llamada ya conectada para probar el caso de error"""
    with obtener_sesion_context() as db:
        # Crear una llamada de prueba ya conectada
        llamada = Llamada(
            numero_destino="666123456",
            cli="912345678",
            id_campana=1,
            fecha_inicio=datetime.now(),
            fecha_conexion=datetime.now(),
            estado="conectada",
            presiono_1=True
        )
        db.add(llamada)
        db.commit()
        db.refresh(llamada)
        
        # Devolver el ID para usar en las pruebas
        llamada_id = llamada.id
        
    # Despues de la prueba, se limpia automaticamente con el context manager
    return llamada_id

def test_presione1_llamada_no_encontrada():
    """Test para verificar el comportamiento cuando la llamada no existe"""
    
    # ID de llamada que presumiblemente no existe
    datos = {
        "llamada_id": 999999
    }
    
    # Realizar la solicitud POST
    response = client.post(API_URL, json=datos)
    
    # Verificar que devuelve un error 404
    assert response.status_code == 404
    
    # Verificar que el mensaje de error es adecuado
    datos_respuesta = response.json()
    assert "no existe" in datos_respuesta["detail"].lower()

def test_presione1_llamada_estado_incorrecto(crear_llamada_conectada):
    """Test para verificar el comportamiento cuando la llamada ya esta conectada"""
    
    # Obtener ID de la llamada ya conectada
    llamada_id = crear_llamada_conectada
    
    # Datos para la solicitud
    datos = {
        "llamada_id": llamada_id
    }
    
    # Realizar la solicitud POST
    response = client.post(API_URL, json=datos)
    
    # Verificar que devuelve un error 400
    assert response.status_code == 400
    
    # Verificar que el mensaje de error es adecuado
    datos_respuesta = response.json()
    assert "estado" in datos_respuesta["detail"].lower()
    assert "conectada" in datos_respuesta["detail"].lower() or "en_progreso" in datos_respuesta["detail"].lower()

def test_presione1_correcto(crear_llamada_en_progreso):
    """Test para verificar el flujo correcto de presione1"""
    
    # Obtener ID de la llamada en progreso
    llamada_id = crear_llamada_en_progreso
    
    # Datos para la solicitud
    datos = {
        "llamada_id": llamada_id
    }
    
    # Realizar la solicitud POST
    response = client.post(API_URL, json=datos)
    
    # Verificar codigo de estado
    assert response.status_code == 200
    
    # Verificar estructura de la respuesta
    datos_respuesta = response.json()
    assert "mensaje" in datos_respuesta
    assert "estado" in datos_respuesta
    assert "llamada_id" in datos_respuesta
    assert "detalles" in datos_respuesta
    
    # Verificar valores especificos
    assert datos_respuesta["estado"] == "conectada"
    assert datos_respuesta["llamada_id"] == llamada_id
    assert "fecha_conexion" in datos_respuesta["detalles"]
    assert datos_respuesta["detalles"]["dtmf"] == "1"
    
    # Verificar que se ha actualizado en la base de datos
    with obtener_sesion_context() as db:
        llamada = db.query(Llamada).filter(Llamada.id == llamada_id).first()
        assert llamada is not None
        assert llamada.estado == "conectada"
        assert llamada.fecha_conexion is not None
        assert llamada.presiono_1 is True
        assert llamada.dtmf_detectado == "1"

def test_presione1_error_db():
    """Test para verificar el manejo de errores de base de datos"""
    
    # Datos para la solicitud
    datos = {
        "llamada_id": 1  # ID cualquiera
    }
    
    # Simular un error en la base de datos
    with patch('sqlalchemy.orm.Session.commit') as mock_commit:
        # Hacer que commit lance una excepcion
        mock_commit.side_effect = Exception("Error simulado de base de datos")
        
        # Realizar la solicitud POST
        response = client.post(API_URL, json=datos)
    
    # Verificar que devuelve un error 500
    assert response.status_code == 500
    
    # Verificar que el mensaje de error es adecuado
    datos_respuesta = response.json()
    assert "error" in datos_respuesta["detail"].lower() 