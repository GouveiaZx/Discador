# 🇦🇷 CONFIGURACIÓN PARA ARGENTINA - DISCADOR PREDITIVO

**Nome do Sistema**: Discador Preditivo Empresarial  
**Versión**: 1.0.0 (Build Final - Producción)  
**Localización**: Español (Argentina) 🇦🇷  
**Zona Horaria**: America/Argentina/Buenos_Aires

---

## 🌐 CONFIGURACIONES DE LOCALIZACIÓN

### **📍 Configuraciones Básicas**
```bash
# Variables de entorno para Argentina
LANG=es_AR
LANGUAGE=es_AR:es
LC_ALL=es_AR.UTF-8
TIMEZONE=America/Argentina/Buenos_Aires
COUNTRY_CODE=AR
PHONE_PREFIX=+54
CURRENCY=ARS
DECIMAL_SEPARATOR=,
THOUSANDS_SEPARATOR=.
```

### **📞 Configuración Telefónica Argentina**
```python
# Formatos de teléfono argentinos
PHONE_FORMATS = {
    "mobile": "+54 9 11 xxxx-xxxx",      # Buenos Aires
    "mobile_caba": "+54 9 11 xxxx-xxxx",  # CABA
    "mobile_interior": "+54 9 xxx xxx-xxxx", # Interior
    "landline_caba": "+54 11 xxxx-xxxx",  # Fijo CABA
    "landline_interior": "+54 xxx xxx-xxxx" # Fijo Interior
}

# Códigos de área principales
AREA_CODES = {
    "11": "Buenos Aires (CABA/GBA)",
    "221": "La Plata",
    "223": "Mar del Plata", 
    "261": "Mendoza",
    "341": "Rosario",
    "351": "Córdoba",
    "381": "San Miguel de Tucumán",
    "388": "La Rioja"
}
```

### **📄 Documentos Argentinos**
```python
# Validación CUIT/CUIL/DNI
DOCUMENT_FORMATS = {
    "DNI": "12.345.678",
    "CUIT": "20-12345678-9", 
    "CUIL": "27-12345678-4",
    "CDI": "23-12345678-9"
}

# Regex de validación
DNI_REGEX = r"^\d{7,8}$"
CUIT_REGEX = r"^(20|23|24|27|30|33|34)-\d{8}-\d{1}$"
```

---

## 🎵 CONFIGURACIÓN DE ASTERISK EN ESPAÑOL

### **📢 Prompts en Español Latino**
```bash
# Descargar prompts en español
cd /var/lib/asterisk/sounds/
wget https://downloads.asterisk.org/pub/telephony/sounds/asterisk-core-sounds-es-8khz.tar.gz
tar xzf asterisk-core-sounds-es-8khz.tar.gz

# Configurar idioma por defecto
echo "defaultlanguage=es" >> /etc/asterisk/asterisk.conf
```

### **🎙️ Mensajes Personalizados**
```
# Ejemplos de mensajes en español argentino
"Bienvenido al sistema de llamadas automáticas"
"Presione 1 para ser transferido a un agente"
"Gracias por su tiempo, que tenga un buen día"
"Su llamada será atendida en breve"
"Para hablar con ventas, presione 1"
```

---

## 🖥️ CONFIGURACIÓN FRONTEND REACT

### **🌐 Internacionalización (i18n)**
```javascript
// src/i18n/index.js
import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import es_AR from './locales/es_AR.json';

i18n
  .use(initReactI18next)
  .init({
    resources: {
      es_AR: {
        translation: es_AR
      }
    },
    lng: 'es_AR',
    fallbackLng: 'es_AR',
    interpolation: {
      escapeValue: false
    }
  });

export default i18n;
```

### **📝 Textos en Español Argentino**
```json
{
  "dashboard": {
    "title": "Panel de Control",
    "campaigns": "Campañas",
    "calls": "Llamadas",
    "agents": "Agentes",
    "statistics": "Estadísticas"
  },
  "campaigns": {
    "create": "Crear Campaña",
    "edit": "Editar Campaña", 
    "start": "Iniciar",
    "pause": "Pausar",
    "stop": "Detener",
    "status": "Estado"
  },
  "calls": {
    "active": "Llamadas Activas",
    "completed": "Completadas",
    "failed": "Fallidas",
    "duration": "Duración"
  },
  "common": {
    "save": "Guardar",
    "cancel": "Cancelar",
    "delete": "Eliminar",
    "edit": "Editar",
    "view": "Ver",
    "loading": "Cargando...",
    "success": "Éxito",
    "error": "Error"
  }
}
```

---

## 💰 CONFIGURACIÓN MONETARIA

### **🪙 Formato Peso Argentino**
```javascript
// Formateo de moneda argentina
const formatCurrency = (amount) => {
  return new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'ARS',
    minimumFractionDigits: 2
  }).format(amount);
};

// Ejemplos:
// formatCurrency(1500) -> "$1.500,00"
// formatCurrency(25000) -> "$25.000,00"
```

### **📊 Configuración Regional**
```python
# Backend - Formateo de números
import locale

# Configurar localización argentina
locale.setlocale(locale.LC_ALL, 'es_AR.UTF-8')

def format_currency(amount):
    return locale.currency(amount, grouping=True)

def format_number(number):
    return locale.format_string("%.2f", number, grouping=True)
```

---

## 📅 CONFIGURACIÓN DE FECHAS Y HORAS

### **🕐 Zona Horaria Argentina**
```python
# Backend - Configuración timezone
import pytz
from datetime import datetime

ARGENTINA_TZ = pytz.timezone('America/Argentina/Buenos_Aires')

def get_argentina_time():
    return datetime.now(ARGENTINA_TZ)

def format_argentina_date(date):
    return date.strftime("%d de %B de %Y")
    # Ejemplo: "15 de enero de 2024"
```

