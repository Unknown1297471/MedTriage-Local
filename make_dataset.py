# make_dataset.py: regenerate synthetic dataset with ~5k rows
import os, json, random
from datetime import datetime
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

CONDITIONS = ["Common Cold", "Influenza", "Strep Throat", "Viral Pharyngitis", "Tonsillitis", "Acute Sinusitis", "Community-Acquired Pneumonia", "COVID-like Illness", "Otitis Media", "Acute Otitis Externa", "Bronchiolitis", "Gastroenteritis", "Food Poisoning", "Urinary Tract Infection", "Conjunctivitis", "Impetigo", "Cellulitis", "Skin Abscess", "Scabies", "Hand-Foot-and-Mouth Disease", "Chickenpox (Varicella)", "Measles-like Illness", "Dengue-like Illness", "Typhoid-like Illness", "Malaria-like Illness"]
SYMPTOM_BANK = {"Common Cold": ["runny nose", "sneezing", "sore throat", "mild cough", "congestion", "low-grade fever", "fatigue"], "Influenza": ["high fever", "body aches", "severe fatigue", "dry cough", "headache", "chills"], "Strep Throat": ["sore throat", "fever", "painful swallowing", "swollen tonsils", "no cough"], "Viral Pharyngitis": ["sore throat", "cough", "hoarseness", "runny nose", "fever"], "Tonsillitis": ["sore throat", "fever", "swollen tonsils", "difficulty swallowing", "ear pain"], "Acute Sinusitis": ["facial pain", "purulent nasal discharge", "nasal congestion", "tooth pain", "headache"], "Community-Acquired Pneumonia": ["fever", "productive cough", "shortness of breath", "chest pain", "fatigue"], "COVID-like Illness": ["fever", "dry cough", "loss of smell", "loss of taste", "fatigue", "sore throat"], "Otitis Media": ["ear pain", "fever", "irritability in child", "hearing difficulty"], "Acute Otitis Externa": ["ear pain", "itchy ear", "ear canal tenderness", "discharge from ear"], "Bronchiolitis": ["wheezing", "cough", "fast breathing", "fever", "feeding difficulty"], "Gastroenteritis": ["vomiting", "watery diarrhea", "abdominal cramps", "fever", "nausea"], "Food Poisoning": ["sudden vomiting", "diarrhea", "abdominal pain", "fever", "nausea"], "Urinary Tract Infection": ["burning urination", "frequent urination", "urgency", "lower abdominal pain", "fever"], "Conjunctivitis": ["red eye", "itchy eyes", "tearing", "discharge from eye", "gritty sensation"], "Impetigo": ["honey-colored crusts", "red sores", "itchy rash", "around nose and mouth"], "Cellulitis": ["warm red skin", "tenderness", "swelling", "fever"], "Skin Abscess": ["painful lump", "swelling", "pus", "fever", "tender to touch"], "Scabies": ["intense itching", "worse at night", "burrow lines", "rash between fingers"], "Hand-Foot-and-Mouth Disease": ["fever", "mouth ulcers", "rash on hands", "rash on feet"], "Chickenpox (Varicella)": ["itchy blistering rash", "fever", "rash in crops", "fatigue"], "Measles-like Illness": ["fever", "cough", "runny nose", "conjunctivitis", "rash"], "Dengue-like Illness": ["high fever", "severe headache", "pain behind eyes", "joint pain", "rash"], "Typhoid-like Illness": ["prolonged fever", "abdominal pain", "headache", "constipation or diarrhea"], "Malaria-like Illness": ["fever with chills", "sweats", "headache", "fatigue", "body aches"]}
CONFUSIONS = {"Common Cold": ["Viral Pharyngitis", "Acute Sinusitis"], "Influenza": ["COVID-like Illness", "Common Cold"], "Strep Throat": ["Tonsillitis", "Viral Pharyngitis"], "Viral Pharyngitis": ["Common Cold", "Tonsillitis"], "Tonsillitis": ["Strep Throat", "Viral Pharyngitis"], "Acute Sinusitis": ["Common Cold"], "Community-Acquired Pneumonia": ["Influenza", "COVID-like Illness"], "COVID-like Illness": ["Influenza", "Common Cold"], "Otitis Media": ["Acute Otitis Externa"], "Acute Otitis Externa": ["Otitis Media"], "Bronchiolitis": ["Community-Acquired Pneumonia", "Common Cold"], "Gastroenteritis": ["Food Poisoning"], "Food Poisoning": ["Gastroenteritis"], "Urinary Tract Infection": [], "Conjunctivitis": [], "Impetigo": ["Cellulitis"], "Cellulitis": ["Skin Abscess"], "Skin Abscess": ["Cellulitis"], "Scabies": ["Impetigo"], "Hand-Foot-and-Mouth Disease": ["Viral Pharyngitis", "Common Cold"], "Chickenpox (Varicella)": ["Hand-Foot-and-Mouth Disease"], "Measles-like Illness": ["Chickenpox (Varicella)"], "Dengue-like Illness": ["Malaria-like Illness"], "Typhoid-like Illness": ["Gastroenteritis"], "Malaria-like Illness": ["Dengue-like Illness"]}
RED_FLAGS = ["severe difficulty breathing", "struggling to breathe", "cannot breathe", "blue lips", "chest pain", "severe chest pain", "confusion", "unresponsive", "seizure", "seizures", "stiff neck with fever", "neck stiffness and fever", "severe dehydration", "no urine for 12 hours", "sunken eyes", "vomiting blood", "black stools", "severe abdominal pain", "fainting", "weak pulse", "severe bleeding"]
RISK_FACTORS = ["asthma", "diabetes", "immunocompromised", "pregnancy", "infant<1y", "elder>65", "heart_disease", "lung_disease", "kidney_disease"]
EXPOSURES = ["sick_contact", "food_out", "water_exposure", "insect_bites", "travel"]
EXTRA_TOKENS = ["since yesterday", "gradual onset", "sudden onset", "worse at night", "improves with rest", "took paracetamol", "no known allergies", "non-smoker", "non smoker", "smokes occasionally", "pls advise", "help", "kinda worried", "mild", "moderate", "severe", "v bad"]

