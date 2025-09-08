# serve.py: FastAPI microservice
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Optional
from joblib import load
import numpy as np
from rules import triage_from_rules

app = FastAPI(title='AI Symptom Triage (Demo)', version='0.1.0')
vectorizer = load('vectorizer.joblib')
clf = load('classifier.joblib')
mlb = load('mlb.joblib')

class TriageRequest(BaseModel):
    symptoms_text: str = Field('', description='Free-text symptom description')
    age: float = Field(25.0, ge=0, le=110)
    sex: Optional[str] = None
    duration_days: int = Field(3, ge=0, le=60)
    fever_temp_c: Optional[float] = Field(default=None, ge=0, le=45)
    risk_factors: List[str] = Field(default=[])
    exposures: List[str] = Field(default=[])

class TriageResponse(BaseModel):
    triage: str
    emergency: bool
    top_conditions: List[str]
    top_probabilities: List[float]

@app.post('/triage', response_model=TriageResponse)
def triage(req: TriageRequest):
    txt = req.symptoms_text or ''
    X = vectorizer.transform([txt])
    try:
        probs = clf.predict_proba(X)[0]
    except Exception:
        decision = clf.decision_function(X)[0]
        probs = 1 / (1 + np.exp(-decision))
    labels = mlb.classes_
    idx = np.argsort(-probs)[:3]
    top_conditions = [labels[i] for i in idx]
    top_probs = [float(probs[i]) for i in idx]

    triage_label, redflag = triage_from_rules(txt, req.age, req.fever_temp_c, req.duration_days, req.risk_factors)
    return TriageResponse(triage=triage_label, emergency=bool(redflag), top_conditions=top_conditions, top_probabilities=top_probs)

@app.get('/health')
def health():
    return {'status': 'ok'}
