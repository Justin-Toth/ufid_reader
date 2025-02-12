from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from app.api.router import api_router

origins = [
    "http://localhost:5173",
]


# Currently having some problems with CORS Stuff ~ Justin
middleware = [Middleware(
    CORSMiddleware, 
    allow_origins=origins, 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"],
  )
]

app = FastAPI(middleware=middleware)

app.include_router(api_router)