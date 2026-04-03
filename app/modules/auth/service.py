from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from .models import User
from .schemas import UserCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    async def create_user(self, user: UserCreate) -> User:
        hashed_password = pwd_context.hash(user.password)
        db_user = User(email=user.email, hashed_password=hashed_password)
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def authenticate_user(self, email: str, password: str) -> User | None:
        user = await self.get_user_by_email(email)
        if not user:
            return None
        if not pwd_context.verify(password, user.hashed_password):
            return None
        return user
