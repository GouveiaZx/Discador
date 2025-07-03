#!/usr/bin/env python3
"""Script simples para verificar rotas registradas."""

from main import app

def listar_rotas():
    """Listar todas as rotas registradas."""
    print("📋 Rotas registradas no FastAPI:")
    print("-" * 50)
    
    contacts_routes = []
    all_routes = []
    
    for route in app.routes:
        if hasattr(route, 'path'):
            methods = getattr(route, 'methods', {'N/A'})
            methods_str = ', '.join(sorted(methods)) if methods != {'N/A'} else 'N/A'
            route_info = f"{methods_str:<15} {route.path}"
            all_routes.append(route_info)
            
            if 'contacts' in route.path:
                contacts_routes.append(route_info)
    
    # Mostrar todas as rotas
    for route in sorted(all_routes):
        print(f"  {route}")
    
    print("\n🎯 Rotas de contacts encontradas:")
    print("-" * 40)
    if contacts_routes:
        for route in contacts_routes:
            print(f"  ✅ {route}")
    else:
        print("  ❌ Nenhuma rota de contacts encontrada!")
    
    print(f"\n📊 Total de rotas: {len(all_routes)}")
    print(f"📊 Rotas de contacts: {len(contacts_routes)}")

if __name__ == "__main__":
    listar_rotas() 