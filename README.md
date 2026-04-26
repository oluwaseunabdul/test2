# Research Topic Discovery Platform - FREE Version

## 🎯 Zero-Cost Setup (No Paid API Keys Required!)

This platform is now **100% free to use** with no paid API keys required. All core features work out of the box using:
- ✅ **FREE academic APIs**: PubMed, Semantic Scholar, Crossref, OpenAlex (no keys needed)
- ✅ **Local AI processing**: Rule-based NLP for gap categorization and search strategy generation
- ✅ **Template-based generators**: PICO questions, PROSPERO drafts, search strategies

Optional: You can add OpenAI or Anthropic keys later for enhanced AI features, but everything works perfectly without them.

---

## 🚀 Quick Start (5 Minutes)

### Prerequisites
```bash
# Install Python 3.11+ and Node.js 18+
# Install PostgreSQL
```

### Step 1: Set Up Database
```bash
# Create database
sudo -u postgres psql -c "CREATE DATABASE research_platform;"
sudo -u postgres psql -c "ALTER USER postgres PASSWORD 'postgres';"
```

### Step 2: Configure Backend
```bash
cd /workspace/backend

# Create .env file (copy this exactly)
cat > .env << 'ENVEOF'
# NO API KEYS NEEDED - Everything works free!
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/research_platform
SECRET_KEY=change-this-in-production
AI_MODE=local
ENVEOF
```

### Step 3: Install Backend Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run Backend
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Step 5: Install & Run Frontend
```bash
cd /workspace/frontend
npm install
npm run dev
```

### Access the App
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🔑 What Works Without API Keys?

### ✅ FULLY FUNCTIONAL (Free)
| Feature | Description |
|---------|-------------|
| **PubMed Integration** | Fetch systematic reviews, extract gaps |
| **Semantic Scholar** | Search papers, get citations |
| **Crossref** | Metadata lookup |
| **OpenAlex** | Trend analysis |
| **Gap Extraction** | Rule-based NLP categorization |
| **Search Strategies** | Template-based for PubMed, Embase, Scopus, WoS |
| **PICO Builder** | Auto-generate research questions |
| **PROSPERO Drafts** | Complete registration templates |
| **Trend Analysis** | Publication trends, emerging topics |
| **Export** | PDF, Markdown, TXT, RIS formats |
| **Dark Mode** | Theme toggle |
| **Project Saving** | PostgreSQL persistence |

### ⭐ Optional Enhancements (Requires API Keys)
| Enhancement | API Key Needed |
|-------------|----------------|
| Enhanced gap categorization | OpenAI or Anthropic |
| Smarter search strategies | OpenAI or Anthropic |
| Contextual reasoning | OpenAI or Anthropic |

---

## 📁 Project Structure

```
/workspace/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI entry point
│   │   ├── core/config.py       # Settings (no keys needed!)
│   │   ├── services/
│   │   │   ├── ai_service.py    # FREE local AI + optional LLM
│   │   │   └── research_api.py  # Free academic APIs
│   │   └── nlp/
│   │       └── gap_extraction.py # Rule-based gap detection
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── App.tsx
│   │   └── components/
│   └── package.json
└── README.md
```

---

## 🛠️ Configuration Options

### Environment Variables (.env)

```bash
# Required
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/research_platform
SECRET_KEY=your-secret-key-here

# Optional (leave empty for free mode)
OPENAI_API_KEY=           # Leave empty
ANTHROPIC_API_KEY=        # Leave empty
AI_MODE=local             # Use "local" for free mode
```

### Switching to LLM Mode (Optional)
If you later want to add OpenAI/Claude:
```bash
AI_MODE=llm
OPENAI_API_KEY=sk-your-key
```

The app will automatically use LLM when available, fall back to local if not.

---

## 🧪 Testing Without API Keys

```bash
# Test backend health
curl http://localhost:8000/health

# Test gap extraction (free)
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "field": "Sports Science",
    "topic": "exercise intervention diabetes",
    "year_start": 2019,
    "year_end": 2024
  }'
```

---

## 📊 Features Breakdown

### 1. Research Configuration
- Multi-field selection (Sports Science, Medicine, Psychology, etc.)
- Year range slider (3-15 years)
- Min citations filter
- Data source toggle (all free APIs)

### 2. Gap Discovery Engine
- Fetches recent systematic reviews from PubMed
- Extracts "future research" statements
- Categorizes gaps by type (Methodological, Population, etc.)
- Ranks by impact, feasibility, recency

### 3. Trend Analysis
- Time-series publication data
- Emerging topic detection
- Citation velocity tracking
- Interactive charts (Recharts)

### 4. Search Strategy Generator
- PubMed, Embase, Scopus, Web of Science formats
- Boolean logic builder
- Field tags and filters
- One-click copy

### 5. PICO & Protocol Builder
- Interactive PICO form
- Auto research questions
- PRISMA flow diagram estimates
- PROSPERO registration drafts

### 6. Export Options
- PDF reports
- Markdown/TXT
- RIS format (Zotero/EndNote)
- Clipboard copy

---

## 🐳 Docker Deployment (Optional)

```bash
# Build and run with Docker Compose
docker-compose up -d
```

---

## 🆘 Troubleshooting

### "No space left on device"
```bash
# Clean up node_modules if needed
rm -rf frontend/node_modules
npm install
```

### Database connection error
```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Recreate database
sudo -u postgres psql -c "DROP DATABASE IF EXISTS research_platform;"
sudo -u postgres psql -c "CREATE DATABASE research_platform;"
```

### Port already in use
```bash
# Change backend port
uvicorn app.main:app --port 8001

# Change frontend port in vite.config.ts
```

---

## 📝 License

MIT License - Free for academic and commercial use.

## 🤝 Contributing

Contributions welcome! This platform is designed to be:
- 100% free to use
- No mandatory API keys
- Production-ready
- Researcher-friendly
