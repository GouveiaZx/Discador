"""
Migracion para agregar los campos usuario_id y fecha_asignacion a la tabla llamadas.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# Revision Alembic - usa UUID como identificador
revision = '20230801001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Aplica la migracion: agrega las columnas usuario_id y fecha_asignacion"""
    # Agregar la columna usuario_id (con referencia a la tabla usuarios)
    op.add_column('llamadas',
        sa.Column('usuario_id', UUID(as_uuid=True), nullable=True)
    )
    
    # Agregar la columna fecha_asignacion
    op.add_column('llamadas',
        sa.Column('fecha_asignacion', sa.DateTime(), nullable=True)
    )
    
    # Crear el indice para usuario_id
    op.create_index('idx_llamadas_usuario_id', 'llamadas', ['usuario_id'])
    
    # Crear la clave foranea hacia usuarios
    op.create_foreign_key(
        'fk_llamadas_usuarios', 'llamadas', 'usuarios',
        ['usuario_id'], ['id'], ondelete='SET NULL'
    )

def downgrade():
    """Revierte la migracion: elimina las columnas agregadas"""
    # Eliminar la clave foranea
    op.drop_constraint('fk_llamadas_usuarios', 'llamadas', type_='foreignkey')
    
    # Eliminar el indice
    op.drop_index('idx_llamadas_usuario_id', 'llamadas')
    
    # Eliminar las columnas
    op.drop_column('llamadas', 'fecha_asignacion')
    op.drop_column('llamadas', 'usuario_id') 