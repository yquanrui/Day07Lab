"""
prompts.py — all 8 system prompts used by analyzer.py.

Task 3 of the lab (Track A).
Study material references:
  §3.3 Schema-First Prompt Design
  §6.1 Extraction Prompts
  §6.2 Evaluation Prompts
  §6.3 Feedback-Only Principle

Every prompt must follow ICCO structure:
  Instruction  — what the model must do
  Context      — relevant background (rubric description, schema description)
  Constraints  — rules the model must not break
  Output       — the exact JSON schema expected

Every prompt (except OVERALL_SUMMARY_PROMPT) must end with:
  "Output ONLY a valid JSON object matching the schema above. No prose. No
  markdown fences. No commentary. Never rewrite or generate résumé content."

Temperature guidance (set in the ask_json() call in analyzer.py):
  Extraction prompts (RESUME_PROFILE, JD_PROFILE): 0.0
  Evaluation prompts (KEYWORD_MATCH, BULLET_QUALITY, JARGON, STRUCTURE, BACKGROUND_FIT): 0.2–0.3
  OVERALL_SUMMARY_PROMPT: 0.3
"""


# ---------------------------------------------------------------------------
# Extraction prompts
# ---------------------------------------------------------------------------

RESUME_PROFILE_PROMPT = """### Instruction
Extract structured info from a résumé's plain text; return it as a single JSON object matching the schema below.
 
### Context
Input is raw résumé text (may have OCR artifacts or irregular spacing/line breaks). Output feeds a structured candidate profile downstream, so fidelity to the source matters more than polish.
 
### Constraints
- Extract only what is literally present. Never invent, paraphrase, or summarise.
- Missing field: "" for strings, [] for arrays.
- Copy bullet text verbatim.
- "summary" = professional summary/objective if present, else "".
- List education/projects/experience entries in résumé order.
- Never rewrite or generate résumé content.
 
### Output
Return a single JSON object with exactly this schema:
{
  "name": string,
  "contact": {
    "email": string,
    "phone": string,
    "linkedin": string,
    "github": string,
    "portfolio": string
  },
  "summary": string,
  "education": [
    {
      "school": string,
      "degree": string,
      "graduation_date": string,
      "courses": [string]
    }
  ],
  "projects": [
    {
      "title": string,
      "date": string,
      "bullets": [string]
    }
  ],
  "experience": [
    {
      "title": string,
      "company": string,
      "date": string,
      "bullets": [string]
    }
  ],
  "skills": {
    "languages": [string],
    "frameworks": [string],
    "tools": [string],
    "concepts": [string],
    "platforms": [string]
  }
}
 
Output ONLY a valid JSON object matching the schema above. No prose. No markdown fences. No commentary. Never rewrite or generate résumé content."""
 
RESUME_PROFILE_TEMPERATURE = 0.0
 
JD_PROFILE_PROMPT = """### Instruction
Extract role details and requirements from a job description's plain text; return them as a single JSON object matching the schema below.
 
### Context
Input is raw job posting text: title, company, seniority, location, employment type, responsibilities, and a mix of required/preferred qualifications (often under headings like "Requirements", "Qualifications", "Nice to have"). Output is compared against a résumé profile downstream, so required and preferred skills must stay separate.
 
### Constraints
- Extract only what is literally stated. Never invent, infer, or add details not mentioned.
- Missing field: "" for strings, [] for arrays.
- "required" = JD presents it as mandatory (e.g. under "Requirements", or "must have", "required", "X+ years"). "preferred" = JD marks it optional/bonus (e.g. "preferred", "nice to have", "a plus").
- If the JD doesn't clearly distinguish required vs preferred, follow the JD's own structure — plain "Qualifications" with no optional framing counts as required.
- Never duplicate a skill across both lists.
- Copy responsibility bullets close to verbatim — condense only trivial formatting, never substance.
- Never rewrite or generate résumé content.
 
### Output
Return a single JSON object with exactly this schema:
{
  "title": string,
  "company": string,
  "seniority": string,
  "employment_type": string,
  "location": string,
  "years_experience": string,
  "responsibilities": [string],
  "required_skills": [string],
  "preferred_skills": [string]
}
 
Output ONLY a valid JSON object matching the schema above. No prose. No markdown fences. No commentary. Never rewrite or generate résumé content."""
 
