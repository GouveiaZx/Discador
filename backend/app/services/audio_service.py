from sqlalchemy.orm import Session
from app.models.audio import Audio
from app.schemas.audio import AudioCreate, AudioUpdate

class AudioService:
    def __init__(self, db: Session):
        self.db = db

    def create_audio(self, audio_in: AudioCreate) -> Audio:
        audio = Audio(**audio_in.dict())
        self.db.add(audio)
        self.db.commit()
        self.db.refresh(audio)
        return audio

    def get_audio(self, audio_id: int) -> Audio:
        return self.db.query(Audio).filter(Audio.id == audio_id).first()

    def list_audios(self, campaign_id: int = None):
        query = self.db.query(Audio)
        if campaign_id:
            query = query.filter(Audio.campaign_id == campaign_id)
        return query.all()

    def update_audio(self, audio_id: int, audio_in: AudioUpdate) -> Audio:
        audio = self.get_audio(audio_id)
        if not audio:
            return None
        for field, value in audio_in.dict(exclude_unset=True).items():
            setattr(audio, field, value)
        self.db.commit()
        self.db.refresh(audio)
        return audio

    def delete_audio(self, audio_id: int) -> bool:
        audio = self.get_audio(audio_id)
        if not audio:
            return False
        self.db.delete(audio)
        self.db.commit()
        return True 