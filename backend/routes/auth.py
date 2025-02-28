# backend/routes/auth.py
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from backend.models.user import User, Token
from backend.database.connection import get_user_collection
from backend.utils.security import hash_password, verify_password, create_access_token

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)

# Register User
@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(user: User):
    users_collection = get_user_collection()
    existing_user = users_collection.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    hashed_password = hash_password(user.password)
    users_collection.insert_one({
        "email": user.email,
        "password": hashed_password
    })
    return {"message": "User registered successfully"}

# Login User
@auth_router.post("/login", response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    users_collection = get_user_collection()
    user = users_collection.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": user["email"]})
    return {"access_token": access_token, "token_type": "bearer"}
