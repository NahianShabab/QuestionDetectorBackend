from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mypackage import mymodule
import database
from routers import users,setters

app = FastAPI()


origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router)
app.include_router(setters.router)
