# backend/app/services/auth.py
from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
import sqlite3
from typing import Optional

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-secret-key-here"  # W produkcji użyj bezpiecznego klucza!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def get_db():
    conn = sqlite3.connect('dateonic.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

def create_user(email: str, password: str):
    hashed_password = pwd_context.hash(password)
    conn = get_db()
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, hashed_password)
        )
        conn.commit()
        return {"email": email, "id": cursor.lastrowid}
    except sqlite3.IntegrityError:
        raise ValueError("Email already registered")
    finally:
        conn.close()

def authenticate_user(email: str, password: str):
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE email = ?",
        (email,)
    ).fetchone()
    conn.close()

    if user and pwd_context.verify(password, user['password']):
        return {"email": user['email'], "id": user['id']}
    return None

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# backend/app/api/routes.py - dodaj nowe endpointy
from fastapi import APIRouter, HTTPException, Depends
from app.services.auth import create_user, authenticate_user, create_access_token
from app.models.user import UserCreate, UserLogin

router = APIRouter()

@router.post("/register")
async def register(user_data: UserCreate):
    try:
        user = create_user(user_data.email, user_data.password)
        return {"message": "User created successfully", "user": user}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(user_data: UserLogin):
    user = authenticate_user(user_data.email, user_data.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )
    access_token = create_access_token(data={"sub": user['email']})
    return {"access_token": access_token, "token_type": "bearer"}