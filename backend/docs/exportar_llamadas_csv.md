# Documentación: Exportación de Llamadas Finalizadas a CSV

## Descripción

Esta funcionalidad permite a los administradores exportar todas las llamadas con estado "finalizada" en formato CSV para su posterior análisis o integración con otras herramientas.

## Objetivo

Facilitar el acceso a los datos históricos de llamadas finalizadas para:
- Análisis de resultados
- Reportes de gestión
- Auditorías
- Integración con herramientas externas de análisis o BI

## Arquitectura

La implementación se divide en:
1. Servicio: Consulta y prepara los datos, genera el CSV en memoria
2. Ruta REST: Maneja autenticación, encapsula la respuesta y configura los headers para descarga

## API REST

### Ruta

```
GET /api/v1/llamadas/exportar
```

### Autenticación

Acceso restringido a usuarios con rol de administrador.

### Respuesta Exitosa (200 OK)

Se devuelve un archivo CSV descargable con las siguientes columnas:

| Columna | Descripción |
|---------|-------------|
| llamada_id | Identificador único de la llamada |
| numero_destino | Número de teléfono al que se realizó la llamada |
| estado | Estado de la llamada (siempre 'finalizada') |
| resultado | Resultado de la llamada (contestada, no_contesta, buzon, etc.) |
| fecha_asignacion | Fecha y hora en formato ISO de la asignación |
| fecha_conexion | Fecha y hora en formato ISO de la conexión |
| fecha_finalizacion | Fecha y hora en formato ISO de la finalización |
| duracion_segundos | Duración total de la llamada en segundos |
| usuario_email | Correo electrónico del usuario que atendió la llamada |

### Headers de Respuesta

```
Content-Type: text/csv
Content-Disposition: attachment; filename=llamadas_finalizadas_YYYYMMDD_HHMMSS.csv
```

### Respuestas de Error

- **403 Forbidden**: Si el usuario no tiene rol de administrador
- **500 Internal Server Error**: Si ocurre un error al procesar la solicitud

## Implementación

### Servicio

```python
@staticmethod
def exportar_llamadas_finalizadas_csv(db: Session) -> str:
    """
    Exporta todas las llamadas con estado 'finalizada' a un formato CSV.
    """
    # 1. Consulta llamadas finalizadas con join a usuarios
    # 2. Crea buffer en memoria para CSV
    # 3. Escribe encabezados y datos
    # 4. Retorna contenido como string
```

### Ruta

```python
@router.get("/exportar")
async def exportar_llamadas_finalizadas(usuario_actual: Usuario, db: Session):
    """
    Exporta todas las llamadas con estado 'finalizada' a un archivo CSV descargable.
    """
    # 1. Verifica permisos de administrador
    # 2. Obtiene contenido CSV del servicio
    # 3. Devuelve como respuesta descargable
```

## Consideraciones Técnicas

- El CSV se genera completamente en memoria, sin escribir a disco
- Las fechas se formatean en formato ISO (YYYY-MM-DDTHH:MM:SS)
- Se incluye timestamp en el nombre del archivo para evitar problemas de caché
- La consulta está optimizada para grandes volúmenes de datos usando JOIN y filtros específicos

## Ejemplo de Uso desde un Cliente

### Desde un Navegador
Para usuarios administradores, simplemente navegar a:
```
https://api.discador.example.com/api/v1/llamadas/exportar
```
El navegador descargará automáticamente el archivo CSV.

### Desde Código

```python
import requests

# Autenticación
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Petición de exportación
response = requests.get(
    "https://api.discador.example.com/api/v1/llamadas/exportar",
    headers={"Authorization": f"Bearer {token}"},
    stream=True  # Importante para archivos grandes
)

# Guardar el archivo CSV
if response.status_code == 200:
    with open("llamadas_finalizadas.csv", "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print("Archivo descargado correctamente")
else:
    print(f"Error: {response.json()}")
```

## Casos de Uso

- **Informes mensuales**: Exportar datos para generar informes de rendimiento
- **Análisis de tendencias**: Analizar resultados de llamadas en herramientas externas
- **Auditorías**: Documentar actividad histórica para cumplimiento normativo
- **Integración con CRM**: Importar los resultados de llamadas en sistemas externos

## Consideraciones Futuras

- Añadir filtros para exportar por fecha (rango específico)
- Permitir selección de columnas específicas
- Implementar formatos adicionales (Excel, JSON, etc.)
- Añadir exportación asíncrona con notificación para conjuntos de datos muy grandes 