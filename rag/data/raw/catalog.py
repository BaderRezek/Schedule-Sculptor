import re
import pandas as pd
import urllib.parse
import requests
import requests
from bs4 import BeautifulSoup
from bs4 import BeautifulSoup
from urllib.parse import urljoin

base_url = "https://catalog.uic.edu/ucat/course-descriptions/"
response = requests.get(base_url)
soup = BeautifulSoup(response.text, 'html.parser')


subject_links = []
for a in soup.select("a[href]"):
    href = a['href']
    
    if href.startswith("http") and "/course-descriptions/" in href:
        subject_links.append(href)
    elif href.startswith("/"):
        full = urljoin(base_url, href)
        if "/course-descriptions/" in full:
            subject_links.append(full)


# Helper: extract first text
def first_text(el, *sels):
    for s in sels:
        node = el.select_one(s)
        if node:
            return node.get_text(" ", strip=True).replace("\xa0", " ")
    return ""

# --- Regex and utility setup ---
# Accepts single value (3), ranges (1-3 / 1–3), or "3 or 4", with optional decimals
HOURS = r"(?P<credits_raw>\d+(?:\.\d+)?(?:\s*(?:or|-|–)\s*\d+(?:\.\d+)?)?)\s*hour(?:s)?"
HOURS_RX = re.compile(rf"{HOURS}\.?\s*$", re.IGNORECASE)

# Course code like CS 109, MATH 220, BIOS 399A
COURSE_CODE_RX = re.compile(r"\b[A-Z]{2,}\s?\d{2,3}[A-Z]?\b")

# NOTE: Keeping TITLE_RX is optional now (parse_title doesn't use it anymore)
TITLE_RX = re.compile(
    rf"^\s*(?P<course_code>[A-Z& ]+\d+[A-Z]?)\.\s*(?P<class_name>.+?)\.\s*{HOURS}\.?\s*$",
    re.IGNORECASE
)

# Detect "Credit or concurrent registration in ..."
CREDIT_OR_CONCURRENT_RX = re.compile(
    r"(?i)credit\s+or\s+concurrent\s+registration\s+in\s+(?P<target>[^.;]+)"
)

LABELS = [
    r"Prerequisite\(s\):", r"Prerequisites?:",
    r"Corequisite\(s\):", r"Co[- ]?requisites?:",
    r"Requires concurrent registration in ",
    r"Course Information:",
    r"Class Schedule Information:",
    r"Recommended background:"
]
LABEL_RX = re.compile("(?i)" + "(" + "|".join(LABELS) + ")")

def normalize_text(t: str) -> str:
    # FIX: your original ended with `return` (None). Return the cleaned string.
    if t is None:
        return ""
    t = t.replace("\xa0", " ")
    t = re.sub(r"\s+", " ", t).strip()
    t = re.sub(r"\s+\.", ".", t)
    return t  # <-- important

def extract_course_codes(text: str):
    # Dedupe while preserving order
    return list(dict.fromkeys(COURSE_CODE_RX.findall(text or "")))

def parse_title(title_text: str):
    """
    Robustly parse a title like:
      PHIL 106. What Is Religion? 3 hours.
      LING 340. Vocabulary in Action: ... 3 hours.
      BIOS 399. Independent Research. 1–3 hours.
      MATH 220. Calculus. 3 or 4 hours.
    Works regardless of whether the class name ends in '.', '?', ':', etc.
    """
    t = normalize_text(title_text)

    # 1) Extract credits from the tail
    m_hours = HOURS_RX.search(t)
    if not m_hours:
        raise ValueError(f"No hours found: {t}")

    credits_raw = normalize_text(m_hours.group("credits_raw"))
    # derive min/max credits
    nums = re.split(r"(?:or|-|–)", credits_raw)
    nums = [float(x.strip()) for x in nums if x.strip()]
    credits_min = min(nums)
    credits_max = max(nums)

    # Remove the matched credits portion from the tail
    left = t[:m_hours.start()].strip()

    # 2) Extract course code at the start: e.g., "PHIL 106." or "LING 340."
    m_code = re.match(r"^(?P<course_code>[A-Z& ]+\d+[A-Z]?)\.\s*", left)
    if not m_code:
        raise ValueError(f"No course code found: {t}")
    course_code = normalize_text(m_code.group("course_code"))

    # 3) Everything after the code is the class name (strip trailing punctuation)
    class_name = left[m_code.end():].strip().rstrip(" .;:?—–-")
    class_name = normalize_text(class_name)

    return course_code, class_name, credits_raw, credits_min, credits_max

