# 🎯 CLI Aleatorio - Identificador de Chamada Dinâmico

## 📋 Visão Geral

O sistema de **CLI Aleatorio** implementa a geração automática e dinâmica de identificadores de chamada (Caller Line Identification) para cada ligação iniciada. Este sistema permite:

- ✅ **Rotação automática** de CLIs para cada chamada
- ✅ **Gestão centralizada** dos CLIs permitidos
- ✅ **Distribuição equitativa** do uso dos CLIs
- ✅ **Estatísticas detalhadas** de uso
- ✅ **Integração transparente** com o sistema de discado

---

## 🗄️ Base de Dados

### Tabela `cli`

```sql
CREATE TABLE cli (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(20) NOT NULL UNIQUE,
    numero_normalizado VARCHAR(20) NOT NULL UNIQUE,
    descripcion VARCHAR(255),
    activo BOOLEAN DEFAULT TRUE NOT NULL,
    veces_usado INTEGER DEFAULT 0 NOT NULL,
    ultima_vez_usado TIMESTAMP WITH TIME ZONE,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    notas TEXT
);
```

#### Campos:
- **`numero`**: CLI original como foi inserido
- **`numero_normalizado`**: CLI em formato padronizado (+549XXXXXXXXXX)
- **`activo`**: Se o CLI está disponível para uso
- **`veces_usado`**: Contador automático de quantas vezes foi usado
- **`ultima_vez_usado`**: Timestamp da última utilização

---

## 🚀 API Rest - Endpoints

### 1. Gerar CLI Aleatorio

**`GET /api/v1/cli/generar-aleatorio`**

Obtém um CLI aleatório para usar em uma chamada.

**Parâmetros de consulta:**
- `excluir_cli` (opcional): CLI específico para excluir da seleção
- `solo_poco_usados` (opcional): Preferir CLIs menos utilizados

**Exemplo de uso:**
```bash
curl -X GET "http://localhost:8000/api/v1/cli/generar-aleatorio?solo_poco_usados=true"
```

**Resposta:**
```json
{
  "cli_seleccionado": "+5491122334455",
  "cli_id": 1,
  "veces_usado": 6,
  "mensaje": "CLI selecionado: +5491122334455"
}
```

### 2. Adicionar CLI

**`POST /api/v1/cli/agregar`**

Adiciona um novo CLI à base de dados.

**Corpo da requisição:**
```json
{
  "numero": "+5491122334455",
  "descripcion": "CLI principal",
  "notas": "CLI para campanhas prioritárias"
}
```

**Resposta:**
```json
{
  "id": 1,
  "numero": "+5491122334455",
  "numero_normalizado": "+5491122334455",
  "descripcion": "CLI principal",
  "activo": true,
  "veces_usado": 0,
  "fecha_creacion": "2024-12-05T10:30:00Z",
  "fecha_actualizacion": "2024-12-05T10:30:00Z"
}
```

### 3. Adicionar CLIs em Massa

**`POST /api/v1/cli/agregar-bulk`**

Adiciona múltiplos CLIs de uma vez.

**Corpo da requisição:**
```json
{
  "numeros": [
    "+5491122334455",
    "+5491133445566", 
    "+5491144556677"
  ],
  "descripcion": "CLIs para campanha XYZ"
}
```

**Resposta:**
```json
{
  "mensaje": "Processamento completado. 3 CLIs agregados exitosamente.",
  "clis_agregados": 3,
  "clis_duplicados": 0,
  "clis_invalidos": 0,
  "errores": []
}
```

### 4. Listar CLIs

**`GET /api/v1/cli/`**

Lista CLIs registrados com paginação.

**Parâmetros de consulta:**
- `skip`: Número de registros a pular (paginação)
- `limit`: Máximo de registros (default: 100)
- `apenas_ativos`: Mostrar apenas CLIs ativos (default: true)

**Exemplo:**
```bash
curl -X GET "http://localhost:8000/api/v1/cli/?skip=0&limit=10&apenas_ativos=true"
```

### 5. Estatísticas de CLIs

**`GET /api/v1/cli/estadisticas`**

Obtém estatísticas detalhadas dos CLIs.

