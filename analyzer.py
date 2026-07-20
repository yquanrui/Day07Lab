"""
analyzer.py — the 8 analysis functions and the pure-Python score calculator.

Task 4 of the lab (Track A).
Study material references:
  §4 The Multi-Stage Pipeline
  §7.2 Weighted Aggregation

Each of the 8 analysis functions calls ask_json() or ask_text() exactly once.
compute_overall_score() makes NO LLM call — it is pure Python arithmetic.

Imports you will need (already written for you):
"""

"""
analyzer.py — the analysis pipeline for the Résumé × JD Analyzer.
 
Every LLM-backed function here is a thin wrapper: build a user message,
call ask_json() (or ask_text() for the summary) with the matching prompt
from prompts.py, and return the parsed result. All prompt text, schema,
and temperature choices live in prompts.py — this module just wires them
to llm.py and, for compute_overall_score, does local arithmetic.
"""
 
import json
 
from llm import ask_json, ask_text
from prompts import (
    RESUME_PROFILE_PROMPT,
    RESUME_PROFILE_TEMPERATURE,
    JD_PROFILE_PROMPT,
    JD_PROFILE_TEMPERATURE,
    KEYWORD_MATCH_PROMPT,
    KEYWORD_MATCH_TEMPERATURE,
    BULLET_QUALITY_PROMPT,
    BULLET_QUALITY_TEMPERATURE,
    JARGON_AUDIT_PROMPT,
    JARGON_AUDIT_TEMPERATURE,
    STRUCTURE_AUDIT_PROMPT,
    STRUCTURE_AUDIT_TEMPERATURE,
    BACKGROUND_FIT_PROMPT,
    BACKGROUND_FIT_TEMPERATURE,
    DEGREE_ALIGNMENT_PROMPT,
    DEGREE_ALIGNMENT_TEMPERATURE,
    OVERALL_SUMMARY_PROMPT,
    OVERALL_SUMMARY_TEMPERATURE,
)
 
# ---------------------------------------------------------------------------
# Scoring weights (compute_overall_score) — see study material §7.2
# ---------------------------------------------------------------------------
 
_WEIGHT_KEYWORD_MATCH    = 0.35
_WEIGHT_BULLET_QUALITY   = 0.20
_WEIGHT_STRUCTURE        = 0.15
_WEIGHT_JARGON           = 0.10
_WEIGHT_BACKGROUND_FIT   = 0.10
_WEIGHT_DEGREE_ALIGNMENT = 0.10
 
 
# ---------------------------------------------------------------------------
# Extraction
# ---------------------------------------------------------------------------
 
def extract_resume_profile(resume_text: str) -> dict:
    """Extract a structured candidate profile from raw résumé text (LLM)."""
    user = f"RESUME TEXT:\n{resume_text}"
    return ask_json(
        RESUME_PROFILE_PROMPT,
        user,
        temperature=RESUME_PROFILE_TEMPERATURE,
    )
 
 
def extract_jd_profile(jd_text: str) -> dict:
    """Extract a structured role/requirements profile from raw JD text (LLM)."""
    user = f"JOB DESCRIPTION TEXT:\n{jd_text}"
    return ask_json(
        JD_PROFILE_PROMPT,
        user,
        temperature=JD_PROFILE_TEMPERATURE,
    )
 
 
# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------
 
def analyse_keyword_match(resume_profile: dict, jd_profile: dict) -> dict:
    """Compare résumé and JD profiles for keyword coverage (LLM)."""
    user = (
        f"RESUME PROFILE:\n{json.dumps(resume_profile, indent=2)}\n\n"
        f"JD PROFILE:\n{json.dumps(jd_profile, indent=2)}"
    )
    return ask_json(
        KEYWORD_MATCH_PROMPT,
        user,
        temperature=KEYWORD_MATCH_TEMPERATURE,
    )
 
 
def analyse_bullets(resume_profile: dict) -> dict:
    """Score every résumé bullet on the Action/Technology/Impact rubric (LLM)."""
    user = f"RESUME PROFILE:\n{json.dumps(resume_profile, indent=2)}"
    return ask_json(
        BULLET_QUALITY_PROMPT,
        user,
        temperature=BULLET_QUALITY_TEMPERATURE,
    )
 
 