JD_PROFILE_TEMPERATURE = 0.0
 
 
# ---------------------------------------------------------------------------
# Evaluation prompts
# ---------------------------------------------------------------------------
 
KEYWORD_MATCH_PROMPT = """### Instruction
Given a résumé profile (JSON) and a JD profile (JSON), determine which JD keywords are present in the résumé and which are missing, then compute a keyword match score.
 
### Context
Both profiles are already structured (summary, projects, experience, education, skills, etc.) and always fully provided, even with zero overlap — that's a valid, expected result, not missing data. Output shows candidates exactly which JD keywords they do and don't cover.
 
### Constraints
- Mark "present" only if literally locatable in a résumé profile field. Do not infer from synonyms or implied skills.
- Never invent keywords not present in the JD profile.
- "why_it_matters": diagnostic only, ≤25 words, states what the JD says — never suggests résumé changes.
- Empty "present"/"missing" arrays are valid, correct results. Never ask for clarification or claim no profile was given.
- "keyword_match_score" = 100 × (required-category keywords found) / (total required-category keywords). If zero required keywords, use 100.
- Never rewrite or generate résumé content.
 
### Output
Return a single JSON object with exactly this schema:
{
  "present": [
    {
      "keyword": string,
      "category": "language" | "framework" | "tool" | "concept" | "soft_skill" | "buzzword",
      "found_in": "summary" | "projects" | "experience" | "education" | "skills",
      "exact_match": boolean
    }
  ],
  "missing": [
    {
      "keyword": string,
      "category": "language" | "framework" | "tool" | "concept" | "soft_skill" | "buzzword",
      "importance": "required" | "preferred",
      "suggested_section": string,
      "why_it_matters": string
    }
  ],
  "keyword_match_score": integer
}
 
Output ONLY a valid JSON object matching the schema above. No prose. No markdown fences. No commentary. Never rewrite or generate résumé content."""
 
KEYWORD_MATCH_TEMPERATURE = 0.2
 
BULLET_QUALITY_PROMPT = """### Instruction
Given a résumé profile (JSON), score every bullet from its "projects" and "experience" entries using the ATI rubric — Action, Technology, Impact — and return per-bullet scores plus an overall average.
 
### Context
Each bullet is one accomplishment/responsibility statement. ATI dimensions (each scored 0–5, 0=absent, 5=fully demonstrated):
- Action: strong, specific verb (e.g. "architected", "reduced") vs. weak/vague (e.g. "worked on", "responsible for").
- Technology: names a specific tool/language/framework/platform vs. staying generic.
- Impact: states a concrete, ideally quantified outcome vs. only describing an activity.
Scoring must be based only on what the bullet text actually says.
 
### Constraints
- Score only what is literally present in the bullet text.
- Copy each bullet's "text" verbatim.
- "feedback": diagnostic only, ≤25 words, names the weak/missing ATI dimension(s) — never suggests replacement wording.
- "bullet_score" = average of action/technology/impact scores, rounded to 1 decimal.
- "bullet_quality_avg" = average of all "bullet_score" values, rounded to 1 decimal. If no bullets, use 0.
- Empty "bullets" array + 0 avg is a valid result if the résumé has no bullets. Never ask for clarification.
- Never rewrite or generate résumé content.
 
### Output
Return a single JSON object with exactly this schema:
{
  "bullets": [
    {
      "text": string,
      "source_section": "projects" | "experience",
      "action_score": integer,
      "technology_score": integer,
      "impact_score": integer,
      "bullet_score": number,
      "feedback": string
    }
  ],
  "bullet_quality_avg": number
}
 
Output ONLY a valid JSON object matching the schema above. No prose. No markdown fences. No commentary. Never rewrite or generate résumé content."""
 
