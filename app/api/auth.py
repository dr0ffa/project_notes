from fastapi  import APIRouter, Depends, HTTPException, Response, Request
from authx import AuthX, AuthXConfig, RequestToken
from app.schemas.auth_schemas import LoginRequest, RegisterRequest, RefreshResponse
from app.models_bd.database import get_db
from app.models_bd.models import Users
from app.core.security import verify_password, hash_password
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Dict, Any



auth_router = APIRouter()


config = AuthXConfig()
config.JWT_SECRET_KEY = "SECRET_KEY"
config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
config.JWT_REFRESH_COOKIE_NAME = "my_refresh_token"
config.JWT_TOKEN_LOCATION = ["cookies"]

security: AuthX = AuthX(config=config)


@auth_router.post("/auth/login")
def login(creds: LoginRequest, response: Response, db: Session = Depends(get_db)):
   user = db.query(Users).filter(Users.username == creds.username).first()
   if not user or not verify_password(creds.password, str(user.hashed_password)):
      raise HTTPException(status_code=401, detail="Incorrect username or password")
   
   access_token = security.create_access_token(uid=str(user.id), expires_delta=timedelta(minutes=60))
   refresh_token = security.create_refresh_token(uid=str(user.id), subject="refresh", expires_delta=timedelta(days=30))

   response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, access_token)
   response.set_cookie(config.JWT_REFRESH_COOKIE_NAME, refresh_token)

   return {"username": user, "post": creds, "access_token": access_token, "refresh_token": refresh_token}


@auth_router.post("/auth/register")
def register(creds: RegisterRequest, db: Session = Depends(get_db)):
   existing_user = db.query(Users).filter(Users.username == creds.username).first()
   if existing_user:
      raise HTTPException(status_code=400, detail="Username already registered")
   hashed_password = hash_password(creds.password)
   new_user = Users(username=creds.username, hashed_password=hashed_password)
    
   db.add(new_user)
   db.commit()
   db.refresh(new_user)
    
   return {"message": "User created successfully", "user_id": new_user.id}


@auth_router.post("/auth/refresh", response_model=RefreshResponse)
def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
   refresh_token = request.cookies.get("my_refresh_token")
   if not refresh_token:
      raise HTTPException(status_code=401, detail="Refresh token is missing")
   try:
      token_obj = RequestToken(token=refresh_token, location="cookies")
      payload = security.verify_token(token_obj)
      user_id = payload.uid
      print(type(payload))
      user = db.query(Users).filter(Users.id == user_id).first()
      if not user:
         raise HTTPException(status_code=404, detail="User not found")
      
      new_access_token = security.create_access_token(uid=str(user.id), expires_delta=timedelta(minutes=60))
      new_refresh_token = security.create_refresh_token(uid=str(user.id), subject="refresh", expires_delta=timedelta(days=30))

      response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, new_access_token)
      response.set_cookie(config.JWT_REFRESH_COOKIE_NAME, new_refresh_token)

      return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}

   except Exception as e:
      raise HTTPException(status_code=401, detail=f"Invalid refresh token: {str(e)}")




@auth_router.get("/auth/test", dependencies=[Depends(security.access_token_required)])
def protected():
   return {"data": "TOP SECRET"}