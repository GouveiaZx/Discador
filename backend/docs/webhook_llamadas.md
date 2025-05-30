# Documentación: Webhook para Actualización de Estados de Llamadas

## Descripción

Esta funcionalidad proporciona un endpoint webhook que permite a sistemas externos (como centrales telefónicas o integraciones) notificar cambios en el estado de las llamadas de manera segura y validada.

## Objetivo

Permitir que sistemas externos puedan actualizar el estado de una llamada sin necesidad de acceso completo al sistema, respetando validaciones y reglas de negocio para garantizar la integridad de los datos.

## Características

- **Autenticación segura**: Mediante API Key en el encabezado HTTP
- **Validaciones estrictas**: Control de estados permitidos y transiciones válidas
- **Documentación Swagger**: Integrada con la API para facilitar pruebas
- **Auditoría**: Logging detallado de todas las operaciones

## API REST

### Ruta

```
POST /api/v1/llamadas/webhook
```

### Autenticación

Requiere API Key en el encabezado `X-API-Key`. La clave debe configurarse en la variable de entorno `WEBHOOK_API_KEY`.

### Payload (Cuerpo de la solicitud)

```json
{
  "llamada_id": 123,
  "nuevo_estado": "fallida"
}
```

### Estados Válidos

| Estado | Descripción |
|--------|-------------|
| en_progreso | Llamada en curso |
| conectada | Usuario ha contestado la llamada |
| finalizada | Llamada terminada correctamente |
| fallida | Error técnico o problema en la llamada |
| cancelada | Llamada cancelada por el sistema |

### Transiciones de Estado Permitidas

| Estado Actual | Estados Permitidos |
|---------------|-------------------|
| pendiente | en_progreso, cancelada, fallida |
| en_progreso | conectada, finalizada, fallida, cancelada |
| conectada | finalizada, fallida, cancelada |
| finalizada | *ninguno (estado terminal)* |
| fallida | *ninguno (estado terminal)* |
| cancelada | *ninguno (estado terminal)* |

### Respuesta Exitosa (200 OK)

```json
{
  "mensaje": "Estado de llamada actualizado",
  "estado_actual": "fallida"
}
```

### Respuestas de Error

- **403 Forbidden**: API Key inválida o no proporcionada
- **404 Not Found**: Llamada no encontrada
- **422 Unprocessable Entity**: Estado inválido o transición no permitida
- **500 Internal Server Error**: Error de servidor

## Ejemplos de Uso

### Usando curl

```bash
curl -X 'POST' \
  'https://api.discador.example.com/api/v1/llamadas/webhook' \
  -H 'X-API-Key: your_api_key_here' \
  -H 'Content-Type: application/json' \
  -d '{
    "llamada_id": 123,
    "nuevo_estado": "fallida"
  }'
```

### Usando Python

```python
import requests

# Configuración
api_url = "https://api.discador.example.com/api/v1/llamadas/webhook"
api_key = "your_api_key_here"

# Datos de la solicitud
data = {
    "llamada_id": 123,
    "nuevo_estado": "fallida"
}

# Encabezados
headers = {
    "X-API-Key": api_key,
    "Content-Type": "application/json"
}

# Enviar solicitud
response = requests.post(api_url, json=data, headers=headers)

# Procesar respuesta
if response.status_code == 200:
    print(f"Éxito: {response.json()}")
else:
    print(f"Error: {response.status_code} - {response.json()}")
```

## Consideraciones Técnicas

### Seguridad

- La API Key debe ser tratada como información sensible
- Se recomienda rotarla periódicamente
- Se registra cada intento de acceso con API Key inválida

### Validaciones

La funcionalidad implementa múltiples capas de validación:

1. **Esquema de datos**: Validación Pydantic del payload
2. **Validación de estados**: Solo se aceptan estados predefinidos
3. **Validación de transiciones**: Se controla que la transición de estado sea lógica y permitida
4. **Existencia de llamada**: Se verifica que la llamada exista antes de actualizar

### Auditoría

Todas las operaciones se registran en el sistema de logs con la siguiente información:
- ID de la llamada
- Estado anterior y nuevo
- Timestamp de la operación
- Resultado (éxito o error con detalle)

## Integración con Sistemas Externos

Para integrar su sistema con este webhook:

1. Solicite una API Key al administrador del sistema
2. Configure la API Key en su sistema (preferiblemente como variable de entorno)
3. Implemente la lógica para llamar al webhook cuando cambie el estado de una llamada
4. Implemente manejo de errores para los posibles códigos de respuesta

## Limitaciones

- No es posible modificar otros campos de la llamada (como `resultado` o `fecha_finalizacion`)
- No es posible cambiar el estado de una llamada que ya está en estado terminal (finalizada, fallida, cancelada)
- La API Key debe ser la misma para todas las llamadas al webhook desde el mismo sistema

## Preguntas Frecuentes

### ¿Puedo usar este webhook para crear nuevas llamadas?
No, este webhook está diseñado únicamente para actualizar el estado de llamadas existentes.

### ¿Qué debo hacer si necesito más información en la respuesta?
Contacte con el administrador del sistema para discutir posibles extensiones del webhook.

### ¿La API Key expira?
No automáticamente, pero se recomienda rotarla periódicamente por seguridad.

### ¿Puedo cambiar el estado de una llamada finalizada?
No, una vez que una llamada está en estado terminal (finalizada, fallida, cancelada) no se puede cambiar.

### ¿Se puede limitar el acceso a ciertas llamadas?
Actualmente la API Key da acceso a todas las llamadas. Si necesita segmentación, contacte al administrador. 