from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every
# from mypackage import mymodule
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

@app.on_event("startup")
@repeat_every(seconds=10)  # 1 hour
def my_repeating_function():
    # print('hey look! its my repeating function!')
    pass
    