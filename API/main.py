from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .routes.extract_notes import *
from .routes.match import *
import faiss
import os


#allowing openMP to open multiple instances
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"


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
current_dir = os.path.dirname(__file__)
index_path = os.path.join(current_dir, "../Data/perfume_index.faiss")
index = None

@app.on_event("startup")
def load_index():
    global index
    print("Loading FAISS index...")
    index = faiss.read_index(index_path)
    print("FAISS index loaded.")

class Description(BaseModel):
    text: str

@app.get("/")
def home():
    return {"message": "ScentAI backend running"}

@app.post("/generate")
def generate_formula(desc: Description):

    notes = extract_notes(desc.text)
    return match_to_perfumes(notes, index)


