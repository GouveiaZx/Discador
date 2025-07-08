"""
Configuração de conexão com banco de dados
Suporta SQLite local e PostgreSQL (Supabase)
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Base para os models
Base = declarative_base()

# Configuração do banco
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    # Usar SQLite local por padrão para teste
    "sqlite:///./discador.db"
)

# Configurar engine baseado no tipo de banco
if DATABASE_URL.startswith("sqlite"):
    # SQLite local para desenvolvimento
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=True  # Log das queries em desenvolvimento
    )
else:
    # PostgreSQL para produção (Supabase)
    engine = create_engine(
        DATABASE_URL,
        echo=False,  # Sem log em produção
        pool_size=10,
        max_overflow=20
    )

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_database_session():
    """
    Dependency para FastAPI - fornece sessão do banco
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """
    Inicializa o banco de dados criando todas as tabelas
    """
    Base.metadata.create_all(bind=engine)
    print(f"✅ Banco de dados inicializado: {DATABASE_URL}")

def reset_database():
    """
    CUIDADO: Remove todas as tabelas e recria (apenas desenvolvimento)
    """
    if "sqlite" in DATABASE_URL:
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("🔄 Banco SQLite resetado")
    else:
        print("⚠️ Reset não permitido em produção PostgreSQL") 