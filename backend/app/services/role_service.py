from sqlalchemy.orm import Session
from app.models.role import Role, UserRole
from app.schemas.role import RoleCreate, UserRoleCreate

class RoleService:
    def __init__(self, db: Session):
        self.db = db

    # Role
    def create_role(self, role_in: RoleCreate) -> Role:
        role = Role(**role_in.dict())
        self.db.add(role)
        self.db.commit()
        self.db.refresh(role)
        return role

    def get_role(self, role_id: int) -> Role:
        return self.db.query(Role).filter(Role.id == role_id).first()

    def list_roles(self):
        return self.db.query(Role).all()

    def delete_role(self, role_id: int) -> bool:
        role = self.get_role(role_id)
        if not role:
            return False
        self.db.delete(role)
        self.db.commit()
        return True

    # UserRole
    def assign_role(self, user_role_in: UserRoleCreate) -> UserRole:
        user_role = UserRole(**user_role_in.dict())
        self.db.add(user_role)
        self.db.commit()
        self.db.refresh(user_role)
        return user_role

    def list_user_roles(self, user_id: int = None):
        query = self.db.query(UserRole)
        if user_id:
            query = query.filter(UserRole.user_id == user_id)
        return query.all()

    def delete_user_role(self, user_role_id: int) -> bool:
        user_role = self.db.query(UserRole).filter(UserRole.id == user_role_id).first()
        if not user_role:
            return False
        self.db.delete(user_role)
        self.db.commit()
        return True 