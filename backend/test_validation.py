#!/usr/bin/env python3
"""
Script de teste rápido para a validação de números.
"""

import sys
import os

# Adicionar o diretório backend ao path
sys.path.insert(0, os.path.dirname(__file__))

from app.schemas.lista_llamadas import validar_numero_telefono, normalizar_numero_argentino

def test_validacao():
    """Testa a validação de números."""
    
    print("=== Teste de Validação de Números ===\n")
    
    numeros_teste = [
        "+54 9 11 1234-5678",
        "011 1234-5678",
        "11 1234 5678",
        "1112345678",
        "12345678",
        "abc123",
        "",
        "+54911123456789012345"
    ]
    
    for numero in numeros_teste:
        print(f"Número: '{numero}'")
        resultado = validar_numero_telefono(numero)
        print(f"  Válido: {resultado.valido}")
        print(f"  Normalizado: {resultado.numero_normalizado}")
        if not resultado.valido:
            print(f"  Motivo: {resultado.motivo_invalido}")
        print()

def test_normalizacao():
    """Testa a normalização de números."""
    
    print("=== Teste de Normalização ===\n")
    
    numeros_teste = [
        "5491112345678",
        "91112345678", 
        "1112345678",
        "12345678"
    ]
    
    for numero in numeros_teste:
        normalizado = normalizar_numero_argentino(numero)
        print(f"'{numero}' → '{normalizado}'")

if __name__ == "__main__":
    test_validacao()
    test_normalizacao()
    print("✅ Testes de validação concluídos!") 