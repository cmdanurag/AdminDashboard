from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db

# Import schemas and models
from app.schemas.user import UserCreate, UserResponse
from app.models.user import User

# Import security and dependencies
from app.core.security import get_password_hash, verify_password, create_access_token
from app.core.dependencies import get_current_user

# Instantiate the router
router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/signup", response_model=UserResponse, status_code=201)
def signup(payload: UserCreate, db = Depends(get_db)):
    user=db.query(User).filter(User.email == payload.email).first()
    if user:
        raise HTTPException(status_code=400, detail="Email already registered")

    
    # 2. hash_password(payload.password)
    hashed_password = get_password_hash(payload.password)
    new_user=User(name=payload.name,email=payload.email,hashed_password=hashed_password)

    # 3. create User object, db.add, db.commit, db.refresh
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # 4. return user
    return new_user

@router.post("/login")
def login(form: OAuth2PasswordRequestForm = Depends(), db = Depends(get_db)):

    #finding the user based on email
    user=db.query(User).filter(User.email == form.username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    #checking the password
    password=verify_password(form.password,user.hashed_password)
    if not password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # creating token 
    access_token=create_access_token({"sub": str(user.id)})
    
    # returning the token
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
def me(current_user = Depends(get_current_user)):
    return current_user