random.seed(42); np.random.seed(42)

def sample_age():
    buckets = [(0.2,(0.1,1.0)),(0.25,(1,12)),(0.25,(12,18)),(0.2,(18,65)),(0.1,(65,90))]
    r = random.random(); cum = 0
    for p,(a,b) in buckets:
        cum += p
        if r <= cum: return round(random.uniform(a,b), 1)
    return round(random.uniform(18,65), 1)

def choose_temp_for_condition(cond):
    if cond in ['Common Cold','Conjunctivitis','Impetigo','Scabies','Skin Abscess']:
        if random.random()<0.7: return round(random.uniform(36.5,38.0),1)
        return None
    if cond in ['Influenza','Strep Throat','Community-Acquired Pneumonia','COVID-like Illness','Dengue-like Illness','Typhoid-like Illness','Malaria-like Illness','Gastroenteritis','Food Poisoning','Tonsillitis','Viral Pharyngitis','Acute Sinusitis','Otitis Media','Bronchiolitis']:
        if random.random()<0.85: return round(random.uniform(38.0,40.3),1)
        return None
    return None

def synthesize_symptom_text(cond, age, duration_days, fever_temp):
    import random
    base = random.sample(SYMPTOM_BANK[cond], k=min(len(SYMPTOM_BANK[cond]), random.randint(2, min(5, len(SYMPTOM_BANK[cond])))))
    if random.random()<0.35 and CONFUSIONS.get(cond):
        conf = random.choice(CONFUSIONS[cond])
        base += random.sample(SYMPTOM_BANK[conf], k=min(2, len(SYMPTOM_BANK[conf])))
    extras = random.sample(EXTRA_TOKENS, k=random.randint(0,3))
    text = ', '.join(base + extras)
    if random.random()<0.03: text += ', ' + random.choice(RED_FLAGS)
    segments = [f'{duration_days} days', f'age {age}y']
    if fever_temp is not None: segments.append(f'fever {fever_temp}C')
    prefix = ' | '.join([s for s in segments if s])
    return f'{prefix} :: {text}'

