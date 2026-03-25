from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

# Fake DB (temporaire)
fake_users_db = []

# Schema
class User(BaseModel):
    username: str
    password: str

# REGISTER
@router.post("/register")
def register(user: User):
    for u in fake_users_db:
        if u["username"] == user.username:
            raise HTTPException(status_code=400, detail="User already exists")

    fake_users_db.append({
        "username": user.username,
        "password": user.password
    })

    return {"message": "User created"}

# LOGIN
@router.post("/login")
def login(user: User):
    for u in fake_users_db:
        if u["username"] == user.username and u["password"] == user.password:
            return {"message": "Login successful"}

    raise HTTPException(status_code=401, detail="Invalid credentials")

# TEST
@router.get("/auth/test")
def test():
    return {"message": "Auth OK"}