# 📞 Sistema "Presione 1" - Guia Completo

## 🎯 O que é o Sistema "Presione 1"?

O sistema **"Presione 1"** é um discador automático inteligente que:

1. **Liga automaticamente** para números de uma lista
2. **Reproduz uma mensagem de áudio** quando alguém atende
3. **Aguarda que a pessoa pressione a tecla "1"** para demonstrar interesse
4. **Transfere automaticamente** para um agente se pressionar "1"
5. **Encerra a chamada** se não pressionar ou pressionar outra tecla

## 🔄 Como Funciona o Fluxo

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Liga para     │───▶│   Pessoa        │───▶│   Reproduz      │
│ próximo número  │    │   atende?       │    │     áudio       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                │ NÃO                    │
                                ▼                        ▼
                    ┌─────────────────┐    ┌─────────────────┐
                    │   Caixa postal  │    │   Aguarda       │
                    │   ou ocupado    │    │   tecla "1"     │
                    └─────────────────┘    └─────────────────┘
                                │                        │
                                │                        │
                                ▼                        ▼
                    ┌─────────────────┐    ┌─────────────────┐
                    │   Finaliza      │    │   Pressionou    │
                    │   chamada       │    │     "1"?        │
                    └─────────────────┘    └─────────────────┘
                                                    │
                                                    │
                                    ┌───────────────┼───────────────┐
                                    │ SIM           │ NÃO           │
                                    ▼               ▼               ▼
                        ┌─────────────────┐    ┌─────────────────┐
                        │   Transfere     │    │   Finaliza      │
                        │   para agente   │    │   chamada       │
                        └─────────────────┘    └─────────────────┘
