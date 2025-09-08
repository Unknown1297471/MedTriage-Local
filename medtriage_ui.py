
"""
MedTriage UI — Python-only (Tkinter)
Converted from a React app to run using only Python stdlib.

Limitations:
- Tkinter cannot perfectly replicate glassmorphism/gradients, but this UI approximates layout
  (sidebar + form + results), typography, and interactions (multi-selects, numeric steppers).
- The app *attempts* to POST to http://localhost:8000/triage using urllib.request (stdlib).
  If the endpoint isn't reachable, it falls back to a local heuristic simulator.

How to run:
    python medtriage_ui.py              # runs developer tests, then launches the GUI (if a display is available)
    python medtriage_ui.py --no-gui     # runs only the developer tests (useful in headless environments)

This file contains a small developer test harness validating helper functions.

--- Original React (truncated) ---
import React, { useState } from 'react';

// Main App component
const App = () => {
    // State variables for form inputs
    const [symptomsText, setSymptomsText] = useState('');
    const [age, setAge] = useState(12);
    const [durationDays, setDurationDays] = useState(1);
    const [feverTempC, setFeverTempC] = useState(37.0);
    const [riskFactors, setRiskFactors] = useState([]);
    const [exposures, setExposures] = useState([]);
    const [triageResult, setTriageResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

...
"""
from __future__ import annotations

import json
import math
import sys
import threading
import time
import urllib.request
import urllib.error
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any

# Tkinter imports (std lib)
try:
    import tkinter as tk
    from tkinter import ttk, messagebox
except Exception as _tk_err:  # keep import-time failures non-fatal in headless mode
    tk = None
    ttk = None

# ---------------------- Helpers ----------------------

def format_option_name(s: str) -> str:
    """
    Convert tokens like 'sick_contact' -> 'sick contact', 'infant<1y' -> 'infant <1y', 'elder>65' -> 'elder >65'.
    """
    s = str(s).replace('_', ' ')
    # insert space before patterns like <1y (digits then 'y')
    s = re.sub(r'<(\d+)y', r' <\1y', s)
    # insert space before >N
    s = re.sub(r'>(\d+)', r' >\1', s)
    return s

def clamp_and_round(current, delta, min_val=None, max_val=None, dp=None):
    try:
        x = float(current)
    except Exception:
        x = 0.0
    x += float(delta)
    if isinstance(dp, int):
        x = round(x, dp)
    if isinstance(min_val, (int, float)) and x < min_val:
        x = float(min_val)
    if isinstance(max_val, (int, float)) and x > max_val:
        x = float(max_val)
    return x

# ---------------------- Triage Simulation ----------------------

