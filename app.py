import tempfile
import os

import streamlit as st
from dotenv import load_dotenv

from parse import read_resume_pdf
from analyzer import (
    extract_resume_profile, extract_jd_profile, analyse_keyword_match,
    analyse_bullets, analyse_jargon, analyse_structure, analyse_background_fit,
    analyse_degree_alignment, summarise_overall, compute_overall_score,
)

load_dotenv()
VALID_DEGREES = ["RTIS", "IMGD", "UXGD", "BFA"]

st.set_page_config(page_title="Resume Analyzer", layout="wide")
st.title("📄 AI Resume Analyzer")

resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
jd_text = st.text_area("Paste Job Description", height=250)
degree = st.selectbox("Select Degree", VALID_DEGREES)
run = st.button("Analyze Resume")

if run:
    if not resume_file or not jd_text:
        st.error("Please upload resume and paste job description.")
        st.stop()

    status = st.status("Running analysis...", expanded=True)

    def run_step(label, fn, *args, **kwargs):
        try:
            result = fn(*args, **kwargs)
            status.markdown(f":green[✅ {label}]")
            return result
        except Exception as exc:
            status.markdown(f":red[❌ {label} — {exc}]")
            status.update(label="Failed", state="error")
            st.error(f"{label} failed: {exc}")
            st.stop()

    with status:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(resume_file.read())
            tmp_path = tmp.name
        try:
            resume_text = run_step("Parsing résumé", read_resume_pdf, tmp_path)
        finally:
            os.unlink(tmp_path)

        resume_profile   = run_step("Extracting résumé profile", extract_resume_profile, resume_text)
        jd_profile        = run_step("Extracting job description profile", extract_jd_profile, jd_text)
        keyword_match     = run_step("Matching keywords", analyse_keyword_match, resume_profile, jd_profile)
        bullets           = run_step("Auditing bullet points", analyse_bullets, resume_profile)
        jargon            = run_step("Checking jargon", analyse_jargon, resume_profile, jd_profile)
        structure         = run_step("Checking structure", analyse_structure, resume_text)
        background_fit    = run_step("Assessing background fit", analyse_background_fit, resume_profile, jd_profile)
        degree_alignment  = run_step("Assessing degree alignment", analyse_degree_alignment, resume_profile, jd_profile, degree)

    report = {
        "resume_profile":    resume_profile,
        "jd_profile":        jd_profile,
        "keyword_match":     keyword_match,
        "bullets":           bullets,
        "jargon":            jargon,
        "structure":         structure,
        "background_fit":    background_fit,
        "degree_alignment":  degree_alignment,
    }
    report["overall_score"] = compute_overall_score(report)
    report["passes_ats_threshold"] = report["overall_score"] >= 60

    with status:
        report["summary"] = run_step("Generating summary", summarise_overall, report)

    status.update(label="Analysis complete", state="complete", expanded=False)

    verdict = "PASS ✅" if report["passes_ats_threshold"] else "FAIL ❌"
    st.subheader(f"Score: {report['overall_score']}/100 — {verdict} (60% ATS threshold)")
    st.write(report["summary"])

    with st.expander("Keyword Match"):
        st.write(keyword_match)
    with st.expander("Bullet Point Audit"):
        st.write(bullets)
    with st.expander("Jargon Check"):
        st.write(jargon)
    with st.expander("Structure"):
        st.write(structure)
    with st.expander("Background Fit"):
        st.write(background_fit)
    with st.expander("Degree Alignment"):
        st.write(degree_alignment)
    with st.expander("Full Report (raw)"):
=======
import tempfile
import os

import streamlit as st
from dotenv import load_dotenv

from parse import read_resume_pdf
from analyzer import (
    extract_resume_profile, extract_jd_profile, analyse_keyword_match,
    analyse_bullets, analyse_jargon, analyse_structure, analyse_background_fit,
    analyse_degree_alignment, summarise_overall, compute_overall_score,
)

load_dotenv()
VALID_DEGREES = ["RTIS", "IMGD", "UXGD", "BFA"]

st.set_page_config(page_title="Resume Analyzer", layout="wide")
st.title("📄 AI Resume Analyzer")

resume_file = st.file_uploader("Upload Resume (PDF)", type=["pdf"])
jd_text = st.text_area("Paste Job Description", height=250)
degree = st.selectbox("Select Degree", VALID_DEGREES)
run = st.button("Analyze Resume")

if run:
    if not resume_file or not jd_text:
        st.error("Please upload resume and paste job description.")
        st.stop()

    status = st.status("Running analysis...", expanded=True)

    def run_step(label, fn, *args, **kwargs):
        try:
            result = fn(*args, **kwargs)
            status.markdown(f":green[✅ {label}]")
            return result
        except Exception as exc:
            status.markdown(f":red[❌ {label} — {exc}]")
            status.update(label="Failed", state="error")
            st.error(f"{label} failed: {exc}")
            st.stop()

    with status:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(resume_file.read())
            tmp_path = tmp.name
        try:
            resume_text = run_step("Parsing résumé", read_resume_pdf, tmp_path)
        finally:
            os.unlink(tmp_path)

        resume_profile   = run_step("Extracting résumé profile", extract_resume_profile, resume_text)
        jd_profile        = run_step("Extracting job description profile", extract_jd_profile, jd_text)
        keyword_match     = run_step("Matching keywords", analyse_keyword_match, resume_profile, jd_profile)
        bullets           = run_step("Auditing bullet points", analyse_bullets, resume_profile)
        jargon            = run_step("Checking jargon", analyse_jargon, resume_profile, jd_profile)
        structure         = run_step("Checking structure", analyse_structure, resume_text)
        background_fit    = run_step("Assessing background fit", analyse_background_fit, resume_profile, jd_profile)
        degree_alignment  = run_step("Assessing degree alignment", analyse_degree_alignment, resume_profile, jd_profile, degree)

    report = {
        "resume_profile":    resume_profile,
        "jd_profile":        jd_profile,
        "keyword_match":     keyword_match,
        "bullets":           bullets,
        "jargon":            jargon,
        "structure":         structure,
        "background_fit":    background_fit,
        "degree_alignment":  degree_alignment,
    }
    report["overall_score"] = compute_overall_score(report)
    report["passes_ats_threshold"] = report["overall_score"] >= 60

    with status:
        report["summary"] = run_step("Generating summary", summarise_overall, report)

    status.update(label="Analysis complete", state="complete", expanded=False)

    verdict = "PASS ✅" if report["passes_ats_threshold"] else "FAIL ❌"
    st.subheader(f"Score: {report['overall_score']}/100 — {verdict} (60% ATS threshold)")
    st.write(report["summary"])

    with st.expander("Keyword Match"):
        st.write(keyword_match)
    with st.expander("Bullet Point Audit"):
        st.write(bullets)
    with st.expander("Jargon Check"):
        st.write(jargon)
    with st.expander("Structure"):
        st.write(structure)
    with st.expander("Background Fit"):
        st.write(background_fit)
    with st.expander("Degree Alignment"):
        st.write(degree_alignment)
    with st.expander("Full Report (raw)"):
>>>>>>> dfca38701535df6e5e67a5339c26a2b1d4416655
        st.json(report)