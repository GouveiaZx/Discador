#!/usr/bin/env python3
"""
Script de debug para testar validação de contatos
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.schemas.lista_llamadas import validar_numero_telefone

def test_validacao():
    """Testa a validação de telefones"""
    
    numeros_teste = [
        "5551234567",
        "+1 555 123 4567",
        "(555) 123-4567",
        "555-123-4567",
        "1234567890",
        "11987654321",
        "+54 11 1234-5678"
    ]
    
    print("🧪 Testando validação de telefones...")
    
    for numero in numeros_teste:
        resultado = validar_numero_telefone(numero, "auto")
        print(f"📞 {numero:<20} -> Válido: {resultado.valido:<5} | País: {resultado.pais_detectado:<10} | Motivo: {resultado.motivo_invalido}")

if __name__ == "__main__":
    test_validacao() 