def simulate_triage(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Fallback when the FastAPI endpoint is unavailable.
    Produces a reasonable triage level and likely conditions based on simple rules.
    """
    age = int(payload.get("age", 0) or 0)
    fever = float(payload.get("fever_temp_c", 0.0) or 0.0)
    duration = int(payload.get("duration_days", 1) or 1)
    symptoms_text = (payload.get("symptoms_text") or "").lower()
    risks = set(payload.get("risk_factors") or [])
    expos = set(payload.get("exposures") or [])

    triage = "Self-care"
    score = 0

    # Rule of thumb scoring
    if fever >= 40.0: score += 3
    elif fever >= 39.0: score += 2
    elif fever >= 38.0: score += 1

    if duration >= 7: score += 2
    elif duration >= 3: score += 1

    if "chest pain" in symptoms_text or "shortness of breath" in symptoms_text:
        score += 3
    if "dehydration" in symptoms_text or "confusion" in symptoms_text:
        score += 2

    if "immunocompromised" in risks or "pregnancy" in risks:
        score += 2
    if "infant<1y" in risks or "elder>65" in risks:
        score += 2

    # Exposure hints
    if "travel" in expos or "water_exposure" in expos or "insect_bites" in expos:
        score += 1

    if score >= 6: triage = "Emergency"
    elif score >= 4: triage = "Urgent"
    elif score >= 2: triage = "GP within 48h"
    else: triage = "Self-care"

    # crude conditions
    conditions = []
    if "sore throat" in symptoms_text or "throat" in symptoms_text:
        conditions.append(("pharyngitis", 0.34))
    if "cough" in symptoms_text:
        conditions.append(("upper_respiratory_infection", 0.31))
    if "vomit" in symptoms_text or "diarrhea" in symptoms_text:
        conditions.append(("gastroenteritis", 0.27))
    if "headache" in symptoms_text and fever >= 39.0:
        conditions.append(("influenza", 0.29))
    if not conditions:
        conditions = [("non_specific_viral_illness", 0.22), ("tension_headache", 0.15)]

    # normalize probabilities to <= 1 and top 3
    top = conditions[:3]
    # renormalize
    total = sum(p for _, p in top) or 1.0
    top = [(c, p/total) for c, p in top]

    reasons = "Heuristic result based on fever, duration, symptoms, and risk modifiers. For education only."

    return {
        "triage": triage,
        "top_conditions": [{"condition": c, "probability": p} for c, p in top],
        "reasons": reasons,
    }

def call_api_or_simulate(payload: Dict[str, Any]) -> Dict[str, Any]:
    url = "http://localhost:8000/triage"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=3) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception:
        return simulate_triage(payload)

# ---------------------- GUI ----------------------

class MedTriageApp:
    def __init__(self, root):
        self.root = root
        root.title("MedTriage AI — Educational Demo")
        root.geometry("980x640")
        root.configure(bg="#e5e7eb")  # tailwind gray-200-ish

        # Fonts
        self.font_base = ("SF Pro Text", 11)
        self.font_title = ("SF Pro Display", 16, "bold")
        self.font_sub = ("SF Pro Text", 12, "bold")

        # Containers: left sidebar, right main
        self.wrap = tk.Frame(root, bg="#e5e7eb")
        self.wrap.pack(fill="both", expand=True, padx=16, pady=16)

        self.sidebar = tk.Frame(self.wrap, bg="#ffffff", bd=0, highlightthickness=1, highlightbackground="#dbeafe")
        self.sidebar.place(x=0, y=0, width=320, relheight=1.0)

        self.main = tk.Frame(self.wrap, bg="#ffffff", bd=0, highlightthickness=1, highlightbackground="#dbeafe")
        self.main.place(x=336, y=0, relwidth=1.0, relheight=1.0, width=-336)

        # Sidebar content
        tk.Label(self.sidebar, text="Symptom Checker", font=self.font_title, bg="#ffffff").pack(anchor="w", padx=16, pady=(14, 4))
        tk.Label(self.sidebar, text="Get a preliminary recommendation based on common symptoms. For educational purposes only.", font=self.font_base, wraplength=280, justify="left", bg="#ffffff").pack(anchor="w", padx=16, pady=(0, 12))

        box = tk.Frame(self.sidebar, bg="#f8fafc", highlightthickness=1, highlightbackground="#e5e7eb")
        box.pack(fill="x", padx=12, pady=6)
        tk.Label(box, text="How it works:", font=self.font_sub, bg="#f8fafc").pack(anchor="w", padx=10, pady=(8, 2))
        for li in ["Describe symptoms clearly and concisely.",
                   "Provide relevant details like age or fever.",
                   "Receive a triage level and likely conditions."]:
            tk.Label(box, text=f"• {li}", font=self.font_base, bg="#f8fafc", wraplength=270, justify="left").pack(anchor="w", padx=10)

        disclaimer = tk.Label(self.sidebar, text=("Disclaimer: This model is for demonstration and educational use ONLY. "
                    "It is NOT a medical device and should NOT be used for diagnosis or treatment. "
                    "Always consult a qualified professional."), font=("SF Pro Text", 9), wraplength=280, justify="left", bg="#ffffff")
        disclaimer.pack(anchor="w", padx=16, pady=(12, 12))

        # Main content
        tk.Label(self.main, text="Patient Details & Symptoms", font=self.font_sub, bg="#ffffff").pack(anchor="w", padx=16, pady=(14, 6))

        # Symptoms text
        self.symptoms = tk.Text(self.main, height=4, width=60, relief="solid", bd=1, highlightthickness=0)
        self.symptoms.pack(fill="x", padx=16)

        # Numbers row
        row = tk.Frame(self.main, bg="#ffffff")
        row.pack(fill="x", padx=16, pady=10)

        self.age_var = tk.IntVar(value=12)
        self.duration_var = tk.IntVar(value=1)
        self.fever_var = tk.DoubleVar(value=37.0)

        def make_number(col_parent, label, var, step, minv, maxv=None, dp=None, width=10):
            col = tk.Frame(col_parent, bg="#ffffff")
            tk.Label(col, text=label, font=self.font_base, bg="#ffffff").pack(anchor="w")
            inner = tk.Frame(col, bg="#ffffff")
            inner.pack(anchor="w")
            ent = tk.Entry(inner, textvariable=var, width=width, relief="solid", bd=1)
            ent.pack(side="left")
            def inc():
                v = clamp_and_round(var.get(), step, minv, maxv, dp)
                var.set(v if dp else int(v))
            def dec():
                v = clamp_and_round(var.get(), -step, minv, maxv, dp)
                var.set(v if dp else int(v))
            tk.Button(inner, text="▲", command=inc, width=2).pack(side="left", padx=(4,0))
            tk.Button(inner, text="▼", command=dec, width=2).pack(side="left", padx=(2,0))
            return col

        c1 = make_number(row, "Age (Years)", self.age_var, step=1, minv=0)
        c1.pack(side="left", padx=(0, 16))
        c2 = make_number(row, "Duration (Days)", self.duration_var, step=1, minv=1)
        c2.pack(side="left", padx=(0, 16))
        c3 = make_number(row, "Fever Temp (°C)", self.fever_var, step=0.1, minv=35.0, maxv=42.0, dp=1, width=8)
        c3.pack(side="left")

        # Risk factors & exposures
        self.risk_factors = ["asthma", "diabetes", "immunocompromised", "pregnancy", "infant<1y", "elder>65"]
        self.exposures = ["travel", "sick_contact", "food_out", "water_exposure", "insect_bites"]

        def make_check_section(parent, title, options):
            outer = tk.Frame(parent, bg="#ffffff")
            tk.Label(outer, text=title, font=self.font_base, bg="#ffffff").pack(anchor="w")
            grid = tk.Frame(outer, bg="#ffffff")
            grid.pack(anchor="w", pady=(2, 4))
            vars_ = []
            for i, opt in enumerate(options):
                v = tk.BooleanVar(value=False)
                cb = tk.Checkbutton(grid, text=format_option_name(opt), variable=v, bg="#ffffff", anchor="w")
                cb.grid(row=i//2, column=i%2, sticky="w", padx=4, pady=2)
                vars_.append((opt, v))
            return outer, vars_

        rf_section, self.rf_vars = make_check_section(self.main, "Risk Factors", self.risk_factors)
        rf_section.pack(fill="x", padx=16, pady=(2, 4))
        ex_section, self.ex_vars = make_check_section(self.main, "Exposures", self.exposures)
        ex_section.pack(fill="x", padx=16, pady=(2, 8))

        # Submit
        self.submit_btn = tk.Button(self.main, text="Get Triage & Conditions", command=self.on_submit, bg="#2563eb", fg="white")
        self.submit_btn.pack(fill="x", padx=16, pady=(4, 8))

        # Result panel
        self.result_frame = tk.Frame(self.main, bg="#f8fafc", highlightthickness=1, highlightbackground="#dbeafe")
        self.result_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        self.result_title = tk.Label(self.result_frame, text="Recommendation:", font=self.font_sub, bg="#f8fafc")
        self.result_title.pack(anchor="w", padx=12, pady=(8,4))
        self.triage_label = tk.Label(self.result_frame, text="(No result yet)", bg="#e5e7eb", fg="#111827", bd=1, relief="solid")
        self.triage_label.pack(fill="x", padx=12, pady=(0,10))

        self.conditions_container = tk.Frame(self.result_frame, bg="#f8fafc")
        self.conditions_container.pack(fill="x", padx=12, pady=(0, 6))

        self.rationale_label = tk.Label(self.result_frame, text="", wraplength=560, justify="left", bg="#f8fafc")
        self.rationale_label.pack(fill="x", padx=12, pady=(6, 10))

    def _collect_payload(self) -> Dict[str, Any]:
        symptoms_text = self.symptoms.get("1.0", "end").strip()
        age = int(self.age_var.get())
        duration = int(self.duration_var.get())
        fever = float(self.fever_var.get())
        rf = [name for name, var in self.rf_vars if var.get()]
        ex = [name for name, var in self.ex_vars if var.get()]
        return {
            "symptoms_text": symptoms_text,
            "age": age,
            "duration_days": duration,
            "fever_temp_c": fever,
            "risk_factors": rf,
            "exposures": ex
        }

    def _set_triage_chip(self, triage: str):
        # Color mapping similar to React version
        bg = "#86efac"; fg = "#14532d"; border="#86efac"
        if triage == "Emergency":
            bg = "#fecaca"; fg = "#7f1d1d"; border = "#fca5a5"
        elif triage == "Urgent":
            bg = "#fed7aa"; fg = "#7c2d12"; border = "#fdba74"
        elif triage == "GP within 48h":
            bg = "#fde68a"; fg = "#854d0e"; border = "#fcd34d"
        self.triage_label.configure(text=triage, bg=bg, fg=fg, highlightbackground=border)

    def _render_conditions(self, top_conditions: List[Dict[str, Any]]):
        # clear
        for w in self.conditions_container.winfo_children():
            w.destroy()
        for cond in top_conditions or []:
            name = str(cond.get("condition","")).replace("_"," ").title()
            prob = float(cond.get("probability", 0.0))*100.0
            row = tk.Frame(self.conditions_container, bg="#f8fafc")
            row.pack(fill="x", pady=2)
            tk.Label(row, text=name, bg="#f8fafc").pack(side="left")
            tk.Label(row, text=f"{prob:.1f}%", bg="#f8fafc").pack(side="right")

    def on_submit(self):
        payload = self._collect_payload()
        self.submit_btn.configure(state="disabled", text="Analyzing...")
        def worker():
            try:
                data = call_api_or_simulate(payload)
            except Exception as e:
                data = {"triage": "Self-care", "top_conditions": [], "reasons": f"Error: {e}"}
            def ui():
                self._set_triage_chip(data.get("triage","Self-care"))
                self._render_conditions(data.get("top_conditions", []))
                self.rationale_label.configure(text=data.get("reasons",""))
                self.submit_btn.configure(state="normal", text="Get Triage & Conditions")
            try:
                self.root.after(0, ui)
            except Exception:
                pass
        threading.Thread(target=worker, daemon=True).start()

# ---------------------- Developer Tests ----------------------

def run_dev_tests() -> list[tuple[str, bool]]:
    tests = []
    def t(name, fn):
        try:
            ok = bool(fn())
        except Exception:
            ok = False
        tests.append((name, ok))

    # format_option_name
    t("format underscore", lambda: format_option_name("sick_contact") == "sick contact")
    t("format infant<1y", lambda: format_option_name("infant<1y") == "infant <1y")
    t("format elder>65", lambda: format_option_name("elder>65") == "elder >65")
    t("format passthrough", lambda: format_option_name("asthma") == "asthma")

    # clamp_and_round
    t("clamp min", lambda: clamp_and_round(0, -5, 0) == 0.0)
    t("clamp max", lambda: clamp_and_round(41.9, 5, 35, 42, 1) == 42.0)
    t("round 0.1", lambda: clamp_and_round(37.0, 0.1, 35, 42, 1) == 37.1)
    t("coerce str", lambda: clamp_and_round("12", 1, 0) == 13.0)

    # simulate triage basic shape
    sample = simulate_triage({"age": 12, "fever_temp_c": 38.5, "duration_days": 3, "symptoms_text": "fever cough sore throat", "risk_factors": [], "exposures": []})
    t("simulate keys", lambda: all(k in sample for k in ("triage", "top_conditions", "reasons")))

    return tests

def _print_test_summary(tests):
    passed = sum(1 for _, ok in tests if ok)
    total = len(tests)
    print(f"[MedTriage Tests] {passed}/{total} passed")
    for name, ok in tests:
        print(("✓" if ok else "✗") + " " + name)

# ---------------------- Entrypoint ----------------------

def _can_launch_gui() -> bool:
    if tk is None:
        return False
    # On headless systems, creating a root may fail with TclError; test safely.
    try:
        root = tk.Tk()
        root.withdraw()
        root.destroy()
        return True
    except Exception:
        return False

def main(argv=None):
    argv = argv or sys.argv[1:]
    tests = run_dev_tests()
    _print_test_summary(tests)

    headless_only = "--no-gui" in argv or "-q" in argv
    if headless_only:
        return 0

    if not _can_launch_gui():
        print("[Info] GUI not launched (likely headless environment). Run without --no-gui on a desktop to see the UI.")
        return 0

    # Launch the GUI
    root = tk.Tk()
    app = MedTriageApp(root)
    root.mainloop()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
