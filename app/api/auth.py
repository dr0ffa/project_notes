from fastapi  import APIRouter, Depends, HTTPException
from authx import AuthX, AuthXConfig
from app.schemas.auth_schemas import LoginRequest
from app.models_bd.database import get_db
from app.models_bd.models import Users
from app.core.security import verify_password
from sqlalchemy.orm import Session



auth_router = APIRouter()


config = AuthXConfig()
config.JWT_SECRET_KEY = "SECRET_KEY"
config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
config.JWT_TOKEN_LOCATION = ["cookies"]

security: AuthX = AuthX(config=config)


@auth_router.post("/auth/login")
def login(creds: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.username == creds.username).first()
    if not user or not verify_password(creds.password, str(user.hashed_password)):
       raise HTTPException(status_code=401, detail="Incorrect username or password")
    token = security.create_access_token(uid=str(user.id))



    return {"username": user, "post": creds, "access_token": token}