# Documentación: Finalizar Llamada

## Descripción

Esta funcionalidad permite a usuarios (administradores o integradores) finalizar una llamada en curso y registrar su resultado. Esto es útil para:

- Marcar llamadas como finalizadas manualmente
- Registrar el resultado de una llamada (contestada, no contesta, buzón, etc.)
- Calcular la duración de las llamadas
- Liberar al usuario para atender otras llamadas

## Modelo de Datos

Se han agregado los siguientes campos al modelo `Llamada`:

- `resultado`: String que almacena el resultado de la llamada (contestada, no_contesta, buzon, numero_invalido, otro)
- `fecha_finalizacion`: DateTime que registra cuándo se finalizó la llamada

## API REST

### Ruta

```
POST /api/v1/llamadas/finalizar
```

### Autenticación

Requiere usuario autenticado con permisos para gestionar llamadas.

### Cuerpo de la Solicitud

```json
{
  "llamada_id": 123,
  "resultado": "contestada"
}
```

Donde `resultado` puede ser uno de los siguientes valores:
- `contestada`: La llamada fue respondida por una persona
- `no_contesta`: Nadie respondió la llamada
- `buzon`: La llamada fue dirigida a un buzón de voz
- `numero_invalido`: El número no existe o no es válido
- `otro`: Otro resultado no categorizado

### Respuesta Exitosa (200 OK)

```json
{
  "mensaje": "Llamada finalizada correctamente",
  "llamada_id": 123,
  "estado": "finalizada",
  "resultado": "contestada"
}
```

### Respuestas de Error

- **400 Bad Request**: Si el resultado no es válido o la llamada ya está finalizada
- **403 Forbidden**: Si el usuario no tiene permisos para finalizar la llamada
- **404 Not Found**: Si la llamada no existe
- **500 Internal Server Error**: Si ocurre un error interno

## Validaciones

1. El usuario debe tener permisos para gestionar llamadas
2. La llamada debe existir
3. La llamada debe pertenecer al usuario (excepto para administradores)
4. La llamada debe estar en estado "en_progreso" o "conectada"
5. El resultado debe ser uno de los valores permitidos

## Flujo de Proceso

1. El usuario envía la solicitud con el ID de la llamada y el resultado
2. Se verifica que el usuario tenga permisos
3. Se busca la llamada en la base de datos
4. Se valida que la llamada exista y pertenezca al usuario
5. Se valida que la llamada esté en un estado que permita finalizarla
6. Se actualiza el estado a "finalizada", se registra el resultado y la fecha de finalización
7. Se calcula la duración de la llamada
8. Se devuelve la respuesta con los detalles de la llamada finalizada

## Pruebas

Se han implementado pruebas unitarias para:

1. Finalización exitosa de llamadas
2. Finalización de llamadas en diferentes estados
3. Validación de permisos de usuario
4. Validación de propiedad de la llamada
5. Validación de estados permitidos
6. Validación de resultados permitidos
7. Manejo de errores de base de datos

## Consideraciones Futuras

- Agregar más tipos de resultados específicos
- Implementar estadísticas basadas en los resultados
- Añadir notas o comentarios al finalizar una llamada
- Integrar con sistemas de calidad y monitoreo 