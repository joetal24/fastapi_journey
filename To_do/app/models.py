from sqlalchemy import Boolean, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class Todo(Base):
    __tablename__ = "todos"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer,primary_key=True)
    email: Mapped[str] = mapped_column(String)
    hashed_password: Mapped[str] = mapped_column(String)