from app.models import Todo
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import TodoCreate, TodoResponse,TodoUpdate
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from app.dependencies import get_db
from app.dependencies import get_current_user
from app.models import User





router = APIRouter(prefix="/todos", tags=["todos"])

@router.post("/",response_model=TodoResponse)
async def create_todo(todo: TodoCreate,db:AsyncSession= Depends(get_db),current_user: User = Depends(get_current_user) ):
        
        

        new_todo = Todo(
                title = todo.title,
                completed = todo.completed,
                user_id = current_user.id
                )


        db.add(new_todo)

        await db.commit()
        
        await db.refresh(new_todo)
        return new_todo
        
    
    
@router.get("/",response_model=list[TodoResponse])
async def get_todo(db: AsyncSession= Depends(get_db),current_user: User = Depends(get_current_user) ):
        
        
        result = await db.execute(select(Todo).where(Todo.user_id == current_user.id))
        
        return result.scalars().all() 

@router.get("/{id}",response_model=TodoResponse)
async def get_todo(id: int,db:AsyncSession= Depends(get_db),current_user: User = Depends(get_current_user)):
        
        
        
        todo = await db.get(Todo,id)    
        
        
        if todo is None:
                raise HTTPException(status_code=404, detail="Todo not found")
        
        if todo.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not authorized")
        
        
        return todo

@router.delete("/{id}")
async def delete_todo(id:int,db:AsyncSession= Depends(get_db),current_user: User = Depends(get_current_user)):
        
        todo = await db.get(Todo,id)         
                
             
        if todo is None:
                raise HTTPException(status_code=404, detail="Todo not found")
        
        if todo.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not authorized")
        
        await db.delete(todo)
        
        await db.commit()
        
        return "Delete successful"

@router.put("/{id}",response_model=TodoResponse)
async def update_todo(id:int, todo_update:TodoUpdate,db:AsyncSession= Depends(get_db),current_user: User = Depends(get_current_user)):
        
        todo = await db.get(Todo,id)  
        
        
        
              
        if todo is None:
                raise HTTPException(status_code=404, detail="Todo not found")
        
        if todo.user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Not authorized")
        
        if todo_update.title is not None:
                todo.title = todo_update.title
                
        if todo_update.completed is not None:
                todo.completed = todo_update.completed
                
        await db.commit()
        
        await db.refresh(todo)
                
        return todo