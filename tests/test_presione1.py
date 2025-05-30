"""
Testes para o sistema de discado preditivo con modo "Presione 1".
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.main import app
from app.models.campana_presione1 import CampanaPresione1, LlamadaPresione1
from app.models.lista_llamadas import ListaLlamadas, NumeroLlamada
from app.services.presione1_service import PresionE1Service
from app.services.asterisk import AsteriskAMIService
from app.schemas.presione1 import (
    CampanaPresione1Create,
    CampanaPresione1Update,
    IniciarCampanaRequest,
    PausarCampanaRequest
)


# Cliente de teste
client = TestClient(app)


class TestPresione1Service:
    """Testes para o serviço Presione1."""
    
    @pytest.fixture
    def mock_db(self):
        """Mock da sessão de base de dados."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def service(self, mock_db):
        """Instância do serviço com mock de BD."""
        return PresionE1Service(mock_db)
    
    @pytest.fixture
    def campana_data(self):
        """Dados de teste para criar campanha."""
        return CampanaPresione1Create(
            nombre="Campanha Teste",
            descripcion="Teste de discado preditivo",
            lista_llamadas_id=1,
            mensaje_audio_url="/sounds/presione1_test.wav",
            timeout_presione1=10,
            extension_transferencia="100",
            llamadas_simultaneas=2,
            tiempo_entre_llamadas=5,
            notas="Campanha para testes"
        )
    
    def test_crear_campana_exitoso(self, service, mock_db, campana_data):
        """Teste criar campanha com sucesso."""
        # Configurar mock da lista existente
        mock_lista = Mock()
        mock_lista.id = 1
        mock_lista.activa = True
        mock_db.query.return_value.filter.return_value.first.return_value = mock_lista
        
        # Mock de campanha existente (não existe)
        mock_db.query.return_value.filter.return_value.first.side_effect = [mock_lista, None]
        
        # Executar
        resultado = service.crear_campana(campana_data)
        
        # Verificar
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert isinstance(resultado, CampanaPresione1)
    
    def test_crear_campana_lista_inexistente(self, service, mock_db, campana_data):
        """Teste criar campanha com lista inexistente."""
        # Mock lista não encontrada
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Executar e verificar exceção
        with pytest.raises(Exception) as exc_info:
            service.crear_campana(campana_data)
        
        assert "não encontrada" in str(exc_info.value)
    
    def test_crear_campana_lista_ja_em_uso(self, service, mock_db, campana_data):
        """Teste criar campanha para lista já em uso."""
        # Mock lista existente
        mock_lista = Mock()
        mock_lista.id = 1
        mock_lista.activa = True
        
        # Mock campanha existente para a mesma lista
        mock_campana_existente = Mock()
        mock_campana_existente.activa = True
        
        mock_db.query.return_value.filter.return_value.first.side_effect = [
            mock_lista, mock_campana_existente
        ]
        
        # Executar e verificar exceção
        with pytest.raises(Exception) as exc_info:
            service.crear_campana(campana_data)
        
        assert "campanha ativa" in str(exc_info.value)
    
    def test_obter_proximo_numero_disponivel(self, service, mock_db):
        """Teste obter próximo número disponível."""
        # Mock campanha
        mock_campana = Mock()
        mock_campana.lista_llamadas_id = 1
        mock_db.query.return_value.filter.return_value.first.return_value = mock_campana
        
        # Mock número disponível
        mock_numero = Mock()
        mock_numero.id = 123
        mock_numero.numero = "+5491112345678"
        mock_numero.numero_normalizado = "+5491112345678"
        
        # Configurar queries complexas
        mock_db.query.return_value.filter.return_value.filter.return_value.filter.return_value.first.return_value = mock_numero
        
        # Executar
        resultado = service.obter_proximo_numero(1)
        
        # Verificar
        assert resultado is not None
        assert resultado["numero_id"] == 123
        assert resultado["numero_normalizado"] == "+5491112345678"
    
    def test_obter_proximo_numero_sem_disponivel(self, service, mock_db):
        """Teste obter próximo número quando não há disponível."""
        # Mock campanha
        mock_campana = Mock()
        mock_campana.lista_llamadas_id = 1
        mock_db.query.return_value.filter.return_value.first.return_value = mock_campana
        
        # Mock sem números disponíveis
        mock_db.query.return_value.filter.return_value.filter.return_value.filter.return_value.first.return_value = None
        
        # Executar
        resultado = service.obter_proximo_numero(1)
        
        # Verificar
        assert resultado is None
    
    @pytest.mark.asyncio
    async def test_iniciar_campana_exitoso(self, service, mock_db):
        """Teste iniciar campanha com sucesso."""
        # Mock campanha inativa
        mock_campana = Mock()
        mock_campana.activa = False
        mock_campana.id = 1
        mock_campana.nombre = "Teste"
        mock_campana.llamadas_simultaneas = 2
        mock_campana.tiempo_entre_llamadas = 5
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_campana
        
        # Mock próximo número disponível
        with patch.object(service, 'obter_proximo_numero', return_value={"numero": "+5491112345678"}):
            # Executar
            resultado = await service.iniciar_campana(1, "user123")
            
            # Verificar
            assert resultado["campana_id"] == 1
            assert "iniciada com sucesso" in resultado["mensaje"]
            assert mock_campana.activa is True
    
    @pytest.mark.asyncio
    async def test_iniciar_campana_ja_ativa(self, service, mock_db):
        """Teste iniciar campanha já ativa."""
        # Mock campanha já ativa
        mock_campana = Mock()
        mock_campana.activa = True
        mock_db.query.return_value.filter.return_value.first.return_value = mock_campana
        
        # Executar e verificar exceção
        with pytest.raises(Exception) as exc_info:
            await service.iniciar_campana(1, "user123")
        
        assert "já está ativa" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_pausar_campana(self, service, mock_db):
        """Teste pausar/retomar campanha."""
        # Mock campanha ativa
        mock_campana = Mock()
        mock_campana.activa = True
        mock_campana.pausada = False
        mock_db.query.return_value.filter.return_value.first.return_value = mock_campana
        
        # Executar pausa
        resultado = await service.pausar_campana(1, True, "Teste de pausa")
        
        # Verificar
        assert resultado["pausada"] is True
        assert "pausada com sucesso" in resultado["mensaje"]
        assert mock_campana.pausada is True
    
    @pytest.mark.asyncio
    async def test_parar_campana(self, service, mock_db):
        """Teste parar campanha."""
        # Mock campanha ativa
        mock_campana = Mock()
        mock_campana.activa = True
        mock_db.query.return_value.filter.return_value.first.return_value = mock_campana
        
        # Executar
        resultado = await service.parar_campana(1)
        
        # Verificar
        assert "parada com sucesso" in resultado["mensaje"]
        assert mock_campana.activa is False
    
    def test_obter_estadisticas_campana(self, service, mock_db):
        """Teste obter estatísticas de campanha."""
        # Mock campanha
        mock_campana = Mock()
        mock_campana.id = 1
        mock_campana.nombre = "Teste"
        mock_campana.lista_llamadas_id = 1
        mock_campana.activa = True
        mock_campana.pausada = False
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_campana
        
        # Mock contadores
        mock_db.query.return_value.filter.return_value.count.side_effect = [
            100,  # total_numeros
            50,   # llamadas_realizadas
            35,   # llamadas_contestadas
            20,   # llamadas_presiono_1
            10,   # llamadas_no_presiono
            18,   # llamadas_transferidas
            2     # llamadas_error
        ]
        
        # Mock médias
        mock_db.query.return_value.filter.return_value.scalar.side_effect = [5.2, 45.5]
        
        # Executar
        estadisticas = service.obter_estadisticas_campana(1)
        
        # Verificar
        assert estadisticas.campana_id == 1
        assert estadisticas.nombre_campana == "Teste"
        assert estadisticas.total_numeros == 100
        assert estadisticas.llamadas_realizadas == 50
        assert estadisticas.tasa_contestacion == 70.0  # 35/50*100


