from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .routes.extract_notes import extract_notes
from .routes.match import match_to_perfumes

import faiss
import os
from pathlib import Path
import gdown

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "Data"
INDEX_PATH = DATA_DIR / "perfume_index.faiss"
FAISS_INDEX_URL = os.getenv("FAISS_INDEX_URL")

index = None


class Description(BaseModel):
    text: str


def ensure_index_file_exists():
    if INDEX_PATH.exists():
        print(f"FAISS index already exists at: {INDEX_PATH}")
        return

    if not FAISS_INDEX_URL:
        raise RuntimeError("FAISS_INDEX_URL is not set.")

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("Downloading FAISS index from Google Drive...")
    gdown.download(FAISS_INDEX_URL, str(INDEX_PATH), quiet=False, fuzzy=True)
    print(f"FAISS index downloaded to: {INDEX_PATH}")


def get_index():
    global index

    if index is None:
        ensure_index_file_exists()
        print(f"Loading FAISS index from: {INDEX_PATH}")
        index = faiss.read_index(str(INDEX_PATH))
        print("FAISS index loaded successfully.")

    return index


@app.get("/")
def home():
    return {"message": "ScentAI backend running"}


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/generate")
def generate_formula(desc: Description):
    notes = extract_notes(desc.text)
    return match_to_perfumes(notes, get_index())