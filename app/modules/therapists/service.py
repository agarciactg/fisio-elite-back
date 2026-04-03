from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import Therapist
from .schemas import TherapistCreate

class TherapistService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_therapists(self):
        result = await self.db.execute(select(Therapist).filter(Therapist.is_active == True))
        return result.scalars().all()

    async def create_therapist(self, therapist: TherapistCreate) -> Therapist:
        db_therapist = Therapist(**therapist.model_dump())
        self.db.add(db_therapist)
        await self.db.commit()
        await self.db.refresh(db_therapist)
        return db_therapist