def split_labeled_sections(desc_text: str):
    """
    Extract labeled sections (any order), detect "Credit or concurrent registration in X",
    and return (labels_dict, cleaned_description, prereq_codes, coreq_codes).
    """
    text = normalize_text(desc_text)
    out = {
        "prerequisites": "",
        "corequisites": "",
        "course_information": "",
        "class_schedule_information": "",
        "recommended_background": ""
    }
    prereq_codes = []
    coreq_codes = []

    matches = list(LABEL_RX.finditer(text))
    if not matches:
        # Even if no labels, still check for "Credit or concurrent registration in ..."
        additions = []
        for m in CREDIT_OR_CONCURRENT_RX.finditer(text):
            target = m.group("target").strip()
            additions.append((m.span(), target))
            codes = extract_course_codes(target)
            if codes:
                prereq_codes.extend(codes)
                coreq_codes.extend(codes)
            # Append the phrase to both fields (human-readable)
            out["prerequisites"] = (out["prerequisites"] + " " + f"Credit or concurrent registration in {target}").strip()
            out["corequisites"]  = (out["corequisites"]  + " " + f"Credit or concurrent registration in {target}").strip()
        # remove those phrases from the description (from end to start to keep spans valid)
        for (start, end), _ in reversed(additions):
            text = (text[:start] + text[end:]).strip()
        return out, normalize_text(text), list(dict.fromkeys(prereq_codes)), list(dict.fromkeys(coreq_codes))

    # Split into labeled and plain parts
    parts = []
    last = 0
    for i, m in enumerate(matches):
        start = m.start()
        if start > last:
            parts.append(("plain", text[last:start]))
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        parts.append((m.group(0).lower(), text[m.end():end].strip()))
        last = end
    if last < len(text):
        parts.append(("plain", text[last:]))

    # Rebuild remaining description and map labels
    remaining = []
    for kind, chunk in parts:
        if kind == "plain":
            remaining.append(chunk)
        elif "prereq" in kind:
            out["prerequisites"] = chunk
        elif "coreq" in kind or "requires concurrent registration" in kind:
            out["corequisites"] = (out["corequisites"] + " " + chunk).strip()
        elif "course information" in kind:
            out["course_information"] = chunk
        elif "class schedule information" in kind:
            out["class_schedule_information"] = chunk
        elif "recommended background" in kind:
            out["recommended_background"] = chunk

    # Join the “plain” leftovers
    clean_desc = normalize_text(" ".join(remaining))

    # Scan across all fields for "Credit or concurrent registration in ..."
    fields_to_scan = [
        out["prerequisites"], out["corequisites"],
        out["course_information"], out["class_schedule_information"],
        out["recommended_background"], clean_desc
    ]
    additions = []
    for field_text in fields_to_scan:
        for m in CREDIT_OR_CONCURRENT_RX.finditer(field_text or ""):
            target = m.group("target").strip()
            codes = extract_course_codes(target)
            if codes:
                prereq_codes.extend(codes)
                coreq_codes.extend(codes)
            out["prerequisites"] = (out["prerequisites"] + " " + f"Credit or concurrent registration in {target}").strip()
            out["corequisites"]  = (out["corequisites"]  + " " + f"Credit or concurrent registration in {target}").strip()

    # Remove those phrases from the visible description only
    for m in CREDIT_OR_CONCURRENT_RX.finditer(clean_desc):
        additions.append(m.span())
    for start, end in reversed(additions):
        clean_desc = (clean_desc[:start] + clean_desc[end:]).strip()

    # Normalize and dedupe codes
    prereq_codes = list(dict.fromkeys(prereq_codes))
    coreq_codes  = list(dict.fromkeys(coreq_codes))

    return out, normalize_text(clean_desc), prereq_codes, coreq_codes

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (compatible; CourseCatalogScraper/1.0; +https://catalog.uic.edu)"
})

