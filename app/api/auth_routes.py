# app/api/auth_routes.py
from fastapi import APIRouter, HTTPException
from ..services.auth import create_user, authenticate_user, create_access_token
from ..models.user import UserCreate, UserLogin

auth_router = APIRouter()

@auth_router.post("/register")
async def register(user_data: UserCreate):
    try:
        user = create_user(user_data.email, user_data.password)
        return {"message": "User created successfully", "user": user}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@auth_router.post("/login")
async def login(user_data: UserLogin):
    user = authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )
    access_token = create_access_token(data={"sub": user['email']})
    return {"access_token": access_token, "token_type": "bearer"}