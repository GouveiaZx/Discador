#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
sys.path.append('.')

print('✅ Testando imports básicos...')

try:
    from app.services.configuracao_discagem_service import ConfiguracaoDiscagemService
    print('  - ConfiguracaoDiscagemService: OK')
except Exception as e:
    print(f'  - ConfiguracaoDiscagemService: ERRO - {e}')

try:
    from app.services.trunk_service import TrunkService
    print('  - TrunkService: OK')
except Exception as e:
    print(f'  - TrunkService: ERRO - {e}')

try:
    # Testar apenas o serviço sem dependências do modelo llamada
    from app.services.dnc_avancado_service import DNCAvarancadoService
    print('  - DNCAvarancadoService: OK')
except Exception as e:
    print(f'  - DNCAvarancadoService: ERRO - {e}')

try:
    from app.routes.configuracao_discagem import router as config_router
    print('  - Rota configuracao_discagem: OK')
except Exception as e:
    print(f'  - Rota configuracao_discagem: ERRO - {e}')

print('\n🎉 Testes de import concluídos!') 