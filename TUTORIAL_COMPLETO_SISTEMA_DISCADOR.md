# 📞 Tutorial Completo - Sistema Discador Predictivo
*Guía Completa en Español (Argentina) y Português (Brasil)*

---

## 🚀 **Índice / Índice**

### **Español (Argentina)**
1. [Introducción y Características](#introducción-y-características)
2. [Instalación y Configuración Inicial](#instalación-y-configuración-inicial)
3. [Acceso al Sistema](#acceso-al-sistema)
4. [Gestión de Campañas](#gestión-de-campañas)
5. [Gestión de Listas de Contactos](#gestión-de-listas-de-contactos)
6. [Lista Negra (Blacklist)](#lista-negra-blacklist)
7. [Configuración Avanzada Multi-SIP](#configuración-avanzada-multi-sip)
8. [Monitoreo en Tiempo Real](#monitoreo-en-tiempo-real)
9. [Histórico de Llamadas](#histórico-de-llamadas)
10. [Resolución de Problemas](#resolución-de-problemas)

### **Português (Brasil)**
1. [Introdução e Características](#introdução-e-características)
2. [Instalação e Configuração Inicial](#instalação-e-configuração-inicial-br)
3. [Acesso ao Sistema](#acesso-ao-sistema)
4. [Gestão de Campanhas](#gestão-de-campanhas-br)
5. [Gestão de Listas de Contatos](#gestão-de-listas-de-contatos)
6. [Lista Negra (Blacklist)](#lista-negra-blacklist-br)
7. [Configuração Avançada Multi-SIP](#configuração-avançada-multi-sip-br)
8. [Monitoramento em Tempo Real](#monitoramento-em-tempo-real)
9. [Histórico de Chamadas](#histórico-de-chamadas-br)
10. [Solução de Problemas](#solução-de-problemas)

---

# 🇦🇷 **ESPAÑOL (ARGENTINA)**

## **Introducción y Características**

El Sistema Discador Predictivo es una solución completa para centros de llamadas que permite:

### ✨ **Características Principales**
- **Discado Predictivo Inteligente**: Optimiza automáticamente la cantidad de llamadas simultáneas
- **Gestión de Campañas**: Crea y administra múltiples campañas de llamadas
- **Multi-SIP**: Soporte para múltiples proveedores SIP
- **Lista Negra Avanzada**: Filtrado automático de números no deseados
- **Monitoreo en Tiempo Real**: Dashboard con métricas en vivo
- **Histórico Completo**: Reportes detallados de todas las llamadas
- **Interfaz Moderna**: Dashboard profesional y fácil de usar

---

## **Instalación y Configuración Inicial**

### **Requisitos del Sistema**
- **Sistema Operativo**: Windows 10/11, Linux Ubuntu 18+, macOS 10.14+
- **Python**: 3.8 o superior
- **Node.js**: 16.0 o superior
- **Memoria RAM**: Mínimo 4GB (Recomendado 8GB)
- **Espacio en Disco**: Mínimo 2GB

### **Paso 1: Descargar el Sistema**
```bash
# Descargar y extraer el sistema
cd C:\
git clone https://github.com/tu-repo/discador-main.git
cd discador-main
```

### **Paso 2: Instalación Automática**
```bash
# Windows PowerShell
.\install.sh

# Linux/Mac
chmod +x install.sh
./install.sh
```

### **Paso 3: Verificar Instalación**
```bash
# Verificar que todos los componentes están instalados
python validate_system.py
```

### **Paso 4: Iniciar el Sistema**
```bash
# Terminal 1: Backend Principal (Puerto 8000)
python main.py

# Terminal 2: Servicio Multi-SIP (Puerto 8001)  
python quick_fix_routes.py

# Terminal 3: Frontend React (Puerto 3001)
cd frontend
npm start
```

---

## **Acceso al Sistema**

### **URLs de Acceso**
- **Frontend Principal**: `http://localhost:3001`
- **API Backend**: `http://localhost:8000`
- **API Multi-SIP**: `http://localhost:8001`

### **Credenciales por Defecto**
- **Usuario**: `admin@discador.com`
- **Contraseña**: `admin123`

### **Primera Configuración**
1. Acceder a `http://localhost:3001`
2. Iniciar sesión con las credenciales por defecto
3. Ir a **Configuración** para personalizar el sistema
4. Cambiar la contraseña por defecto

---

## **Gestión de Campañas**

### **Crear Nueva Campaña**

1. **Navegar a Campañas**
   - Hacer clic en "📊 Campañas" en el menú lateral

2. **Crear Campaña**
   - Hacer clic en "✅ Nueva Campaña"
   - Completar los datos:
     ```
     Nombre: "Campaña Promocional Q1 2025"
     Descripción: "Promoción de productos para el primer trimestre"
     CLI (Número de origen): "+5411XXXXXXXX"
     Máx. Llamadas Simultáneas: 10
     Máx. Intentos por Contacto: 3
     Intervalo entre Intentos: 300 segundos
     ```

3. **Configuración Avanzada**
   - **Horarios de Llamada**: 09:00 - 18:00
   - **Días Laborables**: Lunes a Viernes
   - **Detección de Contestador**: Activada
   - **Grabación de Llamadas**: Opcional

### **Estados de Campaña**
- 🟢 **Activa**: Realizando llamadas
- 🟡 **Pausada**: Temporalmente detenida
- 🔴 **Detenida**: Completamente finalizada
- ⚫ **Borrador**: En configuración

### **Acciones de Campaña**
- **▶️ Iniciar**: Comenzar las llamadas
- **⏸️ Pausar**: Detener temporalmente
- **⏹️ Detener**: Finalizar completamente
- **✏️ Editar**: Modificar configuración
- **📊 Estadísticas**: Ver métricas detalladas

---

## **Gestión de Listas de Contactos**

### **Subir Lista de Contactos**

1. **Preparar Archivo CSV**
   ```csv
   nombre,telefono,email,observaciones
   Juan Pérez,+5411XXXXXXXX,juan@email.com,Cliente Premium
   María González,+5411YYYYYYYY,maria@email.com,Prospecto
   Carlos López,+5411ZZZZZZZZ,carlos@email.com,Renovación
   ```

2. **Subir Lista**
   - Ir a "📋 Listas"
   - Hacer clic en "📤 Subir Lista"
   - Seleccionar archivo CSV
   - Asignar a campaña existente
   - Verificar vista previa
   - Confirmar importación

### **Gestión de Contactos**
- **Filtros Disponibles**:
  - Por campaña
  - Por estado de llamada
  - Por fecha de última llamada
  - Por número de intentos

- **Estados de Contacto**:
  - ⏳ **Pendiente**: Sin llamar
  - 📞 **En Proceso**: Llamando ahora
  - ✅ **Contactado**: Llamada exitosa
  - ❌ **No Contactado**: Sin respuesta
  - 🚫 **Bloqueado**: En lista negra

---

## **Lista Negra (Blacklist)**

### **Agregar Números a Lista Negra**

1. **Agregar Individual**
   - Ir a "🚫 Lista Negra"
   - Hacer clic en "➕ Agregar Número"
   - Ingresar número: `+5411XXXXXXXX`
   - Motivo: "Solicitud del cliente"
   - Confirmar

2. **Importación Masiva**
   ```csv
   telefono,motivo,fecha_bloqueo
   +5411XXXXXXXX,No molestar,2025-01-01
   +5411YYYYYYYY,Número inválido,2025-01-01
   ```

### **Gestión de Lista Negra**
- **Filtros**: Por motivo, fecha, campaña
- **Acciones**: Eliminar, editar motivo, exportar
- **Automatización**: Bloqueo automático después de X rechazos

---

## **Configuración Avanzada Multi-SIP**

### **Gestión de Proveedores SIP**

1. **Agregar Proveedor**
   - Ir a "⚙️ Configuración" → "Multi-SIP"
   - Completar datos:
     ```
     Nombre: "Proveedor Principal"
     Servidor SIP: "sip.proveedor.com"
     Puerto: 5060
     Usuario: "tu_usuario"
     Contraseña: "tu_contraseña"
     Protocolo: UDP/TCP/TLS
     ```

2. **Configurar Prioridades**
   - Proveedor 1: Prioridad Alta (llamadas premium)
   - Proveedor 2: Prioridad Media (llamadas estándar)
   - Proveedor 3: Prioridad Baja (backup)

### **Gestión de CLIs**

1. **Configurar CLIs**
   - Ir a "Gestión de CLIs"
   - Agregar números autorizados:
     ```
     CLI: "+5411XXXXXXXX"
     Proveedor: "Proveedor Principal"
     Estado: Activo
     Tipo: Nacional
     ```

2. **Distribución Automática**
   - Algoritmo: Round Robin / Menor Uso / Por Región
   - Balanceo de carga automático

---

## **Monitoreo en Tiempo Real**

### **Dashboard Principal**
- **Métricas en Vivo**:
  - 📞 Llamadas Activas: 25
  - ✅ Llamadas Exitosas: 234
  - ❌ Llamadas Fallidas: 45
  - ⏱️ Tiempo Promedio: 2:45
  - 📊 Tasa de Éxito: 84%

### **Gráficos en Tiempo Real**
- **Llamadas por Hora**: Gráfico de líneas
- **Distribución por Estado**: Gráfico circular
- **Proveedores SIP**: Estado y uso
- **Rendimiento por Campaña**: Comparativo

### **Alertas Automáticas**
- 🔴 **Críticas**: Caída de proveedor SIP
- 🟡 **Advertencias**: Baja tasa de contacto
- 🔵 **Informativas**: Campaña completada

---

## **Histórico de Llamadas**

### **Filtros Avanzados**
```
Fecha: 01/01/2025 - 31/01/2025
Campaña: "Campaña Promocional Q1 2025"
Estado: Todas / Exitosas / Fallidas
CLI: "+5411XXXXXXXX"
Duración: 30s - 300s
```

### **Exportación de Reportes**
- **Formatos**: CSV, Excel, PDF
- **Datos Incluidos**:
  - Fecha y hora de llamada
  - Número de destino
  - CLI utilizado
  - Duración
  - Estado final
  - Grabación (si existe)

### **Análisis de Datos**
- **Estadísticas por Período**
- **Comparativos Mensuales**
- **Rendimiento por Agente**
- **ROI por Campaña**

---

## **Resolución de Problemas**

### **Problemas Comunes**

#### **1. No se pueden realizar llamadas**
**Síntomas**: Las campañas no inician llamadas
**Solución**:
```bash
# Verificar estado de proveedores SIP
curl http://localhost:8001/multi-sip/provedores

# Verificar conectividad
ping sip.tu-proveedor.com

# Revisar logs
tail -f logs/sistema.log
```

#### **2. Interface no carga**
**Síntomas**: Pantalla en blanco o errores 404
**Solución**:
```bash
# Verificar servicios
curl http://localhost:8000/health
curl http://localhost:3001

# Reiniciar frontend
cd frontend
npm install
npm start
```

#### **3. Base de datos corrupta**
**Solución**:
```bash
# Backup de emergencia
cp discador.db discador.db.backup

# Verificar integridad
python validate_system.py

# Restaurar si es necesario
python scripts/repair_database.py
```

### **Logs del Sistema**
```bash
# Logs principales
tail -f logs/main.log        # Backend principal
tail -f logs/multisip.log    # Servicio Multi-SIP
tail -f logs/frontend.log    # Frontend React
```

### **Contacto Soporte**
- **Email**: soporte@discador.com
- **WhatsApp**: +54 11 XXXX-XXXX
- **Horario**: Lunes a Viernes 9:00-18:00 (UTC-3)

---

# 🇧🇷 **PORTUGUÊS (BRASIL)**

## **Introdução e Características**

O Sistema Discador Preditivo é uma solução completa para centrais de atendimento que permite:

### ✨ **Características Principais**
- **Discagem Preditiva Inteligente**: Otimiza automaticamente a quantidade de chamadas simultâneas
- **Gestão de Campanhas**: Cria e administra múltiplas campanhas de chamadas
- **Multi-SIP**: Suporte para múltiplos provedores SIP
- **Lista Negra Avançada**: Filtragem automática de números indesejados
- **Monitoramento em Tempo Real**: Dashboard com métricas ao vivo
- **Histórico Completo**: Relatórios detalhados de todas as chamadas
- **Interface Moderna**: Dashboard profissional e fácil de usar

---

## **Instalação e Configuração Inicial (BR)**

### **Requisitos do Sistema**
- **Sistema Operacional**: Windows 10/11, Linux Ubuntu 18+, macOS 10.14+
- **Python**: 3.8 ou superior
- **Node.js**: 16.0 ou superior
- **Memória RAM**: Mínimo 4GB (Recomendado 8GB)
- **Espaço em Disco**: Mínimo 2GB

### **Passo 1: Baixar o Sistema**
```bash
# Baixar e extrair o sistema
cd C:\
git clone https://github.com/seu-repo/discador-main.git
cd discador-main
```

### **Passo 2: Instalação Automática**
```bash
# Windows PowerShell
.\install.sh

# Linux/Mac
chmod +x install.sh
./install.sh
```

### **Passo 3: Verificar Instalação**
```bash
# Verificar que todos os componentes estão instalados
python validate_system.py
```

### **Passo 4: Iniciar o Sistema**
```bash
# Terminal 1: Backend Principal (Porta 8000)
python main.py

# Terminal 2: Serviço Multi-SIP (Porta 8001)  
python quick_fix_routes.py

# Terminal 3: Frontend React (Porta 3001)
cd frontend
npm start
```

---

## **Acesso ao Sistema**

### **URLs de Acesso**
- **Frontend Principal**: `http://localhost:3001`
- **API Backend**: `http://localhost:8000`
- **API Multi-SIP**: `http://localhost:8001`

### **Credenciais Padrão**
- **Usuário**: `admin@discador.com`
- **Senha**: `admin123`

### **Primeira Configuração**
1. Acessar `http://localhost:3001`
2. Fazer login com as credenciais padrão
3. Ir para **Configuração** para personalizar o sistema
4. Alterar a senha padrão

---

## **Gestão de Campanhas (BR)**

### **Criar Nova Campanha**

1. **Navegar para Campanhas**
   - Clicar em "📊 Campanhas" no menu lateral

2. **Criar Campanha**
   - Clicar em "✅ Nova Campanha"
   - Preencher os dados:
     ```
     Nome: "Campanha Promocional Q1 2025"
     Descrição: "Promoção de produtos para o primeiro trimestre"
     CLI (Número de origem): "+5511XXXXXXXX"
     Máx. Chamadas Simultâneas: 10
     Máx. Tentativas por Contato: 3
     Intervalo entre Tentativas: 300 segundos
     ```

3. **Configuração Avançada**
   - **Horários de Chamada**: 09:00 - 18:00
   - **Dias Úteis**: Segunda a Sexta-feira
   - **Detecção de Secretária**: Ativada
   - **Gravação de Chamadas**: Opcional

### **Estados da Campanha**
- 🟢 **Ativa**: Realizando chamadas
- 🟡 **Pausada**: Temporariamente parada
- 🔴 **Parada**: Completamente finalizada
- ⚫ **Rascunho**: Em configuração

### **Ações da Campanha**
- **▶️ Iniciar**: Começar as chamadas
- **⏸️ Pausar**: Parar temporariamente
- **⏹️ Parar**: Finalizar completamente
- **✏️ Editar**: Modificar configuração
- **📊 Estatísticas**: Ver métricas detalhadas

---

## **Gestão de Listas de Contatos**

### **Enviar Lista de Contatos**

1. **Preparar Arquivo CSV**
   ```csv
   nome,telefone,email,observacoes
   João Silva,+5511XXXXXXXX,joao@email.com,Cliente Premium
   Maria Santos,+5511YYYYYYYY,maria@email.com,Prospecto
   Carlos Oliveira,+5511ZZZZZZZZ,carlos@email.com,Renovação
   ```

2. **Enviar Lista**
   - Ir para "📋 Listas"
   - Clicar em "📤 Enviar Lista"
   - Selecionar arquivo CSV
   - Atribuir à campanha existente
   - Verificar pré-visualização
   - Confirmar importação

### **Gestão de Contatos**
- **Filtros Disponíveis**:
  - Por campanha
  - Por estado da chamada
  - Por data da última chamada
  - Por número de tentativas

- **Estados do Contato**:
  - ⏳ **Pendente**: Não chamado
  - 📞 **Em Processo**: Chamando agora
  - ✅ **Contatado**: Chamada bem-sucedida
  - ❌ **Não Contatado**: Sem resposta
  - 🚫 **Bloqueado**: Na lista negra

---

## **Lista Negra (Blacklist) (BR)**

### **Adicionar Números à Lista Negra**

1. **Adicionar Individual**
   - Ir para "🚫 Lista Negra"
   - Clicar em "➕ Adicionar Número"
   - Inserir número: `+5511XXXXXXXX`
   - Motivo: "Solicitação do cliente"
   - Confirmar

2. **Importação em Massa**
   ```csv
   telefone,motivo,data_bloqueio
   +5511XXXXXXXX,Não incomodar,2025-01-01
   +5511YYYYYYYY,Número inválido,2025-01-01
   ```

### **Gestão da Lista Negra**
- **Filtros**: Por motivo, data, campanha
- **Ações**: Remover, editar motivo, exportar
- **Automatização**: Bloqueio automático após X rejeições

---

## **Configuração Avançada Multi-SIP (BR)**

### **Gestão de Provedores SIP**

1. **Adicionar Provedor**
   - Ir para "⚙️ Configuração" → "Multi-SIP"
   - Preencher dados:
     ```
     Nome: "Provedor Principal"
     Servidor SIP: "sip.provedor.com"
     Porta: 5060
     Usuário: "seu_usuario"
     Senha: "sua_senha"
     Protocolo: UDP/TCP/TLS
     ```

2. **Configurar Prioridades**
   - Provedor 1: Prioridade Alta (chamadas premium)
   - Provedor 2: Prioridade Média (chamadas padrão)
   - Provedor 3: Prioridade Baixa (backup)

### **Gestão de CLIs**

1. **Configurar CLIs**
   - Ir para "Gestão de CLIs"
   - Adicionar números autorizados:
     ```
     CLI: "+5511XXXXXXXX"
     Provedor: "Provedor Principal"
     Estado: Ativo
     Tipo: Nacional
     ```

2. **Distribuição Automática**
   - Algoritmo: Round Robin / Menor Uso / Por Região
   - Balanceamento de carga automático

---

## **Monitoramento em Tempo Real**

### **Dashboard Principal**
- **Métricas ao Vivo**:
  - 📞 Chamadas Ativas: 25
  - ✅ Chamadas Bem-sucedidas: 234
  - ❌ Chamadas Falhadas: 45
  - ⏱️ Tempo Médio: 2:45
  - 📊 Taxa de Sucesso: 84%

### **Gráficos em Tempo Real**
- **Chamadas por Hora**: Gráfico de linhas
- **Distribuição por Estado**: Gráfico circular
- **Provedores SIP**: Estado e uso
- **Desempenho por Campanha**: Comparativo

### **Alertas Automáticos**
- 🔴 **Críticos**: Queda de provedor SIP
- 🟡 **Avisos**: Baixa taxa de contato
- 🔵 **Informativos**: Campanha concluída

---

## **Histórico de Chamadas (BR)**

### **Filtros Avançados**
```
Data: 01/01/2025 - 31/01/2025
Campanha: "Campanha Promocional Q1 2025"
Estado: Todas / Bem-sucedidas / Falhadas
CLI: "+5511XXXXXXXX"
Duração: 30s - 300s
```

### **Exportação de Relatórios**
- **Formatos**: CSV, Excel, PDF
- **Dados Incluídos**:
  - Data e hora da chamada
  - Número de destino
  - CLI utilizado
  - Duração
  - Estado final
  - Gravação (se existir)

### **Análise de Dados**
- **Estatísticas por Período**
- **Comparativos Mensais**
- **Desempenho por Agente**
- **ROI por Campanha**

---

## **Solução de Problemas**

### **Problemas Comuns**

#### **1. Não é possível realizar chamadas**
**Sintomas**: As campanhas não iniciam chamadas
**Solução**:
```bash
# Verificar estado dos provedores SIP
curl http://localhost:8001/multi-sip/provedores

# Verificar conectividade
ping sip.seu-provedor.com

# Revisar logs
tail -f logs/sistema.log
```

#### **2. Interface não carrega**
**Sintomas**: Tela em branco ou erros 404
**Solução**:
```bash
# Verificar serviços
curl http://localhost:8000/health
curl http://localhost:3001

# Reiniciar frontend
cd frontend
npm install
npm start
```

#### **3. Base de dados corrompida**
**Solução**:
```bash
# Backup de emergência
cp discador.db discador.db.backup

# Verificar integridade
python validate_system.py

# Restaurar se necessário
python scripts/repair_database.py
```

### **Logs do Sistema**
```bash
# Logs principais
tail -f logs/main.log        # Backend principal
tail -f logs/multisip.log    # Serviço Multi-SIP
tail -f logs/frontend.log    # Frontend React
```

### **Contato Suporte**
- **Email**: suporte@discador.com
- **WhatsApp**: +55 11 XXXX-XXXX
- **Horário**: Segunda a Sexta 9:00-18:00 (UTC-3)

---

## 🔧 **Teste de Funcionalidades Completo**

### **Lista de Verificação**

#### ✅ **Backend (APIs)**
```bash
# Teste de saúde do sistema
curl http://localhost:8000/health

# Teste de campanhas
curl http://localhost:8000/api/v1/campaigns

# Teste de blacklist
curl http://localhost:8000/api/v1/blacklist

# Teste Multi-SIP
curl http://localhost:8001/multi-sip/provedores
```

#### ✅ **Frontend**
- [ ] Login/Logout funcional
- [ ] Dashboard carrega corretamente
- [ ] Criação de campanha
- [ ] Upload de lista
- [ ] Configuração Multi-SIP
- [ ] Monitoreo em tempo real
- [ ] Histórico de chamadas

#### ✅ **Integração**
- [ ] Provedor SIP conectado
- [ ] CLIs configurados
- [ ] Chamadas de teste realizadas
- [ ] Gravações funcionando
- [ ] Relatórios exportando

---

## 📞 **Suporte Técnico**

### **Canais de Atendimento**
- **🇦🇷 Argentina**: +54 11 XXXX-XXXX
- **🇧🇷 Brasil**: +55 11 XXXX-XXXX
- **📧 Email**: soporte@discador.com
- **🌐 Portal**: https://soporte.discador.com

### **Horários de Atendimento**
- **Lunes a Viernes / Segunda a Sexta**: 9:00-18:00
- **Zona Horaria / Fuso Horário**: UTC-3
- **Urgências / Emergências**: 24/7

---

*© 2025 Sistema Discador Predictivo - Todos os direitos reservados* 