from fastapi import FastAPI
from  router import router
app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware
origins = [
    "https://www.mark-build.com",  # Angular frontend origin
    "https://b4kg48k.mark-build.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    
)

app.include_router(router)


