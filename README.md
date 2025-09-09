# MedTriage AI – Symptom Checker & Triage

MedTriage is an AI-powered symptom checker that helps guide users on **common infections and diseases**, providing safe self-care advice and highlighting **red flag symptoms** that require medical attention.  

Live Demo: [MedTriage Streamlit App](https://medtriage-local-finally.streamlit.app)

---

## Features
- Enter common symptoms to get:
  - Possible conditions  
  - Recommended first-line medicines (with dose suggestions)  
  - Safety advisories and red flag alerts  
- Built with **Machine Learning** + **Streamlit UI**  
- Lightweight, easy to use in a browser  

---

## Tech Stack
- Python 3.10+  
- scikit-learn – Model training  
- pandas / numpy – Data handling  
- Streamlit – User interface  

---

## Project Structure

```text
medtriage/
│-- medtriage_streamlit.py   # Streamlit app
│-- trained_model.pkl        # Trained ML model
│-- dataset.csv              # Symptoms dataset
│-- requirements.txt         # Dependencies

```

## Quickstart (Local)
1. **Download this folder** (or the ZIP) to your machine.
2. Create a fresh environment (optional) and install deps:
```bash
pip install -r requirements.txt
```
3. **Run the Streamlit app** (simple website):
```bash
streamlit run app.py
```
Open the local URL it prints (usually http://localhost:8501).

4. **Or run the API** (FastAPI + Uvicorn):
```bash
uvicorn serve:app --host 0.0.0.0 --port 8000
```
Then POST to `/triage` with JSON like:
```json
{
  "symptoms_text": "3 days :: fever 38.5C, sore throat, cough, fatigue",
  "age": 12,
  "duration_days": 3,
  "fever_temp_c": 38.5,
  "risk_factors": ["asthma"],
  "exposures": ["sick_contact"]
}
```

## Re-train the Baseline
```bash
python train_baseline.py --data medtriage_dataset.csv
```
This re-generates `vectorizer.joblib`, `classifier.joblib`, `mlb.joblib` and prints validation F1.

## Re-generate the Dataset
```bash
python make_dataset.py --n 5000 --out medtriage_dataset.csv
python train_baseline.py --data medtriage_dataset.csv
```

## Deploy Options
### 1) Streamlit Community Cloud (free, easiest)
- Push the `medtriage` folder to a public GitHub repo.
- In Streamlit Cloud, **New app** → select your repo/branch → `app.py` as entry point.
- Deploy. Make sure **requirements.txt** is present.

### 2) Render / Railway / Fly.io (FastAPI)
- Use `serve.py` as the web entry.
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn serve:app --host 0.0.0.0 --port $PORT`
- Include `vectorizer.joblib`, `classifier.joblib`, `mlb.joblib`, `rules.py` in the repo.

### 3) Docker
```bash
docker build -t medtriage .
docker run -p 8501:8501 medtriage
```
(Streams the Streamlit app by default). For API, change the CMD or run:
```bash
docker run -p 8000:8000 medtriage uvicorn serve:app --host 0.0.0.0 --port 8000
```

## Safety & Limitations
- This is **not** for diagnosis or treatment; it only suggests triage urgency.
- A fixed rule layer detects **red flags** and will always escalate to **Emergency**.
- The ML model is trained on **synthetic** data; it can be wrong, biased, and poorly calibrated.
- Pediatric care is sensitive; when in doubt, seek professional evaluation.

## Files you can edit
- `rules.py`: tune red flags and triage heuristics.
- `make_dataset.py`: change conditions, symptoms, distribution.
- `train_baseline.py`: adjust vectorizer, model, and metrics.
- `app.py`: change the UI/wording/safety banners.
