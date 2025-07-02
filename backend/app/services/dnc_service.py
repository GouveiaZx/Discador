from sqlalchemy.orm import Session
from app.models.dnc import DNCList, DNCNumber
from app.schemas.dnc import DNCListCreate, DNCNumberCreate

class DNCService:
    def __init__(self, db: Session):
        self.db = db

    # DNCList
    def create_dnc_list(self, dnc_list_in: DNCListCreate) -> DNCList:
        dnc_list = DNCList(**dnc_list_in.dict())
        self.db.add(dnc_list)
        self.db.commit()
        self.db.refresh(dnc_list)
        return dnc_list

    def get_dnc_list(self, dnc_list_id: int) -> DNCList:
        return self.db.query(DNCList).filter(DNCList.id == dnc_list_id).first()

    def list_dnc_lists(self):
        return self.db.query(DNCList).all()

    def delete_dnc_list(self, dnc_list_id: int) -> bool:
        dnc_list = self.get_dnc_list(dnc_list_id)
        if not dnc_list:
            return False
        self.db.delete(dnc_list)
        self.db.commit()
        return True

    # DNCNumber
    def add_dnc_number(self, dnc_list_id: int, dnc_number_in: DNCNumberCreate) -> DNCNumber:
        dnc_number = DNCNumber(dnc_list_id=dnc_list_id, **dnc_number_in.dict())
        self.db.add(dnc_number)
        self.db.commit()
        self.db.refresh(dnc_number)
        return dnc_number

    def list_dnc_numbers(self, dnc_list_id: int):
        return self.db.query(DNCNumber).filter(DNCNumber.dnc_list_id == dnc_list_id).all()

    def delete_dnc_number(self, dnc_number_id: int) -> bool:
        dnc_number = self.db.query(DNCNumber).filter(DNCNumber.id == dnc_number_id).first()
        if not dnc_number:
            return False
        self.db.delete(dnc_number)
        self.db.commit()
        return True 