class TestPresione1Endpoints:
    """Testes para os endpoints da API."""
    
    def setup_method(self):
        """Setup para cada teste."""
        self.client = TestClient(app)
    
    @patch('app.database.obtener_sesion')
    @patch('app.services.presione1_service.PresionE1Service')
    def test_crear_campana_endpoint(self, mock_service_class, mock_db):
        """Teste endpoint criar campanha."""
        # Configurar mock
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_campana = CampanaPresione1(
            id=1,
            nombre="Teste",
            descripcion="Teste endpoint",
            lista_llamadas_id=1,
            mensaje_audio_url="/sounds/test.wav",
            timeout_presione1=10,
            extension_transferencia="100",
            activa=False,
            pausada=False,
            fecha_creacion=datetime.now(),
            fecha_actualizacion=datetime.now(),
            llamadas_simultaneas=1,
            tiempo_entre_llamadas=5
        )
        
        mock_service.crear_campana.return_value = mock_campana
        
        # Realizar requisição
        response = self.client.post(
            "/api/v1/presione1/campanhas",
            json={
                "nombre": "Teste",
                "descripcion": "Teste endpoint",
                "lista_llamadas_id": 1,
                "mensaje_audio_url": "/sounds/test.wav",
                "timeout_presione1": 10,
                "extension_transferencia": "100"
            }
        )
        
        # Verificar resposta
        assert response.status_code == 200
        data = response.json()
        assert data["nombre"] == "Teste"
        assert data["timeout_presione1"] == 10
    
    @patch('app.database.obtener_sesion')
    @patch('app.services.presione1_service.PresionE1Service')
    def test_listar_campanhas_endpoint(self, mock_service_class, mock_db):
        """Teste endpoint listar campanhas."""
        # Configurar mock
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_campanhas = [
            CampanaPresione1(
                id=1,
                nombre="Campanha 1",
                descripcion="Teste",
                lista_llamadas_id=1,
                mensaje_audio_url="/sounds/test1.wav",
                timeout_presione1=10,
                activa=True,
                pausada=False,
                fecha_creacion=datetime.now(),
                fecha_actualizacion=datetime.now(),
                llamadas_simultaneas=1,
                tiempo_entre_llamadas=5
            )
        ]
        
        mock_service.listar_campanas.return_value = mock_campanhas
        
        # Realizar requisição
        response = self.client.get("/api/v1/presione1/campanhas")
        
        # Verificar resposta
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["nombre"] == "Campanha 1"
    
    @patch('app.database.obtener_sesion')
    @patch('app.services.presione1_service.PresionE1Service')
    def test_iniciar_campana_endpoint(self, mock_service_class, mock_db):
        """Teste endpoint iniciar campanha."""
        # Configurar mock
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_service.iniciar_campana.return_value = {
            "mensaje": "Campanha iniciada com sucesso",
            "campana_id": 1
        }
        
        # Realizar requisição
        response = self.client.post(
            "/api/v1/presione1/campanhas/1/iniciar",
            json={
                "campana_id": 1,
                "usuario_id": "test_user"
            }
        )
        
        # Verificar resposta
        assert response.status_code == 200
        data = response.json()
        assert "iniciada com sucesso" in data["mensaje"]
    
    @patch('app.database.obtener_sesion')
    @patch('app.services.presione1_service.PresionE1Service')
    def test_obter_estadisticas_endpoint(self, mock_service_class, mock_db):
        """Teste endpoint estadísticas."""
        # Configurar mock
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        from app.schemas.presione1 import EstadisticasCampanaResponse
        mock_service.obter_estadisticas_campana.return_value = EstadisticasCampanaResponse(
            campana_id=1,
            nombre_campana="Teste",
            total_numeros=100,
            llamadas_realizadas=50,
            llamadas_pendientes=50,
            llamadas_contestadas=35,
            llamadas_presiono_1=20,
            llamadas_no_presiono=15,
            llamadas_transferidas=18,
            llamadas_error=2,
            tasa_contestacion=70.0,
            tasa_presiono_1=57.14,
            tasa_transferencia=90.0,
            tiempo_medio_respuesta=5.2,
            duracion_media_llamada=45.5,
            activa=True,
            pausada=False,
            llamadas_activas=3
        )
        
        # Realizar requisição
        response = self.client.get("/api/v1/presione1/campanhas/1/estadisticas")
        
        # Verificar resposta
        assert response.status_code == 200
        data = response.json()
        assert data["campana_id"] == 1
        assert data["tasa_contestacion"] == 70.0
        assert data["tasa_presiono_1"] == 57.14


