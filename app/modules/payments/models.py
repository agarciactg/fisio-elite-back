from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base_class import Base
from app.db.mixins import TimestampMixin

class Payment(TimestampMixin, Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    appointment_id = Column(Integer, ForeignKey("appointments.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String, default="PENDING") # PAID, PENDING, CANCELED
    payment_method = Column(String, nullable=True) # Cash, Credit Card
    
    appointment = relationship("Appointment", back_populates="payment")
