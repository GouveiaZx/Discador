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
        "apellido": "Tecnico",
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
    Simula la obtencion del usuario actual basado en el header Authorization.
    
    En un entorno real, esto validaria un token JWT, pero aqui simplemente
    usamos el header para identificar al usuario simulado.
    
    Args:
        authorization: Header de autorizacion (debe ser el email del usuario simulado)
        db: Sesion de base de datos
        
    Returns:
        Usuario: Objeto usuario simulado
        
    Raises:
        HTTPException: Si la autenticacion falla o el usuario no existe
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se proporcionaron credenciales de autenticacion",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # En un sistema real, aqui se verificaria el token JWT
    # Aqui simplemente usamos el email como identificador
    email = authorization
    
    if email not in USUARIOS_SIMULADOS:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales de autenticacion invalidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear un objeto Usuario a partir de los datos simulados
    datos_usuario = USUARIOS_SIMULADOS[email]
    usuario = Usuario()
    for key, value in datos_usuario.items():
        setattr(usuario, key, value)
    
    return usuario 