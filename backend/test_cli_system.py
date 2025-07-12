#!/usr/bin/env python3
"""
Script para testar o sistema CLI Pattern Generator
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.cli_pattern_generator_service import CliPatternGeneratorService

# Simular sessão da database
class MockSession:
    pass

def test_cli_system():
    """Testa o sistema CLI completo"""
    print("🔄 Iniciando teste do sistema CLI Pattern Generator...")
    
    # Criar instância do serviço
    service = CliPatternGeneratorService(MockSession())
    
    # Testar países suportados
    print("\n📍 Testando países suportados...")
    countries = service.get_supported_countries()
    print(f"✅ Total de países encontrados: {len(countries)}")
    
    for country in countries:
        print(f"   - {country['country_code']}: {country['country_name']} ({country['phone_code']})")
    
    # Testar geração de CLI para cada país
    print("\n🎯 Testando geração de CLI para cada país...")
    test_numbers = {
        'usa': '+13055551234',
        'canada': '+14165551234',
        'mexico': '+525555551234',
        'brasil': '+5511955551234',
        'colombia': '+5715551234',
        'argentina': '+5491155551234',
        'chile': '+56225551234',
        'peru': '+5115551234'
    }
    
    for country, number in test_numbers.items():
        print(f"\n🔄 Testando {country} com número {number}...")
        result = service.generate_cli_with_pattern(
            destination_number=number,
            quantity=3
        )
        
        if result.get('success'):
            print(f"✅ {country}: {len(result['generated_clis'])} CLIs generados")
            for cli in result['generated_clis']:
                print(f"   - {cli}")
        else:
            print(f"❌ {country}: {result.get('error', 'Error desconocido')}")
    
    # Testar patrón personalizado
    print("\n🎨 Testando patrón personalizado...")
    result = service.generate_cli_with_pattern(
        destination_number='+13055551234',
        custom_pattern='2xx-xxxx',
        quantity=2
    )
    
    if result.get('success'):
        print(f"✅ Patrón personalizado: {len(result['generated_clis'])} CLIs generados")
        for cli in result['generated_clis']:
            print(f"   - {cli}")
    else:
        print(f"❌ Patrón personalizado: {result.get('error', 'Error desconocido')}")
    
    # Testar generación masiva
    print("\n📦 Testando generación masiva...")
    bulk_numbers = ['+13055551234', '+525555551234', '+5511955551234']
    result = service.generate_bulk_patterns(
        destination_numbers=bulk_numbers
    )
    
    if result.get('success'):
        print(f"✅ Generación masiva: {result['successful_generations']}/{result['total_numbers']} exitosas")
        for cli_result in result['generated_clis']:
            if cli_result.get('success'):
                print(f"   - {cli_result['generated_clis'][0]} ({cli_result['country']})")
    else:
        print(f"❌ Generación masiva: {result.get('error', 'Error desconocido')}")
    
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    test_cli_system() 