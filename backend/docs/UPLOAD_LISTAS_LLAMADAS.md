# Documentación del Endpoint de Upload de Listas de Llamadas

## Descripción

Este endpoint permite subir archivos CSV o TXT con números de teléfono para crear listas de llamadas en el sistema. Los números son validados, normalizados y almacenados en la base de datos con detección automática de duplicados.

## Endpoints Disponibles

### POST `/api/v1/listas-llamadas/upload`

Sube un archivo con números de teléfono y crea una nueva lista.

**Parámetros:**
- `archivo` (file): Archivo CSV o TXT con números de teléfono
- `nombre_lista` (string): Nombre único para la lista
- `descripcion` (string, opcional): Descripción de la lista

**Formatos de archivo soportados:**
- **CSV**: Primera columna debe contener los números (puede tener header)
- **TXT**: Un número por línea

**Ejemplo de uso:**

```bash
curl -X POST "http://localhost:8000/api/v1/listas-llamadas/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "archivo=@numeros.csv" \
  -F "nombre_lista=Lista Campaña Diciembre" \
  -F "descripcion=Números para campaña de diciembre 2023"
```

**Respuesta exitosa:**

```json
{
  "mensaje": "Archivo procesado exitosamente. 245 números válidos guardados de 250 líneas procesadas. 3 números inválidos encontrados. 2 números duplicados removidos.",
  "lista_id": 1,
  "nombre_lista": "Lista Campaña Diciembre",
  "archivo_original": "numeros.csv",
  "total_numeros_archivo": 250,
  "numeros_validos": 245,
  "numeros_invalidos": 3,
  "numeros_duplicados": 2,
  "errores": [
    "Línea 45: Formato de número inválido - 'abc123'",
    "Línea 67: Número duplicado - '+54911234567'",
    "Línea 120: Longitud inválida: 5 dígitos - '12345'"
  ]
}
```

### GET `/api/v1/listas-llamadas/`

Lista todas las listas de llamadas disponibles.

**Parámetros de query:**
- `skip` (int): Número de registros a saltar (paginación)
- `limit` (int): Número máximo de registros a retornar

### GET `/api/v1/listas-llamadas/{lista_id}`

Obtiene los detalles de una lista específica.

**Parámetros:**
- `lista_id` (int): ID de la lista
- `incluir_numeros` (bool): Si incluir la lista completa de números

### PUT `/api/v1/listas-llamadas/{lista_id}`

Actualiza los metadatos de una lista.

### DELETE `/api/v1/listas-llamadas/{lista_id}`

Elimina una lista y todos sus números asociados.

## Validación de Números de Teléfono

### Formatos Aceptados

El sistema acepta números argentinos en los siguientes formatos:

- `+54 9 11 1234-5678` (formato internacional completo)
- `011 1234-5678` (formato local con código de área)
- `11 1234 5678` (sin prefijos)
- `1112345678` (números concatenados)
- `12345678` (números cortos - se asume Buenos Aires)

### Normalización

Todos los números válidos son normalizados al formato internacional argentino:
`+549XXXXXXXXXX`

Ejemplos:
- `011 1234-5678` → `+5491112345678`
- `11 1234 5678` → `+5491112345678`
- `+54 9 11 1234-5678` → `+5491112345678`

### Validaciones Aplicadas

1. **Formato**: Solo números argentinos válidos
2. **Longitud**: Entre 11 y 15 dígitos
3. **Duplicados**: Automáticamente removidos dentro del mismo archivo
4. **Caracteres**: Se permiten espacios, guiones y paréntesis que son removidos automáticamente

## Manejo de Errores

### Errores de Validación de Archivo

- **400**: Tipo de archivo no válido (solo CSV y TXT)
- **400**: Archivo demasiado grande (máximo 10MB)
- **400**: Lista con nombre duplicado
- **400**: Error de codificación (debe ser UTF-8)

### Errores de Número

Los números inválidos no detienen el procesamiento, pero se reportan en la respuesta:

```json
{
  "errores": [
    "Línea 5: Número vacío",
    "Línea 12: Formato de número inválido - 'texto'",
    "Línea 18: Longitud inválida: 25 dígitos - '+541234567890123456789012'",
    "Línea 25: Número duplicado - '+5491112345678'"
  ]
}
```

## Ejemplos de Archivos

### Archivo CSV con Header

```csv
telefono,nombre,nota
+5491112345678,Juan Pérez,Cliente VIP
011 8765-4321,María García,
11 9999 8888,Pedro López,Llamar por la mañana
```

### Archivo CSV sin Header

```csv
+5491112345678
011 8765-4321
11 9999 8888
```

### Archivo TXT

```
+5491112345678
011 8765-4321
11 9999 8888
```

## Base de Datos

### Tabla: `listas_llamadas`

Almacena los metadatos de cada lista:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER | ID único |
| nombre | VARCHAR(100) | Nombre único de la lista |
| descripcion | VARCHAR(255) | Descripción opcional |
| archivo_original | VARCHAR(255) | Nombre del archivo original |
| total_numeros | INTEGER | Total de líneas en el archivo |
| numeros_validos | INTEGER | Números válidos guardados |
| numeros_duplicados | INTEGER | Duplicados encontrados |
| fecha_creacion | TIMESTAMP | Fecha de creación |
| fecha_actualizacion | TIMESTAMP | Última actualización |
| activa | BOOLEAN | Si la lista está activa |

### Tabla: `numeros_llamadas`

Almacena los números individuales:

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INTEGER | ID único |
| numero | VARCHAR(20) | Número original del archivo |
| numero_normalizado | VARCHAR(20) | Número normalizado |
| id_lista | INTEGER | Referencia a la lista |
| valido | BOOLEAN | Si el número es válido |
| notas | TEXT | Notas adicionales |
| fecha_creacion | TIMESTAMP | Fecha de creación |

## Tests

Para ejecutar los tests del endpoint:

```bash
cd backend
python -m pytest tests/test_lista_llamadas.py -v
```

### Tests Incluidos

- Validación de números argentinos
- Normalización de formatos
- Procesamiento de archivos CSV y TXT
- Upload exitoso y manejo de errores
- Operaciones CRUD de listas
- Detección de duplicados

## Migraciones

Para crear las tablas en la base de datos:

```bash
psql -d discador -f migrations/create_listas_llamadas.sql
```

## Consideraciones de Performance

- **Archivos grandes**: Máximo 10MB por archivo
- **Números por lista**: Sin límite teórico, pero se recomienda hasta 100,000 números por lista
- **Procesamiento**: Asíncrono para no bloquear la API
- **Índices**: Optimizados para búsquedas por número normalizado

## Integración con Campañas

Las listas creadas pueden ser utilizadas posteriormente en campañas de llamadas a través de otros endpoints del sistema. 