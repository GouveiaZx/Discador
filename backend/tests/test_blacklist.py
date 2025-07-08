"""
Tests para funcionalidade de blacklist/lista negra.
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from app.main import app
from app.models.lista_negra import ListaNegra
from app.services.blacklist_service import BlacklistService
from app.schemas.blacklist import (
    BlacklistCreate,
    BlacklistUpdate,
    BlacklistSearchRequest
)


# Crear cliente de teste
client = TestClient(app)


class TestBlacklistService:
    """Tests para el servicio de blacklist."""
    
    @pytest.fixture
    def mock_db(self):
        """Mock de la sesion de base de datos."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def service(self, mock_db):
        """Instancia del servicio con mock de BD."""
        return BlacklistService(mock_db)
    
    def test_verificar_numero_no_blacklist(self, service, mock_db):
        """Test verificar numero que no esta en blacklist."""
        # Configurar mock
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Ejecutar
        resultado = service.verificar_numero_blacklist("+5491112345678")
        
        # Verificar
        assert resultado.en_blacklist is False
        assert resultado.numero_normalizado == "+5491112345678"
    
    def test_verificar_numero_en_blacklist(self, service, mock_db):
        """Test verificar numero que esta en blacklist."""
        # Configurar mock
        mock_entrada = ListaNegra(
            id=1,
            numero_normalizado="+5491112345678",
            motivo="Numero reportado como spam",
            veces_bloqueado=5,
            activo=True
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_entrada
        
        # Ejecutar
        resultado = service.verificar_numero_blacklist("+54 9 11 1234-5678")
        
        # Verificar
        assert resultado.en_blacklist is True
        assert resultado.motivo == "Numero reportado como spam"
        assert mock_entrada.veces_bloqueado == 6  # Debe incrementar
    
    def test_agregar_numero_blacklist_exitoso(self, service, mock_db):
        """Test agregar numero a blacklist exitosamente."""
        # Configurar mock
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        numero_data = BlacklistCreate(
            numero="+5491112345678",
            motivo="Numero de spam",
            creado_por="admin"
        )
        
        # Ejecutar
        resultado = service.agregar_numero_blacklist(numero_data)
        
        # Verificar
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert isinstance(resultado, ListaNegra)
    
    def test_agregar_numero_ya_existe_activo(self, service, mock_db):
        """Test agregar numero que ya existe y esta activo."""
        # Configurar mock
        mock_entrada_existente = ListaNegra(
            id=1,
            numero_normalizado="+5491112345678",
            activo=True
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_entrada_existente
        
        numero_data = BlacklistCreate(
            numero="+5491112345678",
            motivo="Numero de spam"
        )
        
        # Ejecutar y verificar excepcion
        with pytest.raises(Exception) as exc_info:
            service.agregar_numero_blacklist(numero_data)
        
        assert "ya esta en blacklist" in str(exc_info.value)
    
    def test_agregar_numero_reactivar_inactivo(self, service, mock_db):
        """Test reactivar numero inactivo en blacklist."""
        # Configurar mock
        mock_entrada_existente = ListaNegra(
            id=1,
            numero_normalizado="+5491112345678",
            activo=False,
            motivo="Motivo anterior"
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_entrada_existente
        
        numero_data = BlacklistCreate(
            numero="+5491112345678",
            motivo="Nuevo motivo",
            creado_por="admin"
        )
        
        # Ejecutar
        resultado = service.agregar_numero_blacklist(numero_data)
        
        # Verificar
        assert resultado.activo is True
        assert resultado.motivo == "Nuevo motivo"
        assert resultado.creado_por == "admin"
        mock_db.commit.assert_called_once()
    
    def test_remover_numero_blacklist(self, service, mock_db):
        """Test remover numero da blacklist."""
        # Configurar mock
        mock_entrada = ListaNegra(
            id=1,
            numero_normalizado="+5491112345678",
            activo=True
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_entrada
        
        # Executar
        resultado = service.remover_numero_blacklist(1)
        
        # Verificar
        assert resultado is True
        assert mock_entrada.activo is False
        mock_db.commit.assert_called_once()
    
    def test_buscar_blacklist_por_numero(self, service, mock_db):
        """Test buscar na blacklist por numero."""
        # Configurar mock
        mock_entradas = [
            ListaNegra(id=1, numero_normalizado="+5491112345678"),
            ListaNegra(id=2, numero_normalizado="+5491187654321")
        ]
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_entradas
        
        criterios = BlacklistSearchRequest(numero="11123")
        
        # Executar
        resultado = service.buscar_blacklist(criterios)
        
        # Verificar
        assert len(resultado) == 2
        mock_db.query.assert_called()
    
    def test_agregar_numeros_bulk(self, service):
        """Test agregado masivo de numeros."""
        numeros = [
            "+5491112345678",
            "+5491187654321",
            "numero_invalido",
            "+5491112345678"  # Duplicado
        ]
        
        # Mock do metodo agregar_numero_blacklist
        with patch.object(service, 'agregar_numero_blacklist') as mock_agregar:
            # Configurar comportamento para diferentes numeros
            def side_effect(numero_data):
                if "invalido" in numero_data.numero:
                    raise Exception("Numero invalido")
                elif numero_data.numero == "+5491112345678":
                    # Primeiro sucesso, segundo duplicado
                    if mock_agregar.call_count <= 1:
                        return ListaNegra()
                    else:
                        raise Exception("ya esta en blacklist")
                else:
                    return ListaNegra()
            
            mock_agregar.side_effect = side_effect
            
            # Executar
            resultado = service.agregar_numeros_bulk(numeros, "Teste bulk", "admin")
            
            # Verificar (deve ser ajustado conforme comportamento real)
            assert isinstance(resultado, dict)
            assert 'numeros_agregados' in resultado
            assert 'numeros_duplicados' in resultado
            assert 'numeros_invalidos' in resultado
            assert 'errores' in resultado


class TestBlacklistEndpoints:
    """Tests para os endpoints de blacklist."""
    
    def setup_method(self):
        """Setup para cada test."""
        self.test_client = TestClient(app)
    
    @patch('app.database.obtener_sesion')
    @patch('app.services.blacklist_service.BlacklistService')
    def test_verificar_numero_endpoint(self, mock_service_class, mock_db):
        """Test endpoint de verificacao de numero."""
        # Configurar mock
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        from app.schemas.blacklist import BlacklistVerificationResponse
        mock_service.verificar_numero_blacklist.return_value = BlacklistVerificationResponse(
            numero_original="+5491112345678",
            numero_normalizado="+5491112345678",
            en_blacklist=True,
            motivo="Numero de spam"
        )
        
        # Realizar peticion
        response = self.test_client.post(
            "/api/v1/blacklist/verificar",
            json={"numero": "+5491112345678"}
        )
        
        # Verificar respuesta
        assert response.status_code == 200
        data = response.json()
        assert data["en_blacklist"] is True
        assert data["motivo"] == "Numero de spam"
    
    @patch('app.database.obtener_sesion')
    @patch('app.services.blacklist_service.BlacklistService')
    def test_agregar_numero_endpoint(self, mock_service_class, mock_db):
        """Test endpoint de agregar numero."""
        # Configurar mock
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_entrada = ListaNegra(
            id=1,
            numero="+5491112345678",
            numero_normalizado="+5491112345678",
            motivo="Spam",
            activo=True,
            veces_bloqueado=0
        )
        mock_service.agregar_numero_blacklist.return_value = mock_entrada
        
        # Realizar peticion
        response = self.test_client.post(
            "/api/v1/blacklist/agregar",
            json={
                "numero": "+5491112345678",
                "motivo": "Spam",
                "creado_por": "admin"
            }
        )
        
        # Verificar respuesta
        assert response.status_code == 200
        data = response.json()
        assert data["numero_normalizado"] == "+5491112345678"
        assert data["motivo"] == "Spam"
    
    @patch('app.database.obtener_sesion')
    @patch('app.services.blacklist_service.BlacklistService')
    def test_listar_blacklist_endpoint(self, mock_service_class, mock_db):
        """Test endpoint de listar blacklist."""
        # Configurar mock
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_entradas = [
            ListaNegra(
                id=1,
                numero="+5491112345678",
                numero_normalizado="+5491112345678",
                motivo="Spam",
                activo=True,
                veces_bloqueado=3,
                fecha_creacion=datetime.now(),
                fecha_actualizacion=datetime.now()
            )
        ]
        mock_service.listar_blacklist.return_value = mock_entradas
        
        # Realizar peticion
        response = self.test_client.get("/api/v1/blacklist/")
        
        # Verificar respuesta
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["numero_normalizado"] == "+5491112345678"
    
    @patch('app.database.obtener_sesion')
    @patch('app.services.blacklist_service.BlacklistService')
    def test_agregar_bulk_endpoint(self, mock_service_class, mock_db):
        """Test endpoint de agregado masivo."""
        # Configurar mock
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_service.agregar_numeros_bulk.return_value = {
            'numeros_agregados': 2,
            'numeros_duplicados': 1,
            'numeros_invalidos': 1,
            'errores': ['Numero 3: Numero invalido']
        }
        
        # Realizar peticion
        response = self.test_client.post(
            "/api/v1/blacklist/agregar-bulk",
            json={
                "numeros": ["+5491112345678", "+5491187654321", "invalido", "+5491112345678"],
                "motivo": "Spam masivo",
                "creado_por": "admin"
            }
        )
        
        # Verificar respuesta
        assert response.status_code == 200
        data = response.json()
        assert data["numeros_agregados"] == 2
        assert data["numeros_duplicados"] == 1
        assert data["numeros_invalidos"] == 1
    
    @patch('app.database.obtener_sesion')
    @patch('app.services.blacklist_service.BlacklistService')
    def test_remover_numero_endpoint(self, mock_service_class, mock_db):
        """Test endpoint de remover numero."""
        # Configurar mock
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.remover_numero_blacklist.return_value = True
        
        # Realizar peticao
        response = self.test_client.delete("/api/v1/blacklist/1")
        
        # Verificar resposta
        assert response.status_code == 200
        data = response.json()
        assert "removido" in data["mensaje"]
        assert data["numero_id"] == 1


class TestIntegracionBlacklistDiscado:
    """Tests de integracao entre blacklist e discado."""
    
    @patch('app.database.obtener_sesion')
    @patch('app.services.discado_service.DiscadoService')
    def test_discado_numero_bloqueado(self, mock_service_class, mock_db):
        """Test que el discado bloquea numeros en blacklist."""
        # Configurar mock
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        # Simular numero bloqueado
        mock_service.iniciar_llamada.return_value = {
            "estado": "bloqueado",
            "mensaje": "Numero bloqueado por blacklist: Spam",
            "numero_destino": "+5491112345678",
            "bloqueado_blacklist": True,
            "motivo_bloqueo": "Spam"
        }
        
        # Realizar peticion
        response = client.post(
            "/api/v1/discado/iniciar-llamada",
            json={
                "numero_destino": "+5491112345678",
                "usuario_id": "user123"
            }
        )
        
        # Verificar respuesta
        assert response.status_code == 200
        data = response.json()
        assert data["estado"] == "bloqueado"
        assert data["bloqueado_blacklist"] is True
        assert "Spam" in data["motivo_bloqueo"]


if __name__ == "__main__":
    pytest.main([__file__]) 