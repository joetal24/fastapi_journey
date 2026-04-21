from fastapi import APIRouter,Depends, HTTPException
from passlib.context import CryptContext
from app.schemas import UserCreate, UserResponse
from app.models import User
from app.dependencies import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt
import os 
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register",response_model=UserResponse)
async def register(user: UserCreate,db:AsyncSession= Depends(get_db) ):
        result= await db.execute(select(User).where(User.email == user.email))
        
        existing_user =  result.scalar_one_or_none()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        hashed_password = pwd_context.hash(user.password)
        
        new_user = User(email=user.email, hashed_password=hashed_password)
        
        db.add(new_user)
        
        await db.commit()
        
        await db.refresh(new_user)
        
        
        return new_user
    
@router.post("/login")
async def login(user: UserCreate,db:AsyncSession= Depends(get_db) ):
        result= await db.execute(select(User).where(User.email == user.email))
        
        new_user =  result.scalar_one_or_none()
                
        
        if not new_user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        is_valid = pwd_context.verify(user.password,new_user.hashed_password)
        
        if not is_valid:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        token = jwt.encode(
            {"user_id": new_user.id},
            SECRET_KEY  ,
            algorithm="HS256"
        )
        
        return {"access_token":token}