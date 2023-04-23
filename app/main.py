# from fastapi import FastAPI
import fastapi as _fastapi
import fastapi.security as _security
# from app.db import database, User

import app.services as _services, app.config as _config
import sqlalchemy.orm as _orm
app = _fastapi.FastAPI(title="FastAPI, Docker, and Traefik")
# app = FastAPI(title="FastAPI, Docker, and Traefik")


# @app.get("/")
# async def read_root():
#     return await User.objects.all()
@app.get("/")
def read_root():
    return {"Hello": "World"}

# @app.on_event("startup")
# async def startup():
#     if not database.is_connected:
#         await database.connect()
#     # create a dummy entry
#     await User.objects.get_or_create(email="test@test.com")


# @app.on_event("shutdown")
# async def shutdown():
#     if database.is_connected:
#         await database.disconnect()


@app.post("/api/users")
async def create_user(
    user: _config.UserCreate, db: _orm.Session = _fastapi.Depends(_services.get_db)
):
    db_user = await _services.get_user_by_email(user.email, db)
    if db_user:
        raise _fastapi.HTTPException(status_code=400, detail="Email already in use")
 
    user = await _services.create_user(user, db)
 
    return await _services.create_token(user)

@app.post("/api/token")
async def generate_token(
    form_data: _security.OAuth2PasswordRequestForm = _fastapi.Depends(),
    db: _orm.Session = _fastapi.Depends(_services.get_db),
):
    user = await _services.authenticate_user(form_data.username, form_data.password, db)
 
    if not user:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid Credentials")
 
    return await _services.create_token(user)
 
@app.get("/api/users/myprofile", response_model=_config.User)
async def get_user(user: _config.User = _fastapi.Depends(_services.get_current_user)):
    return user
