# 🎯 SISTEMA DISCADOR PREDICTIVO

> Sistema completo de discado predictivo con interfaz web moderna, backend robusto e integración con Asterisk.

## 🌟 CARACTERÍSTICAS PRINCIPALES

- **Frontend Moderno**: Interfaz React con diseño profesional
- **Backend Robusto**: API FastAPI con autenticación JWT
- **Base de Datos**: PostgreSQL/Supabase con RLS
- **Integración Asterisk**: Dialplan completo y scripts AGI
- **Monitoreo**: Dashboard en tiempo real
- **Gestión Completa**: Campañas, listas, blacklist, DNC

## 🌐 ENLACES DEL SISTEMA

- **🖥️ Frontend**: https://discador.vercel.app/
- **🔧 Backend**: https://discador.onrender.com/
- **📚 Documentación**: https://discador.onrender.com/documentacion

## 🔑 USUARIOS DE PRUEBA

| Usuario     | Contraseña    | Permisos                      |
|-------------|---------------|-------------------------------|
| admin       | admin123      | Acceso completo               |
| supervisor  | supervisor123 | Campañas y reportes           |
| operador    | operador123   | Monitoreo                     |

## 📁 ESTRUCTURA DEL PROYECTO

```
Discador-main/
├── 🎨 frontend/              # Interfaz React + Vite
├── ⚙️ backend/               # API FastAPI + Pydantic v2
├── 📞 asterisk_integration/  # Configuraciones Asterisk + AGI
├── 📚 docs/                  # Documentación específica
├── 🗄️ database/              # Scripts de base de datos
├── 🔄 migrations/            # Migraciones SQL
├── 📋 README_SISTEMA_COMPLETO.md  # Documentación completa
└── 🚀 INICIO_RAPIDO.md       # Guía de inicio rápido
```

## ⚡ INICIO RÁPIDO

### 1. Acceso Inmediato
```
🌐 https://discador.vercel.app/
👤 admin / admin123
```

### 2. Primer Uso (5 minutos)
1. **Login** → Dashboard principal
2. **Campañas** → Visualizar campaña de prueba
3. **Contactos** → 8 contactos incluidos
4. **Monitor** → Estadísticas en tiempo real

📖 **Guía completa**: `INICIO_RAPIDO.md`

## 🛠️ INSTALACIÓN COMPLETA

### Frontend (Vercel)
```bash
cd frontend
npm install
npm run build
# Deploy automático vía GitHub
```

### Backend (Render.com)
```bash
cd backend
pip install -r requirements.txt
python main.py
# Deploy automático vía GitHub
```

### Asterisk (Opcional)
```bash
cp asterisk_integration/* /etc/asterisk/
asterisk -rx "dialplan reload"
```

## 🚀 FUNCIONALIDADES

### 📊 Dashboard Profesional
- Estadísticas en tiempo real
- Gráficos de performance
- Alertas y notificaciones
- Monitoreo de llamadas

### 📞 Discado Predictivo
- Algoritmo inteligente de predicción
- Detección automática de voicemail (AMD)
- Sistema "Presione 1" completo
- Rotación inteligente de CLIs
- Balanceamiento de carga

### 👥 Gestión de Campañas
- Creación y edición de campañas
- Subida de listas CSV (hasta 1000 contactos)
- Configuración de horarios de funcionamiento
- Control de intentos e intervalos
- Reportes detallados de performance

### ⛔ Blacklist y DNC
- Lista de números bloqueados
- Integración con DNC nacional
- Importación/exportación de listas
- Validación automática en tiempo real

### 🔊 Sistema de Audio
- Reproducción de audios personalizados
- Detección de DTMF
- Transferencia automática
- Grabación de llamadas

## 💻 TECNOLOGÍAS

### Frontend
- **React 18** + **Vite** + **TailwindCSS**
- **Axios** para llamadas API
- **React Router** para navegación
- **Lucide React** para íconos

### Backend
- **FastAPI** + **Pydantic v2**
- **SQLAlchemy** + **PostgreSQL**
- **JWT** para autenticación
- **CORS** configurado

### Infraestructura
- **Vercel** (Frontend)
- **Render.com** (Backend)
- **Supabase** (Base de datos)
- **Asterisk** (PBX/AGI)

## 📊 DATOS INCLUIDOS

El sistema ya viene configurado con:
- ✅ **3 usuarios** preconfigurados
- ✅ **1 campaña** de prueba activa
- ✅ **8 contactos** de ejemplo
- ✅ **5 números** en blacklist
- ✅ **Configuraciones** por defecto optimizadas

## 📚 DOCUMENTACIÓN

| Archivo | Descripción |
|---------|-------------|
| `README_SISTEMA_COMPLETO.md` | Documentación técnica completa |
| `INICIO_RAPIDO.md` | Guía de inicio rápido (5 min) |
| `backend/config.env.example` | Variables de entorno |
| `docs/` | Documentación específica por módulo |

## 🆘 SOPORTE

### Problemas Comunes
- **Login falla**: Esperá 1-2 min (backend reiniciándose)
- **Datos no cargan**: Verificá conexión a internet
- **Upload falla**: Formato CSV correcto (phone_number, name)

### Contacto
- 📧 Issues en GitHub
- 📋 Logs en sistema de monitoreo
- 📖 Documentación completa en archivos MD

## ✅ ESTADO DEL SISTEMA

**🎉 Sistema 100% funcional y listo para producción**

- ✅ Frontend sin errores
- ✅ Backend con todos los endpoints funcionando
- ✅ Base de datos configurada
- ✅ Autenticación JWT implementada
- ✅ Integración Asterisk lista
- ✅ CORS configurado
- ✅ Datos de prueba incluidos

---

**🎯 Sistema Discador Predictivo v1.0.0**  
*Desarrollado con ❤️ para operaciones telefónicas eficientes* 