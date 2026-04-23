from ninja import Router
from ninja.pagination import paginate
from ninja_jwt.authentication import JWTAuth
from django.shortcuts import get_object_or_404
from typing import List, Optional
from .models import Course, Category, Enrollment, Progress, Lesson
from .schemas import (
    CourseOut, CourseDetailOut, CourseCreateSchema, CourseUpdateSchema,
    EnrollmentOut, ProgressSchema, CategorySchema
)
from config.permissions import role_required, is_instructor, is_admin
from ninja.errors import HttpError
from django.db.models import Count, Q

router = Router(tags=["Courses"])
enrollment_router = Router(tags=["Enrollments"])

def map_course(c):
    return {
        "id": c.id,
        "name": c.name,
        "slug": c.slug,
        "description": c.description,
        "category": {
            "id": c.category.id,
            "name": c.category.name,
            "slug": c.category.slug
        },
        "instructor_username": c.instructor.username,
        "price": float(c.price),
        "enrollment_count": getattr(c, 'enrollment_count', 0)
    }

# --- Courses Public Endpoints ---

@router.get("/", response=List[CourseOut])
@paginate
def list_courses(
    request, 
    category_id: Optional[int] = None, 
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    ordering: str = "-created_at"
):
    """
    Mengambil daftar semua course dengan filter dan pagination.
    """
    qs = Course.objects.for_listing()
    if category_id:
        qs = qs.filter(category_id=category_id)
    if search:
        qs = qs.filter(Q(name__icontains=search) | Q(description__icontains=search))
    if min_price is not None:
        qs = qs.filter(price__gte=min_price)
    if max_price is not None:
        qs = qs.filter(price__lte=max_price)
    
    return [map_course(c) for c in qs.order_by(ordering)]

@router.get("/{id}", response=CourseDetailOut)
def get_course(request, id: int):
    """
    Detail course beserta daftar materi.
    """
    course = get_object_or_404(Course.objects.for_listing(), id=id)
    lessons = course.lessons.all()
    
    data = map_course(course)
    data["lessons"] = [
        {
            "id": l.id,
            "title": l.title,
            "order": l.order,
            "video_url": l.video_url,
            "content": l.content
        } for l in lessons
    ]
    return data

# --- Courses Protected Endpoints ---

@router.post("/", auth=JWTAuth(), response={201: CourseOut, 403: dict})
@is_instructor
def create_course(request, data: CourseCreateSchema):
    """
    Membuat course baru (Hanya Instructor).
    """
    category = get_object_or_404(Category, id=data.category_id)
    course = Course.objects.create(
        name=data.name,
        slug=data.slug,
        description=data.description,
        category=category,
        instructor=request.auth,
        price=data.price
    )
    course = Course.objects.for_listing().get(id=course.id)
    return 201, map_course(course)

@router.patch("/{id}", auth=JWTAuth(), response={200: CourseOut, 403: dict})
@is_instructor
def update_course(request, id: int, data: CourseUpdateSchema):
    """
    Update data course (Hanya Owner/Admin).
    """
    course = get_object_or_404(Course, id=id)
    if course.instructor != request.auth and request.auth.role != 'admin':
        raise HttpError(403, "You are not the owner of this course")
    
    for attr, value in data.dict(exclude_unset=True).items():
        setattr(course, attr, value)
    course.save()
    
    course = Course.objects.for_listing().get(id=course.id)
    return map_course(course)

@router.delete("/{id}", auth=JWTAuth(), response={204: None, 403: dict})
@is_admin
def delete_course(request, id: int):
    """
    Hapus course (Hanya Admin).
    """
    course = get_object_or_404(Course, id=id)
    course.delete()
    return 204, None

# --- Enrollments Endpoints ---

@enrollment_router.post("/", auth=JWTAuth(), response={201: dict, 400: dict})
def enroll_course(request, course_id: int):
    """
    Mendaftar ke course (Student).
    """
    course = get_object_or_404(Course, id=course_id)
    enrollment, created = Enrollment.objects.get_or_create(user=request.auth, course=course)
    if not created:
        return 400, {"message": "Already enrolled"}
    return 201, {"message": "Successfully enrolled"}

@enrollment_router.get("/my-courses", auth=JWTAuth(), response=List[EnrollmentOut])
def my_courses(request):
    """
    Daftar course yang diikuti oleh user saat ini.
    """
    qs = Enrollment.objects.for_student_dashboard().filter(user=request.auth)
    return [
        {
            "id": e.id,
            "course_name": e.course.name,
            "enrolled_at": e.enrolled_at,
            "progress_percent": (e.completed_lessons_count / e.total_lessons_count * 100) if e.total_lessons_count > 0 else 0
        } for e in qs
    ]

@enrollment_router.post("/{enrollment_id}/progress", auth=JWTAuth(), response={200: dict, 403: dict})
def mark_progress(request, enrollment_id: int, data: ProgressSchema):
    """
    Menandai materi sebagai selesai berdasarkan pendaftaran.
    """
    enrollment = get_object_or_404(Enrollment, id=enrollment_id, user=request.auth)
    lesson = get_object_or_404(Lesson, id=data.lesson_id, course=enrollment.course)
    
    Progress.objects.update_or_create(
        user=request.auth,
        lesson=lesson,
        defaults={"is_completed": data.is_completed}
    )
    return {"message": "Progress updated"}
