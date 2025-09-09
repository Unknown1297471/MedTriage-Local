# medications.py: Contains suggested relief measures for various conditions.
# This is for demonstration purposes ONLY and is not a substitute for medical advice.

MEDICATION_GUIDE = {
    "Common Cold": {
        "title": "Relief for Common Cold",
        "meds": [
            ("Paracetamol (Acetaminophen)", "For sore throat or mild aches. Follow package instructions."),
            ("Decongestant Nasal Spray", "For runny/stuffy nose. Do not use for more than 3 days.")
        ],
        "non_pharm": "Rest and stay hydrated with warm fluids like tea or soup."
    },
    "Influenza": {
        "title": "Relief for Influenza (Flu)",
        "meds": [
            ("Ibuprofen or Paracetamol", "To reduce fever and alleviate body aches. Follow package instructions.")
        ],
        "non_pharm": "Strict bed rest is crucial. Isolate to prevent spreading to others."
    },
    "Gastroenteritis": {
        "title": "Relief for Gastroenteritis",
        "meds": [
            ("Oral Rehydration Salts", "Mix with water to prevent dehydration from diarrhea and vomiting."),
            ("Loperamide", "Can be used for diarrhea in adults if there's no fever or blood in stool.")
        ],
        "non_pharm": "Sip clear fluids. Avoid solid food until vomiting stops, then reintroduce bland foods (e.g., bananas, rice, applesauce, toast)."
    },
    "Severe Bleeding": {
        "title": "Action for Severe Bleeding",
        "meds": [],
        "non_pharm": "**This is a medical emergency. Call emergency services immediately.** Apply firm, direct pressure to the wound with a clean cloth while waiting for professional help."
    },
    "UTI": {
        "title": "Relief for Urinary Tract Infection (UTI)",
        "meds": [
            ("Phenazopyridine", "Can help with the burning pain until a doctor's appointment. This does not cure the infection.")
        ],
        "non_pharm": "Drink plenty of water to help flush out bacteria. A doctor's visit for antibiotics is necessary."
    },
    "Strep Throat": {
        "title": "Relief for Sore Throat",
        "meds": [
            ("Throat Lozenges (with benzocaine)", "Can provide temporary numbing for a very sore throat."),
            ("Paracetamol or Ibuprofen", "For pain and fever relief.")
        ],
        "non_pharm": "Gargle with warm salt water. A doctor's visit is needed to test for strep and get antibiotics if required."
    },
    "Severe Abdominal Pain": {
        "title": "Action for Severe Abdominal Pain",
        "meds": [],
        "non_pharm": "**Do not eat, drink, or take any pain medication.** This could be a surgical emergency (like appendicitis). Seek immediate emergency care."
    },
    "Conjunctivitis": {
        "title": "Relief for Conjunctivitis (Pink Eye)",
        "meds": [
            ("Antihistamine Eye Drops", "Can help if the cause is allergic.")
        ],
        "non_pharm": "Use a warm, damp cloth to gently clean any discharge from the eye. Wash hands frequently to avoid spreading the infection. A doctor can prescribe antibiotic drops if it is bacterial."
    },
    "Infant Fever": {
        "title": "Action for Infant with High Fever",
        "meds": [],
        "non_pharm": "**A high fever in an infant requires immediate medical attention.** A doctor must determine the cause and prescribe the correct medication and dosage. Do not give medication without a doctor's explicit advice."
    },
    "Skin Infection": {
        "title": "Care for Skin Infection",
        "meds": [
            ("Topical Antibiotic Ointment", "Can be applied to a minor cut, but a spreading infection requires a doctor.")
        ],
        "non_pharm": "Keep the area clean and dry. You can draw a line around the red area to monitor if it's spreading. See a doctor, as oral antibiotics are likely necessary."
    }
}
