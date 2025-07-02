# Models do sistema discador
from .audio import Audio
from .trunk import Trunk
from .dnc import DNCList, DNCNumber
from .role import Role, UserRole
from .llamada import Llamada
from .usuario import Usuario

__all__ = [
    "Audio",
    "Trunk", 
    "DNCList",
    "DNCNumber",
    "Role",
    "UserRole",
    "Llamada",
    "Usuario"
] 