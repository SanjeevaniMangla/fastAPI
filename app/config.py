# app/config.py

# import os

# from pydantic import BaseSettings, Field


# class Settings(BaseSettings):
#     db_url: str = Field(..., env='DATABASE_URL')

# settings = Settings()

import datetime as _dt
 
import pydantic as _pydantic
 
class _UserBase(_pydantic.BaseModel):
    email: str
 
class UserCreate(_UserBase):
    hashed_password: str
 
    class Config:
        orm_mode = True
 
class User(_UserBase):
    id: int
 
    class Config:
        orm_mode = True

