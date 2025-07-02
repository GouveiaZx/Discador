from sqlalchemy.orm import Session
from app.models.trunk import Trunk
from app.schemas.trunk import TrunkCreate, TrunkUpdate

class TrunkService:
    def __init__(self, db: Session):
        self.db = db

    def create_trunk(self, trunk_in: TrunkCreate) -> Trunk:
        trunk = Trunk(**trunk_in.dict())
        self.db.add(trunk)
        self.db.commit()
        self.db.refresh(trunk)
        return trunk

    def get_trunk(self, trunk_id: int) -> Trunk:
        return self.db.query(Trunk).filter(Trunk.id == trunk_id).first()

    def list_trunks(self):
        return self.db.query(Trunk).all()

    def update_trunk(self, trunk_id: int, trunk_in: TrunkUpdate) -> Trunk:
        trunk = self.get_trunk(trunk_id)
        if not trunk:
            return None
        for field, value in trunk_in.dict(exclude_unset=True).items():
            setattr(trunk, field, value)
        self.db.commit()
        self.db.refresh(trunk)
        return trunk

    def delete_trunk(self, trunk_id: int) -> bool:
        trunk = self.get_trunk(trunk_id)
        if not trunk:
            return False
        self.db.delete(trunk)
        self.db.commit()
        return True 