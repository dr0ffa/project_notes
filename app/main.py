from fastapi import FastAPI
from .api.auth import auth_router
import uvicorn


app = FastAPI()

app.include_router(auth_router)

#if __name__ == "__main__":
#    uvicorn.run("app.main:app", reload=True)