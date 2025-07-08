# Sistema CODE2BASE Avançado 🚀

Sistema inteligente para seleção automática de CLIs (Caller IDs) baseado em critérios geográficos, operadoras, qualidade e regras de negócio configuráveis.

## 📋 Índice

1. [Descrição](#descrição)
2. [Características](#características)
3. [Instalação](#instalação)
4. [Configuração](#configuração)
5. [Uso Básico](#uso-básico)
6. [API Endpoints](#api-endpoints)
7. [Algoritmos de Seleção](#algoritmos-de-seleção)
8. [Estrutura de Dados](#estrutura-de-dados)
9. [Integração](#integração)
10. [Troubleshooting](#troubleshooting)

## 🎯 Descrição

O **Sistema CODE2BASE** é uma solução avançada que automatiza a seleção de Caller IDs (CLIs) para chamadas saintes em sistemas de telecomunicações. O sistema analisa o número de destino e seleciona automaticamente o CLI mais apropriado baseado em:

- **Geografia**: Correspondência de prefixos e áreas geográficas
- **Operadoras**: Compatibilidade entre operadoras
- **Qualidade**: Histórico de sucesso e qualidade dos CLIs
- **Regras de Negócio**: Regras personalizáveis por campanha ou contexto
- **Aprendizado**: Sistema que aprende com resultados de chamadas

## ✨ Características

### Funcionalidades Principais

- 🌍 **Seleção Geográfica Inteligente**: Escolhe CLIs da mesma área geográfica do destino
- 📊 **Múltiplos Algoritmos**: weighted_score, highest_score, weighted_random
- 🔄 **Aprendizado Automático**: Melhora seleções baseado em resultados
- ⚙️ **Regras Configuráveis**: Sistema flexível de regras de negócio
- 📈 **Estatísticas Detalhadas**: Relatórios completos de performance
- 🔍 **Análise de Destino**: Pré-análise de compatibilidade
- 🚀 **Alta Performance**: Índices otimizados para seleção rápida

### Algoritmos Disponíveis

1. **weighted_score**: Combina geografia, qualidade e uso recente (padrão)
2. **highest_score**: Seleciona sempre o CLI com maior pontuação
3. **weighted_random**: Seleção ponderada aleatória para distribuição equilibrada

## 🛠️ Instalação

### 1. Executar Script de Instalação

```bash
# Navegar para o diretório do backend
cd backend

# Executar instalação automática
python -m app.scripts.setup_code2base
```

### 2. Instalação Manual

Se preferir instalação manual:

```bash
# 1. Aplicar migração SQL
psql "sua_string_de_conexao" -f backend/migrations/create_code2base_tables.sql

# 2. Configurar regras padrão via Python
python -c "
import asyncio
from app.services.code2base_rules_service import Code2BaseRulesService
from app.database import get_db

async def setup():
    async for db in get_db():
        service = Code2BaseRulesService(db)
        await service.criar_regras_padrao()

asyncio.run(setup())
"
```

## ⚙️ Configuração

### 1. Configuração Geográfica

```python
# Adicionar países, estados e cidades
POST /api/v1/code2base/geografia/paises
{
    "codigo": "BR",
    "nome": "Brasil", 
    "codigo_telefone": "+55"
}

POST /api/v1/code2base/geografia/estados  
{
    "codigo": "SP",
    "nome": "São Paulo",
    "pais_id": 1
}

POST /api/v1/code2base/geografia/cidades
{
    "nome": "São Paulo",
    "codigo_postal": "01000",
    "estado_id": 1  
}
```

### 2. Configurar Prefixos

```python
POST /api/v1/code2base/geografia/prefijos
{
    "codigo": "11",
    "tipo_numero": "fijo",
    "operadora": "vivo",
    "pais_id": 1,
    "estado_id": 1,
    "descripcion": "São Paulo - Fixo"
}
```

### 3. Sincronizar CLIs Existentes

```python
POST /api/v1/code2base/clis-geo/sincronizar
# Sincroniza automaticamente CLIs existentes com dados geográficos
```

## 🚀 Uso Básico

### Seleção Inteligente de CLI

```python
# Endpoint principal - seleção automática
POST /api/v1/code2base/seleccionar-cli
{
    "numero_destino": "+5511987654321",
    "campaña_id": 123,                    # Opcional
    "algoritmo": "weighted_score",        # Opcional (padrão)
    "excluir_clis": [456, 789]           # Opcional
}

# Resposta
{
    "cli_seleccionado": {
        "cli_id": 123,
        "numero": "+551134567890",
        "score": 0.9543,
        "motivo_seleccion": "Mesma área geográfica + alta qualidade"
    },
    "algoritmo_usado": "weighted_score",
    "tiempo_seleccion_ms": 15,
    "total_candidatos": 5
}
```

### Análise de Destino

```python
# Analisar destino antes da chamada
POST /api/v1/code2base/analizar-destino
{
    "numero_destino": "+5511987654321"
}

# Resposta
{
    "numero_normalizado": "5511987654321", 
    "prefijo_detectado": "11",
    "informacion_geografica": {
        "pais": "Brasil",
        "estado": "São Paulo", 
        "ciudad": "São Paulo"
    },
    "clis_compatibles": [
        {
            "cli_id": 123,
            "numero": "+551134567890",
            "score_compatibilidad": 0.95,
            "motivo": "Mesma área geográfica"
        }
    ],
    "total_compatibles": 8
}
```

### Feedback de Resultado

```python
# Informar resultado da chamada para aprendizado
POST /api/v1/code2base/atualizar-resultado-llamada
{
    "historial_id": 456,          # ID do histórico de seleção
    "llamada_exitosa": true,
    "duracion_segundos": 120
}
```

## 📊 API Endpoints

### Seleção e Análise

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/seleccionar-cli` | POST | Seleção inteligente de CLI |
| `/analizar-destino` | POST | Análise de destino |
| `/atualizar-resultado-llamada` | POST | Feedback de resultado |

### Gestão Geográfica

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/geografia/paises` | GET/POST | Gestão de países |
| `/geografia/estados` | GET/POST | Gestão de estados |
| `/geografia/cidades` | GET/POST | Gestão de cidades |
| `/geografia/prefijos` | GET/POST | Gestão de prefixos |

### CLIs Geográficos

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/clis-geo` | GET/POST | Gestão de CLIs geográficos |
| `/clis-geo/sincronizar` | POST | Sincronização automática |
| `/clis-geo/{id}/atualizar-stats` | PUT | Atualizar estatísticas |

### Regras de Negócio

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/reglas` | GET/POST | Gestão de regras |
| `/reglas/padrao` | POST | Criar regras padrão |
| `/reglas/{id}/activar` | PUT | Ativar/desativar regra |

### Relatórios e Estatísticas

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/estadisticas` | GET | Estatísticas gerais |
| `/reportes/performance` | GET | Relatório de performance |
| `/reportes/clis-populares` | GET | CLIs mais utilizados |
| `/reportes/reglas-efetividade` | GET | Efetividade das regras |

## 🧠 Algoritmos de Seleção

### 1. weighted_score (Padrão)

Combina múltiplos fatores com pesos:

```python
score = (
    geografia_score * 0.4 +      # 40% - Compatibilidade geográfica  
    qualidade_score * 0.3 +      # 30% - Qualidade do CLI
    tasa_exito_score * 0.2 +     # 20% - Taxa de sucesso histórica
    distribuicao_score * 0.1     # 10% - Distribuição equilibrada
)
```

### 2. highest_score

Seleciona sempre o CLI com maior pontuação total, garantindo máxima qualidade.

### 3. weighted_random

Seleção ponderada aleatória baseada nos scores, promove distribuição equilibrada.

## 📁 Estrutura de Dados

### Modelos Principais

```python
# País
Pais {
    id: int
    codigo: str          # "BR", "ES", etc.
    nome: str
    codigo_telefone: str # "+55", "+34", etc.
}

# Estado/Província  
Estado {
    id: int
    codigo: str          # "SP", "RJ", "MD", etc.
    nome: str
    pais_id: int
}

# Cidade
Cidade {
    id: int 
    nome: str
    codigo_postal: str
    estado_id: int
}

# Prefixo Telefônico
Prefijo {
    id: int
    codigo: str          # "11", "21", "91", etc.
    tipo_numero: TipoNumero
    operadora: TipoOperadora
    pais_id: int
    estado_id: int
    cidade_id: int
}

# CLI Geográfico
CliGeo {
    id: int
    numero: str
    cli_id: int          # Referência ao CLI existente
    prefijo_id: int
    calidad: decimal     # 0.0 - 1.0
    tasa_exito: decimal  # 0.0 - 1.0
    veces_usado: int
}
```

### Regras Configuráveis

```python
ReglaCli {
    nome: str
    tipo_regra: TipoRegra
    condiciones: dict    # JSON configurável
    prioridad: int
    peso: decimal
    activo: bool
}

# Exemplo de condições
{
    "geografia": {
        "mismo_pais": true,
        "mismo_estado": true, 
        "mismo_prefijo": false
    },
    "operadora": {
        "misma_operadora": true,
        "operadoras_permitidas": ["movistar", "vodafone"]
    },
    "horario": {
        "horario_comercial": true,
        "fines_semana": false
    }
}
```

## 🔧 Integração

### Com Sistema de Discado Existente

```python
# No seu serviço de discado atual
from app.services.code2base_engine import Code2BaseEngine

class DiscadoService:
    def __init__(self):
        self.code2base = Code2BaseEngine()
    
    async def realizar_llamada(self, numero_destino, campaña_id=None):
        # 1. Solicitar CLI inteligente
        cli_info = await self.code2base.seleccionar_cli_inteligente(
            numero_destino=numero_destino,
            campaña_id=campaña_id
        )
        
        # 2. Fazer chamada com CLI selecionado
        resultado = await self.asterisk.originate_call(
            cli=cli_info.cli_seleccionado.numero,
            destino=numero_destino
        )
        
        # 3. Informar resultado para aprendizado
        await self.code2base.atualizar_resultado_llamada(
            historial_id=cli_info.historial_id,
            exitosa=resultado.success,
            duracion=resultado.duration
        )
```

### Com Asterisk

```python
# Exemplo de integração com AGI
from asterisk.agi import AGI

def agi_script():
    agi = AGI()
    numero_destino = agi.get_variable('NUMERO_DESTINO')
    
    # Solicitar CLI ao CODE2BASE
    cli_response = requests.post('/api/v1/code2base/seleccionar-cli', {
        'numero_destino': numero_destino
    })
    
    cli_info = cli_response.json()
    
    # Configurar CLI no canal
    agi.set_variable('CALLERID(num)', cli_info['cli_seleccionado']['numero'])
    
    # Continuar com discado...
```

## 🐛 Troubleshooting

### Problemas Comuns

#### 1. Nenhum CLI encontrado

```python
# Erro
{
    "error": "Nenhum CLI compatível encontrado",
    "codigo": "NO_CLI_AVAILABLE"
}

# Soluções
- Verificar se existem CLIs cadastrados
- Verificar regras muito restritivas
- Usar análise de destino para debug
```

#### 2. Performance lenta

```python
# Verificar índices da base de dados
SELECT schemaname, tablename, indexname 
FROM pg_indexes 
WHERE tablename LIKE 'code2base_%';

# Otimizar consulta
ANALYZE code2base_clis_geo;
REINDEX TABLE code2base_clis_geo;
```

#### 3. Regras não funcionam

```python
# Debug de regras ativas
GET /api/v1/code2base/reglas?activo=true

# Verificar logs de aplicação das regras
GET /api/v1/code2base/estadisticas/reglas-debug
```

### Logs Úteis

```python
# Ativar debug detalhado
import logging
logging.getLogger('code2base').setLevel(logging.DEBUG)

# Verificar logs de seleção
tail -f logs/code2base_selection.log
```

### Comandos de Manutenção

```bash
# Limpar histórico antigo (+ 30 dias)
python -c "
from app.services.code2base_engine import Code2BaseEngine
engine = Code2BaseEngine()
await engine.limpar_historial_antigo(dias=30)
"

# Recalcular estatísticas
python -c "
from app.services.code2base_geo_service import Code2BaseGeoService  
await geo_service.recalcular_estadisticas_todos_clis()
"

# Verificar integridade dos dados
python -m app.scripts.verificar_integridade_code2base
```

## 📞 Suporte

Para dúvidas ou problemas:

1. **Documentação da API**: `/documentacao#/code2base`
2. **Logs do Sistema**: `logs/code2base.log`
3. **Status do Sistema**: `GET /api/v1/code2base/status`
4. **Testes de Simulação**: `POST /api/v1/code2base/simular-seleccion`

---

## 📄 Licença

Sistema desenvolvido para uso interno. Todos os direitos reservados.

---

**Versão**: 1.0.0  
**Última Atualização**: 2024  
**Autor**: Sistema CODE2BASE Development Team 