**Resposta:**
```json
{
  "total_clis": 15,
  "clis_activos": 12,
  "clis_inactivos": 3,
  "cli_mas_usado": "+5491122334455",
  "total_usos_hoy": 45,
  "total_usos_mes": 1250
}
```

### 6. Atualizar CLI

**`PUT /api/v1/cli/{cli_id}`**

Atualiza dados de um CLI específico.

**Corpo da requisição:**
```json
{
  "descripcion": "Nova descrição",
  "notas": "Notas atualizadas",
  "activo": true
}
```

### 7. Remover CLI

**`DELETE /api/v1/cli/{cli_id}`**

Remove um CLI (soft delete - marca como inativo).

**Resposta:**
```json
{
  "mensaje": "CLI removido exitosamente",
  "cli_id": 1
}
```

---

## 🔗 Integração com Discado

### Discado com CLI Aleatorio

O sistema de discado agora gera automaticamente um CLI aleatório para cada chamada:

**`POST /api/v1/discado/iniciar-llamada`**

```json
{
  "numero_destino": "+5491112345678",
  "usuario_id": "operador01"
}
```

**Resposta com CLI aleatorio:**
```json
{
  "estado": "iniciado",
  "mensaje": "Llamada iniciada exitosamente",
  "numero_destino": "+5491112345678",
  "numero_normalizado": "+5491112345678",
  "cli_utilizado": "+5491122334455",
  "cli_info": {
    "cli_seleccionado": "+5491122334455",
    "veces_usado": 6,
    "mensaje": "CLI selecionado: +5491122334455"
  },
  "llamada_id": 123,
  "bloqueado_blacklist": false
}
```

### Discado com CLI Personalizado

Também é possível especificar um CLI específico:

```json
{
  "numero_destino": "+5491112345678",
  "usuario_id": "operador01",
  "cli_personalizado": "+5491199887766"
}
```

**Resposta:**
```json
{
  "estado": "iniciado",
  "cli_utilizado": "+5491199887766",
  "cli_info": {
    "mensaje": "CLI personalizado usado: +5491199887766"
  }
}
```

---

## ⚙️ Algoritmo de Seleção

### Critérios de Seleção

1. **CLIs Ativos**: Apenas CLIs marcados como `activo = true`
2. **Distribuição Equitativa**: Opção para preferir CLIs menos usados
3. **Exclusão**: Possibilidade de excluir CLI específico
4. **Aleatoriedade**: Seleção aleatória dentro dos critérios

### Processo de Seleção

```python
def generar_cli_aleatorio(excluir_cli=None, solo_poco_usados=False):
    # 1. Buscar CLIs ativos
    clis_disponibles = query_clis_activos()
    
    # 2. Aplicar filtros
    if excluir_cli:
        clis_disponibles = filter_exclude(clis_disponibles, excluir_cli)
    
    if solo_poco_usados:
        media_usos = calcular_media_usos()
        clis_disponibles = filter_poco_usados(clis_disponibles, media_usos)
    
    # 3. Seleção aleatória
    cli_selecionado = random.choice(clis_disponibles)
    
    # 4. Atualizar contadores
    cli_selecionado.veces_usado += 1
    cli_selecionado.ultima_vez_usado = now()
    
    return cli_selecionado
```

---

## 📊 Monitoramento e Estatísticas

### Métricas Disponíveis

- **Total de CLIs**: Registrados no sistema
- **CLIs Ativos/Inativos**: Estado atual dos CLIs
- **CLI Mais Usado**: CLI com maior número de utilizações
- **Usos Diários/Mensais**: Contadores de utilização

### Dashboard de Uso

```
┌─────────────────────────────────────────┐
│ 📊 Estatísticas de CLI                  │
├─────────────────────────────────────────┤
│ Total CLIs:        15                   │
│ CLIs Ativos:       12                   │
│ CLIs Inativos:     3                    │
│ Mais Usado:        +5491122334455 (45x) │
│ Usos Hoje:         127                  │
│ Usos este Mês:     3,240               │
└─────────────────────────────────────────┘
```

---

## 🔧 Configuração e Setup

### 1. Executar Migração

```bash
psql -d discador -f migrations/create_cli_table.sql
```

### 2. Adicionar CLIs Iniciais

