"""
Flask API for Schedule Sculptor RAG system.
Provides a /query endpoint that accepts course-related questions
and returns relevant course recommendations using the FAISS index.
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
from pathlib import Path
import json
import re

import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Global variables for index and model
index = None
chunks_df = None
model = None
config = None

# Query expansion dictionary (same as query.py)
TOPIC_SYNONYMS = {
    r"\bnlp\b": [
        "natural language processing", "computational linguistics",
        "text mining", "language modeling", "transformers", "sequence models"
    ],
    r"\bml\b|\bmachine learning\b": [
        "supervised learning", "unsupervised learning", "classification",
        "regression", "neural networks", "support vector machines", "clustering"
    ],
    r"\bai\b": [
        "artificial intelligence", "knowledge representation", "search algorithms",
        "planning", "intelligent agents"
    ],
    r"\bdata viz\b|\bvisuali[sz]ation\b|\btableau\b": [
        "data visualization", "tableau", "plotting", "dashboards", "visual analytics"
    ],
    r"\bstats?\b|\bstatistics\b": [
        "statistical inference", "probability", "hypothesis testing",
        "regression analysis", "experimental design"
    ],
    r"\boptimization\b|\boperations research\b|\bor\b": [
        "linear programming", "integer programming", "stochastic optimization",
        "operations research"
    ],
    r"\bcomputational biology\b|\bbioinformatics\b": [
        "genomics", "sequence analysis", "biostatistics", "systems biology"
    ],
    r"\bsecurity\b|\bcybersecurity\b": [
        "cryptography", "network security", "secure systems", "access control"
    ],
    r"\bdatabases?\b": [
        "relational databases", "sql", "transaction processing", "query optimization"
    ],
    r"\beconomics?\b|\becon\b": [
        "microeconomics", "macroeconomics", "econometrics"
    ],
    r"\bpsychology\b|\bcognitive\b": [
        "cognitive science", "perception", "human factors", "behavioral science"
    ],
}

def expand_query(q: str) -> str:
    """Add synonyms/related phrases to the query while keeping the original text."""
    q_low = q.lower()
    expansions = []
    for pattern, syns in TOPIC_SYNONYMS.items():
        if re.search(pattern, q_low):
            expansions.extend(syns)
    if expansions:
        return q + " | " + " ; ".join(dict.fromkeys(expansions))
    return q


def load_index():
    """Load FAISS index, chunks CSV, and embedding model on startup."""
    global index, chunks_df, model, config
    
    print("🚀 [Backend-Load] Starting index loading...")
    
    # We know the exact location relative to app.py
    # app.py is in rag/web/ and data is in rag/data/processed/index
    index_dir = Path(__file__).resolve().parent.parent / "data" / "processed" / "index"
    
    print(f"📁 [Backend-Load] Looking for data in: {index_dir}")
    print(f"📁 [Backend-Load] Absolute path: {index_dir.resolve()}")
    
    if not index_dir.exists():
        print(f"❌ [Backend-Load] Data directory not found: {index_dir}")
        raise FileNotFoundError(f"Data directory not found: {index_dir}")
    
    # Check if required files exist
    idx_path = index_dir / "faiss.index"
    tbl_path = index_dir / "chunks.csv"
    cfg_path = index_dir / "config.json"
    
    required_files = {
        "faiss.index": idx_path,
        "chunks.csv": tbl_path, 
        "config.json": cfg_path
    }
    
    missing_files = []
    for name, path in required_files.items():
        if not path.exists():
            missing_files.append(name)
        else:
            print(f"✅ [Backend-Load] Found {name}: {path.stat().st_size} bytes")
    
    if missing_files:
        print(f"❌ [Backend-Load] Missing files: {missing_files}")
        raise FileNotFoundError(f"Missing index files: {missing_files}")
    
    try:
        print("📥 [Backend-Load] Loading FAISS index...")
        index = faiss.read_index(str(idx_path))
        print(f"✅ [Backend-Load] FAISS index loaded: {index.ntotal} vectors")
        
        print("📥 [Backend-Load] Loading CSV data...")
        chunks_df = pd.read_csv(tbl_path)
        print(f"✅ [Backend-Load] CSV loaded: {len(chunks_df):,} rows, {len(chunks_df.columns)} columns")
        
        print("📥 [Backend-Load] Loading config...")
        config = json.loads(cfg_path.read_text())
        print(f"✅ [Backend-Load] Config loaded with model: {config.get('model')}")
        
        print("📥 [Backend-Load] Loading sentence transformer model...")
        model = SentenceTransformer(config["model"])
        print(f"✅ [Backend-Load] Model loaded: {config['model']}")
        
        print("🎉 [Backend-Load] All components loaded successfully!")
        
    except Exception as e:
        print(f"❌ [Backend-Load] Failed to load components: {e}")
        import traceback
        print(f"❌ [Backend-Load] Traceback: {traceback.format_exc()}")
        raise

def retrieve_and_group(query: str, top_courses: int = 8):
    """Retrieve top courses based on query using RAG."""
    
    print(f"🔍 [Backend-RAG] Starting retrieval for: '{query}'")
    
    if index is None or model is None:
        print("❌ [Backend-RAG] Index or model not available")
        return []
    
    # Check if chunks_df is loaded and has data
    print(f"📊 [Backend-RAG] chunks_df type: {type(chunks_df)}")
    print(f"📊 [Backend-RAG] chunks_df shape: {chunks_df.shape if chunks_df is not None else 'None'}")
    if chunks_df is not None and len(chunks_df) > 0:
        print(f"📊 [Backend-RAG] chunks_df columns: {chunks_df.columns.tolist()}")
        print(f"📊 [Backend-RAG] First few rows sample:")
        print(chunks_df.head(3))
    else:
        print("❌ [Backend-RAG] chunks_df is empty or None")
        return []
    
    # Expand query
    q_expanded = expand_query(query)
    print(f"🔍 [Backend-RAG] Original query: '{query}'")
    print(f"🔍 [Backend-RAG] Expanded query: '{q_expanded}'")
    
    # Encode and search
    print("🔍 [Backend-Road] Encoding query...")
    try:
        q_emb = model.encode([q_expanded], normalize_embeddings=True).astype("float32")
        print(f"🔍 [Backend-RAG] Query embedding shape: {q_emb.shape}")
    except Exception as e:
        print(f"❌ [Backend-RAG] Encoding failed: {e}")
        return []
    
    chunk_k = max(50, top_courses * 5)
    print(f"🔍 [Backend-RAG] Searching index with k={chunk_k}...")
    
    try:
        scores, idxs = index.search(q_emb, chunk_k)
        print(f"🔍 [Backend-RAG] Search completed. Scores: {scores.shape}, Indices: {idxs.shape}")
        print(f"🔍 [Backend-RAG] Top 5 scores: {scores[0][:5]}")
        print(f"🔍 [Backend-RAG] Top 5 indices: {idxs[0][:5]}")
    except Exception as e:
        print(f"❌ [Backend-RAG] Search failed: {e}")
        return []
    
    idxs = idxs[0].tolist()
    scores = scores[0].tolist()
    
    print(f"🔍 [Backend-RAG] Found {len(idxs)} initial chunks")
    print(f"🔍 [Backend-RAG] Score range: min={min(scores):.4f}, max={max(scores):.4f}")
    
    # Check if we have any valid indices
    valid_indices = [idx for idx in idxs if idx < len(chunks_df)]
    print(f"🔍 [Backend-RAG] Valid indices: {len(valid_indices)}/{len(idxs)}")
    
    if not valid_indices:
        print("❌ [Backend-RAG] No valid indices found")
        return []
    
    # Get matching chunks
    res_df = chunks_df.iloc[idxs].copy()
    res_df.insert(0, "score", scores)
    
    print(f"📊 [Backend-RAG] res_df shape: {res_df.shape}")
    print(f"📊 [Backend-RAG] res_df columns: {res_df.columns.tolist()}")
    
    # Check for required columns
    if "metadata.parent_id" not in res_df.columns:
        print("⚠️ [Backend-RAG] 'metadata.parent_id' column not found, using 'id' instead")
        res_df["metadata.parent_id"] = res_df["id"]
    
    print("🔍 [Backend-RAG] Grouping results by course...")
    
    # Check if we have any data to group
    if len(res_df) == 0:
        print("❌ [Backend-RAG] No data in res_df after search")
        return []
    
    try:
        best = (
            res_df
            .sort_values("score", ascending=False)
            .drop_duplicates(subset=["metadata.parent_id"], keep="first")
            .copy()
        )
        print(f"🔍 [Backend-RAG] After grouping: {len(best)} unique courses")
        
        top = best.head(top_courses).copy()
        print(f"🔍 [Backend-RAG] After head({top_courses}): {len(top)} courses")
        
    except Exception as e:
        print(f"❌ [Backend-RAG] Grouping failed: {e}")
        return []
    
    # Extract fields safely
    def safe_get(row, col, default=""):
        val = row.get(col, default)
        return str(val) if pd.notna(val) else default
    
    results = []
    for i, (_, row) in enumerate(top.iterrows()):
        course_code = safe_get(row, "metadata.course_code")
        class_name = safe_get(row, "metadata.class_name")
        subject = safe_get(row, "metadata.subject") or safe_get(row, "metadata.subject_code")
        text = safe_get(row, "text")
        score = float(row["score"]) if "score" in row else 0.0
        
        print(f"📚 [Backend-RAG] Result {i+1}:")
        print(f"   - Course code: '{course_code}'")
        print(f"   - Class name: '{class_name}'")
        print(f"   - Subject: '{subject}'")
        print(f"   - Score: {score:.3f}")
        print(f"   - Text preview: '{text[:100] if text else ''}...'")
        
        results.append({
            "course_code": course_code,
            "class_name": class_name,
            "subject": subject,
            "description": text,
            "score": score
        })
    
    print(f"✅ [Backend-RAG] Returning {len(results)} formatted results")
    return results

@app.route("/")
def home():
    """Health check endpoint."""
    return jsonify({"status": "ok", "message": "Schedule Sculptor RAG API is running"})

@app.route("/health")
def health_check():
    """Detailed health check endpoint."""
    health_info = {
        "status": "ok" if index is not None else "error",
        "index_loaded": index is not None,
        "model_loaded": model is not None, 
        "chunks_loaded": chunks_df is not None,
        "chunks_count": len(chunks_df) if chunks_df is not None else 0,
        "index_size": index.ntotal if index is not None else 0
    }
    return jsonify(health_info)

@app.route("/check-files")
def check_files():
    """Check if data files exist in expected locations."""
    import os
    from pathlib import Path
    
    # Check multiple possible locations
    check_paths = [
        Path("web/data/processed/index"),  # If root is rag/
        Path("web/data/processed"),        # If root is rag/
        Path("data/processed/index"),      # If files are in rag/data/processed/index
        Path(".") / "data" / "processed" / "index",  # Current dir data
        Path(".") / "data" / "processed",           # Current dir data
        Path(__file__).resolve().parent / "data" / "processed" / "index",  # Script relative
        Path(__file__).resolve().parent / "data" / "processed",           # Script relative
    ]
    
    results = {}
    for path in check_paths:
        results[str(path)] = {
            "exists": path.exists(),
            "files": []
        }
        if path.exists():
            for file in path.iterdir():
                results[str(path)]["files"].append({
                    "name": file.name,
                    "size": file.stat().st_size if file.is_file() else "dir",
                    "is_file": file.is_file()
                })
    
    return jsonify({
        "current_directory": str(Path.cwd()),
        "script_directory": str(Path(__file__).resolve().parent),
        "environment_variables": {
            "RENDER": os.environ.get('RENDER'),
            "PORT": os.environ.get('PORT'),
        },
        "file_checks": results
    })

@app.route("/query", methods=["POST"])
def query():
    """
    Query endpoint that accepts a question and returns relevant courses.
    
    Expected JSON body:
    {
        "query": "courses about machine learning",
        "top_courses": 8  // optional, default 8
    }
    
    Returns:
    {
        "query": "...",
        "results": [
            {
                "course_code": "CS 412",
                "class_name": "Introduction to Machine Learning",
                "subject": "Computer Science",
                "description": "...",
                "score": 0.85
            },
            ...
        ]
    }
    """
    try:
        data = request.get_json()
        
        if not data or "query" not in data:
            return jsonify({"error": "Missing 'query' field in request"}), 400
        
        user_query = data["query"]
        top_courses = data.get("top_courses", 8)
        
        if not user_query.strip():
            return jsonify({"error": "Query cannot be empty"}), 400
        
        # Retrieve courses
        results = retrieve_and_group(user_query, top_courses)
        
        return jsonify({
            "query": user_query,
            "results": results,
            "count": len(results)
        })
    
    except Exception as e:
        print(f"[app] Error processing query: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    try:
        load_index()
        print("✅ [Backend] Index loading completed successfully")
    except Exception as e:
        print(f"❌ [Backend] Failed to load index: {e}")
        import traceback
        print(f"❌ [Backend] Traceback: {traceback.format_exc()}")
        index = chunks_df = model = config = None

    # Read port from environment so frontend and backend can be started on the same port.
    # Default to 5001 to avoid common macOS services on 5000.
    port_env = os.environ.get("RAG_API_PORT") or os.environ.get("PORT") or os.environ.get("RAG_PORT")
    try:
        port = int(port_env) if port_env else 5001
    except ValueError:
        port = 5001

    host = os.environ.get("RAG_API_HOST", "127.0.0.1")
    print(f"[app] Starting Flask server on http://{host}:{port}")
    # Bind to host and port from environment
    app.run(debug=True, host=host, port=port)