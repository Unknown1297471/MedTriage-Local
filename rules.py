# rules.py: safety guardrails and triage logic
RED_FLAGS = [
    "severe difficulty breathing", "struggling to breathe", "cannot breathe", "blue lips",
    "chest pain", "severe chest pain", "confusion", "unresponsive", "seizure", "seizures",
    "stiff neck with fever", "neck stiffness and fever", "severe dehydration", "no urine for 12 hours",
    "sunken eyes", "vomiting blood", "black stools", "severe abdominal pain", "fainting", "weak pulse", "severe bleeding"
]

def triage_from_rules(text: str, age: float | None, fever_temp: float | None, duration_days: int | None, risk_list: list[str] | None):
    txt = (text or '').lower()
    if any(flag in txt for flag in RED_FLAGS):
        return 'Emergency', True
    high_risk = any(r in (risk_list or []) for r in ['immunocompromised','pregnancy','infant<1y','elder>65','heart_disease','lung_disease','kidney_disease'])
    urgent_score = 0
    if fever_temp is not None and duration_days is not None and fever_temp >= 39.0 and duration_days >= 3:
        urgent_score += 1
    if any(p in txt for p in ['shortness of breath','breathless','wheezing','fast breathing']):
        urgent_score += 1
    if 'urinary' in txt and ('flank pain' in txt or 'back pain' in txt):
        urgent_score += 1
    if age is not None and age < 1.0 and fever_temp is not None and fever_temp >= 38.0:
        return 'Urgent', False
    if urgent_score >= 1 and high_risk:
        return 'Urgent', False
    if any(p in txt for p in ['high fever','productive cough','persistent','purulent','severe']):
        return 'GP within 48h', False
    return 'Home care', False


