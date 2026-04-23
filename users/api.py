from ninja import Router
from ninja_jwt.authentication import JWTAuth
from django.contrib.auth import get_user_model
from .schemas import RegisterSchema, UserOut, ProfileUpdateSchema
from django.db import IntegrityError
from ninja_jwt.schema_control import SchemaControl
from ninja_jwt.settings import api_settings

User = get_user_model()
router = Router(tags=["Auth"])
schema = SchemaControl(api_settings)

@router.post("/register", response={201: UserOut, 400: dict})
def register(request, data: RegisterSchema):
    try:
        user = User.objects.create_user(
            username=data.username,
            email=data.email,
            password=data.password,
            role=data.role
        )
        return 201, user
    except IntegrityError:
        return 400, {"message": "User already exists"}

@router.post("/login", response=schema.obtain_pair_schema.get_response_schema())
def login(request, user_token: schema.obtain_pair_schema):
    user_token.check_user_authentication_rule()
    return user_token.to_response_schema()

@router.post("/refresh", response=schema.obtain_pair_refresh_schema.get_response_schema())
def refresh(request, refresh_token: schema.obtain_pair_refresh_schema):
    return refresh_token.to_response_schema()

@router.get("/me", auth=JWTAuth(), response=UserOut)
def me(request):
    return request.auth

@router.put("/me", auth=JWTAuth(), response=UserOut)
def update_profile(request, data: ProfileUpdateSchema):
    user = request.auth
    if data.email:
        user.email = data.email
    if data.bio is not None:
        user.bio = data.bio
    user.save()
    return user
