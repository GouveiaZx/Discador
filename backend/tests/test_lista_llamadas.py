"""
Tests para el endpoint de listas de llamadas y upload de archivos.
"""

import pytest
import tempfile
import io
from unittest.mock import Mock, patch, mock_open
from fastapi.testclient import TestClient
from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.main import app
from app.schemas.lista_llamadas import validar_numero_telefono, normalizar_numero_argentino
from app.services.lista_llamadas_service import ListaLlamadasService
from app.models.lista_llamadas import ListaLlamadas, NumeroLlamada
from app.database import obtener_sesion


# Crear cliente de teste
client = TestClient(app)


class TestValidacionNumeros:
    """Tests para las funciones de validacion de numeros."""
    
    def test_validar_numero_argentino_valido(self):
        """Test para numero argentino valido."""
        numero = "+54 9 11 1234-5678"
        resultado = validar_numero_telefono(numero)
        
        assert resultado.valido is True
        assert resultado.numero_normalizado == "+5491112345678"
        assert resultado.numero_original == numero
        assert resultado.motivo_invalido is None
    
    def test_validar_numero_sin_codigo_pais(self):
        """Test para numero sin codigo de pais."""
        numero = "11 1234 5678"
        resultado = validar_numero_telefono(numero)
        
        assert resultado.valido is True
        assert resultado.numero_normalizado == "+54911123456789"
        assert resultado.numero_original == numero
    
    def test_validar_numero_corto_buenos_aires(self):
        """Test para numero corto de Buenos Aires."""
        numero = "12345678"
        resultado = validar_numero_telefono(numero)
        
        assert resultado.valido is True
        assert resultado.numero_normalizado == "+54911123456789"
        assert resultado.numero_original == numero
    
    def test_validar_numero_vacio(self):
        """Test para numero vacio."""
        numero = ""
        resultado = validar_numero_telefono(numero)
        
        assert resultado.valido is False
        assert resultado.numero_normalizado == ""
        assert "vacio" in resultado.motivo_invalido
    
    def test_validar_numero_muy_corto(self):
        """Test para numero demasiado corto."""
        numero = "123"
        resultado = validar_numero_telefono(numero)
        
        assert resultado.valido is False
        assert "Longitud invalida" in resultado.motivo_invalido
    
    def test_validar_numero_muy_largo(self):
        """Test para numero demasiado largo."""
        numero = "+54911123456789012345"
        resultado = validar_numero_telefono(numero)
        
        assert resultado.valido is False
        assert "Longitud invalida" in resultado.motivo_invalido
    
    def test_normalizar_numero_con_codigo_completo(self):
        """Test normalizacion con codigo completo."""
        numero = "5491112345678"
        resultado = normalizar_numero_argentino(numero)
        
        assert resultado == "+5491112345678"
    
    def test_normalizar_numero_con_9_sin_pais(self):
        """Test normalizacion con 9 pero sin codigo de pais."""
        numero = "91112345678"
        resultado = normalizar_numero_argentino(numero)
        
        assert resultado == "+5491112345678"
    
    def test_normalizar_numero_area_code(self):
        """Test normalizacion con codigo de area."""
        numero = "1112345678"
        resultado = normalizar_numero_argentino(numero)
        
        assert resultado == "+5491112345678"


