from sqlalchemy import Column, Integer, String, Boolean
from app.db.base_class import Base
from app.db.mixins import TimestampMixin

class User(TimestampMixin, Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