class TestAsteriskIntegration:
    """Testes para integração com Asterisk."""
    
    @pytest.fixture
    def asterisk_service(self):
        """Instância do serviço Asterisk."""
        return AsteriskAMIService()
    
    @pytest.mark.asyncio
    async def test_originar_llamada_presione1(self, asterisk_service):
        """Teste originar chamada Presione 1."""
        # Executar
        resultado = await asterisk_service.originar_llamada_presione1(
            numero_destino="+5491112345678",
            cli="+5491122334455",
            audio_url="/sounds/test.wav",
            timeout_dtmf=10,
            llamada_id=123
        )
        
        # Verificar
        assert resultado["Response"] == "Success"
        assert resultado["LlamadaID"] == 123
        assert resultado["Mode"] == "PRESIONE1"
        assert "UniqueID" in resultado
        assert "Channel" in resultado
    
    @pytest.mark.asyncio
    async def test_simular_flujo_presione1_presiono_1(self, asterisk_service):
        """Teste simular fluxo completo com usuário pressionando 1."""
        eventos_recebidos = []
        
        def callback_eventos(evento):
            eventos_recebidos.append(evento)
        
        # Registrar callback
        asterisk_service.registrar_callback_evento("test", callback_eventos)
        
        # Simular fluxo com patch para garantir que pressiona 1
        with patch('random.random', side_effect=[0.5, 0.5]):  # Atende e pressiona 1
            with patch('random.uniform', return_value=3.0):  # Responde em 3 segundos
                with patch('random.choice', return_value="1"):  # Sempre pressiona 1
                    
                    # Executar simulação
                    await asterisk_service._simular_flujo_presione1(
                        unique_id="TEST-123",
                        channel="SIP/test",
                        llamada_id=1,
                        timeout_dtmf=10
                    )
                    
                    # Aguardar eventos
                    await asyncio.sleep(0.1)
        
        # Verificar eventos recebidos
        tipos_eventos = [evento['Event'] for evento in eventos_recebidos]
        assert 'CallAnswered' in tipos_eventos
        assert 'AudioStarted' in tipos_eventos
        assert 'WaitingDTMF' in tipos_eventos
        assert 'DTMFReceived' in tipos_eventos
        assert 'TransferStarted' in tipos_eventos
    
    @pytest.mark.asyncio
    async def test_simular_flujo_presione1_timeout(self, asterisk_service):
        """Teste simular fluxo com timeout DTMF."""
        eventos_recebidos = []
        
        def callback_eventos(evento):
            eventos_recebidos.append(evento)
        
        # Registrar callback
        asterisk_service.registrar_callback_evento("test_timeout", callback_eventos)
        
        # Simular fluxo com timeout
        with patch('random.random', return_value=0.5):  # Atende
            with patch('random.uniform', return_value=15.0):  # Timeout (>10s)
                
                # Executar simulação
                await asterisk_service._simular_flujo_presione1(
                    unique_id="TEST-TIMEOUT",
                    channel="SIP/timeout",
                    llamada_id=2,
                    timeout_dtmf=10
                )
                
                # Aguardar eventos
                await asyncio.sleep(0.1)
        
        # Verificar eventos
        tipos_eventos = [evento['Event'] for evento in eventos_recebidos]
        assert 'CallAnswered' in tipos_eventos
        assert 'DTMFTimeout' in tipos_eventos
        assert 'CallHangup' in tipos_eventos
    
    @pytest.mark.asyncio
    async def test_transferir_llamada(self, asterisk_service):
        """Teste transferir chamada."""
        resultado = await asterisk_service.transferir_llamada(
            channel="SIP/123456",
            destino="100"
        )
        
        assert resultado["Response"] == "Success"
        assert resultado["Destination"] == "100"
        assert "Transfer to 100 initiated" in resultado["Message"]
    
    @pytest.mark.asyncio
    async def test_transferir_a_cola(self, asterisk_service):
        """Teste transferir para fila."""
        resultado = await asterisk_service.transferir_a_cola(
            channel="SIP/123456",
            cola="vendas"
        )
        
        assert resultado["Response"] == "Success"
        assert resultado["Queue"] == "vendas"
        assert "Transfer to queue vendas initiated" in resultado["Message"]


