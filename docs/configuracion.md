# Configuración del Sistema

Este documento explica cómo configurar el sistema de Discador Predictivo utilizando variables de entorno.

## Archivo .env

La aplicación utiliza un archivo `.env` para cargar la configuración. Debe crear este archivo en la raíz del proyecto siguiendo el formato de `.env.example`.

Ejemplo de contenido para `.env`:

```
# Configuración general
APP_NAME=Discador Predictivo
APP_VERSION=1.0.0
DEBUG=True

# Configuración del servidor
PUERTO=8000
HOST=0.0.0.0

# Configuración de la base de datos
# Si se proporciona DB_URL, se usará esta en lugar de construirla a partir de los otros parámetros
# DB_URL=postgresql://usuario:contraseña@host:puerto/nombre_db
DB_HOST=localhost
DB_PUERTO=5432
DB_USUARIO=postgres
DB_PASSWORD=postgres
DB_NOMBRE=discador

# Configuración de Asterisk
ASTERISK_HOST=localhost
ASTERISK_PUERTO=5038
ASTERISK_USUARIO=admin
ASTERISK_PASSWORD=admin

# Configuración de STT (Vosk)
VOSK_MODEL_PATH=./vosk-model-en-us-0.22
```

## Cómo funciona la configuración

La aplicación utiliza Pydantic para validar y gestionar la configuración. Los pasos son:

1. Al iniciar la aplicación, se carga el archivo `.env`
2. La clase `Configuracion` procesa las variables de entorno
3. Se validan los valores según los tipos definidos
4. Si falta `DB_URL`, se construye automáticamente a partir de los componentes individuales

## Variables disponibles

| Variable | Descripción | Valor por defecto |
|----------|-------------|-------------------|
| APP_NAME | Nombre de la aplicación | "Discador Predictivo" |
| APP_VERSION | Versión de la aplicación | "1.0.0" |
| DEBUG | Modo de depuración | False |
| PUERTO | Puerto del servidor | 8000 |
| HOST | Host del servidor | "0.0.0.0" |
| DB_URL | URL completa de la base de datos | Construida automáticamente |
| DB_HOST | Host de la base de datos | "localhost" |
| DB_PUERTO | Puerto de la base de datos | 5432 |
| DB_USUARIO | Usuario de la base de datos | "postgres" |
| DB_PASSWORD | Contraseña de la base de datos | "postgres" |
| DB_NOMBRE | Nombre de la base de datos | "discador" |
| ASTERISK_HOST | Host de Asterisk | "localhost" |
| ASTERISK_PUERTO | Puerto de Asterisk | 5038 |
| ASTERISK_USUARIO | Usuario de Asterisk | "admin" |
| ASTERISK_PASSWORD | Contraseña de Asterisk | "admin" |
| VOSK_MODEL_PATH | Ruta al modelo de Vosk | "./vosk-model-en-us-0.22" |

## Uso en el código

Para usar la configuración en cualquier parte del código:

```python
from app.config import configuracion

# Ejemplos de uso
print(configuracion.APP_NAME)
print(configuracion.DB_URL)
print(configuracion.PUERTO)
```

## Recarga de configuración

Si necesita recargar la configuración durante la ejecución (por ejemplo, después de cambiar el archivo `.env`), puede utilizar la función `recargar_configuracion()`:

```python
from app.config import recargar_configuracion

# Recargar desde el archivo .env predeterminado
nueva_config = recargar_configuracion()

# O especificar un archivo diferente
nueva_config = recargar_configuracion("/ruta/a/otro/archivo.env")
```

Esta función actualizará todas las variables globales de configuración, asegurando que toda la aplicación utilice los nuevos valores. 