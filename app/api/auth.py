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
config.JWT_COOKIE_CSRF_PROTECT = False #по хорошему не должно быть так
config.JWT_SECRET_KEY = "SECRET_KEY"
config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
config.JWT_REFRESH_COOKIE_NAME = "my_refresh_token"
config.JWT_TOKEN_LOCATION = ["cookies"]

security: AuthX = AuthX(config=config)
#лучше в мэйне


async def check_access_token(request: Request):
   try:
      result = await security.access_token_required(request)
      print(result)
   except Exception as e:
      print(e)
      raise HTTPException(status_code=401, detail=str(e)) from e



@auth_router.post("/auth/login")
async def login(creds: LoginRequest, response: Response, db: Session = Depends(get_db)):
   user = db.query(Users).filter(Users.username == creds.username).first()
   if not user or not verify_password(creds.password, str(user.hashed_password)):
      raise HTTPException(status_code=401, detail="Incorrect username or password")
   
   access_token = security.create_access_token(uid=str(user.id), expiry=timedelta(minutes=60))
   refresh_token = security.create_refresh_token(uid=str(user.id), subject="refresh", expiry=timedelta(days=30))
   
   print(access_token)

   response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, access_token)
   response.set_cookie(config.JWT_REFRESH_COOKIE_NAME, refresh_token)

   return {"username": user, "post": creds, "access_token": access_token, "refresh_token": refresh_token}


@auth_router.post("/auth/register")
async def register(creds: RegisterRequest, db: Session = Depends(get_db)):
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
async def refresh_token(request: Request, response: Response, db: Session = Depends(get_db)):
   try:
      refresh_token = await security.refresh_token_required(request)
      user = db.query(Users).filter(Users.id == refresh_token.sub).first()
      if not user:
         raise HTTPException(status_code=404, detail="User not found")
      
      new_access_token = security.create_access_token(uid=str(user.id), expiry=timedelta(minutes=60))
      new_refresh_token = security.create_refresh_token(uid=str(user.id), subject="refresh", expiry=timedelta(days=30))

      response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, new_access_token)
      response.set_cookie(config.JWT_REFRESH_COOKIE_NAME, new_refresh_token)

      return {"access_token": new_access_token, "refresh_token": new_refresh_token, "token_type": "bearer"}

   except Exception as e:
      raise HTTPException(status_code=401, detail=f"Invalid refresh token: {str(e)}")




@auth_router.get("/auth/test", dependencies=[Depends(check_access_token)])
def protected():
   return {"data": "TOP SECRET"}