class TestListaLlamadasService:
    """Tests para el servicio de listas de llamadas."""
    
    @pytest.fixture
    def mock_db(self):
        """Mock de la sesion de base de datos."""
        return Mock(spec=Session)
    
    @pytest.fixture
    def service(self, mock_db):
        """Instancia del servicio con mock de BD."""
        return ListaLlamadasService(mock_db)
    
    def test_validar_tipo_archivo_csv_valido(self, service):
        """Test validacion de archivo CSV valido."""
        assert service._validar_tipo_archivo("numeros.csv") is True
        assert service._validar_tipo_archivo("NUMEROS.CSV") is True
    
    def test_validar_tipo_archivo_txt_valido(self, service):
        """Test validacion de archivo TXT valido."""
        assert service._validar_tipo_archivo("numeros.txt") is True
        assert service._validar_tipo_archivo("NUMEROS.TXT") is True
    
    def test_validar_tipo_archivo_invalido(self, service):
        """Test validacion de archivo invalido."""
        assert service._validar_tipo_archivo("numeros.pdf") is False
        assert service._validar_tipo_archivo("numeros.doc") is False
        assert service._validar_tipo_archivo("") is False
        assert service._validar_tipo_archivo(None) is False
    
    @pytest.mark.asyncio
    async def test_procesar_csv_con_header(self, service):
        """Test procesamiento de CSV con header."""
        contenido_csv = "telefone\n+5491112345678\n+5491187654321\n"
        numeros = service._procesar_csv(contenido_csv)
        
        assert len(numeros) == 2
        assert "+5491112345678" in numeros
        assert "+5491187654321" in numeros
    
    @pytest.mark.asyncio
    async def test_procesar_csv_sin_header(self, service):
        """Test procesamiento de CSV sin header."""
        contenido_csv = "+5491112345678\n+5491187654321\n"
        numeros = service._procesar_csv(contenido_csv)
        
        assert len(numeros) == 2
        assert "+5491112345678" in numeros
        assert "+5491187654321" in numeros
    
    def test_procesar_txt(self, service):
        """Test procesamiento de archivo TXT."""
        contenido_txt = "+5491112345678\n+5491187654321\n\n+5491199999999"
        numeros = service._procesar_txt(contenido_txt)
        
        assert len(numeros) == 3
        assert "+5491112345678" in numeros
        assert "+5491187654321" in numeros
        assert "+5491199999999" in numeros
    
    @pytest.mark.asyncio
    async def test_procesar_numeros_validos(self, service):
        """Test procesamiento de numeros validos."""
        contenido = "+5491112345678\n011 8765-4321\ninvalido\n+5491112345678"
        
        resultado = await service._procesar_numeros(contenido, "test.txt")
        
        assert resultado['total_lineas'] == 4
        assert len(resultado['numeros_validos']) == 1  # Solo uno valido sin duplicados
        assert resultado['numeros_invalidos'] == 1
        assert resultado['numeros_duplicados'] == 1
        assert len(resultado['errores']) == 2  # 1 invalido + 1 duplicado


