from fastapi import FastAPI
from mypackage import mymodule
import database
from routers import users,setters

app = FastAPI()


app.include_router(users.router)
app.include_router(setters.router)