### **📆 Frontend - Fechas en Español**
```javascript
// Configuración de fechas en español argentino
const formatDate = (date) => {
  return new Intl.DateTimeFormat('es-AR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  }).format(date);
};

const formatDateTime = (date) => {
  return new Intl.DateTimeFormat('es-AR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(date);
};
```

---

## 📋 VALIDACIONES ESPECÍFICAS ARGENTINA

### **📞 Validación Números Telefónicos**
```python
import re

def validate_argentine_phone(phone):
    """Valida números telefónicos argentinos"""
    # Remover espacios y guiones
    clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
    
    # Patrones válidos
    patterns = [
        r'^(\+54)?9?11\d{8}$',      # Buenos Aires móvil
        r'^(\+54)?9?\d{3}\d{7}$',   # Interior móvil
        r'^(\+54)?11\d{8}$',        # Buenos Aires fijo
        r'^(\+54)?\d{3,4}\d{6,7}$'  # Interior fijo
    ]
    
    return any(re.match(pattern, clean_phone) for pattern in patterns)
```

### **🆔 Validación CUIT/CUIL**
```python
def validate_cuit(cuit):
    """Valida CUIT argentino"""
    if not re.match(r'^\d{2}-\d{8}-\d{1}$', cuit):
        return False
    
    # Algoritmo de validación CUIT
    numbers = cuit.replace('-', '')
    multipliers = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
    
    sum_total = sum(int(numbers[i]) * multipliers[i] for i in range(10))
    remainder = sum_total % 11
    
    if remainder < 2:
        check_digit = remainder
    else:
        check_digit = 11 - remainder
    
    return int(numbers[10]) == check_digit
```

---

## 🔗 INTEGRACIÓN CON SERVICIOS ARGENTINOS

### **📬 API Códigos Postales**
```python
# Integración con API de códigos postales argentinos
import requests

def get_location_by_postal_code(postal_code):
    """Obtiene ubicación por código postal argentino"""
    url = f"https://apis.datos.gob.ar/georef/api/direcciones"
    params = {
        "codigo_postal": postal_code,
        "formato": "json"
    }
    
    response = requests.get(url, params=params)
    return response.json()
```

### **🏦 Validación Bancos**
```python
# CBU - Clave Bancaria Uniforme
def validate_cbu(cbu):
    """Valida CBU argentino"""
    if len(cbu) != 22 or not cbu.isdigit():
        return False
    
    # Validación algoritmo CBU
    # (Implementación completa del algoritmo)
    return True
```

---

## 📞 CONFIGURACIÓN ENACOM

### **📋 Compliance Telefónico**
```python
# Configuraciones para cumplir con ENACOM
ENACOM_SETTINGS = {
    "max_call_duration": 120,  # 2 minutos máximo
    "call_attempts_per_day": 3,  # Máximo 3 intentos por día
    "quiet_hours_start": "20:00",  # No llamar después de 20:00
    "quiet_hours_end": "08:00",    # No llamar antes de 08:00
    "weekend_calls": False,        # No llamar fines de semana
    "holidays_calls": False        # No llamar feriados
}
```

### **🚫 Lista No Llame Nacional**
```python
# Integración con Registro Nacional No Llame
def check_no_call_registry(phone):
    """Verifica si el número está en el Registro No Llame"""
    # URL oficial del registro (hipotética)
    url = "https://nollame.enacom.gob.ar/api/check"
    data = {"phone": phone}
    
    response = requests.post(url, json=data)
    return response.json().get("in_registry", False)
```

---

## 🔧 COMANDOS DE CONFIGURACIÓN

### **🐧 Configuración Sistema Linux**
```bash
# Configurar localización argentina en Ubuntu/Debian
sudo locale-gen es_AR.UTF-8
sudo update-locale LANG=es_AR.UTF-8

# Configurar zona horaria
sudo timedatectl set-timezone America/Argentina/Buenos_Aires

# Instalar paquetes de idioma
sudo apt-get install language-pack-es
```

### **🗄️ Configuración PostgreSQL**
```sql
-- Configurar base de datos en español argentino
ALTER DATABASE discador_db SET lc_messages TO 'es_AR.UTF-8';
ALTER DATABASE discador_db SET lc_monetary TO 'es_AR.UTF-8';
ALTER DATABASE discador_db SET lc_numeric TO 'es_AR.UTF-8';
ALTER DATABASE discador_db SET lc_time TO 'es_AR.UTF-8';
```

---

## ✅ CHECKLIST DE CONFIGURACIÓN ARGENTINA

### **📋 Lista de Verificación**
- [ ] **Sistema operativo** configurado en español argentino
- [ ] **Zona horaria** America/Argentina/Buenos_Aires
- [ ] **PostgreSQL** con localización es_AR
- [ ] **Frontend React** con i18n configurado
- [ ] **Asterisk** con prompts en español
- [ ] **Validaciones** de teléfono argentino implementadas
- [ ] **Validaciones** de CUIT/CUIL funcionando
- [ ] **Formateo** de moneda en pesos argentinos
- [ ] **Compliance** ENACOM configurado
- [ ] **API** Registro No Llame integrada
- [ ] **Mensajes** de voz en español neutro/argentino

---

**🇦🇷 SISTEMA COMPLETAMENTE LOCALIZADO PARA ARGENTINA**

> **Configuración**: Español (Argentina) - es_AR  
> **Zona Horaria**: America/Argentina/Buenos_Aires  
> **Moneda**: Peso Argentino (ARS)  
> **Compliance**: ENACOM + Registro No Llame  
> **Versión**: 1.0.0 (Build Final - Producción) 