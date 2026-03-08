import os
import faiss 
import numpy as np
import json
# from data_scraping import *

current_dir = os.path.dirname(__file__)  # Directory of the current script

def build_query_vector(probable_notes):
    note_vocab_path = os.path.join(current_dir, "../../Data/note_vocab.txt")
    with open(note_vocab_path) as f:
        note_to_idx = {note: i for i, note in enumerate(f.read().splitlines())}
    dim = len(note_to_idx)
    query = np.zeros(dim, dtype=np.float32)

    # probable_notes is a list of tuples [(note, score), ...]
    for note, confidence in probable_notes:
        if note in note_to_idx:
            query[note_to_idx[note]] = confidence

    # Normalize query vector, avoid division by zero
    norm = np.linalg.norm(query)
    if norm > 0:
        query = query / norm
    return query


def match_to_perfumes(probable_notes, index):
    '''Returns perfumes that match the given notes'''
    query = build_query_vector(probable_notes)
    query = query.reshape(1, -1)  # FAISS expects 2D array
    distances, indices = index.search(query, k=5)

    metadata_path = os.path.join(current_dir, "../../Data/perfume_metadata.json")
    with open(metadata_path) as f:
        metadata = json.load(f)

    matches = []
    for idx, score in zip(indices[0], distances[0]):
        matches.append({
            "perfume": metadata[idx]["Perfume"],
            "score": float(score),
            "url": metadata[idx]["url"]
        })

    return matches

    



    