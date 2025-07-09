from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    repeat_password: str

class RefreshResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str