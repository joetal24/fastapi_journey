from fastapi import FastAPI
from app.routes import auth,todo
from contextlib import asynccontextmanager
from .database import engine,Base






@asynccontextmanager
async def lifespan(app: FastAPI):
        
        async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
        yield

app = FastAPI(lifespan=lifespan)


app.include_router(auth.router)
app.include_router(todo.router)