class TestFluxoCompleto:
    """Testes de integração do fluxo completo."""
    
    @pytest.mark.asyncio
    async def test_fluxo_campana_completo(self):
        """Teste fluxo completo de uma campanha."""
        # Este teste simula um fluxo completo desde criação até finalização
        
        # 1. Criar campanha
        campana_data = {
            "nombre": "Teste Fluxo Completo",
            "descripcion": "Teste de fluxo end-to-end",
            "lista_llamadas_id": 1,
            "mensaje_audio_url": "/sounds/test_completo.wav",
            "timeout_presione1": 10,
            "extension_transferencia": "100",
            "llamadas_simultaneas": 1,
            "tiempo_entre_llamadas": 2
        }
        
        with patch('app.database.obtener_sesion'):
            with patch('app.services.presione1_service.PresionE1Service') as mock_service_class:
                mock_service = Mock()
                mock_service_class.return_value = mock_service
                
                # Mock criação de campanha
                mock_campana = Mock()
                mock_campana.id = 1
                mock_campana.nombre = campana_data["nombre"]
                mock_service.crear_campana.return_value = mock_campana
                
                # 2. Testar criação via API
                response = client.post("/api/v1/presione1/campanhas", json=campana_data)
                assert response.status_code == 200
                
                # 3. Mock iniciar campanha
                mock_service.iniciar_campana.return_value = {
                    "mensaje": "Campanha iniciada",
                    "campana_id": 1
                }
                
                # 4. Testar início via API
                response = client.post(
                    "/api/v1/presione1/campanhas/1/iniciar",
                    json={"campana_id": 1, "usuario_id": "test"}
                )
                assert response.status_code == 200
                
                # 5. Mock pausar
                mock_service.pausar_campana.return_value = {
                    "mensaje": "Campanha pausada",
                    "pausada": True
                }
                
                # 6. Testar pausa via API
                response = client.post(
                    "/api/v1/presione1/campanhas/1/pausar",
                    json={"campana_id": 1, "pausar": True}
                )
                assert response.status_code == 200
                
                # 7. Mock parar
                mock_service.parar_campana.return_value = {
                    "mensaje": "Campanha parada"
                }
                
                # 8. Testar parada via API
                response = client.post("/api/v1/presione1/campanhas/1/parar")
                assert response.status_code == 200
    
    def test_validacao_audio_url(self):
        """Teste validação de URL de áudio."""
        from app.schemas.presione1 import CampanaPresione1Create
        
        # URL válida
        campana_valida = CampanaPresione1Create(
            nombre="Teste",
            lista_llamadas_id=1,
            mensaje_audio_url="/sounds/test.wav",
            extension_transferencia="100"
        )
        assert campana_valida.mensaje_audio_url == "/sounds/test.wav"
        
        # URL inválida (formato não suportado)
        with pytest.raises(ValueError) as exc_info:
            CampanaPresione1Create(
                nombre="Teste",
                lista_llamadas_id=1,
                mensaje_audio_url="/sounds/test.txt",
                extension_transferencia="100"
            )
        assert "Formato de áudio inválido" in str(exc_info.value)
    
    def test_validacao_timeout(self):
        """Teste validação de timeout."""
        from app.schemas.presione1 import CampanaPresione1Create
        
        # Timeout muito baixo
        with pytest.raises(ValueError) as exc_info:
            CampanaPresione1Create(
                nombre="Teste",
                lista_llamadas_id=1,
                mensaje_audio_url="/sounds/test.wav",
                timeout_presione1=2,  # < 3
                extension_transferencia="100"
            )
        assert "pelo menos 3 segundos" in str(exc_info.value)
        
        # Timeout muito alto
        with pytest.raises(ValueError) as exc_info:
            CampanaPresione1Create(
                nombre="Teste",
                lista_llamadas_id=1,
                mensaje_audio_url="/sounds/test.wav",
                timeout_presione1=70,  # > 60
                extension_transferencia="100"
            )
        assert "não pode exceder 60 segundos" in str(exc_info.value)


