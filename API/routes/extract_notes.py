import os
import pandas as pd
from transformers import pipeline

current_dir = os.path.dirname(__file__)  # Directory of the current script
data_file_path = os.path.join(current_dir, "../../Data/notes_and_family.csv")

notes_df = pd.read_csv(data_file_path)

candidate_notes = notes_df["Note"].tolist()

classifier = pipeline("zero-shot-classification",
                      model="facebook/bart-large-mnli",
                      device=-1)   # CPU

def extract_notes(description: str, threshold=0.4):

    '''Returns notes relevent to the given scent description'''

    result = classifier(
        description,
        candidate_labels = candidate_notes,
        multi_label=True
    )

    filtered = [
        (label, score) 
        for label, score in zip(result["labels"], result["scores"]) 
        if score >= threshold
    ]

    filtered.sort(key=lambda x: x[1], reverse=True)
    return filtered
