import secrets
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
 
from .models import User
from .schemas import UserCreate
 
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
 
DEFAULT_PASSWORD_LENGTH = 12

def _generate_temp_password() -> str:
    """Generated a random password for the user."""
    return secrets.token_urlsafe(DEFAULT_PASSWORD_LENGTH)

 
class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
 
    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalars().first()
 
    async def create_user(self, user: UserCreate) -> User:
        existing = await self.get_user_by_email(user.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Ya existe un usuario registrado con el correo '{user.email}'.",
            )
 
        try:
            hashed_password = pwd_context.hash(user.password)
            db_user = User(email=user.email, hashed_password=hashed_password, document_number=user.document_number)
            self.db.add(db_user)
            await self.db.commit()
            await self.db.refresh(db_user)
            return db_user
 
        except IntegrityError:
            await self.db.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="El correo ya está en uso. Intenta con otro.",
            )
 
    async def authenticate_user(self, email: str, password: str) -> User:
        user = await self.get_user_by_email(email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo o contraseña incorrectos.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Esta cuenta está desactivada. Contacta al administrador.",
            )
        if not pwd_context.verify(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Correo o contraseña incorrectos.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    @staticmethod
    async def _create_user_if_not_exists(
        db: AsyncSession,
        email: str,
    ) -> tuple[User, str | None]:
        """
        Crea un User en la tabla users si no existe ya uno con ese email.
        Retorna (user, temp_password) si lo creó, o (user, None) si ya existía.
        """
        existing = await db.execute(select(User).filter(User.email == email))
        user = existing.scalars().first()
    
        if user:
            return user, None  # Ya existe, no hacer nada
    
        temp_password = _generate_temp_password()
        new_user = User(
            email=email,
            hashed_password=pwd_context.hash(temp_password),
            is_active=True,
        )
        db.add(new_user)
        return new_user, temp_password
