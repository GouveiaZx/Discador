#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import uvicorn
from main import app

print('✅ Testando inicialização do servidor...')
print('Aplicação FastAPI criada com sucesso!')
print(f'Título: {app.title}')
print(f'Versão: {app.version}')
print(f'Debug: {app.debug}')

print('\nRotas principais:')
route_count = 0
for route in app.routes:
    if hasattr(route, 'path') and route.path.startswith('/api/v1'):
        methods = getattr(route, 'methods', {'GET'})
        print(f'  {list(methods)} {route.path}')
        route_count += 1

print(f'\nTotal de rotas API: {route_count}')
print('\n🎉 Servidor configurado corretamente!') 