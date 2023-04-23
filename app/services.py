import fastapi as _fastapi
import fastapi.security as _security
import jwt as _jwt

import app.db as _database, app.models as _models, app.config as _config

import sqlalchemy.orm as _orm
import passlib.hash as _hash
from datetime import datetime, timedelta

oauth2schema = _security.OAuth2PasswordBearer(tokenUrl="/api/token")

JWT_SECRET = "sanjeevanimangla"



def create_database():
    return _database.Base.metadata.create_all(bind=_database.engine)
 
def get_db():
    db = _database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# create_database()

async def get_user_by_email(email: str, db: _orm.Session):
    return db.query(_models.User).filter(_models.User.email == email).first()

async def create_user(user: _config.UserCreate, db: _orm.Session):
    user_obj = _models.User(
        email=user.email, hashed_password=_hash.bcrypt.hash(user.hashed_password)
    )
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)
    return user_obj


async def authenticate_user(email: str, password: str, db: _orm.Session):
    user = await get_user_by_email(db=db, email=email)
 
    if not user:
        return False
    if not user.verify_password(password):
        return False
    return user


async def create_token(user: _models.User):
    user_obj = _config.User.from_orm(user)
 
    token = _jwt.encode(user_obj.dict(), JWT_SECRET)
 
    return dict(access_token=token, token_type="bearer")

# async def get_current_user(
#     db: _orm.Session = _fastapi.Depends(get_db),
#     token: str = _fastapi.Depends(oauth2schema),
# ):
#     try:
#         payload = _jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
#         user_id = int(payload["id"])
#         if datetime.utcnow() > datetime.fromtimestamp(payload["exp"]):
#             raise _fastapi.HTTPException(status_code=401, detail="Token expired")
#         user = db.query(_models.User).get(user_id)
#     except _jwt.exceptions.DecodeError:
#         raise _fastapi.HTTPException(status_code=401, detail="Invalid token")
#     except Exception:
#         raise _fastapi.HTTPException(
#             status_code=401, detail="Could not validate credentials"
#     )
 
#     return _config.User.from_orm(user)

# async def get_current_user(
#     db: _orm.Session = _fastapi.Depends(get_db),
#     token: str = _fastapi.Depends(oauth2schema),
#     expires_delta: timedelta = timedelta(hours=24)
# ):
#     try:
#         payload = _jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
#         user_id = int(payload["sub"])
#         exp = payload["exp"]
#         if datetime.utcnow() > datetime.fromisoformat(exp):
#             raise ValueError("Token expired")
#     except (_jwt.JWTError, ValueError):
#         raise _fastapi.HTTPException(
#             status_code=_fastapi.HTTP_401_UNAUTHORIZED,
#             detail="Invalid email or password",
#         )
#     user = db.query(_models.User).get(user_id)
#     if not user:
#         raise _fastapi.HTTPException(
#             status_code=_fastapi.HTTP_404_NOT_FOUND,
#             detail="User not found",
#         )
#     return user

async def get_current_user(
    db: _orm.Session = _fastapi.Depends(get_db),
    token: str = _fastapi.Depends(oauth2schema),
    expires_delta: timedelta = timedelta(hours=24)
):
    try:
        payload = _jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
        user_id = int(payload["sub"])
        exp = payload["exp"]
        if datetime.utcnow() > datetime.fromisoformat(exp):
            raise ValueError("Token expired")
    except (_jwt.JWTError, ValueError):
        raise _fastapi.HTTPException(
            status_code=_fastapi.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    user = db.query(_models.User).get(user_id)
    if not user:
        raise _fastapi.HTTPException(
            status_code=_fastapi.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Set expiration time for token
    exp = datetime.utcnow() + expires_delta
    token_data = {"sub": str(user_id), "exp": exp}
    token = _jwt.encode(token_data, JWT_SECRET, algorithm="HS256")
    
    return {"user": user, "access_token": token}




