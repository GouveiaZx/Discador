# 🎯 SISTEMA DISCADOR PREDICTIVO - DOCUMENTACIÓN COMPLETA

## 📋 VISIÓN GENERAL

Sistema completo de discado predictivo con interfaz web moderna, backend robusto e integración con Asterisk. Desarrollado para operaciones de telemarketing, cobranza e investigaciones telefónicas.

## 🌐 ENLACES DEL SISTEMA

- **Frontend**: https://discador.vercel.app/
- **Backend API**: https://discador.onrender.com/
- **Documentación API**: https://discador.onrender.com/documentacion
- **Base de Datos**: Supabase (proyecto: orxxocptgaeoyrtlxwkv)

## 🏗️ ARQUITECTURA

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FRONTEND      │    │     BACKEND     │    │   SUPABASE      │
│   (Vercel)      │◄──►│   (Render.com)  │◄──►│   (Database)    │
│   React + Vite  │    │   FastAPI       │    │   PostgreSQL    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │              ┌─────────────────┐              │
         └─────────────►│    ASTERISK     │◄─────────────┘
                        │   (PBX/AGI)     │
                        └─────────────────┘
```

## 🚀 FUNCIONALIDADES PRINCIPALES

### 📊 Dashboard Profesional
- Monitoreo en tiempo real
- Estadísticas de campañas
- Gráficos y métricas
- Alertas y notificaciones

### 📞 Discado Predictivo
- Algoritmo de predicción inteligente
- Balanceamiento de carga automático
- Detección de voicemail (AMD)
- Sistema "Presione 1"

### 👥 Gestión de Campañas
- Creación y edición de campañas
- Subida de listas de contactos
- Configuración de horarios
- Control de intentos

### 🔊 Sistema de Audio Inteligente
- Reproducción de audios personalizados
- Detección de DTMF
- Transferencia automática
- Grabación de llamadas

### ⛔ Blacklist y DNC
- Lista de números bloqueados
- Integración con DNC nacional
- Importación/exportación
- Validación automática

### 📈 Reportes y Logs
- Histórico completo de llamadas
- Reportes de performance
- Logs detallados
- Exportación a CSV

## 👤 USUARIOS Y PERMISOS

### 🔑 Credenciales de Acceso

| Usuario     | Contraseña   | Permisos                      |
|-------------|--------------|-------------------------------|
| admin       | admin123     | Acceso total al sistema       |
| supervisor  | supervisor123| Campañas, monitoreo           |
| operador    | operador123  | Solo monitoreo                |

### 🛡️ Niveles de Acceso

- **Admin**: Configuración completa, usuarios, sistema
- **Supervisor**: Campañas, listas, reportes
- **Operador**: Visualización de datos, monitoreo

## 🔧 CONFIGURACIÓN TÉCNICA

### 📋 Variables de Entorno

```bash
# BASE DE DATOS
DATABASE_URL=postgresql://user:pass@host:5432/db
SUPABASE_URL=https://orxxocptgaeoyrtlxwkv.supabase.co
SUPABASE_KEY=your_supabase_key

# AUTENTICACIÓN
JWT_SECRET_KEY=sua-chave-secreta-muito-segura-aqui-2024
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30

# API
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=https://discador.vercel.app

# ASTERISK
ASTERISK_HOST=localhost
ASTERISK_PORT=5038
ASTERISK_USERNAME=admin
ASTERISK_PASSWORD=amp111
```

### 🗂️ Estructura de la Base de Datos

```sql
-- Tablas Principales
users           -- Usuarios del sistema
campaigns       -- Campañas de discado
contacts        -- Contactos de las campañas
call_logs       -- Logs de llamadas
blacklist       -- Números bloqueados
audios          -- Archivos de audio
trunks          -- Trunks SIP
dnc_lists       -- Listas DNC
dnc_numbers     -- Números DNC
roles           -- Roles del sistema
user_roles      -- Asociación usuario-rol
```

## 📞 INTEGRACIÓN ASTERISK

### 📁 Archivos de Configuración

1. **extensions_discador.conf** - Dialplan principal
2. **cli_rotation_agi.py** - Script AGI para rotación de CLIs
3. **Configuraciones SIP** - Trunks y proveedores

### 🔄 Contextos del Dialplan

- `discador-outbound` - Llamadas de salida
- `discador-presione1` - Sistema Presione 1
- `discador-voicemail-detection` - Detección de voicemail
- `discador-monitoring` - Monitoreo
- `discador-cli-rotation` - Rotación de CLIs

## 🛠️ INSTALACIÓN Y DEPLOY

### 1. Frontend (Vercel)
```bash
cd frontend
npm install
npm run build
# Deploy automático vía GitHub
```

### 2. Backend (Render.com)
```bash
cd backend
pip install -r requirements.txt
python main.py
# Deploy automático vía GitHub
```

### 3. Base de Datos (Supabase)
```sql
-- Ejecutar scripts SQL proporcionados
-- Configurar RLS (Row Level Security)
-- Configurar webhooks si es necesario
```

### 4. Asterisk (Servidor Local)
```bash
# Copiar archivos de configuración
cp asterisk_integration/* /etc/asterisk/
# Recargar configuraciones
asterisk -rx "dialplan reload"
asterisk -rx "sip reload"
```

## 📊 DATOS INICIALES

El sistema viene con datos de ejemplo:

- **3 usuarios** configurados
- **1 campaña** de prueba
- **8 contactos** de ejemplo
- **5 números** en blacklist
- **Configuraciones** predefinidas

## 🔍 MONITOREO

### 📈 Métricas Disponibles

- Llamadas por minuto
- Tasa de conexión
- Tiempo promedio de llamada
- Distribución por estado
- Performance de los operadores

### 🚨 Alertas

- Fallas de conexión
- Límites de llamadas
- Números bloqueados
- Errores del sistema

## 🔒 SEGURIDAD

### 🛡️ Medidas Implementadas

- Autenticación JWT
- Contraseñas hasheadas
- CORS configurado
- Rate limiting
- Validación de datos
- Logs de auditoría

## 📚 ENDPOINTS API

### 🔑 Autenticación
- `POST /api/v1/auth/login` - Login del usuario
- `GET /api/v1/auth/me` - Datos del usuario actual

### 📊 Dashboard
- `GET /api/v1/stats` - Estadísticas generales
- `GET /api/v1/monitoring/dashboard` - Dashboard

### 📞 Campañas
- `GET /api/v1/campaigns` - Listar campañas
- `POST /api/v1/campaigns` - Crear campaña
- `PUT /api/v1/campaigns/{id}` - Actualizar campaña

### 👥 Contactos
- `GET /api/v1/contacts` - Listar contactos
- `POST /api/v1/contacts/upload` - Subida de lista

### ⛔ Blacklist
- `GET /api/v1/blacklist` - Listar bloqueados
- `POST /api/v1/blacklist` - Agregar número

## 🚀 PRÓXIMOS PASOS

1. **Configurar Asterisk** con archivos proporcionados
2. **Importar listas** de contactos reales
3. **Configurar proveedores SIP** reales
4. **Ajustar parámetros** de discado
5. **Entrenar equipo** en el uso del sistema

## 📞 SOPORTE

Para soporte técnico:
- Documentación: `/docs` en el proyecto
- Issues: GitHub del proyecto
- Logs: Sistema de monitoreo

## 📄 LICENCIA

Sistema desarrollado para uso comercial.
Todos los derechos reservados.

---

**🎉 Sistema Discador Predictivo - Versión 1.0.0**
*Desarrollado con ❤️ para operaciones telefónicas eficientes* 