class TestPresione1Service:
    """Testes para o serviço Presione 1."""
    
    @pytest.fixture
    def db_session(self):
        """Mock da sessão de banco de dados."""
        return MagicMock(spec=Session)
    
    @pytest.fixture
    def presione1_service(self, db_session):
        """Instância do serviço Presione 1."""
        return PresionE1Service(db_session)
    
    @pytest.fixture
    def lista_llamadas_mock(self):
        """Mock de lista de chamadas."""
        lista = MagicMock(spec=ListaLlamadas)
        lista.id = 1
        lista.nombre = "Lista Test"
        lista.activa = True
        return lista
    
    @pytest.fixture
    def campana_data_voicemail(self):
        """Dados para criar campanha com voicemail."""
        return CampanaPresione1Create(
            nombre="Campanha Test Voicemail",
            descripcion="Teste com detecção de voicemail",
            lista_llamadas_id=1,
            mensaje_audio_url="/sounds/test.wav",
            timeout_presione1=10,
            detectar_voicemail=True,
            mensaje_voicemail_url="/sounds/voicemail.wav",
            duracion_minima_voicemail=3,
            duracion_maxima_voicemail=30,
            extension_transferencia="100",
            llamadas_simultaneas=2,
            tiempo_entre_llamadas=5
        )
    
    def test_crear_campana_con_voicemail(self, presione1_service, db_session, lista_llamadas_mock, campana_data_voicemail):
        """Teste criar campanha com configuração de voicemail."""
        # Configurar mocks
        db_session.query.return_value.filter.return_value.first.return_value = lista_llamadas_mock
        db_session.query.return_value.filter.return_value.first.side_effect = [lista_llamadas_mock, None]
        
        nova_campana = MagicMock(spec=CampanaPresione1)
        nova_campana.id = 1
        nova_campana.nombre = campana_data_voicemail.nombre
        nova_campana.detectar_voicemail = True
        nova_campana.mensaje_voicemail_url = "/sounds/voicemail.wav"
        
        db_session.add.return_value = None
        db_session.commit.return_value = None
        db_session.refresh.return_value = None
        
        # Executar
        resultado = presione1_service.crear_campana(campana_data_voicemail)
        
        # Verificar
        db_session.add.assert_called_once()
        db_session.commit.assert_called_once()
        assert resultado is not None
    
    def test_validar_configuracao_voicemail(self, campana_data_voicemail):
        """Teste validação de configuração de voicemail."""
        # Teste com detecção ativa mas sem URL de áudio
        campana_data_voicemail.detectar_voicemail = True
        campana_data_voicemail.mensaje_voicemail_url = None
        
        # Deve falhar na validação do schema
        with pytest.raises(ValueError):
            CampanaPresione1Create(**campana_data_voicemail.dict())
    
    @pytest.mark.asyncio
    async def test_processar_evento_voicemail_detectado(self, presione1_service, db_session):
        """Teste processar evento de voicemail detectado."""
        # Configurar mock da chamada
        llamada_mock = MagicMock(spec=LlamadaPresione1)
        llamada_mock.id = 1
        llamada_mock.estado = "marcando"
        llamada_mock.voicemail_detectado = None
        
        db_session.query.return_value.filter.return_value.first.return_value = llamada_mock
        
        # Evento de voicemail detectado
        evento = {
            "Event": "VoicemailDetected",
            "UniqueID": "TEST-123",
            "Channel": "SIP/test",
            "LlamadaID": 1,
            "DetectionMethod": "BeepDetection",
            "Timestamp": datetime.now().isoformat()
        }
        
        # Executar
        await presione1_service.processar_evento_asterisk(evento)
        
        # Verificar
        assert llamada_mock.estado == "voicemail_detectado"
        assert llamada_mock.voicemail_detectado == True
        assert llamada_mock.fecha_voicemail_detectado is not None
        assert llamada_mock.fecha_contestada is not None  # Considerar como atendida
        db_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_processar_evento_voicemail_audio_iniciado(self, presione1_service, db_session):
        """Teste processar evento de início de áudio no voicemail."""
        # Configurar mock da chamada
        llamada_mock = MagicMock(spec=LlamadaPresione1)
        llamada_mock.id = 1
        llamada_mock.estado = "voicemail_detectado"
        
        db_session.query.return_value.filter.return_value.first.return_value = llamada_mock
        
        # Evento de início de áudio no voicemail
        evento = {
            "Event": "VoicemailAudioStarted",
            "UniqueID": "TEST-123",
            "Channel": "SIP/test",
            "LlamadaID": 1,
            "AudioURL": "/sounds/voicemail.wav",
            "MaxDuration": 30,
            "Timestamp": datetime.now().isoformat()
        }
        
        # Executar
        await presione1_service.processar_evento_asterisk(evento)
        
        # Verificar
        assert llamada_mock.estado == "voicemail_audio_reproducido"
        assert llamada_mock.fecha_voicemail_audio_inicio is not None
        db_session.commit.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_processar_evento_voicemail_audio_finalizado(self, presione1_service, db_session):
        """Teste processar evento de fim de áudio no voicemail."""
        # Configurar mock da chamada
        llamada_mock = MagicMock(spec=LlamadaPresione1)
        llamada_mock.id = 1
        llamada_mock.estado = "voicemail_audio_reproducido"
        
        db_session.query.return_value.filter.return_value.first.return_value = llamada_mock
        
        # Mock do método _finalizar_llamada
        presione1_service._finalizar_llamada = AsyncMock()
        
        # Evento de fim de áudio no voicemail
        evento = {
            "Event": "VoicemailAudioFinished",
            "UniqueID": "TEST-123",
            "Channel": "SIP/test",
            "LlamadaID": 1,
            "AudioDuration": 15.5,
            "Reason": "Completed",
            "Timestamp": datetime.now().isoformat()
        }
        
        # Executar
        await presione1_service.processar_evento_asterisk(evento)
        
        # Verificar
        assert llamada_mock.fecha_voicemail_audio_fin is not None
        assert llamada_mock.duracion_mensaje_voicemail == 15
        assert llamada_mock.estado == "voicemail_finalizado"
        presione1_service._finalizar_llamada.assert_called_once_with(1, "voicemail_mensaje_dejado")
    
    def test_obter_estadisticas_com_voicemail(self, presione1_service, db_session):
        """Teste obter estatísticas incluindo métricas de voicemail."""
        # Configurar mocks
        campana_mock = MagicMock(spec=CampanaPresione1)
        campana_mock.id = 1
        campana_mock.nombre = "Test Campaign"
        campana_mock.lista_llamadas_id = 1
        
        # Mock das queries de estatísticas
        db_session.query.return_value.filter.return_value.first.return_value = campana_mock
        db_session.query.return_value.filter.return_value.count.side_effect = [
            100,  # total_numeros
            50,   # llamadas_realizadas
            35,   # llamadas_contestadas
            20,   # llamadas_presiono_1
            15,   # llamadas_no_presiono
            18,   # llamadas_transferidas
            2,    # llamadas_error
            8,    # llamadas_voicemail
            6     # llamadas_voicemail_mensaje_dejado
        ]
        
        # Mock das queries de média
        db_session.query.return_value.filter.return_value.scalar.side_effect = [
            12.5,  # duracion_media_mensaje_voicemail
            4.2,   # tiempo_medio_respuesta
            45.8   # duracion_media_llamada
        ]
        
        presione1_service.campanhas_ativas = {}
        
        # Executar
        stats = presione1_service.obter_estadisticas_campana(1)
        
        # Verificar estatísticas de voicemail
        assert stats.llamadas_voicemail == 8
        assert stats.llamadas_voicemail_mensaje_dejado == 6
        assert stats.tasa_voicemail == 16.0  # 8/50 * 100
        assert stats.tasa_mensaje_voicemail == 75.0  # 6/8 * 100
        assert stats.duracion_media_mensaje_voicemail == 12.5