def analyse_jargon(resume_profile: dict, jd_profile: dict) -> dict:
    """Flag résumé/JD terminology mismatches for the same underlying skill (LLM)."""
    user = (
        f"RESUME PROFILE:\n{json.dumps(resume_profile, indent=2)}\n\n"
        f"JD PROFILE:\n{json.dumps(jd_profile, indent=2)}"
    )
    return ask_json(
        JARGON_AUDIT_PROMPT,
        user,
        temperature=JARGON_AUDIT_TEMPERATURE,
    )
 
 
def analyse_structure(resume_text: str) -> dict:
    """Check the résumé profile for ATS-unfriendly structural issues (LLM).
 
    NOTE: despite taking resume_text as the parameter (per main.py's call
    signature), the structure audit prompt expects a résumé PROFILE, since
    it reasons about missing/empty structured fields as a proxy for
    formatting problems in the source document. We re-extract the profile
    here so this function is self-contained and matches its documented
    input/output contract.
    """
    resume_profile = extract_resume_profile(resume_text)
    user = f"RESUME PROFILE:\n{json.dumps(resume_profile, indent=2)}"
    return ask_json(
        STRUCTURE_AUDIT_PROMPT,
        user,
        temperature=STRUCTURE_AUDIT_TEMPERATURE,
    )
 
 
def analyse_background_fit(resume_profile: dict, jd_profile: dict) -> dict:
    """Assess overall professional/experiential alignment with the JD (LLM)."""
    user = (
        f"RESUME PROFILE:\n{json.dumps(resume_profile, indent=2)}\n\n"
        f"JD PROFILE:\n{json.dumps(jd_profile, indent=2)}"
    )
    return ask_json(
        BACKGROUND_FIT_PROMPT,
        user,
        temperature=BACKGROUND_FIT_TEMPERATURE,
    )
 
 
def analyse_degree_alignment(resume_profile: dict, jd_profile: dict, degree: str) -> dict:
    """Assess whether the candidate's declared degree program fits the JD's field-of-study expectations (LLM)."""
    user = (
        f"DECLARED DEGREE:\n{degree}\n\n"
        f"RESUME PROFILE:\n{json.dumps(resume_profile, indent=2)}\n\n"
        f"JD PROFILE:\n{json.dumps(jd_profile, indent=2)}"
    )
    return ask_json(
        DEGREE_ALIGNMENT_PROMPT,
        user,
        temperature=DEGREE_ALIGNMENT_TEMPERATURE,
    )


# ---------------------------------------------------------------------------
# Synthesis
# ---------------------------------------------------------------------------
 
def summarise_overall(report: dict) -> str:
    """Produce a 3-bullet plain Markdown executive summary of the report (LLM)."""
    user = f"ANALYSIS REPORT:\n{json.dumps(report, indent=2)}"
    return ask_text(
        OVERALL_SUMMARY_PROMPT,
        user,
        temperature=OVERALL_SUMMARY_TEMPERATURE,
    )
 
 
# ---------------------------------------------------------------------------
# Local scoring (no LLM call)
# ---------------------------------------------------------------------------
 
def compute_overall_score(report: dict) -> int:
    """
    Compute the weighted overall score (0-100) from the five sub-scores
    already present in *report*:
 
      keyword_match_score    (weight 0.35)
      bullet_quality_avg     (weight 0.20)
      structure_score        (weight 0.15)
      jargon_score           (weight 0.10)
      background_fit_score   (weight 0.10)
      degree_alignment_score (weight 0.10)
 
    Returns int(round(total)).
    """
    keyword_match_score    = report["keyword_match"]["keyword_match_score"]
    bullet_quality_avg     = report["bullets"]["bullet_quality_avg"]  # 0-5 scale
    structure_score        = report["structure"]["structure_score"]
    jargon_score            = report["jargon"]["jargon_score"]
    background_fit_score   = report["background_fit"]["background_fit_score"]
    degree_alignment_score = report["degree_alignment"]["degree_alignment_score"]

    bullet_quality_score = (bullet_quality_avg / 5) * 100  # normalise to 0-100

    total = (
        keyword_match_score    * _WEIGHT_KEYWORD_MATCH
        + bullet_quality_score   * _WEIGHT_BULLET_QUALITY
        + structure_score        * _WEIGHT_STRUCTURE
        + jargon_score            * _WEIGHT_JARGON
        + background_fit_score   * _WEIGHT_BACKGROUND_FIT
        + degree_alignment_score * _WEIGHT_DEGREE_ALIGNMENT
    )
    return int(round(total))