from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_utils.tasks import repeat_every
# from mypackage import mymodule
import database
from routers import users,setters,composers

app = FastAPI()


origins = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = False,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(users.router)
app.include_router(setters.router)
app.include_router(composers.router)

@app.on_event("startup")
@repeat_every(seconds=20)  # 1 hour
async def my_repeating_function():
    print('Assiging Composers...',end=None)
    await database.assign_composers_to_images()
    print('Done!')
    pass
    