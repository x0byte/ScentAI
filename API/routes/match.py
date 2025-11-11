import pandas as pd
import os
import faiss 
import numpy as np
import json

current_dir = os.path.dirname(__file__)  # Directory of the current script

def build_query_vector(probable_notes):
    note_to_idx = {note: i for i, note in enumerate(open("../../Data/note_vocab.txt").read().splitlines())}
    dim = len(note_to_idx)
    query = np.zeros(dim, dtype=np.float32)

    for note, confidence in probable_notes.items():
        if note in note_to_idx:
            query[note_to_idx[note]] = confidence

    query = query / np.linalg.norm(query)
    return query


def match_to_perfumes(probable_notes, index):
    '''Returns perfumes that match the given notes'''
    query = build_query_vector(probable_notes)
    query = query.reshape(1, -1)  # FAISS expects 2D array
    distances, indices = index.search(query, k=5)

    with open("../../Data/perfume_metadata.json") as f:
        metadata = json.load(f)

    matches = []
    for idx, score in zip(indices[0], distances[0]):
        matches.append({
            "perfume": metadata[idx]["Perfume"],
            "score": float(score),
            "url": metadata[idx]["url"]
        })

    return matches

    



    