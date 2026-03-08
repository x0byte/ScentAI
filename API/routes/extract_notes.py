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
embedder = SentenceTransformer(model_name)

# Precompute note embeddings once at import to keep requests fast.
note_embeddings = embedder.encode(candidate_notes, normalize_embeddings=True)
note_embeddings = np.asarray(note_embeddings, dtype=np.float32)


def extract_notes(description: str, threshold: float = 0.35, top_k: int = 30):
    """Return probable notes for a scent description.

    Uses cosine similarity between the description embedding and precomputed
    note embeddings, then filters by threshold and top_k.
    """

    t0 = time.perf_counter()

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

    t1 = time.perf_counter()
    print(f"extract_notes took {t1 - t0:.3f}s for input length {len(description)}")

    return filtered    

    