```

## 📋 Passos para Usar o Sistema

### 1. **Criar uma Campanha**
- Vá para **Campanhas** no menu lateral
- Clique em **"Nueva Campaña"**
- Preencha os dados:
  - Nome da campanha
  - Número CLI (que aparece para quem recebe)
  - Quantas chamadas simultâneas
  - Tentativas máximas

### 2. **Adicionar Contatos**
- Vá para **Listas** no menu lateral
- Faça upload de um arquivo CSV com os números
- Associe a lista à campanha

### 3. **Configurar Áudio**
- Defina a mensagem que será reproduzida
- Exemplo: *"Olá! Você tem interesse em nossos produtos? Pressione 1 para falar com um atendente."*

### 4. **Iniciar a Campanha**
- Volte para **Campanhas**
- Clique no botão verde **"Iniciar"**
- A campanha ficará **ATIVA** (verde)

### 5. **Monitorar em Tempo Real**
- Vá para **Monitoreo** no menu lateral
- Veja as campanhas ativas e métricas
- Acompanhe as chamadas em andamento

## 🖥️ Telas do Sistema

### 🏠 **Tela Principal - Campanhas**
- Lista todas as campanhas criadas
- Mostra status: **Borrador**, **Activa**, **Pausada**
- Botões de ação: **Iniciar**, **Pausar**, **Parar**, **Editar**

### 📊 **Tela de Monitoramento**
- Métricas em tempo real:
  - **Total de chamadas realizadas**
  - **Chamadas atendidas**
  - **Pessoas que pressionaram "1"**
  - **Transferências realizadas**
- Taxas de conversão
- Lista de campanhas ativas

### 📞 **Tela de Atendimento (Para Agentes)**
- Recebe as chamadas transferidas
- Mostra dados do contato
- Permite conversar com quem pressionou "1"

## 🎛️ Controles da Campanha

### ▶️ **Iniciar**
- Começa o discado automático
- Status muda para **ATIVA** (verde)
- Sistema liga para os números da lista

### ⏸️ **Pausar**
- Para o discado de novos números
- Chamadas em andamento continuam
- Status muda para **PAUSADA** (amarelo)
- Pode ser retomada a qualquer momento

### ⏹️ **Parar**
- Para completamente a campanha
- Finaliza todas as chamadas ativas
- Status muda para **PARADA** (cinza)
- Precisa ser iniciada novamente

### 🔄 **Retomar**
- Continua uma campanha pausada
- Status volta para **ATIVA** (verde)
- Retoma o discado automático

## 📈 Métricas Importantes

### **Taxa de Atendimento**
```
Taxa = (Chamadas Atendidas / Chamadas Realizadas) × 100
```
- Mostra quantas pessoas atenderam o telefone
- Ideal: acima de 30%

### **Taxa de Interesse (Presione 1)**
```
Taxa = (Pressionaram 1 / Chamadas Atendidas) × 100
```
- Mostra quantas pessoas demonstraram interesse
- Ideal: acima de 10%

### **Taxa de Transferência**
```
Taxa = (Transferências Realizadas / Pressionaram 1) × 100
```
- Mostra quantas transferências foram bem-sucedidas
- Ideal: acima de 90%

## 🔧 Sincronização entre Telas

### **Todas as telas são sincronizadas automaticamente:**

1. **Campanhas** ↔️ **Monitoreo**
   - Quando inicia uma campanha, aparece no monitoramento
   - Quando pausa, o status muda em ambas as telas

2. **Atualização Automática**
   - Métricas atualizadas a cada 3 segundos
   - Status das campanhas sincronizado
   - Não precisa recarregar a página

3. **Estados em Tempo Real**
   - ✅ **Activa**: Discando números
   - ⏸️ **Pausada**: Parada temporariamente
   - ⏹️ **Parada**: Finalizada
   - 📝 **Borrador**: Não iniciada

## 🎧 Para Agentes (Quem Atende)

### **O que acontece quando alguém pressiona "1":**

1. **Transferência Automática**
   - Chamada é transferida para fila de agentes
   - Agente recebe notificação de chamada

2. **Informações Disponíveis**
   - Número que pressionou "1"
   - Campanha de origem
   - Horário da chamada

3. **Próximos Passos**
   - Agente conversa com o interessado
   - Pode agendar, vender ou qualificar o lead

## 🚨 Resolução de Problemas

### **Campanha não inicia:**
- ✅ Verifique se há contatos na lista
- ✅ Confirme se a campanha tem um número CLI
- ✅ Verifique se não há erros na configuração

### **Não aparece no monitoramento:**
- ✅ Campanha deve estar **ATIVA**
- ✅ Aguarde alguns segundos para sincronização
- ✅ Recarregue a página se necessário

### **Não recebe chamadas transferidas:**
- ✅ Verifique configuração do agente
- ✅ Confirme se está logado no sistema
- ✅ Teste com número conhecido

## 📞 Exemplo Prático

### **Cenário: Campanha de Vendas**

1. **Preparação:**
   - Lista com 1000 números
   - Mensagem: "Olá! Temos uma oferta especial. Pressione 1 para saber mais."
   - 3 chamadas simultâneas

2. **Execução:**
   - Inicia campanha às 9h
   - Sistema liga para 3 números por vez
   - Quando alguém atende, reproduz o áudio
   - Se pressiona "1", transfere para vendedor

3. **Resultados Esperados:**
   - 1000 chamadas realizadas
   - 300 atendidas (30% taxa atendimento)
   - 30 pressionaram "1" (10% taxa interesse)
   - 27 transferências realizadas (90% taxa transferência)

## 🎯 Dicas de Sucesso

### **Para Melhorar Taxa de Atendimento:**
- ⏰ Ligue em horários adequados (9h-18h)
- 📱 Use números locais como CLI
- 🔄 Evite ligar múltiplas vezes no mesmo dia

### **Para Melhorar Taxa de Interesse:**
- 🎵 Mensagem clara e direta
- ⏱️ Não muito longa (máximo 15 segundos)
- 🎯 Oferta atrativa e específica

### **Para Melhorar Transferências:**
- 👥 Agentes treinados e preparados
- ⚡ Transferência rápida (máximo 3 segundos)
- 📋 Script de atendimento definido

---

## 🆘 Precisa de Ajuda?

Se tiver dúvidas sobre qualquer parte do sistema, consulte:

1. **Este guia** - Explica como usar cada funcionalidade
2. **Tela de monitoramento** - Mostra métricas em tempo real
3. **Logs do sistema** - Para problemas técnicos
4. **Suporte técnico** - Para configurações avançadas

**Lembre-se:** O sistema é automático, mas precisa de configuração inicial correta para funcionar bem! 🚀 