class TestEndpointsListaLlamadas:
    """Tests para los endpoints de listas de llamadas."""
    
    def setup_method(self):
        """Setup para cada test."""
        self.test_client = TestClient(app)
    
    @patch('app.database.obtener_sesion')
    @patch('app.services.lista_llamadas_service.ListaLlamadasService')
    def test_upload_archivo_exitoso(self, mock_service_class, mock_db):
        """Test upload exitoso de archivo."""
        # Configurar mocks
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_resultado = {
            'lista_id': 1,
            'nombre_lista': 'Lista Test',
            'archivo_original': 'test.csv',
            'total_numeros_archivo': 3,
            'numeros_validos': 2,
            'numeros_invalidos': 1,
            'numeros_duplicados': 0,
            'errores': ['Linea 3: Formato invalido - abc123']
        }
        mock_service.procesar_archivo.return_value = mock_resultado
        
        # Preparar archivo de teste
        contenido_archivo = b"+5491112345678\n+5491187654321\nabc123"
        archivo = ("test.csv", contenido_archivo, "text/csv")
        
        # Realizar peticion
        response = self.test_client.post(
            "/api/v1/listas-llamadas/upload",
            files={"archivo": archivo},
            data={
                "nombre_lista": "Lista Test",
                "descripcion": "Lista de teste"
            }
        )
        
        # Verificar respuesta
        assert response.status_code == 200
        data = response.json()
        
        assert data["lista_id"] == 1
        assert data["nombre_lista"] == "Lista Test"
        assert data["archivo_original"] == "test.csv"
        assert data["total_numeros_archivo"] == 3
        assert data["numeros_validos"] == 2
        assert data["numeros_invalidos"] == 1
        assert len(data["errores"]) == 1
    
    @patch('app.database.obtener_sesion')
    def test_upload_archivo_tipo_invalido(self, mock_db):
        """Test upload de arquivo com tipo invalido."""
        archivo = ("test.pdf", b"conteudo", "application/pdf")
        
        response = self.test_client.post(
            "/api/v1/listas-llamadas/upload",
            files={"archivo": archivo},
            data={"nombre_lista": "Lista Test"}
        )
        
        assert response.status_code == 400
        assert "Tipo de archivo no valido" in response.json()["detail"]
    
    @patch('app.database.obtener_sesion')
    @patch('app.services.lista_llamadas_service.ListaLlamadasService')
    def test_listar_listas(self, mock_service_class, mock_db):
        """Test listar listas de llamadas."""
        # Configurar mock
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_lista = ListaLlamadas(
            id=1,
            nombre="Lista Test",
            archivo_original="test.csv",
            total_numeros=10,
            numeros_validos=9,
            numeros_duplicados=1
        )
        mock_service.listar_listas.return_value = [mock_lista]
        
        # Realizar peticion
        response = self.test_client.get("/api/v1/listas-llamadas/")
        
        # Verificar respuesta
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 1
        assert data[0]["id"] == 1
        assert data[0]["nombre"] == "Lista Test"
    
    @patch('app.database.obtener_sesion')
    @patch('app.services.lista_llamadas_service.ListaLlamadasService')
    def test_obtener_lista_por_id(self, mock_service_class, mock_db):
        """Test obtener lista especifica por ID."""
        # Configurar mock
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_lista = ListaLlamadas(
            id=1,
            nombre="Lista Test",
            archivo_original="test.csv",
            total_numeros=10,
            numeros_validos=9,
            numeros_duplicados=1
        )
        mock_lista.numeros = []  # Lista vacia de numeros
        mock_service.obtener_lista.return_value = mock_lista
        
        # Realizar peticion
        response = self.test_client.get("/api/v1/listas-llamadas/1")
        
        # Verificar respuesta
        assert response.status_code == 200
        data = response.json()
        
        assert data["id"] == 1
        assert data["nombre"] == "Lista Test"
        assert data["numeros"] == []
    
    @patch('app.database.obtener_sesion')
    @patch('app.services.lista_llamadas_service.ListaLlamadasService')
    def test_eliminar_lista(self, mock_service_class, mock_db):
        """Test eliminar lista."""
        # Configurar mock
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        mock_service.eliminar_lista.return_value = True
        
        # Realizar peticion
        response = self.test_client.delete("/api/v1/listas-llamadas/1")
        
        # Verificar respuesta
        assert response.status_code == 200
        data = response.json()
        
        assert "eliminada exitosamente" in data["mensaje"]
        assert data["lista_id"] == 1
    
    @patch('app.database.obtener_sesion')
    @patch('app.services.lista_llamadas_service.ListaLlamadasService')
    def test_actualizar_lista(self, mock_service_class, mock_db):
        """Test actualizar lista."""
        # Configurar mock
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        mock_lista = ListaLlamadas(
            id=1,
            nombre="Lista Actualizada",
            descripcion="Nueva descripcion",
            archivo_original="test.csv",
            total_numeros=10,
            numeros_validos=9,
            numeros_duplicados=1,
            activa=True
        )
        mock_service.obtener_lista.return_value = mock_lista
        mock_db.query.return_value.filter.return_value.first.return_value = None
        
        # Realizar peticion
        datos_actualizacion = {
            "nombre": "Lista Actualizada",
            "descripcion": "Nueva descripcion"
        }
        
        response = self.test_client.put(
            "/api/v1/listas-llamadas/1",
            json=datos_actualizacion
        )
        
        # Verificar respuesta
        assert response.status_code == 200
        data = response.json()
        
        assert data["nombre"] == "Lista Actualizada"
        assert data["descripcion"] == "Nueva descripcion"


class TestIntegracionCompleta:
    """Tests de integracion completa."""
    
    @pytest.mark.asyncio
    async def test_flujo_completo_upload_y_consulta(self):
        """Test del flujo completo de upload y consulta."""
        # Este test requeriria una base de datos de teste real
        # Por ahora es un placeholder para documentar la funcionalidad esperada
        pass


if __name__ == "__main__":
    pytest.main([__file__]) 