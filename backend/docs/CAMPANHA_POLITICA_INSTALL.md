# 🏛️ **MÓDULO DE CAMPANHAS POLÍTICAS - GUIA DE INSTALAÇÃO**

## 📋 Visão Geral

Este módulo implementa funcionalidades específicas para **conformidade com legislação eleitoral** durante campanhas de chamadas automáticas e manuais, garantindo:

- ✅ **Cumprimento de horários legais** por país/região
- ✅ **Mensagens obrigatórias** no início/fim das ligações
- ✅ **Sistema de opt-out** obrigatório
- ✅ **Logs imutáveis** para auditoria
- ✅ **Calendário eleitoral** integrado
- ✅ **Exportação segura** para autoridades

---

## 🔧 **INSTALAÇÃO PASSO A PASSO**

### **1. Aplicar Migração no Banco de Dados**

Execute a migração SQL no seu banco PostgreSQL:

```bash
# Se você tem o psql instalado:
psql "postgresql://seu_usuario:sua_senha@seu_host:5432/seu_banco" -f backend/migrations/create_campanha_politica_tables.sql

# OU execute o SQL diretamente no seu client PostgreSQL favorito
```

A migração irá criar:
- ✅ **6 tabelas principais** para campanhas políticas
- ✅ **ENUMs específicos** para tipos eleitorais
- ✅ **Triggers de imutabilidade** para logs
- ✅ **Índices otimizados** para performance
- ✅ **Dados iniciais** (configurações Brasil/Espanha)

### **2. Instalar Dependências Python**

Se não existir, adicione ao `requirements.txt`:

```txt
cryptography>=3.4.8
```

E instale:

```bash
pip install cryptography
```

### **3. Verificar Instalação**

Reinicie o servidor FastAPI:

```bash
# Na pasta backend/
python main.py
```

Acesse a documentação automática:
- **Swagger UI**: `http://localhost:8000/docs`
- **Endpoints**: `http://localhost:8000/api/v1/campanha-politica/`

---

## 📡 **ENDPOINTS PRINCIPAIS**

### **Configuração Eleitoral**
```http
POST /api/v1/campanha-politica/configuracao-eleitoral
GET  /api/v1/campanha-politica/configuracao-eleitoral
```

### **Calendário Eleitoral**
```http
POST /api/v1/campanha-politica/calendario-eleitoral
GET  /api/v1/campanha-politica/calendario-eleitoral
```

### **Campanhas Políticas**
```http
POST /api/v1/campanha-politica/campanhas
GET  /api/v1/campanha-politica/campanhas
```

### **Validações de Conformidade**
```http
POST /api/v1/campanha-politica/validar-horario
POST /api/v1/campanha-politica/validar-periodo/{campanha_id}
GET  /api/v1/campanha-politica/pode-ligar/{campanha_id}
```

### **Logs Eleitorais Imutáveis**
```http
POST /api/v1/campanha-politica/logs-eleitorais
GET  /api/v1/campanha-politica/logs-eleitorais/{campanha_id}
```

---

## 🔐 **FUNCIONALIDADES DE SEGURANÇA**

### **1. Logs Imutáveis**
- **Hash SHA-256** de cada registro
- **Cadeia de blocos** (blockchain-like)
- **Triggers** que impedem alterações
- **UUID únicos** para rastreabilidade

### **2. Validações Automáticas**
- **Horários legais** por país
- **Períodos eleitorais** válidos
- **Silêncio eleitoral** automático
- **Opt-out obrigatório**

### **3. Auditoria Completa**
- **Exportação criptografada** para autoridades
- **Assinatura digital** dos arquivos
- **Rastro completo** de todas as operações
- **Timestamps** em UTC e local

---

## 📊 **EXEMPLO DE USO**

### **1. Configurar País (Brasil)**
```python
import requests

# Já criado automaticamente pela migração
config_brasil = {
    "pais_codigo": "BR",
    "pais_nome": "Brasil", 
    "horario_inicio_permitido": "08:00",
    "horario_fim_permitido": "22:00",
    "dias_semana_permitidos": [0,1,2,3,4,5,6],
    "mensagem_inicial_obrigatoria": "Esta é uma chamada de conteúdo eleitoral...",
    "mensagem_opt_out_obrigatoria": "Para não receber mais chamadas..."
}
```

