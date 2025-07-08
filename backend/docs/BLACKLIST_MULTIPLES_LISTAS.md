# Blacklist e Múltiplas Listas de Chamadas

## Visão Geral

Este documento descreve a implementação completa do sistema de blacklist (lista negra) e múltiplas listas de chamadas no discador predictivo. O sistema permite gerenciar números bloqueados automaticamente e organizar chamadas por listas específicas.

## Funcionalidades Implementadas

### 1. Sistema de Blacklist
- ✅ Verificação automática antes de cada chamada
- ✅ Adição individual e em massa de números
- ✅ Remoção (soft delete) de números
- ✅ Busca avançada com filtros
- ✅ Estatísticas detalhadas
- ✅ Contador de tentativas de bloqueio
- ✅ Histórico de bloqueios

### 2. Múltiplas Listas de Chamadas
- ✅ Associação de chamadas a listas específicas
- ✅ Upload de arquivos CSV/TXT
- ✅ Validação e normalização de números
- ✅ Estatísticas por lista
- ✅ Discado sequencial por lista

### 3. Serviço de Discado Integrado
- ✅ Verificação automática de blacklist
- ✅ Integração com múltiplas listas
- ✅ Registro de chamadas bloqueadas
- ✅ Estatísticas em tempo real

## Estrutura da Base de Dados

### Tabla: `lista_negra` (Blacklist)

```sql
CREATE TABLE lista_negra (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(20) NOT NULL,
    numero_normalizado VARCHAR(20) UNIQUE NOT NULL,
    motivo VARCHAR(255),
    observaciones TEXT,
    activo BOOLEAN DEFAULT TRUE NOT NULL,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    creado_por VARCHAR(100),
    veces_bloqueado INTEGER DEFAULT 0 NOT NULL,
    ultima_vez_bloqueado TIMESTAMP WITH TIME ZONE
);
```

**Campos principais:**
- `numero_normalizado`: Formato padrão (+549XXXXXXXXXX) para comparações
- `activo`: Permite soft delete (desativar sem remover)
- `veces_bloqueado`: Contador automático de tentativas bloqueadas
- `ultima_vez_bloqueado`: Timestamp da última tentativa

### Tabla: `llamadas` (Atualizada)

```sql
ALTER TABLE llamadas ADD COLUMN:
- numero_normalizado VARCHAR(20) NOT NULL
- id_lista_llamadas INTEGER REFERENCES listas_llamadas(id)
- bloqueado_blacklist BOOLEAN DEFAULT FALSE
```

## API Endpoints

### Blacklist Management

#### `POST /api/v1/blacklist/verificar`
Verifica se um número está na blacklist.

```json
{
  "numero": "+5491112345678"
}
```

**Resposta:**
```json
{
  "numero_original": "+5491112345678",
  "numero_normalizado": "+5491112345678",
  "en_blacklist": true,
  "motivo": "Número reportado como spam",
  "fecha_bloqueo": "2023-12-01T10:00:00Z"
}
```

#### `POST /api/v1/blacklist/agregar`
Adiciona um número à blacklist.

```json
{
  "numero": "+5491112345678",
  "motivo": "Número de spam",
  "observaciones": "Reportado por múltiplos usuários",
  "creado_por": "admin"
}
```

#### `POST /api/v1/blacklist/agregar-bulk`
Adiciona múltiplos números de uma vez.

```json
{
  "numeros": [
    "+5491112345678",
    "+5491187654321",
    "011 8888-9999"
  ],
  "motivo": "Importação de lista de spam",
  "creado_por": "admin"
}
```

#### `GET /api/v1/blacklist/`
Lista números na blacklist com paginação.

**Parâmetros:**
- `skip`: Registros a pular (paginação)
- `limit`: Máximo de registros
- `apenas_ativos`: Apenas números ativos

#### `POST /api/v1/blacklist/buscar`
Busca avançada na blacklist.

