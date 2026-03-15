import json
import re
import math

#loading the perfume json
print("Loading perfume database...")

with open("./Data/perfumes.json", "r", encoding="utf-8") as f:
    raw_perfumes = json.load(f)

PERFUME_DICT = {}
all_notes_set = set()
all_accords_set = set()

for p in raw_perfumes:
    #Convert lists to sets
    p["top"] = set(p["top"])
    p["middle"] = set(p["middle"])
    p["base"] = set(p["base"])
    p["accords"] = set(p["accords"])
    
    #Map by ID for instant O(1) lookups when FAISS returns an ID
    PERFUME_DICT[p["id"]] = p
    
    #Collect global vocabularies
    all_notes_set.update(p["top"] | p["middle"] | p["base"])
    all_accords_set.update(p["accords"])

ALL_NOTES = sorted(all_notes_set)
ALL_ACCORDS = sorted(all_accords_set)

print(f"Loaded {len(PERFUME_DICT)} perfumes instantly.")


# ACCORD DICTIONARY
ACCORD_HINTS = {
    "fresh": {"fresh", "fresh spicy", "citrus", "aromatic", "aquatic", "marine", "ozonic", "green", "soapy"},
    "clean": {"fresh", "musky", "citrus", "soapy", "aldehydic", "powdery", "white floral", "lavender"},
    "dark": {"amber", "woody", "leather", "smoky", "warm spicy", "oud", "animalic", "tobacco", "earthy"},
    "warm": {"warm spicy", "amber", "balsamic", "vanilla", "woody", "honey", "rum", "whiskey"},
    "cozy": {"vanilla", "amber", "musky", "powdery", "lactonic", "sweet", "caramel"},
    "sensual": {"musky", "amber", "animalic", "leather", "tuberose", "warm spicy"},
    "woody": {"woody", "oud", "patchouli", "mossy", "conifer"},
    "floral": {"floral", "white floral", "yellow floral", "rose", "tuberose", "violet", "iris"},
    "spicy": {"warm spicy", "fresh spicy", "soft spicy", "spicy", "cinnamon", "anis"},
    "sweet": {"sweet", "vanilla", "fruity", "caramel", "honey", "chocolate", "cacao", "coconut", "cherry"},
    "fruity": {"fruity", "tropical", "cherry", "coconut"},
    "green": {"green", "herbal", "mossy", "patchouli", "conifer", "cannabis", "camphor"},
    "earthy": {"earthy", "mossy", "patchouli", "mineral", "clay", "terpenic"},
    "aquatic": {"aquatic", "marine", "ozonic", "salty", "sand"},
    "powdery": {"powdery", "iris", "violet", "aldehydic"},
    "musky": {"musky", "animalic"},
    "leather": {"leather", "animalic", "suede"}, 
    "smoky": {"smoky", "tobacco", "leather", "oud", "incense"},
    "amber": {"amber", "balsamic"},
    "balsamic": {"balsamic", "amber", "resinous"},
    "animalic": {"animalic", "leather", "musky", "civet", "castoreum"},
    "gourmand": {"sweet", "vanilla", "caramel", "chocolate", "cacao", "coffee", "almond", "nutty", "honey", "lactonic", "coconut"},
    "nutty": {"nutty", "almond"},
    "creamy": {"lactonic", "coconut", "vanilla", "sandalwood"}, 
    "chocolate": {"chocolate", "cacao"},
    "coffee": {"coffee"},
    "boozy": {"rum", "whiskey", "champagne", "wine", "vodka", "alcohol", "coca-cola"},
    "rose": {"rose", "floral"},
    "lavender": {"lavender", "aromatic", "herbal"},
    "iris": {"iris", "powdery", "floral"},
    "violet": {"violet", "powdery", "floral"},
    "tuberose": {"tuberose", "white floral"},
    "soapy": {"soapy", "aldehydic", "clean", "fresh"},
    "metallic": {"metallic", "mineral", "aldehydic"},
    "salty": {"salty", "marine", "mineral", "sand"}
}


# PARSING & SCORING FUNCTIONS

