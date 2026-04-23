from ninja import NinjaAPI
from users.api import router as auth_router
from courses.api import router as courses_router, enrollment_router

api = NinjaAPI(
    title="Simple LMS API",
    version="1.0.0",
    description="REST API for Learning Management System"
)

# Auth endpoints (Register, Login, Refresh, Me, Update Profile)
api.add_router("/auth", auth_router)

# Course endpoints
api.add_router("/courses", courses_router)

# Enrollment endpoints
api.add_router("/enrollments", enrollment_router)
