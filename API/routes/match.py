import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# Import your new structured scorer
from .structured_ranking import rerank_faiss_results 

current_dir = os.path.dirname(__file__)


print("Booting up matching engine...")

# Load embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Load Dense FAISS index (.bin)
index_path = os.path.join(current_dir, "../../Data/perfume_index.bin")
faiss_index = faiss.read_index(index_path)

# Load FAISS ID Mapping
mapping_path = os.path.join(current_dir, "../../Data/faiss_mapping.json")
with open(mapping_path, "r") as f:
    ID_MAPPING = json.load(f)

print("Engine ready.")


def hybrid_search(user_query: str, final_top_k: int = 5, faiss_candidates: int = 50):
    """
    1. Semantic Search (FAISS) -> gets top 50 vibe matches.
    2. Structured Rerank -> fact-checks notes/accords and returns top 5.
    """
    
    # Embed the raw user query directly
    query_vector = embedder.encode([user_query], normalize_embeddings=True)
    query_vector = np.array(query_vector, dtype=np.float32)
    
    # Search FAISS
    distances, indices = faiss_index.search(query_vector, k=faiss_candidates)
    
    # Map FAISS row indices back to your actual database IDs
    candidate_ids = []
    for idx in indices[0]:
        if idx != -1: # -1 means FAISS didn't find enough results
            real_id = ID_MAPPING[idx]
            candidate_ids.append(real_id)
            
    # Pass the candidate IDs to our structured scorer
    parsed_intent, top_results = rerank_faiss_results(user_query, candidate_ids, top_k=final_top_k)
    
    return parsed_intent, top_results