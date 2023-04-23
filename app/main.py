# from fastapi import FastAPI
import fastapi as _fastapi
import fastapi.security as _security
# from app.db import database, User
import tweepy as _tweepy
import app.services as _services, app.config as _config
import sqlalchemy.orm as _orm

app = _fastapi.FastAPI(title="FastAPI, Docker, and Traefik")
# app = FastAPI(title="FastAPI, Docker, and Traefik")

consumer_key = 'GNII3b5t0BRRtz18DZFicuwhm0gf'
consumer_secret = 'mJOdWfcnn7HZQ2J1QvwHn7EoAoa4pkH47sFNnQ6VQyBY4fbhK10hv'
access_token = '1318846941011144704-QoEdNVxQvbkJWKazJGFfCLi9XrzYqF0bn'
access_token_secret = 'QjFTCChHZ2P683L6DIEvYw5vOl4hLESm7d8FlSCrWS58h0nb'

#define your tweepy authentication handler
auth_handler = _tweepy.OAuthHandler(consumer_key, consumer_secret)
auth_handler.set_access_token(access_token, access_token_secret)

# define tweepy api object using the auth_handler
api = _tweepy.API(auth_handler)

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


@app.post("/api/twitter/connect")
async def connect_to_twitter(
    bearer_token: str, 
    consumer_key: str, 
    consumer_secret: str, 
    access_token: str, 
    access_token_secret: str
):
    # create tweepy auth handler
    auth_handler = _tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth_handler.set_access_token(access_token, access_token_secret)
    
    # set the bearer token
    auth_handler.access_token = {"bearer_token": bearer_token}
    
    # create the tweepy api object
    api = _tweepy.API(auth_handler)
    
    # check if the authentication is successful
    try:
        api.verify_credentials()
        return {"message": "Twitter authentication successful!"}
    except:
        raise _fastapi.HTTPException(status_code=401, detail="Invalid Twitter credentials")

@app.get("/api/twitter/followers")
async def get_twitter_followers(
    user: _config.User = _fastapi.Depends(_services.get_current_user)
):
    # retrieve the user's twitter profile information from the database
    db_user = await _services.get_user_by_id(user.id)
    if not db_user:
        raise _fastapi.HTTPException(status_code=404, detail="User not found")
    
    # check if the user has connected their twitter profile
    if not db_user.twitter_bearer_token:
        raise _fastapi.HTTPException(status_code=400, detail="Twitter profile not connected")
    
    # create tweepy auth handler
    auth_handler = _tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth_handler.set_access_token(access_token, access_token_secret)
    auth_handler.access_token = {"bearer_token": db_user.twitter_bearer_token}
    
    # create the tweepy api object
    api = _tweepy.API(auth_handler)
    
    # retrieve the user's twitter followers
    followers = []
    cursor = _tweepy.Cursor(api.followers)
    for page in cursor.pages():
        followers.extend(page)
    
    # store the retrieved followers to the database
    for follower in followers:
        # create a database record for the follower if not exists
        db_follower = await _services.get_follower_by_id(follower.id)
        if not db_follower:
            db_follower = await _services.create_follower(follower)
        
        # add the follower to the user's followers list if not exists
        if db_follower not in db_user.followers:
            db_user.followers.append(db_follower)
    
    # commit the changes to the database
    await _services.commit_db()
    
    return {"message": f"Retrieved {len(followers)} followers from Twitter"}