BULLET_QUALITY_TEMPERATURE = 0.2
 
 
JARGON_AUDIT_PROMPT = """### Instruction
Given a résumé profile (JSON) and a JD profile (JSON), flag places where they refer to the same skill/concept using different terminology, then compute a jargon alignment score.
 
### Context
ATS and recruiters often match on exact terminology, so "Postgres" vs "PostgreSQL", "ML" vs "Machine Learning", or "React.js" vs "ReactJS" can cause a real match to be missed. Surface these purely as a diagnostic — not a rewrite.
 
### Constraints
- Only flag where résumé and JD terms clearly refer to the same underlying skill (abbreviation, casing, synonym, or alternate name). Don't flag genuinely different skills.
- Copy "resume_term"/"jd_term" verbatim from their profiles.
- "explanation": diagnostic only, ≤25 words — how the terms differ and why it matters for matching. Never suggests replacement wording.
- Zero mismatches → empty "flags" array is a valid result. Never ask for clarification.
- "jargon_score": 0–100 integer, 100 = no mismatches found, lower = more/worse mismatches.
- Never rewrite or generate résumé content.
 
### Output
Return a single JSON object with exactly this schema:
{
  "flags": [
    {
      "resume_term": string,
      "jd_term": string,
      "issue_type": "abbreviation" | "casing" | "synonym" | "alternate_name" | "other",
      "explanation": string
    }
  ],
  "jargon_score": integer
}
 
Output ONLY a valid JSON object matching the schema above. No prose. No markdown fences. No commentary. Never rewrite or generate résumé content."""
 
# Evaluation prompt — moderate temperature for judgment calls on term equivalence.
JARGON_AUDIT_TEMPERATURE = 0.2
 
STRUCTURE_AUDIT_PROMPT = """### Instruction
Given a résumé profile (JSON), check it for formatting/structural issues that would make the original résumé harder for an ATS to parse, and compute a structure score.
 
### Context
The profile was produced by parsing the original résumé, so gaps or empty fields are a reasonable proxy for parsing/formatting problems in the source (e.g. missing "email" usually means no recognizable email was extracted; an empty "experience" array on an otherwise populated résumé usually means that section used a format standard parsers can't read, like a table or text box).
 
### Constraints
- Only flag issues evidenced by what's present/missing in the profile — don't speculate about visual formatting the profile can't show.
- "description": diagnostic only, ≤25 words — what's missing/inconsistent and why it matters for ATS parsing. Never suggests rewritten text.
- Missing contact fields (email, phone) are more severe than missing optional ones (linkedin, github, portfolio).
- Flag inconsistent/missing date formats across education/projects/experience.
- Zero issues → empty "issues" array + "structure_score": 100 is a valid result. Never ask for clarification.
- "structure_score": 0–100 integer, 100 = no issues, lower = more/more severe issues.
- Never rewrite or generate résumé content.
 
### Output
Return a single JSON object with exactly this schema:
{
  "issues": [
    {
      "issue_type": "missing_contact_field" | "missing_section" | "empty_section" | "inconsistent_dates" | "other",
      "section": string,
      "description": string
    }
  ],
  "structure_score": integer
}
 
Output ONLY a valid JSON object matching the schema above. No prose. No markdown fences. No commentary. Never rewrite or generate résumé content."""
 
# Evaluation prompt — moderate temperature for judgment calls on structural severity.
STRUCTURE_AUDIT_TEMPERATURE = 0.2
 
BACKGROUND_FIT_PROMPT = """### Instruction
Given a résumé profile (JSON) and a JD profile (JSON), assess how well the candidate's overall professional background aligns with the role, and compute a background fit score.
 
### Context
"Background fit" means professional/experiential alignment only — domain/industry experience, seniority, years of experience vs. what the JD asks for, and relevant education. It does NOT mean keyword overlap (handled elsewhere).
 
### Constraints
- Base assessments only on professional/experiential info literally present: job titles, industries, seniority, years of experience, project domains, education.
- Never infer, assume, or reference age, gender, race, ethnicity, national origin, disability, or any other protected/demographic characteristic — even indirectly via name, school, or graduation date.
- "assessment": diagnostic only, ≤25 words — what the JD asks for vs. how the résumé's background matches. Never suggests résumé changes.
- Only assess factors the JD profile actually specifies or implies.
- Sparse or empty "factors" is a valid result reflecting available evidence. Never ask for clarification.
- "background_fit_score": 0–100 integer, 100 = background closely matches every JD aspect, lower = greater misalignment.
- Never rewrite or generate résumé content.
 
### Output
Return a single JSON object with exactly this schema:
{
  "factors": [
    {
      "factor": string,
      "alignment": "strong" | "partial" | "weak" | "absent",
      "assessment": string
    }
  ],
  "background_fit_score": integer
}
 
Output ONLY a valid JSON object matching the schema above. No prose. No markdown fences. No commentary. Never rewrite or generate résumé content."""
 