```json
{
  "numero": "1112",
  "motivo": "spam",
  "creado_por": "admin",
  "activo": true,
  "fecha_desde": "2023-01-01T00:00:00Z",
  "fecha_hasta": "2023-12-31T23:59:59Z"
}
```

#### `GET /api/v1/blacklist/estadisticas`
Obtém estatísticas da blacklist.

**Resposta:**
```json
{
  "total_numeros": 1250,
  "numeros_activos": 1100,
  "numeros_inactivos": 150,
  "total_bloqueos_hoy": 45,
  "total_bloqueos_mes": 1200,
  "numero_mas_bloqueado": "+5491112345678"
}
```

### Discado Integrado

#### `POST /api/v1/discado/iniciar-llamada`
Inicia uma chamada com verificação automática de blacklist.

```json
{
  "numero_destino": "+5491112345678",
  "campana_id": 1,
  "lista_llamadas_id": 5,
  "usuario_id": "user123"
}
```

**Resposta (número permitido):**
```json
{
  "estado": "iniciado",
  "mensaje": "Llamada iniciada exitosamente",
  "numero_destino": "+5491112345678",
  "numero_normalizado": "+5491112345678",
  "cli_utilizado": "+5491122334455",
  "llamada_id": 123,
  "unique_id": "SIM-abc123def456",
  "bloqueado_blacklist": false
}
```

**Resposta (número bloqueado):**
```json
{
  "estado": "bloqueado",
  "mensaje": "Número bloqueado por blacklist: Spam",
  "numero_destino": "+5491112345678",
  "numero_normalizado": "+5491112345678",
  "bloqueado_blacklist": true,
  "motivo_bloqueo": "Spam",
  "fecha_bloqueo": "2023-12-01T10:00:00Z",
  "llamada_id": 124
}
```

#### `POST /api/v1/discado/llamar-siguiente-lista`
Chama o próximo número disponível de uma lista.

```json
{
  "lista_llamadas_id": 5,
  "campana_id": 1,
  "usuario_id": "user123"
}
```

#### `GET /api/v1/discado/proximo-numero-lista/{lista_id}`
Obtém o próximo número sem iniciar a chamada.

#### `GET /api/v1/discado/estadisticas-lista/{lista_id}`
Estatísticas detalhadas de uma lista.

```json
{
  "lista_id": 5,
  "nombre_lista": "Campanha Dezembro",
  "total_numeros": 1000,
  "llamadas_realizadas": 750,
  "llamadas_bloqueadas": 50,
  "llamadas_exitosas": 600,
  "numeros_pendientes": 250,
  "porcentaje_completado": 75.0,
  "tasa_exito": 80.0
}
```

## Fluxo de Trabalho

### 1. Configuração Inicial

```bash
# 1. Executar migrações
psql -d discador -f migrations/create_listas_llamadas.sql
psql -d discador -f migrations/update_blacklist_and_llamadas.sql

# 2. Importar lista de números
curl -X POST "http://localhost:8000/api/v1/listas-llamadas/upload" \
  -F "archivo=@numeros.csv" \
  -F "nombre_lista=Campanha Natal" \
  -F "descripcion=Lista para campanha de Natal 2023"

# 3. Adicionar números à blacklist
curl -X POST "http://localhost:8000/api/v1/blacklist/agregar-bulk" \
  -H "Content-Type: application/json" \
  -d '{
    "numeros": ["+5491100000000", "+5491100000001"],
    "motivo": "Números de teste - não chamar",
    "creado_por": "admin"
  }'
```

### 2. Discado com Verificação Automática

```python
import requests

# Chamar próximo número da lista
response = requests.post("http://localhost:8000/api/v1/discado/llamar-siguiente-lista", 
    json={
        "lista_llamadas_id": 1,
        "campana_id": 1,
        "usuario_id": "operador01"
    }
)

result = response.json()
if result["estado"] == "bloqueado":
    print(f"Número {result['numero_destino']} bloqueado: {result['motivo_bloqueo']}")
elif result["estado"] == "iniciado":
    print(f"Chamada iniciada para {result['numero_destino']}")
elif result["estado"] == "sin_numeros":
    print("Não há mais números na lista")
```

