from fastapi import APIRouter

from app.api.v1 import admins, ai, analytics, auth, complaints, dashboard, feedback, reports, settings

api_router = APIRouter()

api_router.include_router(admins.router, prefix="/admins", tags=["Admins"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["Dashboard"])
api_router.include_router(feedback.router, prefix="/feedback", tags=["Feedback"])
api_router.include_router(complaints.router, prefix="/complaints", tags=["Complaints"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(reports.router, prefix="/reports", tags=["Reports"])
api_router.include_router(ai.router, prefix="/ai", tags=["AI"])
api_router.include_router(settings.router, prefix="/settings", tags=["Settings"])