# Evaluation prompt — moderate-high temperature for holistic, judgment-based fit assessment.
BACKGROUND_FIT_TEMPERATURE = 0.3

DEGREE_ALIGNMENT_PROMPT = """### Instruction
Given a résumé profile (JSON), a JD profile (JSON), and the candidate's declared degree program, assess how well that degree program aligns with the role's field-of-study expectations, then compute a degree alignment score.

### Context
The candidate selects their degree program from a fixed list (RTIS, IMGD, UXGD, BFA) separately from résumé parsing. "Degree alignment" means whether that declared program is a reasonable academic match for the JD's stated or implied field-of-study expectations — it does NOT mean years of experience or seniority (handled elsewhere). Use the résumé profile's "education" entries only to corroborate the declared degree, never to override it.

### Constraints
- Base the assessment only on the declared degree, the résumé profile's education entries, and what the JD profile literally states or clearly implies about field of study.
- Never infer, assume, or reference age, gender, race, ethnicity, national origin, disability, or any other protected/demographic characteristic.
- "assessment": diagnostic only, ≤25 words — what the JD expects vs. how the declared degree matches. Never suggests résumé changes.
- If the JD profile states no field-of-study expectation, treat any declared degree as a valid, full match.
- "degree_alignment_score": 0–100 integer, 100 = degree closely matches JD's field-of-study expectations, lower = greater misalignment.
- Never rewrite or generate résumé content.

### Output
Return a single JSON object with exactly this schema:
{
  "declared_degree": string,
  "jd_field_expectation": string,
  "alignment": "strong" | "partial" | "weak" | "absent",
  "assessment": string,
  "degree_alignment_score": integer
}

Output ONLY a valid JSON object matching the schema above. No prose. No markdown fences. No commentary. Never rewrite or generate résumé content."""

# Evaluation prompt — moderate temperature for judgment calls on field-of-study relevance.
DEGREE_ALIGNMENT_TEMPERATURE = 0.2


# ---------------------------------------------------------------------------
# Synthesis prompt
# ---------------------------------------------------------------------------
 
# Purpose: produce a 3-bullet plain Markdown executive summary from the full report.
# Input to ask_text(): system=OVERALL_SUMMARY_PROMPT, user="ANALYSIS REPORT:\n{json}"
# Returns: plain Markdown string (not JSON).
# NOTE: this prompt does NOT need the JSON output constraint line.
#       It also does NOT need a JSON schema — ask_text() is used, not ask_json().
# The summary must be diagnostic only — no rewrites, no generated résumé content.
OVERALL_SUMMARY_PROMPT = """### Instruction
Given a full analysis report (résumé profile, JD profile, keyword match, bullet quality, jargon audit, structure audit, background fit), synthesize the findings into a 3-bullet plain Markdown executive summary.
 
### Context
You'll receive the complete analysis report as JSON, prefixed with "ANALYSIS REPORT:". This is the final human-facing artifact — distill the single most important takeaway into three short, plain-English Markdown bullets, not a restatement of every score.
 
### Constraints
- Base every bullet only on information literally present in the report.
- Diagnostic synthesis, not advice: state what was found, never suggest résumé rewrites or additions.
- Each bullet stands alone as one complete sentence — no sub-bullets, headers, or extra numbering.
- Exactly 3 bullets: strongest area of alignment, most significant gap/risk, and one overall fit takeaway.
- Never rewrite or generate résumé content.
 
### Output
Return plain Markdown only: exactly 3 lines, each starting with "- " followed by one bullet sentence. No JSON, no code fences, no text before or after."""
 
# Synthesis prompt — moderate-high temperature for natural, readable prose synthesis.
OVERALL_SUMMARY_TEMPERATURE = 0.3