-- Migración para crear las tablas de listas de llamadas
-- Ejecutar como migration para crear las nuevas tablas

-- Crear tabla listas_llamadas
CREATE TABLE IF NOT EXISTS listas_llamadas (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL UNIQUE,
    descripcion VARCHAR(255),
    archivo_original VARCHAR(255) NOT NULL,
    total_numeros INTEGER DEFAULT 0 NOT NULL,
    numeros_validos INTEGER DEFAULT 0 NOT NULL,
    numeros_duplicados INTEGER DEFAULT 0 NOT NULL,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    fecha_actualizacion TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL,
    activa BOOLEAN DEFAULT TRUE NOT NULL
);

-- Crear tabla numeros_llamadas
CREATE TABLE IF NOT EXISTS numeros_llamadas (
    id SERIAL PRIMARY KEY,
    numero VARCHAR(20) NOT NULL,
    numero_normalizado VARCHAR(20) NOT NULL,
    id_lista INTEGER NOT NULL REFERENCES listas_llamadas(id) ON DELETE CASCADE,
    valido BOOLEAN DEFAULT TRUE NOT NULL,
    notas TEXT,
    fecha_creacion TIMESTAMP WITH TIME ZONE DEFAULT NOW() NOT NULL
);

-- Crear índices para listas_llamadas
CREATE INDEX IF NOT EXISTS idx_listas_nombre ON listas_llamadas(nombre);
CREATE INDEX IF NOT EXISTS idx_listas_activa ON listas_llamadas(activa);
CREATE INDEX IF NOT EXISTS idx_listas_fecha ON listas_llamadas(fecha_creacion);

-- Crear índices para numeros_llamadas
CREATE INDEX IF NOT EXISTS idx_numeros_numero ON numeros_llamadas(numero);
CREATE INDEX IF NOT EXISTS idx_numeros_normalizado ON numeros_llamadas(numero_normalizado);
CREATE INDEX IF NOT EXISTS idx_numeros_lista ON numeros_llamadas(id_lista);
CREATE INDEX IF NOT EXISTS idx_numeros_valido ON numeros_llamadas(valido);

-- Crear índice único para evitar duplicados por lista
CREATE UNIQUE INDEX IF NOT EXISTS idx_unique_numero_lista 
ON numeros_llamadas(numero_normalizado, id_lista);

-- Trigger para actualizar fecha_actualizacion automáticamente
CREATE OR REPLACE FUNCTION update_fecha_actualizacion()
RETURNS TRIGGER AS $$
BEGIN
    NEW.fecha_actualizacion = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_listas_llamadas_fecha
BEFORE UPDATE ON listas_llamadas
FOR EACH ROW
EXECUTE FUNCTION update_fecha_actualizacion();

-- Comentarios en las tablas
COMMENT ON TABLE listas_llamadas IS 'Tabla para almacenar listas de números de teléfono';
COMMENT ON TABLE numeros_llamadas IS 'Tabla para almacenar números individuales de cada lista';

COMMENT ON COLUMN listas_llamadas.nombre IS 'Nombre único de la lista';
COMMENT ON COLUMN listas_llamadas.archivo_original IS 'Nombre del archivo original subido';
COMMENT ON COLUMN listas_llamadas.total_numeros IS 'Total de números en el archivo original';
COMMENT ON COLUMN listas_llamadas.numeros_validos IS 'Cantidad de números válidos guardados';
COMMENT ON COLUMN listas_llamadas.numeros_duplicados IS 'Cantidad de números duplicados encontrados';

COMMENT ON COLUMN numeros_llamadas.numero IS 'Número de teléfono original del archivo';
COMMENT ON COLUMN numeros_llamadas.numero_normalizado IS 'Número normalizado al formato argentino +549XXXXXXXXXX';
COMMENT ON COLUMN numeros_llamadas.id_lista IS 'Referencia a la lista a la que pertenece el número';
COMMENT ON COLUMN numeros_llamadas.valido IS 'Indica si el número pasó las validaciones'; 