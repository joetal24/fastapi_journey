from pydantic import BaseModel
from typing import Optional

class TodoCreate(BaseModel):
    title:str
    completed:bool = False
    
class TodoResponse(BaseModel):
    id: int
    title: str
    completed: bool = False
    


class TodoUpdate(BaseModel):
    title: Optional[str] = None
    completed: Optional[bool] = None
    
class UserCreate(BaseModel):
    email:str
    password:str
    
class UserResponse(BaseModel):
    id:int
    email:str