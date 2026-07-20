"""
parse.py

Utilities for reading and validating résumé PDFs and job description text
files before they are fed into downstream processing (e.g. LLM prompts).
"""

import os
import re
import sys

from pypdf import PdfReader

MAX_RESUME_CHARS = 24_000
MIN_RESUME_CHARS = 200
MIN_JD_CHARS = 100
MAX_RESUME_PAGES = 2


def read_resume_pdf(path: str) -> str:
    """
    Read a résumé PDF and return its cleaned text content.

    Args:
        path: Path to the PDF file.

    Returns:
        The extracted (and cleaned) text of the résumé.

    Raises:
        ValueError: If the file cannot be found/opened, if the extracted
            text is too short (suggesting an image-based/scanned PDF),
            or for any other read failure.
    """
    if not os.path.isfile(path):
        raise ValueError(f"Résumé PDF not found: '{path}'")

    try:
        reader = PdfReader(path)
    except Exception as exc:
        raise ValueError(f"Could not open résumé PDF '{path}': {exc}") from exc

    num_pages = len(reader.pages)
    if num_pages > MAX_RESUME_PAGES:
        print(
            f"Warning: résumé '{path}' has {num_pages} pages "
            f"(expected at most {MAX_RESUME_PAGES}).",
            file=sys.stderr,
        )

    try:
        page_texts = [page.extract_text() or "" for page in reader.pages]
    except Exception as exc:
        raise ValueError(f"Could not extract text from résumé PDF '{path}': {exc}") from exc

    text = "\n\n".join(page_texts)

    # Collapse runs of 3+ blank lines down to 2.
    text = re.sub(r"\n{3,}", "\n\n", text)

    if len(text) < MIN_RESUME_CHARS:
        raise ValueError(
            f"Extracted text from '{path}' is too short ({len(text)} chars). "
            "The PDF may be image-based (scanned) rather than text-based."
        )

    if len(text) > MAX_RESUME_CHARS:
        print(
            f"Warning: résumé text truncated from {len(text)} to "
            f"{MAX_RESUME_CHARS} characters.",
            file=sys.stderr,
        )
        text = text[:MAX_RESUME_CHARS]

    return text


def read_jd_text(path: str) -> str:
    """
    Read a job description from a UTF-8 plain text file.

    Args:
        path: Path to the text file.

    Returns:
        The job description text.

    Raises:
        ValueError: If the file cannot be found, or if the content is
            too short after stripping whitespace.
    """
    if not os.path.isfile(path):
        raise ValueError(f"Job description file not found: '{path}'")

    try:
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception as exc:
        raise ValueError(f"Could not read job description file '{path}': {exc}") from exc

    if len(text.strip()) < MIN_JD_CHARS:
        raise ValueError(
            f"Job description in '{path}' is too short "
            f"({len(text.strip())} chars after stripping whitespace; "
            f"minimum is {MIN_JD_CHARS})."
        )

    return text