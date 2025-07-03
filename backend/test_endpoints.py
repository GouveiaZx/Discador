#!/usr/bin/env python3
"""Script para testar se os endpoints estão registrados corretamente."""

from main import app
from fastapi.testclient import TestClient

def test_endpoints():
    """Testar endpoints de contacts."""
    client = TestClient(app)
    
    print("🔍 Testando endpoints de contacts...")
    
    # Testar endpoint de teste
    try:
        response = client.get("/api/v1/contacts/test")
        print(f"✅ GET /api/v1/contacts/test: {response.status_code}")
        if response.status_code == 200:
            print(f"   Resposta: {response.json()}")
    except Exception as e:
        print(f"❌ Erro no GET /api/v1/contacts/test: {e}")
    
    # Testar endpoint de upload (sem arquivo)
    try:
        response = client.post("/api/v1/contacts/upload")
        print(f"✅ POST /api/v1/contacts/upload (sem arquivo): {response.status_code}")
        if response.status_code != 200:
            print(f"   Erro esperado: {response.json()}")
    except Exception as e:
        print(f"❌ Erro no POST /api/v1/contacts/upload: {e}")
    
    # Listar todas as rotas
    print("\n📋 Rotas registradas:")
    for route in app.routes:
        if hasattr(route, 'path') and 'contacts' in route.path:
            methods = getattr(route, 'methods', ['N/A'])
            print(f"   {methods} {route.path}")

if __name__ == "__main__":
    test_endpoints() 