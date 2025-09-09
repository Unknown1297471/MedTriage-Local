# demo_cases.py: Hardcoded test cases for demonstration purposes.
# This version uses extensive keyword lists for more flexible matching.

DEMO_CASES = [
    {
        "trigger_keywords": ["runny nose", "sneezing", "mild sore throat", "stuffy nose", "nasal congestion", "sore throat", "cough", "phlegm", "common cold", "post nasal drip", "head cold", "throat hurts", "itchy throat", "chest cough"],
        "triage": "Home care",
        "conditions": [
            ("Common Cold", 0.85),
            ("Viral Pharyngitis", 0.10),
            ("Acute Sinusitis", 0.05)
        ],
        "med_keys": ["Common Cold"]
    },
    {
        "trigger_keywords": ["high fever", "severe body aches", "chills", "feverish", "feeling hot", "temperature", "muscle pain", "flu-like symptoms", "influenza", "sweating", "headache", "aches all over", "extreme fatigue", "exhaustion", "weakness"],
        "triage": "Urgent",
        "conditions": [
            ("Influenza", 0.90),
            ("COVID-like Illness", 0.05),
            ("Community-Acquired Pneumonia", 0.05)
        ],
        "med_keys": ["Influenza"]
    },
    {
        "trigger_keywords": ["watery diarrhea", "nausea", "vomiting", "stomach cramps", "food poisoning", "stomach bug", "gastroenteritis", "stomach flu", "loose stools", "sick to my stomach", "upset stomach", "dehydrated", "cramping", "bathroom a lot"],
        "triage": "Home care",
        "conditions": [
            ("Gastroenteritis", 0.70),
            ("Food Poisoning", 0.30)
        ],
        "med_keys": ["Gastroenteritis"]
    },
    {
        "trigger_keywords": ["severe bleeding", "won't stop bleeding", "heavy bleeding", "deep cut", "gushing blood", "traumatic injury", "serious wound", "bleeding profusely", "uncontrolled bleeding", "arterial bleed", "vein cut"],
        "triage": "Emergency",
        "conditions": [
            ("Traumatic Injury", 0.99)
        ],
        "med_keys": ["Severe Bleeding"]
    },
    {
        "trigger_keywords": ["frequent urge to urinate", "burning sensation", "painful urination", "uti", "urinary tract infection", "bladder infection", "pain peeing", "burning pee", "can't hold it", "cloudy urine"],
        "triage": "GP within 48h",
        "conditions": [
            ("Urinary Tract Infection", 0.95)
        ],
        "med_keys": ["UTI"]
    },
    {
        "trigger_keywords": ["painful sore throat", "hurts to swallow", "strep throat", "white spots on tonsils", "swollen tonsils", "sore throat", "strep", "throat pain", "scratchy throat", "difficulty swallowing", "painful swallowing"],
        "triage": "GP within 48h",
        "conditions": [
            ("Strep Throat", 0.75),
            ("Tonsillitis", 0.20),
            ("Viral Pharyngitis", 0.05)
        ],
        "med_keys": ["Strep Throat"]
    },
    {
        "trigger_keywords": ["severe abdominal pain", "lower right side", "appendicitis", "stomach pain", "severe stomach pain", "sharp pain in abdomen", "belly pain", "abdominal cramps", "sudden abdominal pain", "pain in belly button", "side pain"],
        "triage": "Emergency",
        "conditions": [
            ("Suspected Appendicitis", 0.90),
            ("Gastroenteritis", 0.10)
        ],
        "med_keys": ["Severe Abdominal Pain"]
    },
    {
        "trigger_keywords": ["red eye", "itchy eye", "yellow discharge", "goopy eye", "pink eye", "conjunctivitis", "eye infection", "crusty eye", "eye is swollen", "sore eye", "eye is watery"],
        "triage": "Home care",
        "conditions": [
            ("Conjunctivitis", 0.98)
        ],
        "med_keys": ["Conjunctivitis"]
    },
    {
        "trigger_keywords": ["infant", "high fever", "baby crying", "not feeding well", "infant sick", "baby fever", "child fever", "baby fussy", "infant fever", "fever in baby", "baby with temp", "baby has cough"],
        "triage": "Urgent",
        "conditions": [
            ("Bronchiolitis", 0.40),
            ("Common Cold", 0.30),
            ("Otitis Media (Ear Infection)", 0.20)
        ],
        "med_keys": ["Infant Fever"]
    },
    {
        "trigger_keywords": ["cut on leg", "red and swollen", "skin infection", "cellulitis", "spreading redness", "abscess", "infected wound", "warm to touch", "pus", "boil"],
        "triage": "GP within 48h",
        "conditions": [
            ("Cellulitis", 0.80),
            ("Skin Abscess", 0.20)
        ],
        "med_keys": ["Skin Infection"]
    }
]
