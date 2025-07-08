"""
Tests para funcionalidade de CLI (Caller Line Identification).
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from app.main import app
from app.models.cli import Cli
from app.services.cli_service import CliService
from app.schemas.cli import (
    CliCreate,
    CliUpdate,
    CliRandomRequest
)


# Crear cliente de teste
client = TestClient(app)


class TestCliService:
    """Tests para el servicio de CLI."""
    
    @pytest.fixture
    def mock_db(self):
        """Mock de la sesion de base de datos."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def service(self, mock_db):
        """Instancia del servicio con mock de BD."""
        return CliService(mock_db)
    
    def test_generar_cli_aleatorio_exitoso(self, service, mock_db):
        """Test generar CLI aleatorio exitosamente."""
        # Configurar mock
        mock_cli = Cli(
            id=1,
            numero_normalizado="+5491122334455",
            veces_usado=5,
            activo=True
        )
        mock_db.query.return_value.filter.return_value.all.return_value = [mock_cli]
        
        # Executar
        with patch('random.choice', return_value=mock_cli):
            resultado = service.generar_cli_aleatorio()
        
        # Verificar
        assert resultado.cli_seleccionado == "+5491122334455"
        assert resultado.veces_usado == 6  # Debe incrementar
        mock_db.commit.assert_called_once()
    
    def test_generar_cli_aleatorio_sin_clis_disponibles(self, service, mock_db):
        """Test generar CLI cuando no hay CLIs disponibles."""
        # Configurar mock
        mock_db.query.return_value.filter.return_value.all.return_value = []
        
        # Executar y verificar excepcion
        with pytest.raises(Exception) as exc_info:
            service.generar_cli_aleatorio()
        
        assert "Nenhum CLI disponivel" in str(exc_info.value)
    
    def test_generar_cli_aleatorio_con_exclusion(self, service, mock_db):
        """Test generar CLI excluyendo un CLI especifico."""
        # Configurar mock
        mock_cli1 = Cli(id=1, numero_normalizado="+5491122334455", activo=True)
        mock_cli2 = Cli(id=2, numero_normalizado="+5491133445566", activo=True)
        
        mock_db.query.return_value.filter.return_value.filter.return_value.all.return_value = [mock_cli2]
        
        # Executar
        with patch('random.choice', return_value=mock_cli2):
            resultado = service.generar_cli_aleatorio(excluir_cli="+5491122334455")
        
        # Verificar que excluye el CLI especificado
        assert resultado.cli_seleccionado == "+5491133445566"
    
    def test_generar_cli_aleatorio_poco_usados(self, service, mock_db):
        """Test preferir CLIs menos usados."""
        # Configurar mock
        mock_cli = Cli(id=1, numero_normalizado="+5491122334455", veces_usado=2, activo=True)
        
        # Mock para avg que retorna 5
        mock_db.query.return_value.filter.return_value.scalar.return_value = 5
        mock_db.query.return_value.filter.return_value.filter.return_value.all.return_value = [mock_cli]
        
        # Executar
        with patch('random.choice', return_value=mock_cli):
            resultado = service.generar_cli_aleatorio(solo_poco_usados=True)
        
        # Verificar
        assert resultado.cli_seleccionado == "+5491122334455"
    
    def test_agregar_cli_exitoso(self, service, mock_db):
        """Test agregar CLI exitosamente."""
        # Configurar mock
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        cli_data = CliCreate(
            numero="+5491122334455",
            descripcion="CLI de teste"
        )
        
        # Executar
        resultado = service.agregar_cli(cli_data)
        
        # Verificar
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert isinstance(resultado, Cli)
    
    def test_agregar_cli_ya_existe_activo(self, service, mock_db):
        """Test agregar CLI que ya existe y esta activo."""
        # Configurar mock
        mock_cli_existente = Cli(
            id=1,
            numero_normalizado="+5491122334455",
            activo=True
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_cli_existente
        
        cli_data = CliCreate(
            numero="+5491122334455",
            descripcion="CLI de teste"
        )
        
        # Executar y verificar excepcion
        with pytest.raises(Exception) as exc_info:
            service.agregar_cli(cli_data)
        
        assert "ja existe" in str(exc_info.value)
    
    def test_agregar_cli_reactivar_inactivo(self, service, mock_db):
        """Test reactivar CLI inactivo."""
        # Configurar mock
        mock_cli_existente = Cli(
            id=1,
            numero_normalizado="+5491122334455",
            activo=False,
            descripcion="Descripcion anterior"
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_cli_existente
        
        cli_data = CliCreate(
            numero="+5491122334455",
            descripcion="Nueva descripcion"
        )
        
        # Executar
        resultado = service.agregar_cli(cli_data)
        
        # Verificar
        assert resultado.activo is True
        assert resultado.descripcion == "Nueva descripcion"
        mock_db.commit.assert_called_once()
    
    def test_agregar_clis_bulk(self, service):
        """Test agregado masivo de CLIs."""
        numeros = [
            "+5491122334455",
            "+5491133445566",
            "numero_invalido",
            "+5491122334455"  # Duplicado
        ]
        
        # Mock do metodo agregar_cli
        with patch.object(service, 'agregar_cli') as mock_agregar:
            # Configurar comportamento para diferentes numeros
            def side_effect(cli_data):
                if "invalido" in cli_data.numero:
                    raise Exception("Numero CLI invalido")
                elif cli_data.numero == "+5491122334455":
                    # Primeiro sucesso, segundo duplicado
                    if mock_agregar.call_count <= 1:
                        return Cli()
                    else:
                        raise Exception("ja existe")
                else:
                    return Cli()
            
            mock_agregar.side_effect = side_effect
            
            # Executar
            resultado = service.agregar_clis_bulk(numeros, "Teste bulk")
            
            # Verificar
            assert isinstance(resultado, dict)
            assert 'clis_agregados' in resultado
            assert 'clis_duplicados' in resultado
            assert 'clis_invalidos' in resultado
            assert 'errores' in resultado
    
    def test_listar_clis(self, service, mock_db):
        """Test listar CLIs."""
        # Configurar mock
        mock_clis = [
            Cli(id=1, numero_normalizado="+5491122334455"),
            Cli(id=2, numero_normalizado="+5491133445566")
        ]
        mock_db.query.return_value.filter.return_value.order_by.return_value.offset.return_value.limit.return_value.all.return_value = mock_clis
        
        # Executar
        resultado = service.listar_clis()
        
        # Verificar
        assert len(resultado) == 2
        mock_db.query.assert_called()
    
    def test_atualizar_cli(self, service, mock_db):
        """Test atualizar CLI."""
        # Configurar mock
        mock_cli = Cli(
            id=1,
            numero_normalizado="+5491122334455",
            descripcion="Descripcion anterior"
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_cli
        
        dados_atualizacao = CliUpdate(descripcion="Nueva descripcion")
        
        # Executar
        resultado = service.atualizar_cli(1, dados_atualizacao)
        
        # Verificar
        assert resultado.descripcion == "Nueva descripcion"
        mock_db.commit.assert_called_once()
    
    def test_remover_cli(self, service, mock_db):
        """Test remover CLI."""
        # Configurar mock
        mock_cli = Cli(
            id=1,
            numero_normalizado="+5491122334455",
            activo=True
        )
        mock_db.query.return_value.filter.return_value.first.return_value = mock_cli
        
        # Executar
        resultado = service.remover_cli(1)
        
        # Verificar
        assert resultado is True
        assert mock_cli.activo is False
        mock_db.commit.assert_called_once()


class TestCliEndpoints:
    """Tests para os endpoints de CLI."""
    
    def setup_method(self):
        """Setup para cada test."""
        self.test_client = TestClient(app)
    
    @patch('app.database.obtener_sesion')
    @patch('app.services.cli_service.CliService')
    def test_generar_cli_aleatorio_endpoint(self, mock_service_class, mock_db):
        """Test endpoint de geracao de CLI aleatorio."""
        # Configurar mock
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        from app.schemas.cli import CliRandomResponse
        mock_service.generar_cli_aleatorio.return_value = CliRandomResponse(
            cli_seleccionado="+5491122334455",
            cli_id=1,
            veces_usado=5,
            mensaje="CLI selecionado: +5491122334455"
        )
        
        # Realizar peticion
        response = self.test_client.get("/api/v1/cli/generar-aleatorio")
        
        # Verificar respuesta
        assert response.status_code == 200
        data = response.json()
        assert data["cli_seleccionado"] == "+5491122334455"
        assert data["veces_usado"] == 5
    
    @patch('app.database.obtener_sesion')
    @patch('app.services.cli_service.CliService')
    def test_agregar_cli_endpoint(self, mock_service_class, mock_db):
        """Test endpoint de agregar CLI."""
        # Configurar mock
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_cli = Cli(
            id=1,
            numero="+5491122334455",
            numero_normalizado="+5491122334455",
            descripcion="CLI de teste",
            activo=True,
            veces_usado=0
        )
        mock_service.agregar_cli.return_value = mock_cli
        
        # Realizar peticion
        response = self.test_client.post(
            "/api/v1/cli/agregar",
            json={
                "numero": "+5491122334455",
                "descripcion": "CLI de teste"
            }
        )
        
        # Verificar respuesta
        assert response.status_code == 200
        data = response.json()
        assert data["numero_normalizado"] == "+5491122334455"
        assert data["descripcion"] == "CLI de teste"
    
    @patch('app.database.obtener_sesion')
    @patch('app.services.cli_service.CliService')
    def test_listar_clis_endpoint(self, mock_service_class, mock_db):
        """Test endpoint de listar CLIs."""
        # Configurar mock
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_clis = [
            Cli(
                id=1,
                numero="+5491122334455",
                numero_normalizado="+5491122334455",
                descripcion="CLI 1",
                activo=True,
                veces_usado=5,
                fecha_creacion=datetime.now(),
                fecha_actualizacion=datetime.now()
            )
        ]
        mock_service.listar_clis.return_value = mock_clis
        
        # Realizar peticion
        response = self.test_client.get("/api/v1/cli/")
        
        # Verificar respuesta
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["numero_normalizado"] == "+5491122334455"
    
    @patch('app.database.obtener_sesion')
    @patch('app.services.cli_service.CliService')
    def test_agregar_bulk_cli_endpoint(self, mock_service_class, mock_db):
        """Test endpoint de agregado masivo."""
        # Configurar mock
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_service.agregar_clis_bulk.return_value = {
            'clis_agregados': 2,
            'clis_duplicados': 1,
            'clis_invalidos': 1,
            'errores': ['CLI 3: Numero CLI invalido']
        }
        
        # Realizar peticion
        response = self.test_client.post(
            "/api/v1/cli/agregar-bulk",
            json={
                "numeros": ["+5491122334455", "+5491133445566", "invalido", "+5491122334455"],
                "descripcion": "CLIs de teste"
            }
        )
        
        # Verificar respuesta
        assert response.status_code == 200
        data = response.json()
        assert data["clis_agregados"] == 2
        assert data["clis_duplicados"] == 1
        assert data["clis_invalidos"] == 1


class TestIntegracionCliDiscado:
    """Tests de integracion entre CLI y discado."""
    
    @patch('app.database.obtener_sesion')
    @patch('app.services.discado_service.DiscadoService')
    def test_discado_con_cli_aleatorio(self, mock_service_class, mock_db):
        """Test que el discado usa CLI aleatorio."""
        # Configurar mock
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        # Simular discado con CLI aleatorio
        mock_service.iniciar_llamada.return_value = {
            "estado": "iniciado",
            "mensaje": "Llamada iniciada exitosamente",
            "numero_destino": "+5491112345678",
            "cli_utilizado": "+5491122334455",
            "cli_info": {
                "cli_seleccionado": "+5491122334455",
                "veces_usado": 6,
                "mensaje": "CLI selecionado: +5491122334455"
            },
            "bloqueado_blacklist": False
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
        assert data["estado"] == "iniciado"
        assert "cli_utilizado" in data
        assert "cli_info" in data
    
    @patch('app.database.obtener_sesion')
    @patch('app.services.discado_service.DiscadoService')
    def test_discado_con_cli_personalizado(self, mock_service_class, mock_db):
        """Test que el discado acepta CLI personalizado."""
        # Configurar mock
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        # Simular discado con CLI personalizado
        mock_service.iniciar_llamada.return_value = {
            "estado": "iniciado",
            "mensaje": "Llamada iniciada exitosamente",
            "numero_destino": "+5491112345678",
            "cli_utilizado": "+5491199887766",
            "cli_info": {"mensaje": "CLI personalizado usado: +5491199887766"},
            "bloqueado_blacklist": False
        }
        
        # Realizar peticion
        response = client.post(
            "/api/v1/discado/iniciar-llamada",
            json={
                "numero_destino": "+5491112345678",
                "usuario_id": "user123",
                "cli_personalizado": "+5491199887766"
            }
        )
        
        # Verificar respuesta
        assert response.status_code == 200
        data = response.json()
        assert data["cli_utilizado"] == "+5491199887766"


if __name__ == "__main__":
    pytest.main([__file__]) 