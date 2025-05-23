from fastapi import Depends, HTTPException, status, Header
from sqlalchemy.orm import Session
import uuid
from typing import Optional, Dict, Any

from app.database import obtener_sesion
from app.models.usuario import Usuario

# Usuarios simulados para pruebas
USUARIOS_SIMULADOS = {
    "admin@example.com": {
        "id": uuid.uuid4(),
        "nombre": "Admin",
        "apellido": "Sistema",
        "email": "admin@example.com",
        "hashed_password": "hashed_secret",
        "rol": "administrador",
        "activo": True
    },
    "integrador@example.com": {
        "id": uuid.uuid4(),
        "nombre": "Integrador",
        "apellido": "Técnico",
        "email": "integrador@example.com",
        "hashed_password": "hashed_secret",
        "rol": "integrador",
        "activo": True
    },
    "cliente@example.com": {
        "id": uuid.uuid4(),
        "nombre": "Cliente",
        "apellido": "Normal",
        "email": "cliente@example.com",
        "hashed_password": "hashed_secret",
        "rol": "cliente",
        "activo": True
    },
}

async def get_current_user_simulado(
    authorization: Optional[str] = Header(None),
    db: Session = Depends(obtener_sesion)
) -> Usuario:
    """
    Simula la obtención del usuario actual basado en el header Authorization.
    
    En un entorno real, esto validaría un token JWT, pero aquí simplemente
    usamos el header para identificar al usuario simulado.
    
    Args:
        authorization: Header de autorización (debe ser el email del usuario simulado)
        db: Sesión de base de datos
        
    Returns:
        Usuario: Objeto usuario simulado
        
    Raises:
        HTTPException: Si la autenticación falla o el usuario no existe
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionaron credenciales de autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # En un sistema real, aquí se verificaría el token JWT
    # Aquí simplemente usamos el email como identificador
    email = authorization
    
    if email not in USUARIOS_SIMULADOS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de autenticación inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear un objeto Usuario a partir de los datos simulados
    datos_usuario = USUARIOS_SIMULADOS[email]
    usuario = Usuario()
    for key, value in datos_usuario.items():
        setattr(usuario, key, value)
    
    return usuario 