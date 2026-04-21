from sqlalchemy.ext.asyncio import AsyncSession
from .database import AsyncSessionLocal
from fastapi.security import OAuth2PasswordBearer
from jose import jwt,JWTError
import os 
from dotenv import load_dotenv
from fastapi import HTTPException,Depends
from app.models import User



load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")



oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
        
        
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
        try:
            payload =jwt.decode(token,SECRET_KEY,algorithms=["HS256"])
        
            user_id = payload.get("user_id")
            
        except JWTError:
        
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        user = await db.get(User, user_id)
        
        if user is None:
            raise HTTPException(status_code=401, detail="Unauthorized")
        
        
        
        return user
        