# Backend del Discador Predictivo

Este directorio contiene el código backend del sistema de Discador Predictivo, implementado con FastAPI.

## Estructura del Proyecto

```
📦 backend/
├── main.py                # Punto de entrada de la aplicación
├── requirements.txt       # Dependencias del proyecto
└── app/                   # Paquete principal de la aplicación
    ├── __init__.py        # Inicializador del paquete app
    ├── config.py          # Configuración de la aplicación
    ├── database.py        # Configuración de la base de datos
    ├── routes/            # Controladores y rutas de la API
    │   ├── __init__.py
    │   ├── llamadas.py    # Rutas para gestionar llamadas
    │   ├── listas.py      # Rutas para gestionar listas y lista negra
    │   ├── cli.py         # Rutas para generación de CLI
    │   ├── stt.py         # Rutas para reconocimiento de voz
    │   └── reportes.py    # Rutas para generación de reportes
    ├── models/            # Modelos de datos (SQLAlchemy)
    │   ├── __init__.py
    │   ├── lista_negra.py # Modelo para lista negra
    │   ├── campana.py     # Modelo para campañas
    │   ├── lead.py        # Modelo para leads
    │   └── llamada.py     # Modelo para llamadas
    ├── services/          # Servicios de lógica de negocio
    │   └── __init__.py
    └── utils/             # Utilidades
        ├── __init__.py
        └── logger.py      # Configuración de logs
```

## Instalación

1. Crea un entorno virtual:
   ```
   python -m venv venv
   ```

2. Activa el entorno virtual:
   - Windows: `venv\Scripts\activate`
   - Linux/Mac: `source venv/bin/activate`

3. Instala las dependencias:
   ```
   pip install -r requirements.txt
   ```

4. Crea un archivo `.env` en la raíz basado en el ejemplo proporcionado en la documentación.

## Ejecución

Para ejecutar la aplicación en modo desarrollo:

```
python main.py
```

La API estará disponible en `http://localhost:8000`.

La documentación de la API estará disponible en:
- Swagger UI: `http://localhost:8000/documentacion`
- ReDoc: `http://localhost:8000/redoc`

## Configuración

La aplicación utiliza un sistema de configuración basado en variables de entorno y un archivo `.env`. 
Para más detalles, consulta el archivo `app/config.py` y la documentación en `docs/configuracion.md`. 