#!/usr/bin/env python3
# Teste mínimo para verificar FastAPI

try:
    print("🔍 Testando FastAPI...")
    from fastapi import FastAPI
    print("✅ FastAPI importado com sucesso")
    
    app = FastAPI(title="Teste Mínimo")
    
    @app.get("/health")
    def health_check():
        return {"status": "ok", "message": "Servidor funcionando"}
    
    @app.post("/test-pause")
    def test_pause(data: dict):
        return {"status": "success", "message": "Teste de pausar funcionando", "data": data}
    
    print("✅ App FastAPI criado com sucesso")
    print("🚀 Para testar, execute: uvicorn minimal_test:app --reload --port 8001")
    
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()