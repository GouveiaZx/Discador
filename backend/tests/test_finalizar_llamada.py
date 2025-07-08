import pytest
import uuid
from unittest.mock import MagicMock, patch
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.models.llamada import Llamada
from app.models.usuario import Usuario
from app.services.llamadas import LlamadasService

# Fixtures para los tests
@pytest.fixture
def mock_db():
    """Crea un mock de la sesion de base de datos"""
    return MagicMock()

@pytest.fixture
def usuario_regular():
    """Crea un usuario regular para las pruebas"""
    return Usuario(
        id=uuid.uuid4(),
        email="usuario@test.com",
        nombre="Usuario Test",
        es_administrador=False,
        tiene_permiso_llamadas=True
    )

@pytest.fixture
def usuario_admin():
    """Crea un usuario administrador para las pruebas"""
    return Usuario(
        id=uuid.uuid4(),
        email="admin@test.com",
        nombre="Admin Test",
        es_administrador=True,
        tiene_permiso_llamadas=True
    )

@pytest.fixture
def llamada_activa(usuario_regular):
    """Crea una llamada en progreso para las pruebas"""
    return Llamada(
        id=123,
        numero_destino="+5491112345678",
        usuario_id=usuario_regular.id,
        fecha_inicio=datetime.now() - timedelta(minutes=5),
        estado="en_progreso"
    )

@pytest.fixture
def llamada_conectada(usuario_regular):
    """Crea una llamada conectada para las pruebas"""
    return Llamada(
        id=124,
        numero_destino="+5491112345679",
        usuario_id=usuario_regular.id,
        fecha_inicio=datetime.now() - timedelta(minutes=5),
        fecha_conexion=datetime.now() - timedelta(minutes=3),
        estado="conectada",
        presiono_1=True
    )

@pytest.fixture
def llamada_finalizada(usuario_regular):
    """Crea una llamada finalizada para las pruebas"""
    return Llamada(
        id=125,
        numero_destino="+5491112345680",
        usuario_id=usuario_regular.id,
        fecha_inicio=datetime.now() - timedelta(minutes=10),
        fecha_conexion=datetime.now() - timedelta(minutes=8),
        fecha_finalizacion=datetime.now() - timedelta(minutes=2),
        estado="finalizada",
        resultado="contestada",
        presiono_1=True
    )

# Tests para finalizar_llamada
def test_finalizar_llamada_exitoso(mock_db, usuario_regular, llamada_activa):
    """Test para finalizar una llamada correctamente"""
    # Configurar el mock para devolver la llamada
    mock_db.query.return_value.filter.return_value.first.return_value = llamada_activa
    
    # Ejecutar el metodo finalizar_llamada
    resultado = LlamadasService.finalizar_llamada(
        db=mock_db,
        llamada_id=llamada_activa.id,
        resultado="contestada",
        usuario=usuario_regular
    )
    
    # Verificar que se actualizo la llamada
    assert resultado.estado == "finalizada"
    assert resultado.resultado == "contestada"
    assert resultado.fecha_finalizacion is not None
    
    # Verificar que se hizo commit a la base de datos
    mock_db.commit.assert_called_once()

def test_finalizar_llamada_conectada(mock_db, usuario_regular, llamada_conectada):
    """Test para finalizar una llamada que esta en estado conectada"""
    # Configurar el mock para devolver la llamada
    mock_db.query.return_value.filter.return_value.first.return_value = llamada_conectada
    
    # Ejecutar el metodo finalizar_llamada
    resultado = LlamadasService.finalizar_llamada(
        db=mock_db,
        llamada_id=llamada_conectada.id,
        resultado="no_contesta",
        usuario=usuario_regular
    )
    
    # Verificar que se actualizo la llamada
    assert resultado.estado == "finalizada"
    assert resultado.resultado == "no_contesta"
    assert resultado.fecha_finalizacion is not None
    
    # Verificar que se hizo commit a la base de datos
    mock_db.commit.assert_called_once()

