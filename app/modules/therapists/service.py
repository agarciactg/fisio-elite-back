from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
 
from .models import Therapist
from .schemas import TherapistCreate
 
 
class TherapistService:
    def __init__(self, db: AsyncSession):
        self.db = db
 
    async def get_therapists(self) -> list[Therapist]:
        result = await self.db.execute(
            select(Therapist).filter(Therapist.is_active == True)
        )
        return result.scalars().all()
 
    async def create_therapist(self, therapist: TherapistCreate) -> Therapist:
        if therapist.email:
            existing = await self.db.execute(
                select(Therapist).filter(Therapist.email == therapist.email)
            )
            if existing.scalars().first():
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Ya existe un terapeuta registrado con el correo '{therapist.email}'.",
                )
 
        try:
            db_therapist = Therapist(**therapist.model_dump())
            self.db.add(db_therapist)
            await self.db.commit()
            await self.db.refresh(db_therapist)
            return db_therapist
 
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Error de integridad al crear el terapeuta. El correo ya puede estar en uso.",
            )
