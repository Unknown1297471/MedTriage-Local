# app.py: Streamlit demo for the symptom-triage model
import streamlit as st
import numpy as np
from joblib import load
from rules import triage_from_rules

st.set_page_config(page_title='AI Symptom Triage (Demo)', page_icon='🩺', layout='centered')

st.title('🩺 AI Symptom Triage (Demo)')
st.caption('Educational demo only — not medical advice. In emergencies, seek immediate care.')

@st.cache_resource
def load_artifacts():
    vectorizer = load('vectorizer.joblib')
    clf = load('classifier.joblib')
    mlb = load('mlb.joblib')
    return vectorizer, clf, mlb

vectorizer, clf, mlb = load_artifacts()

with st.form('triage_form'):
    symptoms_text = st.text_area('Describe symptoms (free text)', height=160, placeholder='e.g., 3 days :: fever 38.5C, sore throat, cough, fatigue, took paracetamol')
    col1, col2 = st.columns(2)
    with col1:
        age = st.number_input('Age (years)', min_value=0.0, max_value=110.0, value=25.0, step=0.1)
        duration_days = st.number_input('Duration (days)', min_value=0, max_value=60, value=3, step=1)
    with col2:
        fever_temp_c = st.number_input('Fever temperature (°C)', min_value=0.0, max_value=45.0, value=0.0, step=0.1)
        sex = st.selectbox('Sex', ['', 'M', 'F'], index=0)
    risks = st.multiselect('Risk factors', ['asthma','diabetes','immunocompromised','pregnancy','infant<1y','elder>65','heart_disease','lung_disease','kidney_disease'])
    exposures = st.multiselect('Exposures', ['sick_contact','food_out','water_exposure','insect_bites','travel'])
    agree = st.checkbox('I understand this is not medical advice and is for education only.')
    submitted = st.form_submit_button('Run Triage')

if submitted:
    if not agree:
        st.warning('Please acknowledge the disclaimer to continue.')
    else:
        txt = symptoms_text or ''
        X = vectorizer.transform([txt])
        try:
            probs = clf.predict_proba(X)[0]
        except Exception:
            decision = clf.decision_function(X)[0]
            probs = 1 / (1 + np.exp(-decision))
        labels = mlb.classes_
        top_idx = np.argsort(-probs)[:5]
        top = [(labels[i], float(probs[i])) for i in top_idx]
        fever_val = None if (fever_temp_c is None or fever_temp_c == 0.0) else float(fever_temp_c)
        triage, redflag = triage_from_rules(txt, float(age), fever_val, int(duration_days), risks)
        st.subheader('Triage Recommendation')
        if triage == 'Emergency':
            st.error('🚑 EMERGENCY: Seek immediate medical care now.')
        elif triage == 'Urgent':
            st.warning('⚠️ URGENT: See a clinician as soon as possible (same day).')
        elif triage == 'GP within 48h':
            st.info('ℹ️ See a GP/clinician within 48 hours.')
        else:
            st.success('🏠 Home care likely appropriate. Monitor and rest.')
        st.markdown('---')
        st.subheader('Most Likely Conditions')
        for name, p in top[:3]:
            st.write(f'- **{name}** — probability ~ {p:.2f}')
        st.caption('This demo only suggests possibilities. It may be wrong. Always use clinical judgment and local guidelines.')
