from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from backend.auth.security import hash_password, verify_password
from backend.db.models import users_collection
from backend.auth.security import hash_password

router= APIRouter()

class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/signup")
def signup(user: SignupRequest):
    existing_user = users_collection.find_one
    (
        {"email": user.email}
    )

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )
    
    hashed_password = hash_password(user.password)

    new_user = {
        "username": user.username,
        "email": user.email,
        "password": hashed_password
    }

    users_collection.insert_one(new_user)

    return {
        "message": "User registered successfully"
    }

    
@router.post("/login")
def login(user: LoginRequest):

    db_user=users_collection.find_one(
        {
            "email":user.email
        }
    )

    if not db_user:
        raise HTTPException(
        status_code=401,
        detail="Invalid email or password"
    )

    if not verify_password(user.password, db_user["password"]):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    return {
        "message": "Login successful",
        "user_id": str(db_user["_id"]),
        "username": db_user["username"],
        "email": db_user["email"]
    }