from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .routes.match import hybrid_search 

import os
from pathlib import Path

os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later to your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Description(BaseModel):
    text: str

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Fragrance AI is running!"}

@app.post("/match")
def match_perfumes(request: Description):
    """
    Takes the user's natural language query and returns the top 5 perfumes
    using the Hybrid Pipeline (FAISS Dense Search + Structured Reranking).
    """
    # Calls the new unified pipeline
    parsed_intent, top_results = hybrid_search(request.text, final_top_k=5)
    
    return {
        "query_intent": parsed_intent,
        "matches": top_results
    }