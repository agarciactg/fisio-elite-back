from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.db.mixins import TimestampMixin

class Appointment(TimestampMixin, Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id", ondelete="CASCADE"), nullable=False)
    therapist_id = Column(Integer, ForeignKey("therapists.id", ondelete="CASCADE"), nullable=False)
    
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    
    status = Column(String, default="Confirmed") # Confirmed, Arrived, Canceled
    treatment = Column(String, nullable=True) # e.g. "Rehab. Post-quirúrgica"
    
    # Relationships
    patient = relationship("Patient", back_populates="appointments")
    therapist = relationship("Therapist", back_populates="appointments")
    payment = relationship("Payment", back_populates="appointment", uselist=False)
