# 📞 Guía de Uso - Sistema Discador Predictivo

## 🌐 **Acceso al Sistema**
**URL:** https://discador-predictivo.vercel.app  
**Usuario:** admin  
**Contraseña:** admin123

---

## 🇦🇷 **ESPAÑOL (ARGENTINA)**

### 📊 **1. Gestión de Campañas**
**Ubicación:** Menú lateral → "Gestión de Campañas"

**Crear campaña:**
1. Clic en "Nueva Campaña"
2. Completar:
   - Nombre: "Campaña Demo Argentina"
   - Descripción: "Prueba del sistema"
   - Llamadas Simultáneas: 5
   - Intentos Máximos: 3
3. Clic en "Crear Campaña"

**¿Qué verificar?**
- ✅ Métricas actualizadas
- ✅ Nueva campaña en lista
- ✅ Estado "Borrador"
- ✅ Botones de acción funcionando

### 📂 **2. Upload de Listas**
**Ubicación:** Menú lateral → "Upload de Listas"

**Formato CSV requerido:**
```csv
telefono,nombre,apellido,email
+5491123456789,Juan,Pérez,juan@email.com
+5491198765432,María,González,maria@email.com
```

**Proceso:**
1. Seleccionar archivo CSV
2. Clic en "Subir Lista"
3. Verificar validación automática

**¿Qué verificar?**
- ✅ Detección de duplicados
- ✅ Validación de números argentinos (+54)
- ✅ Mensaje de éxito
- ✅ Lista actualizada

### 🚫 **3. Lista Negra (Blacklist)**
**Ubicación:** Menú lateral → "Lista Negra"

**Agregar número:**
1. Clic en "Agregar a Blacklist"
2. Completar:
   - Número: +5491123456789
   - Motivo: "No molestar"
3. Clic en "Agregar"

**Funcionalidades:**
- ✅ Búsqueda en tiempo real
- ✅ Filtro por motivo
- ✅ Exportación CSV
- ✅ Eliminación individual

### ⚙️ **4. Configuración Multi-SIP**
**Ubicación:** Menú lateral → "Configuración Avanzada"

**Pestañas disponibles:**
- **Proveedores:** Ver y probar conexiones SIP
- **CLIs:** Gestionar números salientes
- **Contextos:** Administrar audios

**Agregar CLI:**
1. Ir a pestaña "CLIs"
2. Completar número: +5491123456789
3. Seleccionar proveedor
4. Estado: Activo

### 📈 **5. Monitoreo en Tiempo Real**
**Ubicación:** Menú lateral → "Monitoreo"

**Métricas disponibles:**
- 📊 Llamadas Activas
- ⏱️ Tiempo Promedio
- 📞 Total del Día
- 📈 Tasa de Éxito

**Gráficos:**
- Llamadas por hora (líneas)
- Distribución por resultado (circular)
- Comparativo por campaña (barras)

### 📋 **6. Histórico de Llamadas**
**Ubicación:** Menú lateral → "Histórico"

**Filtros disponibles:**
- 📅 Fecha (rango personalizado)
- 📞 Estado (Exitosa, Fallida, Ocupada)
- 🏷️ Campaña específica
- ⏱️ Duración (min/max)

**Acciones:**
- 👁️ Ver detalle completo
- 📞 Rellamar contacto
- 📊 Exportar selección

---

## 🇧🇷 **PORTUGUÊS (BRASIL)**

### 📊 **1. Gestão de Campanhas**
**Localização:** Menu lateral → "Gestión de Campañas"

**Criar campanha:**
1. Clicar em "Nueva Campaña"
2. Preencher:
   - Nome: "Campanha Demo Brasil"
   - Descrição: "Teste do sistema"
   - Chamadas Simultâneas: 5
   - Tentativas Máximas: 3
3. Clicar em "Crear Campaña"

**O que verificar?**
- ✅ Métricas atualizadas
- ✅ Nova campanha na lista
- ✅ Status "Borrador"
- ✅ Botões de ação funcionando

### 📂 **2. Upload de Listas**
**Localização:** Menu lateral → "Upload de Listas"

**Formato CSV obrigatório:**
```csv
telefono,nombre,apellido,email
+5511987654321,João,Silva,joao@email.com
+5511876543210,Maria,Santos,maria@email.com
```

**Processo:**
1. Selecionar arquivo CSV
2. Clicar em "Subir Lista"
3. Verificar validação automática

**O que verificar?**
- ✅ Detecção de duplicados
- ✅ Validação de números brasileiros (+55)
- ✅ Mensagem de sucesso
- ✅ Lista atualizada

### 🚫 **3. Lista Negra (Blacklist)**
**Localização:** Menu lateral → "Lista Negra"

**Adicionar número:**
1. Clicar em "Agregar a Blacklist"
2. Preencher:
   - Número: +5511987654321
   - Motivo: "Não incomodar"
3. Clicar em "Agregar"

**Funcionalidades:**
- ✅ Busca em tempo real
- ✅ Filtro por motivo
- ✅ Exportação CSV
- ✅ Remoção individual

### ⚙️ **4. Configuração Multi-SIP**
**Localização:** Menu lateral → "Configuración Avanzada"

**Abas disponíveis:**
- **Proveedores:** Ver e testar conexões SIP
- **CLIs:** Gerenciar números de saída
- **Contextos:** Administrar áudios

**Adicionar CLI:**
1. Ir para aba "CLIs"
2. Preencher número: +5511987654321
3. Selecionar provedor
4. Status: Ativo

### 📈 **5. Monitoramento em Tempo Real**
**Localização:** Menu lateral → "Monitoreo"

**Métricas disponíveis:**
- 📊 Chamadas Ativas
- ⏱️ Tempo Médio
- 📞 Total do Dia
- 📈 Taxa de Sucesso

**Gráficos:**
- Chamadas por hora (linhas)
- Distribuição por resultado (circular)
- Comparativo por campanha (barras)

### 📋 **6. Histórico de Chamadas**
**Localização:** Menu lateral → "Histórico"

**Filtros disponíveis:**
- 📅 Data (período personalizado)
- 📞 Status (Bem-sucedida, Falhada, Ocupada)
- 🏷️ Campanha específica
- ⏱️ Duração (min/max)

**Ações:**
- 👁️ Ver detalhe completo
- 📞 Religar contato
- 📊 Exportar seleção

---

## 🎯 **FUNCIONALIDADES DO SISTEMA**

### ✅ **Módulos Implementados:**
- **Backend API REST** com FastAPI
- **Frontend React** moderno e responsivo
- **Sistema de discagem** preditiva
- **Analytics** em tempo real
- **Segurança** e compliance

### 🚀 **Tecnologias:**
- **Backend:** Python, FastAPI, PostgreSQL
- **Frontend:** React, Vite, TailwindCSS
- **Deploy:** Vercel + Railway
- **Idioma:** 100% Espanhol Argentino

### 🎉 **Status:**
✅ **Sistema 100% funcional**  
✅ **Totalmente traduzido**  
✅ **Pronto para produção**  
✅ **Todas as APIs operacionais**

---

**Repositório:** https://github.com/GouveiaZx/Discador.git 