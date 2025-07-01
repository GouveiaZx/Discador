# 🗺️ MAPA COMPLETO DAS ROTAS API

## 🔗 URL Base da API
**Production:** `https://graceful-courtesy-production.up.railway.app`  
**Swagger:** `https://graceful-courtesy-production.up.railway.app/docs`

---

## 📞 ROTAS CHAMADAS (`/llamadas`)

```
GET    /llamadas/proxima/{campana_id}      - Próxima chamada da campanha
POST   /llamadas/iniciar                   - Iniciar nova chamada
PUT    /llamadas/{llamada_id}/finalizar    - Finalizar chamada
GET    /llamadas/{llamada_id}/status       - Status da chamada
GET    /llamadas/campana/{campana_id}      - Llamadas por campanha
POST   /llamadas/webhook/asterisk          - Webhook do Asterisk
```

---

## 🎪 ROTAS CAMPANHAS (`/campanas`)

```
POST   /campanas                          - Crear nueva campaña
GET    /campanas                          - Listar campanhas
PUT    /campanas/{campana_id}             - Atualizar campanha
DELETE /campanas/{campana_id}             - Deletar campanha
POST   /campanas/{campana_id}/iniciar     - Iniciar campanha
POST   /campanas/{campana_id}/pausar      - Pausar campanha
POST   /campanas/{campana_id}/parar       - Parar campanha
```

---

## 📋 ROTAS LISTAS (`/listas`)

```
POST   /listas/upload                     - Upload arquivo CSV/Excel
GET    /listas/{lista_id}/numeros         - Números da lista
POST   /listas/{lista_id}/validar         - Validar números
GET    /listas/estadisticas               - Estatísticas das listas
DELETE /listas/{lista_id}                 - Deletar lista
```

---

## 🛡️ ROTAS BLACKLIST (`/blacklist`)

```
POST   /blacklist/numeros                 - Adicionar número
GET    /blacklist/numeros                 - Listar números bloqueados
DELETE /blacklist/numeros/{numero}        - Remover da blacklist
POST   /blacklist/import                  - Importar lista DNC
GET    /blacklist/validar/{numero}        - Verificar se está bloqueado
```

---

## 📊 ROTAS MONITORAMENTO (`/monitoring`)

```
GET    /monitoring/dashboard              - Métricas em tempo real
GET    /monitoring/llamadas-activas       - Chamadas ativas
GET    /monitoring/estadisticas-tiempo-real - Stats WebSocket
GET    /monitoring/alertas                - Alertas do sistema
POST   /monitoring/configurar-alertas     - Configurar alertas
```

---

## 📡 ROTAS MULTI-SIP (`/multi-sip`)

```
POST   /multi-sip/provedores              - Criar provedor SIP
GET    /multi-sip/provedores              - Listar provedores
PUT    /multi-sip/provedores/{id}         - Atualizar provedor
DELETE /multi-sip/provedores/{id}         - Deletar provedor
POST   /multi-sip/tarifas                 - Criar tarifa
GET    /multi-sip/tarifas                 - Listar tarifas
GET    /multi-sip/selecionar/{numero}     - Selecionar melhor provedor
GET    /multi-sip/estadisticas            - Estatísticas Multi-SIP
```

---

## 🤖 ROTAS ÁUDIO INTELIGENTE (`/audio`)

```
POST   /audio/contextos                   - Criar contexto de áudio
GET    /audio/contextos                   - Listar contextos
PUT    /audio/contextos/{id}              - Atualizar contexto
DELETE /audio/contextos/{id}              - Deletar contexto
POST   /audio/sessoes                     - Criar sessão de áudio
GET    /audio/sessoes/{id}/status         - Status da sessão
POST   /audio/eventos                     - Processar evento
POST   /audio/setup-padrao                - Setup contexto padrão
GET    /audio/templates                   - Listar templates
```

---

## 🎯 ROTAS CODE2BASE (`/code2base`)