def test_finalizar_llamada_admin_cualquier_llamada(mock_db, usuario_admin, llamada_activa):
    """Test para verificar que un admin puede finalizar cualquier llamada"""
    # Configurar la llamada para que pertenezca a otro usuario
    llamada_activa.usuario_id = uuid.uuid4()  # ID diferente al del admin
    
    # Configurar el mock para devolver la llamada
    mock_db.query.return_value.filter.return_value.first.return_value = llamada_activa
    
    # Ejecutar el metodo finalizar_llamada
    resultado = LlamadasService.finalizar_llamada(
        db=mock_db,
        llamada_id=llamada_activa.id,
        resultado="buzon",
        usuario=usuario_admin
    )
    
    # Verificar que se actualizo la llamada
    assert resultado.estado == "finalizada"
    assert resultado.resultado == "buzon"
    
    # Verificar que se hizo commit a la base de datos
    mock_db.commit.assert_called_once()

def test_finalizar_llamada_no_existe(mock_db, usuario_regular):
    """Test para finalizar una llamada que no existe"""
    # Configurar el mock para devolver None (llamada no encontrada)
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    # Verificar que se lance la excepcion HTTP
    with pytest.raises(HTTPException) as excinfo:
        LlamadasService.finalizar_llamada(
            db=mock_db,
            llamada_id=999,
            resultado="contestada",
            usuario=usuario_regular
        )
    
    # Verificar el codigo de estado y el mensaje
    assert excinfo.value.status_code == 404
    assert "no existe" in excinfo.value.detail

def test_finalizar_llamada_no_pertenece_al_usuario(mock_db, usuario_regular, llamada_activa):
    """Test para finalizar una llamada que pertenece a otro usuario"""
    # Configurar la llamada para que pertenezca a otro usuario
    llamada_activa.usuario_id = uuid.uuid4()  # ID diferente al del usuario regular
    
    # Configurar el mock para devolver la llamada
    mock_db.query.return_value.filter.return_value.first.return_value = llamada_activa
    
    # Verificar que se lance la excepcion HTTP
    with pytest.raises(HTTPException) as excinfo:
        LlamadasService.finalizar_llamada(
            db=mock_db,
            llamada_id=llamada_activa.id,
            resultado="contestada",
            usuario=usuario_regular
        )
    
    # Verificar el codigo de estado y el mensaje
    assert excinfo.value.status_code == 403
    assert "No tienes permiso" in excinfo.value.detail

def test_finalizar_llamada_ya_finalizada(mock_db, usuario_regular, llamada_finalizada):
    """Test para finalizar una llamada que ya esta finalizada"""
    # Configurar el mock para devolver la llamada
    mock_db.query.return_value.filter.return_value.first.return_value = llamada_finalizada
    
    # Verificar que se lance la excepcion HTTP
    with pytest.raises(HTTPException) as excinfo:
        LlamadasService.finalizar_llamada(
            db=mock_db,
            llamada_id=llamada_finalizada.id,
            resultado="contestada",
            usuario=usuario_regular
        )
    
    # Verificar el codigo de estado y el mensaje
    assert excinfo.value.status_code == 400
    assert "no puede ser finalizada" in excinfo.value.detail

def test_finalizar_llamada_resultado_invalido(mock_db, usuario_regular, llamada_activa):
    """Test para finalizar una llamada con un resultado invalido"""
    # Configurar el mock para devolver la llamada
    mock_db.query.return_value.filter.return_value.first.return_value = llamada_activa
    
    # Verificar que se lance la excepcion HTTP
    with pytest.raises(HTTPException) as excinfo:
        LlamadasService.finalizar_llamada(
            db=mock_db,
            llamada_id=llamada_activa.id,
            resultado="resultado_invalido",
            usuario=usuario_regular
        )
    
    # Verificar el codigo de estado y el mensaje
    assert excinfo.value.status_code == 400
    assert "no es valido" in excinfo.value.detail

def test_finalizar_llamada_error_db(mock_db, usuario_regular, llamada_activa):
    """Test para finalizar una llamada con error en la base de datos"""
    # Configurar el mock para devolver la llamada
    mock_db.query.return_value.filter.return_value.first.return_value = llamada_activa
    
    # Configurar el mock para lanzar una excepcion al hacer commit
    mock_db.commit.side_effect = SQLAlchemyError("Error de base de datos")
    
    # Verificar que se lance la excepcion HTTP
    with pytest.raises(HTTPException) as excinfo:
        LlamadasService.finalizar_llamada(
            db=mock_db,
            llamada_id=llamada_activa.id,
            resultado="contestada",
            usuario=usuario_regular
        )
    
    # Verificar el codigo de estado y el mensaje
    assert excinfo.value.status_code == 500
    assert "Error" in excinfo.value.detail
    
    # Verificar que se hizo rollback
    mock_db.rollback.assert_called_once() 