### 3. Gestão da Blacklist

```python
# Verificar se número está bloqueado
response = requests.post("http://localhost:8000/api/v1/blacklist/verificar",
    json={"numero": "+5491112345678"}
)

if response.json()["en_blacklist"]:
    print("Número está na blacklist")

# Obter estatísticas
stats = requests.get("http://localhost:8000/api/v1/blacklist/estadisticas").json()
print(f"Total bloqueados hoje: {stats['total_bloqueos_hoy']}")
```

## Testes

### Executar Testes Unitários

```bash
# Testes da blacklist
python -m pytest tests/test_blacklist.py -v

# Testes das listas de chamadas
python -m pytest tests/test_lista_llamadas.py -v

# Todos os testes
python -m pytest tests/ -v
```

### Testes de Integração

```bash
# Teste do fluxo completo
python -m pytest tests/test_integracao_completa.py -v
```

## Monitoramento e Métricas

### Dashboards Recomendados

1. **Métricas de Blacklist**
   - Números bloqueados por dia
   - Top 10 números mais bloqueados
   - Efetividade da blacklist (% de bloqueios)

2. **Métricas por Lista**
   - Progresso de cada lista
   - Taxa de sucesso por lista
   - Números bloqueados por lista

3. **Métricas de Discado**
   - Chamadas realizadas vs bloqueadas
   - Tempo médio por lista
   - Eficiência do discado

### Logs Importantes

```python
# Configurar logging para acompanhar atividade
import logging

logger = logging.getLogger('discador.blacklist')
logger.info(f"Número {numero} bloqueado por blacklist: {motivo}")

logger = logging.getLogger('discador.listas')
logger.info(f"Lista {lista_id} processada: {stats}")
```

## Performance e Otimização

### Índices Importantes

```sql
-- Blacklist
CREATE INDEX idx_lista_negra_normalizado ON lista_negra(numero_normalizado);
CREATE INDEX idx_lista_negra_activo ON lista_negra(activo);

-- Chamadas
CREATE INDEX idx_llamadas_numero_normalizado ON llamadas(numero_normalizado);
CREATE INDEX idx_llamadas_lista ON llamadas(id_lista_llamadas);
CREATE INDEX idx_llamadas_bloqueado ON llamadas(bloqueado_blacklist);
```

### Recomendações

1. **Cache**: Implementar cache Redis para blacklist mais acessada
2. **Batch Processing**: Processar verificações em lotes para alta volumetria
3. **Arquivamento**: Mover números inativos da blacklist para tabela histórica
4. **Monitoramento**: Alertas para crescimento excessivo da blacklist

## Troubleshooting

### Problemas Comuns

1. **Número não normalizado corretamente**
   ```python
   from app.schemas.lista_llamadas import validar_numero_telefono
   resultado = validar_numero_telefono("+54 9 11 1234-5678")
   print(f"Normalizado: {resultado.numero_normalizado}")
   ```

2. **Blacklist não funcionando**
   - Verificar se números estão marcados como `activo = true`
   - Confirmar normalização consistente

3. **Performance lenta**
   - Verificar se índices foram criados
   - Analisar queries com EXPLAIN ANALYZE

### Logs de Debug

```bash
# Verificar logs da aplicação
tail -f logs/discador.log | grep -i blacklist

# Logs do PostgreSQL
tail -f /var/log/postgresql/postgresql.log
```

## Próximos Passos

### Funcionalidades Futuras

1. **Whitelist**: Lista de números sempre permitidos
2. **Blacklist Temporal**: Bloqueios com data de expiração
3. **ML Integration**: Detecção automática de spam
4. **API Externa**: Integração com serviços de verificação
5. **Blacklist Compartilhada**: Entre diferentes campanhas/clientes

### Melhorias de Performance

1. **Cache Distribuído**: Redis cluster para blacklist
2. **Particionamento**: Tabelas particionadas por data
3. **Replicação**: Read replicas para consultas
4. **Sharding**: Distribuição por faixas de números 