```
POST   /code2base/seleccionar             - Selecionar CLI inteligente
GET    /code2base/clis                    - Listar CLIs disponíveis
POST   /code2base/clis                    - Criar novo CLI
PUT    /code2base/clis/{id}               - Atualizar CLI
DELETE /code2base/clis/{id}               - Deletar CLI
GET    /code2base/reglas                  - Listar regras
POST   /code2base/reglas                  - Criar regra
PUT    /code2base/reglas/{id}             - Atualizar regra
DELETE /code2base/reglas/{id}             - Deletar regra
GET    /code2base/estadisticas            - Estatísticas CODE2BASE
POST   /code2base/testar                  - Testar sistema
GET    /code2base/configuracion           - Ver configuração
PUT    /code2base/configuracion           - Atualizar configuração
```

---

## 🗳️ ROTAS CAMPANHAS POLÍTICAS (`/campanha-politica`)

```
POST   /campanha-politica/configuracao-eleitoral  - Configuração país
GET    /campanha-politica/configuracao-eleitoral  - Listar configurações
POST   /campanha-politica/calendario-eleitoral    - Calendário eleitoral
GET    /campanha-politica/calendario-eleitoral    - Listar calendários
POST   /campanha-politica/campanhas               - Criar campanha política
GET    /campanha-politica/campanhas               - Listar campanhas
POST   /campanha-politica/validar-horario         - Validar horário legal
GET    /campanha-politica/logs-eleitorais/{id}    - Logs auditoria
GET    /campanha-politica/status/{id}             - Status campanha
```

---

## 📈 ROTAS RELATÓRIOS (`/reportes`)

```
GET    /reportes/llamadas                 - Relatório de chamadas
GET    /reportes/campanas                 - Relatório de campanhas
GET    /reportes/efectividad              - Relatório de efetividade
POST   /reportes/exportar                 - Exportar dados
GET    /reportes/estadisticas-operadores  - Stats operadores
GET    /reportes/cdr                      - Call Detail Records
```

---

## 📞 ROTAS CLIs (`/cli`)

```
POST   /cli/clis                          - Crear CLI
GET    /cli/clis                          - Listar CLIs
PUT    /cli/clis/{id}                     - Atualizar CLI
DELETE /cli/clis/{id}                     - Deletar CLI
POST   /cli/validar                       - Validar CLI
GET    /cli/estadisticas                  - Estatísticas CLIs
POST   /cli/testar/{id}                   - Testar CLI
```

---

## 🔊 ROTAS STT (Speech-to-Text) (`/stt`)

```
POST   /stt/transcribir                   - Transcrever áudio
GET    /stt/configuracion                 - Configuração STT
PUT    /stt/configuracion                 - Atualizar configuração
GET    /stt/historico                     - Histórico transcrições
```

---

## 🚀 WEBSOCKETS

```
WS     /ws/monitoring                     - Updates em tempo real
WS     /ws/llamadas                       - Status chamadas
WS     /ws/dashboard                      - Dashboard real-time
```

---

## 🔧 ROTAS SISTEMA

```
GET    /                                  - Health check
GET    /health                            - Status do sistema
GET    /docs                              - Documentação Swagger
GET    /redoc                             - Documentação ReDoc
GET    /openapi.json                      - Schema OpenAPI
```

---

## 🎯 PRINCIPAIS FLUXOS DE USO

### 1. **Criar e Iniciar Campanha:**
```
1. POST /campanas - Criar campanha
2. POST /listas/upload - Upload números
3. POST /campanas/{id}/iniciar - Iniciar
4. WS /ws/monitoring - Monitorar em tempo real
```

### 2. **Configurar Multi-SIP:**
```
1. POST /multi-sip/provedores - Criar provedores
2. POST /multi-sip/tarifas - Configurar tarifas
3. GET /multi-sip/selecionar/{numero} - Testar seleção
```

### 3. **Setup Áudio Inteligente:**
```
1. POST /audio/setup-padrao - Setup inicial
2. POST /audio/contextos - Criar contexto custom
3. POST /audio/sessoes - Iniciar sessão
```

### 4. **Monitoramento:**
```
1. GET /monitoring/dashboard - Dashboard
2. WS /ws/monitoring - Real-time updates
3. GET /reportes/llamadas - Relatórios
```

---

**💡 Dica:** Use `/docs` para testar todas as rotas interativamente! 