# 📞 Tutorial de Uso - Sistema Discador Predictivo
*Guía Completa de Uso en Español (Argentina) y Português (Brasil)*

---

## 🌐 **Acceso al Sistema**

**URL de Acceso:** [https://discador-predictivo.vercel.app](https://discador-predictivo.vercel.app)

---

## 📋 **Índice / Índice**

### **Español (Argentina)**
1. [Acceso y Login](#acceso-y-login-es)
2. [Gestión de Campañas](#gestión-de-campañas-es)
3. [Upload de Listas de Contactos](#upload-de-listas-es)
4. [Lista Negra (Blacklist)](#lista-negra-es)
5. [Configuración Avanzada Multi-SIP](#configuración-multi-sip-es)
6. [Monitoreo en Tiempo Real](#monitoreo-es)
7. [Histórico de Llamadas](#histórico-es)

### **Português (Brasil)**
1. [Acesso e Login](#acesso-e-login-br)
2. [Gestão de Campanhas](#gestão-de-campanhas-br)
3. [Upload de Listas de Contatos](#upload-de-listas-br)
4. [Lista Negra (Blacklist)](#lista-negra-br)
5. [Configuração Avançada Multi-SIP](#configuração-multi-sip-br)
6. [Monitoramento em Tempo Real](#monitoramento-br)
7. [Histórico de Chamadas](#histórico-br)

---

# 🇦🇷 **ESPAÑOL (ARGENTINA)**

## <a id="acceso-y-login-es"></a>🔐 **1. Acceso y Login**

### **Cómo acceder:**
1. **Abrir navegador** y ir a: `https://discador-predictivo.vercel.app`
2. **Login del sistema:**
   - Usuario: `admin`
   - Contraseña: `admin123`
3. **Verificar acceso correcto:** Deberías ver el dashboard principal

### **¿Qué esperar?**
- ✅ **Dashboard principal** con métricas en tiempo real
- ✅ **Menú lateral** con todas las funcionalidades
- ✅ **Interfaz moderna** completamente en español argentino

---

## <a id="gestión-de-campañas-es"></a>📊 **2. Gestión de Campañas**

### **Ubicación:** Menú lateral → "Gestión de Campañas"

### **Crear Nueva Campaña:**

1. **Hacer clic** en "Nueva Campaña" (botón azul)
2. **Completar formulario:**
   ```
   Nombre: "Campaña Demo Argentina"
   Descripción: "Prueba de funcionalidad del sistema"
   Llamadas Simultáneas: 5
   Intentos Máximos: 3
   ```
3. **Hacer clic** en "Crear Campaña"

### **¿Qué deberías ver?**
- ✅ **Métricas actualizadas** en tiempo real
- ✅ **Lista de campañas** con la nueva entrada
- ✅ **Estado "Borrador"** para la campaña recién creada
- ✅ **Botones de acción** (Editar, Eliminar)

### **Estados de Campaña:**
- 🟢 **Activa:** Realizando llamadas
- 🟡 **Pausada:** Temporalmente detenida  
- ⚪ **Borrador:** Sin iniciar
- 🔵 **Completada:** Finalizada

---

## <a id="upload-de-listas-es"></a>📂 **3. Upload de Listas de Contactos**

### **Ubicación:** Menú lateral → "Upload de Listas"

### **Probar Upload:**

1. **Preparar archivo CSV** con formato:
   ```csv
   telefono,nombre,apellido,email
   +5491123456789,Juan,Pérez,juan@email.com
   +5491198765432,María,González,maria@email.com
   ```

2. **Proceso de Upload:**
   - Hacer clic en "Seleccionar Archivo"
   - Elegir tu archivo CSV
   - Hacer clic en "Subir Lista"

### **¿Qué verificar?**
- ✅ **Validación automática** del formato
- ✅ **Detección de duplicados**
- ✅ **Validación de números argentinos** (+54)
- ✅ **Mensaje de éxito** con cantidad procesada
- ✅ **Lista actualizada** en tiempo real

### **Formatos Soportados:**
- ✅ **CSV** con delimitador coma
- ✅ **Números internacionales** (+54, +55, etc.)
- ✅ **Campos opcionales** (nombre, email)

---

## <a id="lista-negra-es"></a>🚫 **4. Lista Negra (Blacklist)**

### **Ubicación:** Menú lateral → "Lista Negra"

### **Agregar número a blacklist:**

1. **Hacer clic** en "Agregar a Blacklist"
2. **Completar datos:**
   ```
   Número: +5491123456789
   Motivo: No molestar - Cliente solicita exclusión
   ```
3. **Hacer clic** en "Agregar"

### **Funcionalidades para probar:**
- ✅ **Búsqueda en tiempo real** (escribir número para buscar)
- ✅ **Filtro por motivo** (desplegable)
- ✅ **Exportación CSV** (botón "Exportar")
- ✅ **Eliminación individual** (botón rojo)
- ✅ **Validación automática** contra próximas campañas

### **¿Qué verificar?**
- ✅ **Números agregados** aparecen instantáneamente
- ✅ **Contador actualizado** en métricas
- ✅ **Validación de formato** de números

---

## <a id="configuración-multi-sip-es"></a>⚙️ **5. Configuración Avanzada Multi-SIP**

### **Ubicación:** Menú lateral → "Configuración Avanzada"

### **Proveedores SIP:**

1. **Ver proveedores disponibles** en la pestaña "Proveedores"
2. **Probar conexión** con botón "Probar"
3. **Verificar estado** (Activo/Inactivo)

### **CLIs (Números Salientes):**

1. **Ir a pestaña "CLIs"**
2. **Agregar nuevo CLI:**
   ```
   Número CLI: +5491123456789
   Proveedor: Seleccionar de lista
   Estado: Activo
   ```
3. **Hacer clic** en "Agregar CLI"

### **Contextos de Audio:**

1. **Ir a pestaña "Contextos de Audio"**
2. **Crear nuevo contexto:**
   ```
   Nombre: "Saludo Argentina"
   Descripción: "Audio para campañas en Argentina"
   URL Audio: https://ejemplo.com/audio.wav
   ```

### **¿Qué verificar?**
- ✅ **Lista de proveedores** carga correctamente
- ✅ **Pruebas de conexión** funcionan
- ✅ **CLIs se agregan** sin errores
- ✅ **Contextos se crean** exitosamente

---

## <a id="monitoreo-es"></a>📈 **6. Monitoreo en Tiempo Real**

### **Ubicación:** Menú lateral → "Monitoreo"

### **Dashboard de Métricas:**

#### **Métricas Principales:**
- 📊 **Llamadas Activas:** Número en tiempo real
- ⏱️ **Tiempo Promedio:** Duración de llamadas
- 📞 **Total del Día:** Llamadas realizadas
- 📈 **Tasa de Éxito:** Porcentaje de conexiones exitosas

#### **Gráficos en Tiempo Real:**
- 📊 **Gráfico de líneas:** Llamadas por hora
- 🥧 **Gráfico circular:** Distribución por resultado
- 📊 **Barras:** Comparativo por campaña

### **¿Qué probar?**
- ✅ **Actualización automática** cada 30 segundos
- ✅ **Hover en gráficos** muestra detalles
- ✅ **Filtros por fecha** funcionan
- ✅ **Exportación de reportes** en PDF/CSV

---

## <a id="histórico-es"></a>📋 **7. Histórico de Llamadas**

### **Ubicación:** Menú lateral → "Histórico"

### **Búsqueda y Filtros:**

1. **Usar buscador:** Escribir número o nombre
2. **Filtros disponibles:**
   - 📅 **Fecha:** Rango personalizado
   - 📞 **Estado:** Exitosa, Fallida, Ocupada
   - 🏷️ **Campaña:** Seleccionar específica
   - ⏱️ **Duración:** Mínima y máxima

### **Acciones disponibles:**
- 👁️ **Ver detalle:** Hacer clic en el ojo
- 📞 **Rellamar:** Botón de re-contacto  
- 📊 **Exportar:** Descargar selección en CSV

### **Detalle de Llamada:**
Al hacer clic en "Ver detalle":
- ⏱️ **Duración completa**
- 📞 **Número marcado**
- 🎯 **Resultado final**
- 📅 **Fecha y hora exacta**
- 👤 **Agente asignado**
- 📝 **Notas adicionales**

### **¿Qué verificar?**
- ✅ **Búsqueda instantánea** funciona
- ✅ **Filtros combinados** muestran resultados correctos
- ✅ **Paginación** navega correctamente
- ✅ **Exportación** descarga archivo válido
- ✅ **Detalle completo** muestra toda la información

---

# 🇧🇷 **PORTUGUÊS (BRASIL)**

## <a id="acesso-e-login-br"></a>🔐 **1. Acesso e Login**

### **Como acessar:**
1. **Abrir navegador** e ir para: `https://discador-predictivo.vercel.app`
2. **Login no sistema:**
   - Usuário: `admin`
   - Senha: `admin123`
3. **Verificar acesso correto:** Você deve ver o dashboard principal

### **O que esperar?**
- ✅ **Dashboard principal** com métricas em tempo real
- ✅ **Menu lateral** com todas as funcionalidades
- ✅ **Interface moderna** completamente em espanhol argentino

---

## <a id="gestão-de-campanhas-br"></a>📊 **2. Gestão de Campanhas**

### **Localização:** Menu lateral → "Gestión de Campañas"

### **Criar Nova Campanha:**

1. **Clicar** em "Nueva Campaña" (botão azul)
2. **Preencher formulário:**
   ```
   Nome: "Campanha Demo Brasil"
   Descrição: "Teste de funcionalidade do sistema"
   Chamadas Simultâneas: 5
   Tentativas Máximas: 3
   ```
3. **Clicar** em "Crear Campaña"

### **O que você deve ver?**
- ✅ **Métricas atualizadas** em tempo real
- ✅ **Lista de campanhas** com a nova entrada
- ✅ **Status "Borrador"** para a campanha recém-criada
- ✅ **Botões de ação** (Editar, Eliminar)

### **Estados da Campanha:**
- 🟢 **Activa:** Realizando chamadas
- 🟡 **Pausada:** Temporariamente parada
- ⚪ **Borrador:** Sem iniciar
- 🔵 **Completada:** Finalizada

---

## <a id="upload-de-listas-br"></a>📂 **3. Upload de Listas de Contatos**

### **Localização:** Menu lateral → "Upload de Listas"

### **Testar Upload:**

1. **Preparar arquivo CSV** com formato:
   ```csv
   telefono,nombre,apellido,email
   +5511987654321,João,Silva,joao@email.com
   +5511876543210,Maria,Santos,maria@email.com
   ```

2. **Processo de Upload:**
   - Clicar em "Seleccionar Archivo"
   - Escolher seu arquivo CSV
   - Clicar em "Subir Lista"

### **O que verificar?**
- ✅ **Validação automática** do formato
- ✅ **Detecção de duplicados**
- ✅ **Validação de números brasileiros** (+55)
- ✅ **Mensagem de sucesso** com quantidade processada
- ✅ **Lista atualizada** em tempo real

### **Formatos Suportados:**
- ✅ **CSV** com delimitador vírgula
- ✅ **Números internacionais** (+54, +55, etc.)
- ✅ **Campos opcionais** (nome, email)

---

## <a id="lista-negra-br"></a>🚫 **4. Lista Negra (Blacklist)**

### **Localização:** Menu lateral → "Lista Negra"

### **Adicionar número à blacklist:**

1. **Clicar** em "Agregar a Blacklist"
2. **Preencher dados:**
   ```
   Número: +5511987654321
   Motivo: Não incomodar - Cliente solicita exclusão
   ```
3. **Clicar** em "Agregar"

### **Funcionalidades para testar:**
- ✅ **Busca em tempo real** (digitar número para buscar)
- ✅ **Filtro por motivo** (dropdown)
- ✅ **Exportação CSV** (botão "Exportar")
- ✅ **Remoção individual** (botão vermelho)
- ✅ **Validação automática** contra próximas campanhas

### **O que verificar?**
- ✅ **Números adicionados** aparecem instantaneamente
- ✅ **Contador atualizado** nas métricas
- ✅ **Validação de formato** de números

---

## <a id="configuração-multi-sip-br"></a>⚙️ **5. Configuração Avançada Multi-SIP**

### **Localização:** Menu lateral → "Configuración Avanzada"

### **Provedores SIP:**

1. **Ver provedores disponíveis** na aba "Proveedores"
2. **Testar conexão** com botão "Probar"
3. **Verificar status** (Ativo/Inativo)

### **CLIs (Números de Saída):**

1. **Ir para aba "CLIs"**
2. **Adicionar novo CLI:**
   ```
   Número CLI: +5511987654321
   Provedor: Selecionar da lista
   Status: Ativo
   ```
3. **Clicar** em "Agregar CLI"

### **Contextos de Áudio:**

1. **Ir para aba "Contextos de Audio"**
2. **Criar novo contexto:**
   ```
   Nome: "Saudação Brasil"
   Descrição: "Áudio para campanhas no Brasil"
   URL Áudio: https://exemplo.com/audio.wav
   ```

### **O que verificar?**
- ✅ **Lista de provedores** carrega corretamente
- ✅ **Testes de conexão** funcionam
- ✅ **CLIs são adicionados** sem erros
- ✅ **Contextos são criados** com sucesso

---

## <a id="monitoramento-br"></a>📈 **6. Monitoramento em Tempo Real**

### **Localização:** Menu lateral → "Monitoreo"

### **Dashboard de Métricas:**

#### **Métricas Principais:**
- 📊 **Chamadas Ativas:** Número em tempo real
- ⏱️ **Tempo Médio:** Duração das chamadas
- 📞 **Total do Dia:** Chamadas realizadas
- 📈 **Taxa de Sucesso:** Porcentagem de conexões bem-sucedidas

#### **Gráficos em Tempo Real:**
- 📊 **Gráfico de linhas:** Chamadas por hora
- 🥧 **Gráfico circular:** Distribuição por resultado
- 📊 **Barras:** Comparativo por campanha

### **O que testar?**
- ✅ **Atualização automática** a cada 30 segundos
- ✅ **Hover nos gráficos** mostra detalhes
- ✅ **Filtros por data** funcionam
- ✅ **Exportação de relatórios** em PDF/CSV

---

## <a id="histórico-br"></a>📋 **7. Histórico de Chamadas**

### **Localização:** Menu lateral → "Histórico"

### **Busca e Filtros:**

1. **Usar buscador:** Digitar número ou nome
2. **Filtros disponíveis:**
   - 📅 **Data:** Período personalizado
   - 📞 **Status:** Bem-sucedida, Falhada, Ocupada
   - 🏷️ **Campanha:** Selecionar específica
   - ⏱️ **Duração:** Mínima e máxima

### **Ações disponíveis:**
- 👁️ **Ver detalhe:** Clicar no olho
- 📞 **Religar:** Botão de re-contato
- 📊 **Exportar:** Baixar seleção em CSV

### **Detalhe da Chamada:**
Ao clicar em "Ver detalle":
- ⏱️ **Duração completa**
- 📞 **Número discado**
- 🎯 **Resultado final**
- 📅 **Data e hora exata**
- 👤 **Agente designado**
- 📝 **Notas adicionais**

### **O que verificar?**
- ✅ **Busca instantânea** funciona
- ✅ **Filtros combinados** mostram resultados corretos
- ✅ **Paginação** navega corretamente
- ✅ **Exportação** baixa arquivo válido
- ✅ **Detalhe completo** mostra toda a informação

---

## 🎯 **FUNCIONALIDADES PRINCIPAIS DO SISTEMA**

### **✅ Módulos Implementados:**

#### **🔧 Backend (API REST)**
- FastAPI com documentação automática
- SQLAlchemy para gestão de banco de dados
- Sistema de autenticação com JWT
- Validação automática de dados
- Logs detalhados para debugging

#### **🎨 Frontend (React + Vite)**
- Interface moderna e responsiva
- Gráficos interativos em tempo real
- Componentes reutilizáveis
- Gestão de estado eficiente
- Design system consistente

#### **📞 Sistema de Discagem**
- Algoritmo preditivo inteligente
- Múltiplos provedores SIP
- Gestão de filas dinâmicas
- Controle de taxa de chamadas
- Detecção de caixa postal

#### **📊 Analytics e Reportes**
- Métricas em tempo real
- Dashboard executivo
- Relatórios customizáveis
- Exportação em múltiplos formatos
- Análise de performance

#### **🛡️ Segurança e Compliance**
- Lista negra automática
- Validação de números
- Logs de auditoria
- Backup automático
- Conformidade com regulamentações

### **🚀 Tecnologias Utilizadas:**

#### **Backend:**
- Python 3.9+
- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis (cache)
- Celery (tarefas assíncronas)

#### **Frontend:**
- React 18
- Vite
- TailwindCSS
- Chart.js
- Axios
- React Router

#### **Infraestrutura:**
- Vercel (Frontend)
- Railway (Backend)
- PostgreSQL (Banco)
- Redis (Cache)
- GitHub Actions (CI/CD)

---

## 🎉 **Conclusão**

O sistema está **100% funcional** e **completamente traduzido** para espanhol argentino. Todas as funcionalidades principais foram testadas e estão operacionais:

✅ **Gestão completa de campanhas**  
✅ **Upload e validação de listas**  
✅ **Sistema de blacklist robusto**  
✅ **Configuração Multi-SIP avançada**  
✅ **Monitoramento em tempo real**  
✅ **Histórico detalhado de chamadas**  
✅ **Interface moderna e intuitiva**  
✅ **APIs documentadas e funcionais**  

O sistema está **pronto para produção** e pode ser usado imediatamente pelo cliente para gestão profissional de campanhas telefônicas.

---

**📧 Suporte:** Para dúvidas ou suporte técnico, entre em contato através do repositório GitHub: https://github.com/GouveiaZx/Discador.git 