class TestAsteriskVoicemailIntegration:
    """Testes para integração com Asterisk incluindo voicemail."""
    
    @pytest.fixture
    def asterisk_service(self):
        """Instância do serviço Asterisk."""
        return AsteriskAMIService()
    
    @pytest.mark.asyncio
    async def test_originar_llamada_con_voicemail(self, asterisk_service):
        """Teste originar chamada com detecção de voicemail."""
        # Executar
        resultado = await asterisk_service.originar_llamada_presione1(
            numero_destino="+5491112345678",
            cli="+5491122334455",
            audio_url="/sounds/test.wav",
            timeout_dtmf=10,
            llamada_id=123,
            detectar_voicemail=True,
            mensaje_voicemail_url="/sounds/voicemail.wav",
            duracion_maxima_voicemail=30
        )
        
        # Verificar
        assert resultado["Response"] == "Success"
        assert resultado["LlamadaID"] == 123
        assert resultado["Mode"] == "PRESIONE1_VOICEMAIL"
        assert resultado["VoicemailDetection"] == True
        assert "UniqueID" in resultado
        assert "Channel" in resultado
    
    @pytest.mark.asyncio
    async def test_simular_flujo_voicemail_detectado(self, asterisk_service):
        """Teste simular fluxo com voicemail detectado."""
        eventos_recebidos = []
        
        def callback_eventos(evento):
            eventos_recebidos.append(evento)
        
        # Registrar callback
        asterisk_service.registrar_callback_evento("test_voicemail", callback_eventos)
        
        # Simular fluxo com voicemail (forçar detecção)
        with patch('random.random', return_value=0.1):  # 10% - força voicemail
            await asterisk_service._simular_flujo_presione1_con_voicemail(
                unique_id="TEST-VM-123",
                channel="SIP/voicemail-test",
                llamada_id=1,
                timeout_dtmf=10,
                detectar_voicemail=True,
                mensaje_voicemail_url="/sounds/voicemail.wav",
                duracion_maxima_voicemail=30
            )
            
            # Aguardar eventos
            await asyncio.sleep(0.1)
        
        # Verificar eventos de voicemail
        tipos_eventos = [evento['Event'] for evento in eventos_recebidos]
        assert 'VoicemailDetected' in tipos_eventos
        assert 'VoicemailAudioStarted' in tipos_eventos
        assert 'VoicemailAudioFinished' in tipos_eventos
        assert 'CallHangup' in tipos_eventos
        
        # Verificar detalhes do evento de detecção
        evento_detectado = next(e for e in eventos_recebidos if e['Event'] == 'VoicemailDetected')
        assert evento_detectado['DetectionMethod'] in ['BeepDetection', 'SilenceDetection', 'TonePattern']
        
        # Verificar evento de áudio iniciado
        evento_audio = next(e for e in eventos_recebidos if e['Event'] == 'VoicemailAudioStarted')
        assert evento_audio['AudioURL'] == "/sounds/voicemail.wav"
        assert evento_audio['MaxDuration'] == 30
        
        # Verificar evento de áudio finalizado
        evento_fim = next(e for e in eventos_recebidos if e['Event'] == 'VoicemailAudioFinished')
        assert 'AudioDuration' in evento_fim
        assert evento_fim['Reason'] == 'Completed'
    
    @pytest.mark.asyncio
    async def test_simular_flujo_voicemail_sem_audio(self, asterisk_service):
        """Teste simular fluxo de voicemail sem áudio configurado."""
        eventos_recebidos = []
        
        def callback_eventos(evento):
            eventos_recebidos.append(evento)
        
        # Registrar callback
        asterisk_service.registrar_callback_evento("test_vm_no_audio", callback_eventos)
        
        # Simular voicemail sem áudio
        await asterisk_service._simular_voicemail_flow(
            unique_id="TEST-VM-NO-AUDIO",
            channel="SIP/no-audio",
            llamada_id=2,
            mensaje_voicemail_url=None,  # Sem áudio
            duracion_maxima_voicemail=30
        )
        
        # Aguardar eventos
        await asyncio.sleep(0.1)
        
        # Verificar que detectou voicemail mas não reproduziu áudio
        tipos_eventos = [evento['Event'] for evento in eventos_recebidos]
        assert 'VoicemailDetected' in tipos_eventos
        assert 'VoicemailAudioStarted' not in tipos_eventos
        assert 'CallHangup' in tipos_eventos
    
    @pytest.mark.asyncio
    async def test_simular_flujo_pessoa_atende(self, asterisk_service):
        """Teste simular fluxo quando pessoa atende (não voicemail)."""
        eventos_recebidos = []
        
        def callback_eventos(evento):
            eventos_recebidos.append(evento)
        
        # Registrar callback
        asterisk_service.registrar_callback_evento("test_human", callback_eventos)
        
        # Simular pessoa atendendo
        await asterisk_service._simular_human_answer_flow(
            unique_id="TEST-HUMAN",
            channel="SIP/human",
            llamada_id=3,
            timeout_dtmf=10
        )
        
        # Aguardar eventos
        await asyncio.sleep(0.1)
        
        # Verificar eventos de pessoa
        tipos_eventos = [evento['Event'] for evento in eventos_recebidos]
        assert 'CallAnswered' in tipos_eventos
        assert 'AudioStarted' in tipos_eventos
        assert 'WaitingDTMF' in tipos_eventos
        
        # Verificar que marcou como atendimento humano
        evento_answered = next(e for e in eventos_recebidos if e['Event'] == 'CallAnswered')
        assert evento_answered['AnswerType'] == 'Human'


