"""
Migracion para crear la tabla usuarios.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID
import uuid

# Revision Alembic - usa UUID como identificador
revision = '20230801000'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    """Aplica la migracion: crea la tabla usuarios"""
    op.create_table(
        'usuarios',
        sa.Column('id', UUID(as_uuid=True), primary_key=True, default=uuid.uuid4),
        sa.Column('nombre', sa.String(100), nullable=False),
        sa.Column('apellido', sa.String(100), nullable=False),
        sa.Column('email', sa.String(100), unique=True, nullable=False),
        sa.Column('hashed_password', sa.String(100), nullable=False),
        sa.Column('rol', sa.String(20), nullable=False, server_default='cliente'),
        sa.Column('activo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('fecha_creacion', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('fecha_actualizacion', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    
    # Crear indices
    op.create_index('idx_usuarios_id', 'usuarios', ['id'])
    op.create_index('idx_usuarios_email', 'usuarios', ['email'])
    op.create_index('idx_usuarios_rol', 'usuarios', ['rol'])

def downgrade():
    """Revierte la migracion: elimina la tabla usuarios"""
    op.drop_index('idx_usuarios_rol', 'usuarios')
    op.drop_index('idx_usuarios_email', 'usuarios')
    op.drop_index('idx_usuarios_id', 'usuarios')
    op.drop_table('usuarios') 