# ---- Helpers for response type ----
def looks_like_pdf(url: str) -> bool:
    """Return True if a URL likely points to a PDF, so we can skip it."""
    return url.lower().endswith(".pdf")

def is_html_response(resp) -> bool:
    """Return True if the server's Content-Type header is HTML."""
    ctype = (resp.headers.get("Content-Type") or "").lower()
    return "text/html" in ctype

# Scraper loop
rows = []
parse_errors = []

for subject_url in subject_links:
    url = urllib.parse.urljoin("https://catalog.uic.edu", subject_url)

    # Skip non-HTML files (like the giant PDF course catalog)
    if looks_like_pdf(url):
        print("skip non-HTML (pdf):", url)
        continue
    
    try:
        r = session.get(url, timeout=20)
    except requests.RequestException as e:
        print("request error:", e, url)
        continue

    if r.status_code != 200:
        print("bad status", r.status_code, url)
        continue

    subject_soup = BeautifulSoup(r.text, "html.parser")
    blocks = subject_soup.select(".courseblock")
    if not blocks:
        print("no course blocks on", url)
        continue

    # Useful to capture the section (subject) title once per page
    sectiontitle_el = subject_soup.select_one("h1.page-title")
    sectiontitle_page = sectiontitle_el.get_text(strip=True) if sectiontitle_el else ""

    for i, course_block in enumerate(blocks):
        # Reset per-course vars
        course_code = ""
        class_name = ""
        credits_raw = ""
        credits_min = None
        credits_max = None

        # Extract title/description (guard against missing nodes)
        title = first_text(course_block, ".courseblocktitle strong", ".courseblocktitle") or ""
        desc  = first_text(course_block, ".courseblockdesc") or ""

        # Parse structured info from title
        try:
            course_code, class_name, credits_raw, credits_min, credits_max = parse_title(title)
        except ValueError as e:
            # Keep going: log and at least keep a readable class_name
            parse_errors.append(f"{url} | block {i}: {e}")
            class_name = normalize_text(title) or class_name  # fallback to raw title text
            # If there are totally untitled blocks, you can skip them:
            if not class_name and not course_code:
                continue

        # Split labeled sections (prereq/coreq/etc.)
        labels, desc_clean, prereq_codes, coreq_codes = split_labeled_sections(desc)

        # Clean up occasional junk artifacts
        junk = "non-javascript:;"
        for k in list(labels.keys()):
            labels[k] = (labels.get(k) or "").replace(junk, "").strip()
        desc_clean = (desc_clean or "").replace(junk, "").strip()

        # Append structured row
        rows.append({
            "section_title": sectiontitle_page,          # page-level title (subject)
            "course_code": course_code,
            "class_name": class_name,
            "credits_raw": credits_raw,
            "credits_min": credits_min,
            "credits_max": credits_max,
            "description": desc_clean,
            "prerequisites": labels.get("prerequisites", ""),
            "corequisites": labels.get("corequisites", ""),
            "course_information": labels.get("course_information", ""),
            "class_schedule_information": labels.get("class_schedule_information", ""),
            "recommended_background": labels.get("recommended_background", ""),
            "prereq_codes": prereq_codes,                # list
            "coreq_codes": coreq_codes,                  # list
            "source_url": url,                           # helpful for debugging
            "block_idx": i                               # block index on page
        })

# Build final DataFrame
full_course_data = pd.DataFrame(rows)

# RAG export: build per-course documents + chunks and write JSONL/Parquet

import json, re, math, hashlib, unicodedata
from pathlib import Path

import numpy as np
import pandas as pd

# ----------------- Helpers -----------------
def slugify(text: str, keep: str = "-") -> str:
    text = unicodedata.normalize("NFKD", text or "").encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", keep, text).strip(keep)
    return text.lower()