def extract_query_notes(query, all_notes):
    q = query.lower()
    found = set()
    for note in all_notes:
        pattern = rf"\b{re.escape(note)}\b"
        if re.search(pattern, q): found.add(note)
    return found

def infer_query_accords(query, all_accords):
    q = query.lower()
    found = set()
    for word, mapped_accords in ACCORD_HINTS.items():
        if word in q: found.update(mapped_accords)
    return found & set(all_accords)

def extract_query_gender(query):
    q = query.lower()
    if any(w in q for w in ["masculine", "male", "man", "for men", "guy", "boy"]): return "male"
    if any(w in q for w in ["feminine", "female", "woman", "for women", "girl", "lady"]): return "female"
    if "unisex" in q or "shared" in q: return "unisex"
    return None

def parse_structured_query(query):
    return {
        "raw_query": query,
        "notes": extract_query_notes(query, ALL_NOTES),
        "accords": infer_query_accords(query, ALL_ACCORDS),
        "gender": extract_query_gender(query)
    }

def structured_score_breakdown(query, perfume):
    # ACCORD SCORE
    if not query["accords"]: a = 0.0
    else: a = len(query["accords"] & perfume["accords"]) / len(query["accords"])

    # NOTE SCORE
    if not query["notes"]: n = 0.0
    else:
        score = 0.0
        max_possible = len(query["notes"]) * 1.6
        for note in query["notes"]:
            if note in perfume["top"]: score += 1.0
            elif note in perfume["middle"]: score += 1.3
            elif note in perfume["base"]: score += 1.6
        n = score / max_possible

    # GENDER SCORE
    g = 0.0
    if query["gender"]:
        if query["gender"] == perfume["gender"]: g = 1.0
        elif perfume["gender"] == "unisex": g = 0.5

    # POPULARITY SCORE
    p = min(math.log1p(perfume["rating_count"]) / 10, 1.0)

    # FINAL COMBINED SCORE
    w_accord, w_note, w_gender, w_pop = 0.50, 0.30, 0.05, 0.15
    total_weight = 0
    if query["accords"]: total_weight += w_accord
    if query["notes"]: total_weight += w_note
    total_weight += w_gender + w_pop
    
    final = ((w_accord * a) + (w_note * n) + (w_gender * g) + (w_pop * p)) / total_weight if total_weight > 0 else 0.0

    return {
        "id": perfume["id"],
        "perfume": perfume["perfume"],
        "brand": perfume["brand"],
        "image_url": perfume["image_url"],
        "url": perfume["url"],
        "final_structured_score": round(final, 4),
        "matched_accords": list(query["accords"] & perfume["accords"]),
        "matched_notes": list((query["notes"] & perfume["top"]) | 
                              (query["notes"] & perfume["middle"]) | 
                              (query["notes"] & perfume["base"]))
    }

# HYBRID RERANKING WRAPPER
def rerank_faiss_results(query_text, faiss_candidate_ids, top_k=5):
    """
    Takes a list of IDs returned by your FAISS semantic search,
    scores them using the structured rules, and sorts them.
    """
    parsed_query = parse_structured_query(query_text)
    
    results = []
    
    for pid in faiss_candidate_ids:
        # Instant memory lookup using the Dictionary
        perfume = PERFUME_DICT.get(pid) 
        if not perfume:
            continue
            
        breakdown = structured_score_breakdown(parsed_query, perfume)
        results.append(breakdown)

    # Sort descending by structured score
    results.sort(key=lambda x: x["final_structured_score"], reverse=True)
    
    return parsed_query, results[:top_k]

# #testing
# if __name__ == "__main__":
#     # Simulate FAISS returning IDs [0, 1, 2, 4] for a search
#     mock_faiss_ids = [0, 1, 2, 4] 
#     user_search = "fresh citrus sweet for men"
    
#     parsed, top_results = rerank_faiss_results(user_search, mock_faiss_ids, top_k=3)
    
#     import pprint
#     print(f"\nQUERY INTENT: {parsed['accords']} | Gender: {parsed['gender']}")
#     print("\n--- TOP STRUCTURED RESULTS ---")
#     pprint.pprint(top_results)