# 🎓 Schedule Sculptor - AI Assistant Quick Start

Your RAG model is now fully integrated into the Schedule Sculptor app!

## ✅ What's Been Done

1. **Flask Backend** (`rag/web/app.py`)
   - Loads your FAISS index on startup
   - Exposes `/query` endpoint for course searches
   - Includes query expansion for better results
   - Running on `http://localhost:5000`

2. **React Frontend** (`frontend/src/AIAssistant.jsx`)
   - Beautiful themed interface matching your app
   - Search bar with example queries
   - Real-time results with relevance scores
   - Loading states and error handling

3. **Routing & Navigation**
   - New `/ai-assistant` route in App.jsx
   - "AI Assistant" button in header now works
   - Fully integrated with your existing app theme

## 🚀 How to Run

### Option 1: One Command (Recommended)
```bash
./start.sh
```

### Option 2: Manual (Two Terminals)

**Terminal 1 - Flask Backend:**
```bash
cd rag/web
python app.py
```

**Terminal 2 - React Frontend:**
```bash
cd frontend
npm run dev
```

## 🎯 How to Use

1. Open browser to `http://localhost:5173`
2. Click "AI Assistant" in the header
3. Ask questions like:
   - "Courses about machine learning"
   - "Classes with no prerequisites"
   - "Data visualization electives"
   - "Natural language processing courses"

## 📦 Dependencies Needed

Make sure these are installed in your conda environment:

```bash
pip install flask flask-cors pandas numpy faiss-cpu sentence-transformers
```

Or use the requirements file:
```bash
cd rag/web
pip install -r requirements.txt
```

## 🎨 Design Features

The AI Assistant matches your app's theme:
- ✅ Greek column decorations
- ✅ Purple accent color (#4C3B6F)
- ✅ Cream background (#FAF8F5)
- ✅ Cormorant Garamond serif titles
- ✅ Smooth animations and transitions
- ✅ Responsive mobile design

## 📊 What It Does

1. Takes your natural language question
2. Expands it with synonyms (e.g., "ML" → "machine learning, neural networks...")
3. Converts to vector embedding
4. Searches your FAISS index (all UIC course data)
5. Returns top 8 most relevant courses
6. Shows course code, name, subject, description, and match score

## 🔍 Example Queries to Try

- "What are good intro CS classes?"
- "Advanced data science courses"
- "Classes about artificial intelligence"
- "Electives with no prerequisites"
- "Courses taught in Python"
- "Database design classes"

## 🐛 Troubleshooting

**"Unable to connect to AI Assistant"**
- Make sure Flask is running: `cd rag/web && python app.py`
- Check terminal for errors
- Verify port 5000 isn't already in use

**"Import errors" when starting Flask**
- Install missing packages: `pip install -r rag/web/requirements.txt`
- Make sure you're in your conda environment

**No results showing**
- Check browser console for errors (F12)
- Verify FAISS index exists: `ls rag/data/processed/index/`
- Should see: `faiss.index`, `chunks.csv`, `config.json`

## 📁 Files Created/Modified

```
✅ rag/web/app.py              (Flask API backend)
✅ rag/web/requirements.txt    (Python dependencies)
✅ rag/web/README.md           (Detailed docs)
✅ frontend/src/AIAssistant.jsx (React component)
✅ frontend/src/App.jsx        (Added route)
✅ frontend/src/Layout.jsx     (Connected nav link)
✅ start.sh                    (Startup script)
```

## 🎉 You're All Set!

The RAG model you built is now accessible through a beautiful UI that matches your app's design. Students can ask questions in plain English and get instant, relevant course recommendations!

---

**Questions?** Check `rag/web/README.md` for more details.
