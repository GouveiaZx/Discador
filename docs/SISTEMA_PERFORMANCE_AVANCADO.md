# Sistema de Performance Avançado - Guia Completo

## 📋 Índice
1. [Visão Geral](#visão-geral)
2. [Funcionalidades Implementadas](#funcionalidades-implementadas)
3. [Limites de DID por País](#limites-de-did-por-país)
4. [Configuração DTMF por País](#configuração-dtmf-por-país)
5. [Sistema de 20-30 CPS](#sistema-de-20-30-cps)
6. [Testes de Carga](#testes-de-carga)
7. [Dashboard de Monitoramento](#dashboard-de-monitoramento)
8. [API Reference](#api-reference)
9. [Configuração e Deployment](#configuração-e-deployment)

---

## 🎯 Visão Geral

O Sistema de Performance Avançado foi implementado para atender às necessidades específicas do cliente:

### ✅ **Funcionalidades Implementadas**

1. **🔢 Limites de DID por País**
   - ✅ Limite de 100 usos/dia para USA/Canadá
   - ✅ Sem limites para América Latina  
   - ✅ Reset automático diário
   - ✅ Rotação inteligente de 20,000+ DIDs

2. **📱 DTMF Específico por País**
   - ✅ "Oprimir 3" para México (vs "Oprimir 1" padrão)
   - ✅ Configuração flexível por país
   - ✅ Contextos de áudio personalizados

3. **🚀 CPS 20-30 Chamadas/Segundo**
   - ✅ Sistema de alta performance
   - ✅ Auto-ajuste inteligente
   - ✅ Emergency brake para proteção

4. **🧪 Testes de Carga Automatizados**
   - ✅ Validação de 20-30 CPS
   - ✅ Relatórios detalhados
   - ✅ Monitoramento em tempo real

5. **📊 Dashboard Avançado**
   - ✅ Métricas em tempo real
   - ✅ Gráficos interativos
   - ✅ Alertas automáticos

---

## 🌍 Limites de DID por País

### **Como Funciona**

O sistema implementa controles específicos por país para cumprir regulamentações locais:

```python
# Limites configurados
COUNTRY_DAILY_LIMITS = {
    'usa': 100,      # Máximo 100 usos por dia
    'canada': 100,   # Máximo 100 usos por dia
    'mexico': 0,     # Sem limite
    'brasil': 0,     # Sem limite
    'colombia': 0,   # Sem limite
    'argentina': 0,  # Sem limite
    # ... outros países
}
```

### **Funcionalidades**

1. **Detecção Automática de País**
   - Analisa o número de destino
   - Aplica limite específico do país
   - Seleciona DID apropriado

2. **Rotação Inteligente**
   - Prioriza DIDs menos usados
   - Evita DIDs próximos do limite
   - Suporta 20,000+ DIDs

3. **Reset Automático**
   - Reset diário às 00:00
   - Logs detalhados
   - Notificações automáticas

### **Uso via API**

```bash
# Verificar limites atuais
curl -X GET "http://localhost:8000/api/performance/cli/limits"

# Definir novo limite para um país
curl -X POST "http://localhost:8000/api/performance/cli/limits/usa" \
  -H "Content-Type: application/json" \
  -d '{"daily_limit": 150}'

# Obter estatísticas de uso
curl -X GET "http://localhost:8000/api/performance/cli/usage"
```

---

## 📞 Configuração DTMF por País

### **Problema Resolvido**

Como solicitado pelo cliente: *"en los contextos por ejemplo yo necesito por ejemplo cuando llamo a Mexico y uso oprimir 1 me trasnfiere mucha contestadora por lo tanto tengo que usar oprimir el 3"*

### **Configurações por País**

```python
COUNTRY_DTMF_CONFIG = {
    'usa': {
        'connect_key': '1',
        'instructions': 'Press 1 to connect, 9 to be removed from list'
    },
    'mexico': {
        'connect_key': '3',  # ESPECIAL: México usa tecla 3
        'instructions': 'Presione 3 para conectar, 9 para salir de la lista'
    },
    'brasil': {
        'connect_key': '1',
        'instructions': 'Pressione 1 para conectar, 9 para sair da lista'
    }
    # ... outros países
}
```

### **Funcionalidades**

1. **Teclas Personalizadas**
   - Conectar: 1 (padrão) ou 3 (México)
   - Desconectar: 9 (universal)
   - Repetir: 0 (universal)

2. **Áudios Localizados**
   - Instruções em idioma local
   - Contextos específicos por país
   - Suporte a múltiplos formatos

3. **Detecção Automática**
   - Identifica país pelo número
   - Aplica configuração apropriada
   - Cria contexto dinamicamente

### **Uso via API**

```bash
# Obter configurações atuais
curl -X GET "http://localhost:8000/api/performance/dtmf/config"

# Atualizar configuração do México
curl -X POST "http://localhost:8000/api/performance/dtmf/config/mexico" \
  -H "Content-Type: application/json" \
  -d '{
    "connect_key": "3",
    "disconnect_key": "9",
    "instructions": "Presione 3 para conectar, 9 para salir"
  }'
```

---

## 🚀 Sistema de 20-30 CPS

### **Arquitetura de Alta Performance**

O sistema foi projetado para suportar 20-30 chamadas por segundo conforme solicitado:

```python
class HighPerformanceDialer:
    def __init__(self):
        self.max_cps = 30.0
        self.thread_pool_size = 100
        self.max_concurrent_calls = 1000
        self.auto_adjust_cps = True
```

### **Funcionalidades Principais**

1. **Auto-Ajuste Inteligente**
   - Monitora taxa de sucesso
   - Ajusta CPS automaticamente
   - Evita sobrecarga do sistema

2. **Emergency Brake**
   - Ativa quando taxa de sucesso < 10%
   - Protege contra blacklisting
   - Alerta automático

3. **Monitoramento em Tempo Real**
   - Métricas de performance
   - Gráficos ao vivo
   - Alertas proativos

### **Configuração**

```python
# Configuração de performance
performance_config = {
    "max_cps": 30.0,
    "initial_cps": 5.0,
    "ramp_up_step": 2.0,
    "ramp_up_interval": 10,
    "max_concurrent_calls": 1000,
    "auto_adjust_cps": True,
    "emergency_brake_threshold": 0.1,
    "quality_threshold": 0.8
}
```

### **Uso via API**

```bash
# Iniciar sistema de discado
curl -X POST "http://localhost:8000/api/performance/dialer/start" \
  -H "Content-Type: application/json" \
  -d '{
    "max_cps": 30.0,
    "initial_cps": 5.0,
    "auto_adjust_cps": true
  }'

# Definir CPS manualmente
curl -X POST "http://localhost:8000/api/performance/dialer/cps/25"

# Obter métricas em tempo real
curl -X GET "http://localhost:8000/api/performance/metrics/realtime"
```

---

## 🧪 Testes de Carga

### **Validação de Performance**

Como solicitado: *"necesito probar todo la creacion de contextos audios reconocimiento de voces y el rendimiento cuando le ponga 20 o 30 llamadas por segundo"*

### **Tipos de Teste**

1. **Teste de CPS**
   - Valida 20-30 CPS
   - Monitora taxa de sucesso
   - Mede latência

2. **Teste de Contextos**
   - Testa criação de contextos
   - Valida DTMF por país
   - Verifica áudios

3. **Teste de Reconhecimento**
   - AMD (Answering Machine Detection)
   - Detecção de teclas DTMF
   - Classificação de resultados

### **Configuração de Teste**

```json
{
  "target_cps": 25.0,
  "duration_minutes": 10,
  "countries_to_test": ["usa", "mexico", "brasil", "colombia"],
  "number_of_clis": 1000,
  "test_scenarios": [
    "cps_validation",
    "context_creation",
    "dtmf_recognition",
    "amd_detection"
  ]
}
```

### **Uso via API**

```bash
# Iniciar teste de carga
curl -X POST "http://localhost:8000/api/performance/load-test/start" \
  -H "Content-Type: application/json" \
  -d '{
    "target_cps": 25.0,
    "duration_minutes": 10,
    "countries_to_test": ["usa", "mexico", "brasil"]
  }'

# Monitorar status
curl -X GET "http://localhost:8000/api/performance/load-test/status"

# Obter resultados
curl -X GET "http://localhost:8000/api/performance/load-test/results?format=json"
```

### **Exemplo de Relatório**

```
RELATÓRIO DE TESTE DE CARGA
===========================

Teste ID: 12345-abcde-67890
Data/Hora: 2024-01-15 10:00:00 - 2024-01-15 10:10:00
Duração: 10 minutos

CONFIGURAÇÃO
------------
CPS Alvo: 25.0
Países: USA, México, Brasil, Colômbia
CLIs: 1000

RESULTADOS GERAIS
-----------------
Chamadas Tentadas: 15,000
Chamadas Bem-sucedidas: 13,500
Chamadas Falhadas: 1,500
Taxa de Sucesso: 90.00%

PERFORMANCE
-----------
CPS Médio: 24.8
CPS Máximo: 29.2
Tempo Médio Setup: 0.245s
Chamadas Concorrentes Máx: 742

ESTATÍSTICAS POR PAÍS
--------------------
USA: 3,750 chamadas, 88.5% sucesso
MEXICO: 3,750 chamadas, 92.1% sucesso (DTMF tecla 3)
BRASIL: 3,750 chamadas, 90.8% sucesso
COLOMBIA: 3,750 chamadas, 89.2% sucesso
```

---

## 📊 Dashboard de Monitoramento

### **Interface Avançada**

Dashboard em tempo real com:

1. **Métricas Principais**
   - CPS atual vs alvo
   - Taxa de sucesso
   - Chamadas concorrentes
   - Carga do sistema

2. **Gráficos Interativos**
   - Linha temporal de CPS
   - Distribuição por país
   - Uso de CLIs
   - Tendências de performance

3. **Alertas Automáticos**
   - Emergency brake ativo
   - Limite de DID excedido
   - Queda de performance

### **Acesso**

```bash
# Frontend
http://localhost:3000/dashboard/performance

# WebSocket para tempo real
ws://localhost:8000/api/performance/ws/performance
```

### **Funcionalidades**

1. **Monitoramento Real-time**
   - Atualização a cada segundo
   - Gráficos animados
   - Alertas visuais

2. **Controle de Testes**
   - Iniciar/parar testes
   - Configurar parâmetros
   - Visualizar resultados

3. **Análise de CLIs**
   - Estatísticas de uso
   - Identificação de bloqueios
   - Otimização automática

---

## 🔧 API Reference

### **Endpoints Principais**

#### **Performance**
- `GET /api/performance/metrics/realtime` - Métricas em tempo real
- `GET /api/performance/metrics/history` - Histórico de métricas
- `POST /api/performance/dialer/start` - Iniciar discador
- `POST /api/performance/dialer/stop` - Parar discador
- `POST /api/performance/dialer/cps/{cps}` - Definir CPS

#### **Testes de Carga**
- `POST /api/performance/load-test/start` - Iniciar teste
- `POST /api/performance/load-test/stop` - Parar teste
- `GET /api/performance/load-test/status` - Status do teste
- `GET /api/performance/load-test/results` - Resultados

#### **CLIs e Países**
- `GET /api/performance/cli/limits` - Limites por país
- `POST /api/performance/cli/limits/{country}` - Definir limite
- `GET /api/performance/cli/usage` - Estatísticas de uso
- `POST /api/performance/cli/reset` - Reset diário

#### **DTMF**
- `GET /api/performance/dtmf/config` - Configurações DTMF
- `POST /api/performance/dtmf/config/{country}` - Atualizar config

#### **WebSocket**
- `WS /api/performance/ws/performance` - Métricas em tempo real

### **Autenticação**

```bash
# Todas as APIs requerem autenticação
curl -X GET "http://localhost:8000/api/performance/metrics/realtime" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## ⚙️ Configuração e Deployment

### **Requisitos**

1. **Python 3.8+**
2. **Node.js 16+**
3. **SQLite/PostgreSQL**
4. **Redis (opcional)**

### **Instalação**

```bash
# Backend
cd backend
pip install -r requirements.txt

# Executar migração
python run_migration.py

# Iniciar servidor
python main.py

# Frontend
cd frontend
npm install
npm run dev
```

### **Configuração**

```env
# .env
DATABASE_URL=sqlite:///discador.db
REDIS_URL=redis://localhost:6379
LOG_LEVEL=INFO
MAX_CPS=30.0
ENABLE_PERFORMANCE_MONITORING=true
```

### **Deployment**

```bash
# Produção
docker-compose up -d

# ou
pm2 start ecosystem.config.js
```

---

## 📈 Métricas de Performance

### **KPIs Principais**

1. **CPS (Calls Per Second)**
   - Alvo: 20-30 CPS
   - Atual: Monitorado em tempo real
   - Eficiência: % do alvo alcançado

2. **Taxa de Sucesso**
   - Alvo: > 80%
   - Por país: Variável
   - Tendência: Monitorada

3. **Tempo de Setup**
   - Média: < 300ms
   - P95: < 500ms
   - P99: < 1000ms

4. **Uso de CLIs**
   - USA/Canadá: < 100/dia
   - América Latina: Ilimitado
   - Rotação: Balanceada

### **Alertas Configurados**

1. **Emergency Brake**
   - Trigger: Taxa de sucesso < 10%
   - Ação: Parar discado
   - Notificação: Imediata

2. **Limite de DID**
   - Trigger: CLI próximo do limite
   - Ação: Rotacionar para outro CLI
   - Notificação: Log

3. **Performance Degradada**
   - Trigger: CPS < 70% do alvo
   - Ação: Investigar causa
   - Notificação: Dashboard

---

## 🎯 Cenários de Uso

### **1. Campanha USA/Canadá**

```python
# Configuração automática
config = {
    "target_country": "usa",
    "cli_limit": 100,
    "dtmf_connect_key": "1",
    "max_cps": 25.0,
    "auto_rotate_clis": True
}
```

### **2. Campanha México**

```python
# Configuração especial
config = {
    "target_country": "mexico", 
    "cli_limit": 0,  # Sem limite
    "dtmf_connect_key": "3",  # Tecla 3 ao invés de 1
    "max_cps": 30.0,
    "context_suffix": "_mexico"
}
```

### **3. Teste de Carga**

```python
# Validação de performance
test_config = {
    "target_cps": 25.0,
    "duration_minutes": 15,
    "countries": ["usa", "mexico", "brasil"],
    "validate_dtmf": True,
    "validate_amd": True
}
```

---

## 🔍 Troubleshooting

### **Problemas Comuns**

1. **CPS Baixo**
   - Verificar limites de CLI
   - Checar qualidade dos números
   - Analisar performance do Asterisk

2. **Emergency Brake Ativo**
   - Verificar qualidade da lista
   - Checar configurações DTMF
   - Analisar logs detalhados

3. **CLIs Bloqueados**
   - Verificar limites por país
   - Checar reset diário
   - Analisar histórico de uso

### **Logs Importantes**

```bash
# Logs de performance
tail -f logs/performance.log

# Logs de CLI
tail -f logs/cli_manager.log

# Logs de testes
tail -f logs/load_test.log
```

---

## 📞 Suporte

Para dúvidas ou problemas:

1. **Logs**: Verificar arquivos de log
2. **Dashboard**: Monitorar métricas
3. **API**: Usar endpoints de health check
4. **Documentação**: Consultar este guia

---

## 🚀 Próximos Passos

### **Funcionalidades Futuras**

1. **IA Preditiva**
   - Predição de melhores horários
   - Otimização automática de CLIs
   - Análise de padrões

2. **Integração Cloud**
   - AWS/GCP deployment
   - Escalabilidade automática
   - Backup automático

3. **Análise Avançada**
   - Machine Learning para AMD
   - Análise de sentimentos
   - Otimização de conversão

---

**✅ SISTEMA PRONTO PARA PRODUÇÃO**

Todas as funcionalidades solicitadas foram implementadas e testadas. O sistema está pronto para validação com 20-30 CPS e suporte completo a limites por país e DTMF customizado. 