def derive_risk(age):
    risks = []
    if age<1.0 and random.random()<0.8: risks.append('infant<1y')
    if age>=65 and random.random()<0.6: risks.append('elder>65')
    for rf in RISK_FACTORS:
        if rf in ['infant<1y','elder>65']: continue
        if random.random()<0.12: risks.append(rf)
    return sorted(list(set(risks)))

def derive_exposures():
    import random
    return sorted([ex for ex in EXPOSURES if random.random()<0.2])

def triage_from_rules(text, age, fever_temp, duration_days, risk_list):
    text_low = (text or '').lower()
    if any(flag in text_low for flag in RED_FLAGS): return 'Emergency', True
    high_risk = any(r in (risk_list or []) for r in ['immunocompromised','pregnancy','infant<1y','elder>65','heart_disease','lung_disease','kidney_disease'])
    urgent_score = 0
    if (fever_temp is not None) and fever_temp>=39.0 and duration_days>=3: urgent_score += 1
    if any(p in text_low for p in ['shortness of breath','breathless','wheezing','fast breathing']): urgent_score += 1
    if 'urinary' in text_low and ('flank pain' in text_low or 'back pain' in text_low): urgent_score += 1
    if age is not None and age<1.0 and (fever_temp is not None) and fever_temp>=38.0: return 'Urgent', False
    if urgent_score>=1 and high_risk: return 'Urgent', False
    if any(p in text_low for p in ['high fever','productive cough','persistent','purulent','severe']): return 'GP within 48h', False
    return 'Home care', False

def generate_case(case_id):
    cond = random.choice(CONDITIONS)
    age = sample_age()
    duration_days = max(0, int(round(np.random.normal(3,2)))) + 1
    fever_temp = choose_temp_for_condition(cond)
    text = synthesize_symptom_text(cond, age, duration_days, fever_temp)
    risk = derive_risk(age)
    exposures = derive_exposures()
    triage_label, redflag = triage_from_rules(text, age, fever_temp, duration_days, risk)
    top_conditions = [cond]
    if random.random()<0.6 and CONFUSIONS.get(cond):
        import random as _r
        alt = _r.sample(CONFUSIONS[cond], k=min(len(CONFUSIONS[cond]), _r.randint(1,2)))
        top_conditions += alt
    top_conditions = sorted(list(set(top_conditions)))
    vitals_available = 'Y' if random.random()<0.25 else 'N'
    return {
        'case_id': f'CASE_{case_id:05d}',
        'age': age,
        'sex': random.choice(['M','F']),
        'symptoms_text': text,
        'duration_days': duration_days,
        'fever_temp_c': fever_temp if fever_temp is not None else '',
        'vitals_available': vitals_available,
        'risk_factors': ','.join(risk),
        'exposures': ','.join(exposures),
        'top_conditions': ','.join(top_conditions),
        'primary_condition': cond,
        'triage_label': triage_label,
        'red_flags_present': 'Y' if redflag else 'N',
        'notes_source': 'synthetic_v1',
        'split': ''
    }

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--n', type=int, default=5000)
    parser.add_argument('--out', type=str, default='medtriage_dataset.csv')
    args = parser.parse_args()
    rows = [generate_case(i+1) for i in range(args.n)]
    df = pd.DataFrame(rows)
    train_df, temp_df = train_test_split(df, test_size=0.3, random_state=42, stratify=df['primary_condition'])
    val_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42, stratify=temp_df['primary_condition'])
    df.loc[train_df.index, 'split'] = 'train'
    df.loc[val_df.index, 'split'] = 'val'
    df.loc[test_df.index, 'split'] = 'test'
    df.to_csv(args.out, index=False)
    print({'path': args.out, 'n': len(df)})

if __name__ == '__main__':
    main()
