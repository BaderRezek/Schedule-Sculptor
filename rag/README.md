# 🧩 RAG — Course Catalog Retrieval Pipeline

This repository powers the **Schedule Sculptor RAG system**, a retrieval-augmented pipeline that turns unstructured university catalog data into structured, searchable, and chunked course information ready for large-language-model applications.

---

## 📚 Overview

The goal of this pipeline is to **extract, clean, and prepare academic catalog data** for intelligent querying — for example, “Which UIC classes require Calculus II?” or “Find electives with no prerequisites in Computer Science.”

It does this by scraping the public UIC catalog, structuring the course metadata, and exporting clean text chunks optimized for vector-based retrieval.

---

## 🧠 Pipeline Flow

data/raw/catalog.py
↓
raw DataFrame of courses
↓
processed/rag_export/
├── rag_docs.jsonl   ← full course documents
├── rag_chunks.jsonl ← chunked text for embeddings
├── rag_docs.csv     ← tabular for inspection
└── rag_chunks.csv   ← chunk-level table
↓
src/ingest.py → future embedding & retrieval stage

---

## 📂 Folder Structure
rag/
├── data/
│   ├── raw/
│   │   ├── catalog.ipynb   ← interactive scraper
│   │   ├── catalog.py      ← CLI scraper version
│   │   └── init.py
│   └── processed/
│       └── rag_export/     ← final outputs (JSONL & CSV)
│
├── src/
│   ├── ingest.py           ← ingestion script (planned)
│   └── init.py
│
└── README.md               ← you are here

---

## ⚙️ How It Works

1. **Scraper (`data/raw/catalog.py`)**
   - Collects all UIC subject URLs.
   - Parses titles, credits, and descriptions.
   - Detects and separates prerequisites, corequisites, and background info.
   - Handles exceptions (e.g., “Credit or concurrent registration in ...”).

2. **Processing**
   - Normalizes messy text into structured columns.
   - Builds unique, stable course IDs and deduplicates overlapping entries.

3. **RAG Export**
   - Creates two layers of outputs:
     - **Docs**: one per course, with full metadata.
     - **Chunks**: overlapping ~500-word text slices for embedding.
   - Saves both JSONL and CSV for flexibility.

4. **Ingestion (coming soon)**
   - Will embed chunks using OpenAI, Hugging Face, or sentence-transformers.
   - Enables semantic search, retrieval-augmented QA, and schedule planning tools.

---

## 📦 Outputs

| File | Description |
|------|--------------|
| `rag_docs.jsonl` | One JSON object per course with metadata |
| `rag_chunks.jsonl` | Smaller overlapping text chunks for embeddings |
| `rag_docs.csv` | Flattened course-level data |
| `rag_chunks.csv` | Flattened chunk-level data |

All outputs are stored in: data/processed/rag_export/

---

## 🧰 Requirements

```bash
conda install -c conda-forge pandas beautifulsoup4 requests pyarrow
# or
pip install pandas beautifulsoup4 requests pyarrow
```
---

## 🚀 Run the Scraper

From the data/raw/ folder:
python catalog.py

This will generate and export the processed files automatically.


