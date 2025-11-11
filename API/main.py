from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from routes.extract_notes import *
from routes.match import *
import faiss

app = FastAPI()

# allow frontend to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#loading the faiss index
index = faiss.read_index("perfume_index.faiss")

class Description(BaseModel):
    text: str

@app.get("/")
def home():
    return {"message": "ScentAI backend running"}

@app.post("/generate")
def generate_formula(desc: Description):

    notes = extract_notes(desc.text)
    return match_to_perfumes(notes)


