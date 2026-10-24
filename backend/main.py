from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dataclasses import asdict
from wfa_2d import WFA2D

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

wfa = WFA2D([
    (1, 2),
    (6, 2),
    (8, 7)
])

class MessRequest(BaseModel):
    x: float
    y: float

@app.post("/mess")
def handle_mess(request: MessRequest):
    step = wfa.serve((request.x, request.y))
    return asdict(step)
