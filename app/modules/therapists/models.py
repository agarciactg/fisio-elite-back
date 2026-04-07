from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.db.mixins import TimestampMixin

class Therapist(TimestampMixin, Base):
    __tablename__ = "therapists"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    specialty = Column(String, nullable=False) # e.g. "Osteopatía"
    email = Column(String, unique=True, index=True, nullable=True)
    document_number = Column(String, unique=True, nullable=True)
    is_active = Column(Boolean, default=True)

    appointments = relationship("Appointment", back_populates="therapist")
