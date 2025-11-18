# Schedule Sculptor - RAG Integration Guide

## Overview
The AI Assistant is now integrated into Schedule Sculptor! It uses RAG (Retrieval-Augmented Generation) with FAISS vector search to help students find relevant courses.

## Architecture
- **Backend**: Flask API (`rag/web/app.py`) serves the RAG model (default dev port 5001; configurable via env var RAG_API_PORT)
- **Frontend**: React component (`frontend/src/AIAssistant.jsx`) provides the UI
- **Index**: FAISS vector database in `rag/data/processed/index/`

## Setup & Running

### 1. Install Backend Dependencies

First, make sure you're in your conda environment, then install the Python dependencies:

```bash
cd rag/web
pip install -r requirements.txt
```

Or if using conda:
```bash
conda install flask flask-cors pandas numpy
pip install faiss-cpu sentence-transformers
```

### 2. Start the Flask Backend

From the `rag/web` directory:

```bash
python app.py
```

You should see:
```
[app] Loading index from .../rag/data/processed/index...
[app] Loaded index with X,XXX chunks
[app] Starting Flask server on http://localhost:5001
```

### 3. Start the React Frontend

In a **separate terminal**, from the `frontend` directory:

```bash
npm run dev
```

### 4. Access the AI Assistant

1. Open your browser to the Vite dev server URL (usually `http://localhost:5173`)
2. Click "AI Assistant" in the header navigation
3. Try asking questions like:
   - "Courses about machine learning"
   - "Classes with no prerequisites"
   - "Natural language processing courses"
   - "Data visualization electives"

## How It Works

1. **User Query**: User types a question in natural language
2. **Query Expansion**: Backend expands the query with synonyms (e.g., "ML" → "machine learning, classification, neural networks")
3. **Vector Search**: Query is embedded and compared against the FAISS index
4. **Retrieval**: Top matching course chunks are retrieved
5. **Grouping**: Results are grouped by course and deduplicated
6. **Display**: Frontend shows courses with relevance scores

## API Endpoint

### POST /query

Request:
```json
{
  "query": "machine learning courses",
  "top_courses": 8
}
```

Response:
```json
{
  "query": "machine learning courses",
  "count": 8,
  "results": [
    {
      "course_code": "CS 412",
      "class_name": "Introduction to Machine Learning",
      "subject": "Computer Science",
      "description": "...",
      "score": 0.85
    }
  ]
}
```

## Troubleshooting

### "Unable to connect to AI Assistant"
- Make sure Flask is running on port 5000
- Check that CORS is enabled in `app.py`
- Verify the frontend is making requests to the correct API URL (default `http://localhost:5001/query` or the value of `VITE_API_URL`)

### "Missing index files"
- Ensure you've built the FAISS index first:
  ```bash
  cd rag/src
  python build_index.py
  ```
- Check that `rag/data/processed/index/` contains:
  - `faiss.index`
  - `chunks.csv`
  - `config.json`

### Backend crashes on startup
- Install missing dependencies from `requirements.txt`
- Check Python version (3.8+ recommended)
- Verify FAISS is installed correctly

## Customization

### Changing the number of results
Edit `AIAssistant.jsx` line 35:
```javascript
top_courses: 8  // Change this number
```

### Adding query synonyms
Edit `app.py` `TOPIC_SYNONYMS` dictionary to add more domain-specific expansions.

### Styling changes
The component uses the same theme as other pages:
- Purple accent color: `#4C3B6F`
- Background: `#FAF8F5`
- Fonts: Cormorant Garamond (serif) + Inter (sans)

## Next Steps

- [ ] Add authentication/rate limiting to the API
- [ ] Cache common queries
- [ ] Add filtering by subject/department
- [ ] Show prerequisites in results
- [ ] Add "Save to schedule" button
- [ ] Integrate with the Dashboard view
