from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.db.mixins import TimestampMixin

class Patient(TimestampMixin, Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=True)
    notes = Column(String, nullable=True)

    appointments = relationship("Appointment", back_populates="patient")