### **2. Criar Calendário Eleitoral**
```python
calendario = {
    "pais_codigo": "BR",
    "tipo_eleicao": "municipal",
    "nome_eleicao": "Eleições Municipais 2024",
    "data_inicio_campanha": "2024-08-16T00:00:00Z",
    "data_fim_campanha": "2024-10-05T23:59:59Z", 
    "data_eleicao": "2024-10-06T00:00:00Z",
    "orgao_responsavel": "Tribunal Superior Eleitoral"
}

response = requests.post("http://localhost:8000/api/v1/campanha-politica/calendario-eleitoral", json=calendario)
```

### **3. Criar Campanha Política**
```python
campanha = {
    "campanha_base_id": 1,  # ID de campanha existente
    "candidato_nome": "João da Silva",
    "candidato_numero": "123",
    "partido_sigla": "PART",
    "partido_nome": "Partido Exemplo",
    "cargo_candidatura": "Prefeito",
    "configuracao_eleitoral_id": 1,
    "calendario_eleitoral_id": 1
}

response = requests.post("http://localhost:8000/api/v1/campanha-politica/campanhas", json=campanha)
```

### **4. Validar Antes de Ligar**
```python
# Verificar se pode realizar ligação
response = requests.get(
    f"http://localhost:8000/api/v1/campanha-politica/pode-ligar/{campanha_id}",
    params={"numero_destino": "+5511999999999"}
)

if response.json()["pode_ligar"]:
    # Realizar ligação
    pass
else:
    print("Bloqueado:", response.json()["motivos_bloqueio"])
```

### **5. Registrar Log de Ligação**
```python
log_data = {
    "campanha_politica_id": 1,
    "numero_destino": "+5511999999999",
    "numero_cli_usado": "+5511888888888",
    "timestamp_local": "2024-10-01T14:30:00",
    "timezone_local": "America/Sao_Paulo",
    "tipo_log": "ligacao_iniciada",
    "descricao_evento": "Ligação iniciada automaticamente",
    "dentro_horario_legal": True,
    "endereco_ip_servidor": "192.168.1.100",
    "versao_sistema": "1.0.0"
}

response = requests.post("http://localhost:8000/api/v1/campanha-politica/logs-eleitorais", json=log_data)
```

---

## ⚖️ **CONFORMIDADE LEGAL**

### **Horários Permitidos**
- **Brasil**: 08:00 às 22:00, todos os dias
- **Espanha**: 09:00 às 21:00, segunda a sexta

### **Mensagens Obrigatórias**
- **Início**: Identificação de conteúdo eleitoral
- **Opt-out**: Instrução para remoção da lista

### **Períodos Eleitorais**
- **Campanha**: Só durante período oficial
- **Silêncio**: Bloqueio automático antes da eleição

### **Logs Auditáveis**
- **Imutáveis**: Não podem ser alterados
- **Assinados**: Hash SHA-256 único
- **Rastreáveis**: UUID para cada evento

---

## 🚨 **IMPORTANTE**

1. **Configure corretamente** os horários por país
2. **Aplique a migração** antes de usar
3. **Teste as validações** antes de produção
4. **Monitore os logs** regularmente
5. **Exporte dados** conforme solicitado por autoridades

---

## 🛠️ **TROUBLESHOOTING**

### Erro: "Tabela não existe"
```bash
# Execute a migração novamente
psql -f backend/migrations/create_campanha_politica_tables.sql
```

### Erro: "Logs imutáveis"
```
# Normal! Logs não podem ser alterados por design
```

### Erro: "Fora do horário legal"
```python
# Verifique a configuração do país
GET /api/v1/campanha-politica/configuracao-eleitoral?pais_codigo=BR
```

---

## 📞 **SUPORTE**

Para dúvidas sobre conformidade eleitoral:
- 📧 Consulte a legislação local
- 🏛️ Entre em contato com órgãos eleitorais
- 📋 Mantenha logs para auditoria

**⚖️ RESPONSABILIDADE**: Este sistema auxilia na conformidade, mas a responsabilidade legal final é do usuário. 