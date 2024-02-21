from fastapi import FastAPI
from .routers import record, user
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
#    "http://localhost:3000"
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(record.router)
app.include_router(user.router)

@app.get("/api")
def test_root():
    return {"msg": "test main root"}