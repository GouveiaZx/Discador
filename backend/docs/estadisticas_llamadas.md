# Documentación: Estadísticas de Llamadas

## Descripción

Esta funcionalidad proporciona métricas agregadas sobre las llamadas realizadas por el sistema, permitiendo a los administradores visualizar el estado global del discador y la distribución de llamadas por diferentes criterios.

## Objetivo

Ofrecer una visión general del uso del sistema de llamadas para facilitar la toma de decisiones, monitoreo del rendimiento y distribución de carga entre usuarios.

## API REST

### Ruta

```
GET /api/v1/llamadas/estadisticas
```

### Autenticación

Requiere usuario autenticado con rol de administrador. Los usuarios sin este rol recibirán un error 403 Forbidden.

### Respuesta Exitosa (200 OK)

```json
{
  "total_llamadas": 132,
  "por_estado": {
    "pendiente": 12,
    "en_progreso": 15,
    "conectada": 20,
    "finalizada": 85
  },
  "por_resultado": {
    "contestada": 40,
    "no_contesta": 30,
    "buzon": 10,
    "numero_invalido": 5,
    "otro": 0
  },
  "en_progreso_por_usuario": {
    "integrador1@example.com": 2,
    "integrador2@example.com": 3
  }
}
```

### Respuestas de Error

- **403 Forbidden**: Si el usuario no tiene rol de administrador
- **500 Internal Server Error**: Si ocurre un error al procesar la solicitud

## Métricas Disponibles

### Total de Llamadas
Número total de llamadas registradas en el sistema.

### Llamadas por Estado
Conteo de llamadas agrupadas por su estado actual:
- **pendiente**: Llamadas que aún no han sido iniciadas
- **en_progreso**: Llamadas que están siendo procesadas actualmente
- **conectada**: Llamadas que han sido conectadas (el usuario presionó 1)
- **finalizada**: Llamadas que han sido completadas

### Llamadas por Resultado
Conteo de llamadas finalizadas agrupadas por su resultado:
- **contestada**: La llamada fue respondida por una persona
- **no_contesta**: Nadie respondió la llamada
- **buzon**: La llamada fue dirigida a un buzón de voz
- **numero_invalido**: El número no existe o no es válido
- **otro**: Otro resultado no categorizado

### Llamadas en Progreso por Usuario
Conteo de llamadas actualmente en progreso agrupadas por el correo electrónico del usuario asignado.

## Implementación Técnica

### Optimización de Consultas

La implementación utiliza consultas SQL optimizadas mediante:
- Uso de `func.count` y `group_by` para realizar agregaciones en la base de datos
- Joins optimizados para resolver los IDs de usuario a correos electrónicos
- Filtros selectivos para reducir el conjunto de datos procesado

### Consideraciones de Rendimiento

- Las consultas están diseñadas para funcionar eficientemente con grandes volúmenes de datos
- Se utilizan índices en las columnas relevantes (estado, resultado, usuario_id)
- Los resultados se formatean en el formato JSON requerido para facilitar su consumo por frontends

## Casos de Uso

- **Monitoreo en tiempo real**: Visualizar la cantidad de llamadas en progreso y por usuario
- **Análisis de resultados**: Evaluar la distribución de resultados de llamadas
- **Planificación de capacidad**: Determinar la carga del sistema y distribución de llamadas
- **Dashboards de administración**: Alimentar interfaces gráficas con métricas relevantes

## Ejemplo de Uso

```python
import requests

# Autenticación
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# Petición de estadísticas
response = requests.get(
    "https://api.discador.example.com/api/v1/llamadas/estadisticas",
    headers={"Authorization": f"Bearer {token}"}
)

# Procesar respuesta
if response.status_code == 200:
    estadisticas = response.json()
    print(f"Total de llamadas: {estadisticas['total_llamadas']}")
    print(f"Llamadas en progreso: {estadisticas['por_estado']['en_progreso']}")
    # Más procesamiento...
else:
    print(f"Error: {response.json()}")
```

## Consideraciones Futuras

- Agregar filtros por fecha para obtener estadísticas de periodos específicos
- Incluir métricas de duración promedio de llamadas
- Agregar métricas por campaña
- Implementar cache para mejorar el rendimiento en sistemas con muchas llamadas 