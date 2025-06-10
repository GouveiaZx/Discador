"""
Migracion para agregar los campos resultado y fecha_finalizacion a la tabla llamadas.
"""
from alembic import op
import sqlalchemy as sa

# Revision Alembic - usa UUID como identificador
revision = '20230802001'
down_revision = '20230801001'  # Debe apuntar a la migracion anterior
branch_labels = None
depends_on = None

def upgrade():
    """Aplica la migracion: agrega las columnas resultado y fecha_finalizacion"""
    # Agregar la columna resultado
    op.add_column('llamadas',
        sa.Column('resultado', sa.String(20), nullable=True)
    )
    
    # Agregar la columna fecha_finalizacion
    op.add_column('llamadas',
        sa.Column('fecha_finalizacion', sa.DateTime(), nullable=True)
    )
    
    # Crear el indice para resultado
    op.create_index('idx_llamadas_resultado', 'llamadas', ['resultado'])

def downgrade():
    """Revierte la migracion: elimina las columnas agregadas"""
    # Eliminar el indice
    op.drop_index('idx_llamadas_resultado', 'llamadas')
    
    # Eliminar las columnas
    op.drop_column('llamadas', 'fecha_finalizacion')
    op.drop_column('llamadas', 'resultado') 