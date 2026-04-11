from app.modules.patients.models import Patient
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.core.security import create_access_token
from .schemas import UserCreate, UserResponse, Token
from .service import AuthService
from sqlalchemy.future import select
from app.modules.therapists.models import Therapist

router = APIRouter()

def get_auth_service(db: AsyncSession = Depends(get_db)):
    return AuthService(db)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, service: AuthService = Depends(get_auth_service)):
    existing = await service.get_user_by_email(user.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return await service.create_user(user)

@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    user = await service.authenticate_user(form_data.username, form_data.password)
 
    therapist_result = await db.execute(
        select(Therapist).where(Therapist.email == user.email)
    )
    therapist = therapist_result.scalars().first()
 
    patient_result = await db.execute(
        select(Patient).where(Patient.email == user.email)
    )
    patient = patient_result.scalars().first()
 
    if therapist:
        role = "therapist"
    elif patient:
        role = "patient"
    else:
        role = "admin"
 
    user_name = getattr(user, 'name', 'Admin') 
    
    token = create_access_token(
        data={
            "sub": user.email, 
            "role": role, 
            "name": user_name, 
            "email": user.email
        }
    )

    return {
        "access_token": token,
        "token_type":   "bearer",
        "role":         role,
        "name":         user_name,
        "email":        user.email,
    }
