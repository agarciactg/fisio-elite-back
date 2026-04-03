from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Backend API for Fisio Élite built with Domain-Driven Design."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Expand later to specific frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health", tags=["Health"])
def healthcheck():
    return {"status": "ok", "project": settings.PROJECT_NAME}

from app.modules.auth.routes import router as auth_router
from app.modules.patients.routes import router as patients_router
from app.modules.therapists.routes import router as therapists_router
from app.modules.appointments.routes import router as appointments_router
from app.modules.payments.routes import router as payments_router
from app.modules.dashboard.routes import router as dashboard_router

app.include_router(auth_router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(patients_router, prefix="/api/v1/patients", tags=["Patients"])
app.include_router(therapists_router, prefix="/api/v1/therapists", tags=["Therapists"])
app.include_router(appointments_router, prefix="/api/v1/appointments", tags=["Appointments"])
app.include_router(payments_router, prefix="/api/v1/payments", tags=["Payments"])
app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["Dashboard"])