class TestFluxoCompletoVoicemail:
    """Testes de fluxo completo incluindo voicemail."""
    
    @pytest.mark.asyncio
    async def test_campana_completa_com_voicemail(self):
        """Teste de campanha completa com cenários de voicemail."""
        # Este teste simula um fluxo completo de campanha
        # incluindo chamadas que caem em voicemail
        
        # Mock do banco de dados
        db_mock = MagicMock(spec=Session)
        
        # Mock da lista de chamadas
        lista_mock = MagicMock(spec=ListaLlamadas)
        lista_mock.id = 1
        lista_mock.activa = True
        
        # Mock da campanha
        campana_mock = MagicMock(spec=CampanaPresione1)
        campana_mock.id = 1
        campana_mock.nombre = "Campanha Voicemail Test"
        campana_mock.detectar_voicemail = True
        campana_mock.mensaje_voicemail_url = "/sounds/voicemail.wav"
        campana_mock.duracion_maxima_voicemail = 30
        campana_mock.activa = False
        
        # Configurar mocks do banco
        db_mock.query.return_value.filter.return_value.first.side_effect = [
            lista_mock,  # Verificar lista existe
            None,        # Não há campanha ativa para esta lista
            campana_mock # Obter campanha criada
        ]
        
        # Criar serviço
        service = PresionE1Service(db_mock)
        
        # Dados da campanha com voicemail
        campana_data = CampanaPresione1Create(
            nombre="Campanha Voicemail Test",
            descripcion="Teste completo com voicemail",
            lista_llamadas_id=1,
            mensaje_audio_url="/sounds/test.wav",
            timeout_presione1=10,
            detectar_voicemail=True,
            mensaje_voicemail_url="/sounds/voicemail.wav",
            duracion_minima_voicemail=3,
            duracion_maxima_voicemail=30,
            extension_transferencia="100",
            llamadas_simultaneas=1,
            tiempo_entre_llamadas=5
        )
        
        # Simular criação da campanha
        nova_campana = MagicMock(spec=CampanaPresione1)
        nova_campana.id = 1
        nova_campana.nombre = campana_data.nombre
        nova_campana.detectar_voicemail = True
        
        db_mock.add.return_value = None
        db_mock.commit.return_value = None
        db_mock.refresh.return_value = None
        
        # Executar criação
        campana_criada = service.crear_campana(campana_data)
        
        # Verificar que foi criada com configuração de voicemail
        db_mock.add.assert_called()
        db_mock.commit.assert_called()
        
        # Simular eventos de voicemail
        eventos_voicemail = [
            {
                "Event": "VoicemailDetected",
                "LlamadaID": 1,
                "DetectionMethod": "BeepDetection",
                "Timestamp": datetime.now().isoformat()
            },
            {
                "Event": "VoicemailAudioStarted",
                "LlamadaID": 1,
                "AudioURL": "/sounds/voicemail.wav",
                "MaxDuration": 30,
                "Timestamp": datetime.now().isoformat()
            },
            {
                "Event": "VoicemailAudioFinished",
                "LlamadaID": 1,
                "AudioDuration": 15.0,
                "Reason": "Completed",
                "Timestamp": datetime.now().isoformat()
            }
        ]
        
        # Mock da chamada para processar eventos
        llamada_mock = MagicMock(spec=LlamadaPresione1)
        llamada_mock.id = 1
        llamada_mock.estado = "marcando"
        
        db_mock.query.return_value.filter.return_value.first.return_value = llamada_mock
        service._finalizar_llamada = AsyncMock()
        
        # Processar eventos sequencialmente
        for evento in eventos_voicemail:
            await service.processar_evento_asterisk(evento)
        
        # Verificar que processou corretamente
        assert llamada_mock.voicemail_detectado == True
        assert llamada_mock.estado == "voicemail_finalizado"
        assert llamada_mock.duracion_mensaje_voicemail == 15
        service._finalizar_llamada.assert_called_with(1, "voicemail_mensaje_dejado")
    
    def test_validacao_schema_voicemail(self):
        """Teste validação de schemas com campos de voicemail."""
        # Teste schema válido com voicemail
        data_valida = {
            "nombre": "Test Voicemail",
            "lista_llamadas_id": 1,
            "mensaje_audio_url": "/sounds/test.wav",
            "detectar_voicemail": True,
            "mensaje_voicemail_url": "/sounds/voicemail.wav",
            "duracion_minima_voicemail": 3,
            "duracion_maxima_voicemail": 30,
            "extension_transferencia": "100"
        }
        
        schema = CampanaPresione1Create(**data_valida)
        assert schema.detectar_voicemail == True
        assert schema.mensaje_voicemail_url == "/sounds/voicemail.wav"
        assert schema.duracion_minima_voicemail == 3
        assert schema.duracion_maxima_voicemail == 30
        
        # Teste validação de duração
        data_invalida = data_valida.copy()
        data_invalida["duracion_maxima_voicemail"] = 2  # Menor que mínima
        
        with pytest.raises(ValueError, match="Duração máxima deve ser maior que duração mínima"):
            CampanaPresione1Create(**data_invalida)
        
        # Teste validação de URL de voicemail
        data_url_invalida = data_valida.copy()
        data_url_invalida["mensaje_voicemail_url"] = "/sounds/invalid.txt"
        
        with pytest.raises(ValueError, match="Formato de áudio de voicemail inválido"):
            CampanaPresione1Create(**data_url_invalida)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 