def stable_id(*parts) -> str:
    base = "::".join([p or "" for p in parts])
    h = hashlib.sha1(base.encode("utf-8")).hexdigest()[:12]
    return f"{slugify(base)}::{h}"

def norm_str(x):
    if x is None:
        return ""
    if isinstance(x, float) and math.isnan(x):
        return ""
    return str(x).strip()

def normalize_list(x):
    """
    Return a clean Python list of strings.
    Handles: None/NaN, list/tuple, numpy arrays, strings, and scalars.
    """
    # None / NaN (float NaN)
    if x is None:
        return []
    if isinstance(x, float):
        return [] if math.isnan(x) else [str(x).strip()]

    # Strings: split on common delimiters, keep order
    if isinstance(x, str):
        s = x.strip()
        if not s:
            return []
        parts = re.split(r"[;,]\s*|\s{2,}", s)
        return [p for p in (p.strip() for p in parts) if p]

    # List/tuple
    if isinstance(x, (list, tuple)):
        return [str(v).strip() for v in x if str(v).strip()]

    # NumPy array
    if isinstance(x, np.ndarray):
        return [str(v).strip() for v in x.tolist() if str(v).strip()]

    # Pandas NA scalar
    if pd.api.types.is_scalar(x):
        try:
            if pd.isna(x):
                return []
        except Exception:
            pass
        s = str(x).strip()
        return [s] if s else []

    # Fallback single value
    s = str(x).strip()
    return [s] if s else []

def chunk_text_words(text: str, max_words: int = 500, overlap: int = 80):
    """
    Simple word-based chunker (model-agnostic).
    max_words ~ 500 keeps embeddings small; overlap ~ 80 preserves context.
    """
    text = norm_str(text)
    words = text.split()
    if not words:
        return [text]
    chunks, i = [], 0
    step = max_words - overlap if max_words > overlap else max_words
    while i < len(words):
        chunks.append(" ".join(words[i:i + max_words]))
        i += step
    return chunks

def subject_code_from_course(course_code: str) -> str:
    """
    Extracts leading alphabetic subject code from e.g. 'MATH 220' -> 'MATH'.
    """
    m = re.match(r"^\s*([A-Z&]+)\s*\d", norm_str(course_code))
    return m.group(1) if m else ""

# ----------------- Validate source df -----------------
required_cols = [
    "section_title","course_code","class_name","description",
    "credits_raw","credits_min","credits_max",
    "prerequisites","corequisites","course_information",
    "class_schedule_information","recommended_background",
    "prereq_codes","coreq_codes","source_url","block_idx"
]
missing = [c for c in required_cols if c not in full_course_data.columns]
if missing:
    print("WARNING: missing expected columns:", missing)

df = full_course_data.copy()

# Fill/normalize columns safely (strings)
for c in ["section_title","course_code","class_name","description",
          "credits_raw","prerequisites","corequisites",
          "course_information","class_schedule_information","recommended_background","source_url"]:
    if c not in df.columns:
        df[c] = ""
    df[c] = df[c].apply(norm_str)

# Numeric credits min/max
for c in ["credits_min","credits_max"]:
    if c not in df.columns:
        df[c] = None

# Parsed code lists
for c in ["prereq_codes","coreq_codes"]:
    if c not in df.columns:
        df[c] = [[]]
    df[c] = df[c].apply(normalize_list)

# De-duplicate per (course_code, class_name); keep longest description
df["desc_len"] = df["description"].str.len().fillna(0)
df = df.sort_values(["course_code","class_name","desc_len"], ascending=[True,True,False])
df_unique = df.drop_duplicates(subset=["course_code","class_name"], keep="first").drop(columns=["desc_len"])