```bash
curl -X POST "http://localhost:8000/api/v1/cli/agregar-bulk" \
  -H "Content-Type: application/json" \
  -d '{
    "numeros": [
      "+5491122334455",
      "+5491133445566",
      "+5491144556677"
    ],
    "descripcion": "CLIs iniciais do sistema"
  }'
```

### 3. Verificar Funcionamento

```bash
# Gerar CLI aleatorio
curl -X GET "http://localhost:8000/api/v1/cli/generar-aleatorio"

# Discado com CLI aleatorio
curl -X POST "http://localhost:8000/api/v1/discado/iniciar-llamada" \
  -H "Content-Type: application/json" \
  -d '{
    "numero_destino": "+5491112345678",
    "usuario_id": "test_user"
  }'
```

---

## 🛡️ Características de Segurança

### Validações

- ✅ **Formato de número**: Valida formato argentino
- ✅ **CLIs únicos**: Evita duplicação de CLIs
- ✅ **CLIs ativos**: Apenas CLIs ativos são selecionados
- ✅ **Fallback**: CLI de emergência se nenhum disponível

### Manejo de Erros

- **Nenhum CLI disponível**: Retorna erro específico
- **CLI inválido**: Validação de formato
- **Duplicados**: Reativação automática de CLIs inativos

---

## 🧪 Testes

### Executar Testes

```bash
# Testes unitários
python -m pytest tests/test_cli.py -v

# Teste funcional completo
python test_funcionalidade_cli.py
```

### Cobertura de Testes

- ✅ **Geração aleatória**: Com e sem filtros
- ✅ **CRUD de CLIs**: Criar, ler, atualizar, remover
- ✅ **Integração com discado**: CLIs em chamadas
- ✅ **Validações**: Números inválidos e duplicados
- ✅ **Estatísticas**: Cálculos e métricas

---

## 📈 Benefícios do Sistema

### Para Operações

- **Distribuição Automática**: CLIs são rotacionados automaticamente
- **Gestão Centralizada**: Todos os CLIs gerenciados em um só lugar
- **Monitoramento**: Estatísticas detalhadas de uso

### Para Campanhas

- **Variedade**: Diferentes CLIs para diferentes campanhas
- **Controle**: CLI específico quando necessário
- **Flexibilidade**: Ativação/desativação dinâmica

### Para Compliance

- **Rastreabilidade**: Histórico completo de uso
- **Auditoria**: Logs detalhados de seleção
- **Controle**: CLIs permitidos vs utilizados

---

## 🔮 Funcionalidades Futuras

### Planejadas

- **CLIs por Campanha**: Associar CLIs específicos a campanhas
- **Horários de Uso**: CLIs diferentes por horário do dia
- **Geolocalização**: CLIs baseados na região do destino
- **Balanceamento Inteligente**: Algoritmos avançados de distribuição

### Integrações

- **Sistemas Externos**: Import/export de CLIs
- **APIs de Terceiros**: Validação de CLIs em tempo real
- **Analytics**: Dashboard avançado de uso

---

## 📞 Suporte e Ajuda

### Logs

Os logs do sistema CLI estão disponíveis em:
- Aplicação: `/logs/app.log`
- Sistema: Console de aplicação

### Troubleshooting

**Problema**: Nenhum CLI disponível
```
Solução: Verificar se há CLIs ativos na base de dados
curl -X GET "http://localhost:8000/api/v1/cli/estadisticas"
```

**Problema**: CLI não válido
```
Solução: CLIs devem estar no formato +549XXXXXXXXXX
```

**Problema**: Discado sem CLI
```
Solução: Sistema usa CLI de fallback automaticamente
```

---

## ✅ Checklist de Implementação

- [x] **Modelo de dados** - Tabela `cli` criada
- [x] **Schemas** - Validações e DTOs implementados
- [x] **Serviço** - Lógica de negócio completa
- [x] **API** - Endpoints REST funcionais
- [x] **Integração** - Discado com CLI aleatorio
- [x] **Testes** - Cobertura completa
- [x] **Migração** - Script SQL de criação
- [x] **Documentação** - Guia completo

---

**🎉 Sistema CLI Aleatorio implementado com sucesso!**

*Data: Dezembro 2024*  
*Versão: 1.0*  
*Status: ✅ Completo e Funcional* 