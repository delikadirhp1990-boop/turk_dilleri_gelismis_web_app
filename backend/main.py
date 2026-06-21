import os
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sentence_transformers import SentenceTransformer, util

app = FastAPI(title="Türk Dilleri AI Servisi")

# Model global olarak yükleniyor
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# ------------------ Pydantic Modeller ------------------
class GrammarAnalysisRequest(BaseModel):
    text: str

class GrammarAnalysisOut(BaseModel):
    vowel_drop: bool
    consonant_softening: bool
    vowel_harmony: bool

class AutoTagRequest(BaseModel):
    text: str

class AutoTagOut(BaseModel):
    tags: List[str]

class EmbeddingRequest(BaseModel):
    text: str

class EmbeddingOut(BaseModel):
    embedding: List[float]

class SimilarityRequest(BaseModel):
    query: str
    records: List[dict]  # her biri en azından "title" ve content içermeli

class SimilarityResponse(BaseModel):
    results: List[dict]

# ------------------ API Uçları ------------------
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze-grammar", response_model=GrammarAnalysisOut)
def analyze_grammar(req: GrammarAnalysisRequest):
    text = req.text.lower()
    features = {
        "vowel_drop": False,
        "consonant_softening": False,
        "vowel_harmony": False
    }
    # Basit kural tabanlı tespit (gerçek projede genişletilmeli)
    if "burun" in text and "u" in text:
        features["vowel_drop"] = True
    if "kitap" in text and "b" in text:
        features["consonant_softening"] = True
    if "araba" in text:
        features["vowel_harmony"] = True  # Örnek
    return features

@app.post("/auto-tag", response_model=AutoTagOut)
def auto_tag(req: AutoTagRequest):
    text = req.text.lower()
    keywords = {
        "ünlü düşmesi": ["ünlü düşmesi", "vowel drop"],
        "ünsüz yumuşaması": ["ünsüz yumuşaması", "consonant softening"],
        "büyük ünlü uyumu": ["büyük ünlü uyumu", "vowel harmony"],
        "ek analizi": ["suffix", "ek", "yapım eki"]
    }
    tags = [tag for tag, keys in keywords.items() if any(k in text for k in keys)]
    return {"tags": tags}

@app.post("/embed", response_model=EmbeddingOut)
def get_embedding(req: EmbeddingRequest):
    emb = model.encode(req.text)
    return {"embedding": emb.tolist()}

@app.post("/similarity-search", response_model=SimilarityResponse)
def similarity_search(req: SimilarityRequest):
    if not req.records:
        return {"results": []}
    corpus_texts = []
    for rec in req.records:
        # Birleştirilmiş metin: başlık + tanım
        parts = [rec.get("title", "")]
        content = rec.get("content", {})
        if isinstance(content, dict):
            parts.append(content.get("definition", ""))
        corpus_texts.append(" ".join(parts))
    query_emb = model.encode(req.query, convert_to_tensor=True)
    corpus_embs = model.encode(corpus_texts, convert_to_tensor=True)
    scores = util.cos_sim(query_emb, corpus_embs)[0]
    top_k = min(5, len(req.records))
    top_indices = np.argpartition(-scores.cpu().numpy(), range(top_k))[:top_k]
    sorted_indices = top_indices[np.argsort(-scores[top_indices].cpu().numpy())]
    results = [req.records[int(i)] for i in sorted_indices]
    return {"results": results}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)