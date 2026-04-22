# 🚀 Setup Guide - TodoApp with AI Agent

## Prerequisites

- Python 3.10+
- pip (Python package manager)
- Git

## Installation Steps

### 1. Clone Repository (hoặc download code)
```bash
git clone <your-repo-url>
cd ToDoApp
```

### 2. Create Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Environment Variables
```bash
# Copy example file
cp .env.example .env

# Edit .env and add your values:
# - GOOGLE_API_KEY (required - get from https://aistudio.google.com)
# - DATABASE_URL (optional - default is SQLite)
```

### 5. Initialize Database
```bash
# For SQLite (default)
python -c "from database import engine, Base; Base.metadata.create_all(bind=engine); print('✅ Database initialized')"

# For Alembic migrations (if needed)
# alembic upgrade head
```

### 6. Run Tests
```bash
python test_agent.py
```

### 7. Start Server
```bash
uvicorn main:app --reload
```

Server will run at: `http://localhost:8000`
API docs: `http://localhost:8000/docs`

## Project Structure

```
ToDoApp/
├── requirements.txt          # ← Dependencies (install via pip install -r requirements.txt)
├── .env.example             # ← Template for environment variables
├── SETUP.md                 # ← This file
├── main.py                  # FastAPI app
├── database.py              # Database config
├── models.py                # SQLAlchemy models
├── agents/                  # AI Agent
│   ├── __init__.py
│   └── todo_agent.py
├── routers/                 # API endpoints
│   ├── auth.py
│   ├── todos.py
│   ├── gemini.py
│   ├── users.py
│   └── admin.py
└── doc/                     # Documentation
    ├── README_AI_AGENT.md
    ├── QUICK_REFERENCE.md
    └── ...
```

## Quick Verification

After setup, verify everything is working:

```bash
# Test 1: Check Python version
python --version

# Test 2: Check imports
python -c "import fastapi, sqlalchemy, langchain; print('✅ All imports OK')"

# Test 3: Run test suite
python test_agent.py

# Test 4: Start server
uvicorn main:app --reload
```

## Troubleshooting

### Issue: "No module named 'fastapi'"
**Solution:**
```bash
pip install -r requirements.txt
```

### Issue: "GOOGLE_API_KEY not found"
**Solution:**
1. Create `.env` file (copy from `.env.example`)
2. Add your Google Gemini API key
3. Restart server

### Issue: "Module not found"
**Solution:**
```bash
# Make sure virtual environment is activated
# Windows
.venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

pip install -r requirements.txt
```

### Issue: Port 8000 already in use
**Solution:**
```bash
uvicorn main:app --reload --port 8001
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| GOOGLE_API_KEY | ✅ Yes | Google Gemini API key |
| DATABASE_URL | ❌ No | Database connection string (default: SQLite) |
| SECRET_KEY | ❌ No | JWT secret key |

## Next Steps

1. ✅ Install dependencies: `pip install -r requirements.txt`
2. ✅ Setup `.env` file with API key
3. ✅ Run tests: `python test_agent.py`
4. ✅ Start server: `uvicorn main:app --reload`
5. ✅ Open: `http://localhost:8000/docs`
6. ✅ Test the API

## Documentation

- `README_AI_AGENT.md` - Complete overview
- `QUICK_REFERENCE.md` - Quick tips
- `TOOL_CALLING_EXPLAINED.md` - Technical deep dive

## Database Support

**SQLite** (default - no setup needed)
```
Works out of the box, data stored in test.db
```

**PostgreSQL** (production recommended)
```bash
# Install PostgreSQL adapter
pip install psycopg2-binary

# Update .env
DATABASE_URL=postgresql://user:password@localhost:5432/tododb
```

**MySQL**
```bash
# Install MySQL adapter
pip install mysql-connector-python

# Update .env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/tododb
```

---

**Status:** ✅ Ready to Setup  
**Last Updated:** April 22, 2026