# ----------------- Build canonical doc text per course -----------------
def build_doc_row(row: pd.Series):
    subject      = norm_str(row.get("section_title"))
    code         = norm_str(row.get("course_code"))
    subj_code    = subject_code_from_course(code)
    title        = norm_str(row.get("class_name"))
    desc         = norm_str(row.get("description"))
    cred_r       = norm_str(row.get("credits_raw"))
    cred_min     = row.get("credits_min")
    cred_max     = row.get("credits_max")
    prereq       = norm_str(row.get("prerequisites"))
    coreq        = norm_str(row.get("corequisites"))
    info         = norm_str(row.get("course_information"))
    sched        = norm_str(row.get("class_schedule_information"))
    backgr       = norm_str(row.get("recommended_background"))
    url          = norm_str(row.get("source_url"))
    prereq_codes = normalize_list(row.get("prereq_codes"))
    coreq_codes  = normalize_list(row.get("coreq_codes"))

    # Canonical RAG-friendly body
    parts = [
        f"Course: {code} — {title}",
        f"Subject: {subject}" if subject else (f"Subject Code: {subj_code}" if subj_code else ""),
        f"Credits: {cred_r}" if cred_r else "",
        "",
        "Description:",
        desc or "(No description provided.)",
    ]
    if prereq:
        parts += ["", "Prerequisites:", prereq]
    if coreq:
        parts += ["", "Corequisites:", coreq]
    if info:
        parts += ["", "Course Information:", info]
    if sched:
        parts += ["", "Class Schedule Information:", sched]
    if backgr:
        parts += ["", "Recommended Background:", backgr]
    if prereq_codes:
        parts += ["", "Prereq Codes (parsed):", ", ".join(prereq_codes)]
    if coreq_codes:
        parts += ["", "Coreq Codes (parsed):", ", ".join(coreq_codes)]

    text = "\n".join([p for p in parts if p != ""]).strip()

    metadata = {
        "course_code": code,
        "class_name": title,
        "subject": subject,
        "subject_code": subj_code,
        "credits_raw": cred_r,
        "credits_min": float(cred_min) if cred_min is not None else None,
        "credits_max": float(cred_max) if cred_max is not None else None,
        "prereq_codes": prereq_codes,
        "coreq_codes": coreq_codes,
        "source_url": url,
    }

    doc_id = stable_id(code, title)  # deterministic upsert key
    return {"id": doc_id, "text": text, "metadata": metadata}

docs = [build_doc_row(r) for _, r in df_unique.iterrows()]

# ----------------- Chunk for embeddings -----------------
def build_chunks(docs, max_words=500, overlap=80):
    out = []
    for d in docs:
        chunks = chunk_text_words(d["text"], max_words=max_words, overlap=overlap)
        total = len(chunks)
        for idx, chunk in enumerate(chunks, start=1):
            out.append({
                "id": f"{d['id']}::chunk-{idx}",
                "text": chunk,
                "metadata": {
                    **d["metadata"],
                    "parent_id": d["id"],
                    "chunk_index": idx,
                    "chunk_count": total
                }
            })
    return out

chunks = build_chunks(docs, max_words=500, overlap=80)

# ----------------- Save to JSONL (RAG-ready) -----------------
base_dir = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
out_dir = (base_dir.parent / "processed" / "rag_export").resolve()
out_dir.mkdir(parents=True, exist_ok=True)

docs_path   = out_dir / "rag_docs.jsonl"
chunks_path = out_dir / "rag_chunks.jsonl"

with docs_path.open("w", encoding="utf-8") as f:
    for d in docs:
        f.write(json.dumps(d, ensure_ascii=False) + "\n")

with chunks_path.open("w", encoding="utf-8") as f:
    for c in chunks:
        f.write(json.dumps(c, ensure_ascii=False) + "\n")


# ----------------- Save to CSV (RAG-ready) -----------------
# Export to data/processed/rag_export relative to this notebook/script
base_dir = Path(__file__).resolve().parent if "__file__" in globals() else Path.cwd()
out_dir = (base_dir.parent / "processed" / "rag_export").resolve()
out_dir.mkdir(parents=True, exist_ok=True)

# Convert docs and chunks to DataFrames
docs_df   = pd.json_normalize(docs)
chunks_df = pd.json_normalize(chunks)

# Save as CSV
docs_path   = out_dir / "rag_docs.csv"
chunks_path = out_dir / "rag_chunks.csv"

docs_df.to_csv(docs_path, index=False, encoding="utf-8")
chunks_df.to_csv(chunks_path, index=False, encoding="utf-8")