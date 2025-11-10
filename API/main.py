from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# allow frontend to talk to this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Description(BaseModel):
    text: str

@app.get("/")
def home():
    return {"message": "ScentAI backend running"}

@app.post("/generate")
def generate_formula(desc: Description):
    # For now, fake output 
    text = desc.text.lower()
    if "rose" in text:
        formula = [{"molecule": "Phenylethyl Alcohol", "ratio": 2.5}]
    else:
        formula = [{"molecule": "Iso E Super", "ratio": 3.0}]
    return {"description": desc.text, "formula": formula}
