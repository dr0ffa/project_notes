from fastapi import FastAPI
from .api.auth import auth_router
from .api.notes import notes_router
import uvicorn


app = FastAPI()

app.include_router(auth_router)
app.include_router(notes_router)

#if __name__ == "__main__":
#    uvicorn.run("app.main:app", reload=True)