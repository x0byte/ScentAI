import os
import time
import numpy as np
from sentence_transformers import SentenceTransformer

current_dir = os.path.dirname(__file__)  # Directory of the current script
data_file_path = os.path.join(current_dir, "../../Data/note_vocab.txt")

with open(data_file_path, "r") as file:
    candidate_notes = [line.strip() for line in file if line.strip()]

# Faster note extraction using sentence embeddings (1 forward pass per request).
model_name = os.getenv("NOTE_EMB_MODEL", "all-MiniLM-L6-v2")

embedder = None
note_embeddings = None

def get_embedder():
    global embedder, note_embeddings

    if embedder is None:
        print("Loading sentence transformer...")
        embedder = SentenceTransformer(model_name)

        print("Computing note embeddings...")
        note_embeddings_local = embedder.encode(candidate_notes, normalize_embeddings=True)
        note_embeddings = np.asarray(note_embeddings_local, dtype=np.float32)

    return embedder


def extract_notes(description: str, threshold: float = 0.35, top_k: int = 30):
    """Return probable notes for a scent description.

    Uses cosine similarity between the description embedding and precomputed
    note embeddings, then filters by threshold and top_k.
    """

    embedder = get_embedder()
    desc_emb = embedder.encode([description], normalize_embeddings=True)[0]
    scores = note_embeddings @ desc_emb  # cosine similarities

    # Highest scores first
    sorted_idx = np.argsort(scores)[::-1]

    filtered = []
    for idx in sorted_idx[:top_k]:
        score = float(scores[idx])
        if score < threshold:
            break
        filtered.append((candidate_notes[idx], score))

    return filtered    

    

