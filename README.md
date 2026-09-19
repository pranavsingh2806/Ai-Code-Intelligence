# 🚀 AI Code Intelligence Platform

**Automated Code Documentation, Explanation, and Optimization using IBM Granite, Watson & Bob**

Transform raw code into professional documentation, visual diagrams, and optimized solutions in seconds.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Development](#development)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

---

## 🎯 Overview

**AI Code Intelligence** is a web platform that leverages IBM's AI services to automatically:

- 📝 Generate professional documentation and docstrings
- 🔍 Explain complex code step-by-step
- ♻️ Refactor and optimize code
- 📊 Create architecture diagrams
- 🧠 Analyze code semantics and sentiment

Perfect for developers, teams, and enterprises who want to accelerate documentation and knowledge transfer.

---

## ✨ Features

### Core Capabilities

| Feature | Service | What It Does |
|---------|---------|-------------|
| **Auto-Documentation** | IBM Granite | Generates docstrings, README, API docs |
| **Code Explanation** | IBM Bob | Step-by-step walkthroughs with visuals |
| **Code Refactoring** | IBM Granite | Optimizes, fixes bugs, improves security |
| **Architecture Diagrams** | IBM Bob | Auto-generates Mermaid diagrams |
| **NLP Analysis** | IBM Watson | Sentiment analysis, entity extraction, keywords |
| **Full Analysis** | All Three | Complete code intelligence report |

### User Experience

✅ **Simple UI** - Upload code or paste directly  
✅ **Multiple Languages** - Python, JavaScript, Java, Go, C++  
✅ **Real-time Results** - See documentation and refactored code instantly  
✅ **Copy-Paste Ready** - All outputs ready to use in your project  
✅ **Export Options** - Download as PDF, Markdown, or JSON  

---

## 🛠️ Tech Stack

### Frontend
- **React 18** - UI components
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **Axios** - HTTP client
- **React Syntax Highlighter** - Code display
- **Mermaid** - Diagram rendering

### Backend
- **FastAPI** - Python web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation

### AI Services
- **IBM Granite** - LLM for code analysis
- **IBM Bob** - Code explanation & architecture
- **IBM Watson NLU** - Natural language processing

### Database
- **PostgreSQL** - Data persistence
- **Prisma** - ORM

### Deployment
- **Vercel** - Frontend hosting
- **IBM Cloud** - Backend & services
- **Docker** - Containerization

---

## 🚀 Quick Start

### Prerequisites
- Node.js 16+
- Python 3.8+
- IBM Cloud account
- PostgreSQL (local or cloud)

### 5-Minute Setup

```bash
# 1. Clone repository
git clone https://github.com/yourusername/ai-code-intelligence.git
cd ai-code-intelligence

# 2. Set up environment
cp .env.example .env
# Edit .env with your IBM Cloud credentials

# 3. Install dependencies
pip install -r requirements.txt
cd frontend && npm install

# 4. Run services
# Terminal 1: Backend
python backend/main.py

# Terminal 2: Frontend
cd frontend && npm start

# 5. Open browser
# http://localhost:3000
```

---

## 📦 Installation

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt

# Verify installation
python -c "import ibm_watsonx_ai; print('✓ IBM Watsonx installed')"
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Verify React
npm list react
```

### Database Setup

```bash
# Create PostgreSQL database
createdb ai_code_intelligence

# Run migrations (if using Prisma)
npx prisma migrate dev
```

---

## ⚙️ Configuration

### Environment Variables

Create `.env` file in project root:

```env
# ========== IBM SERVICES ==========
# Watsonx (Granite LLM)
IBM_API_KEY=your_ibm_api_key_here
IBM_PROJECT_ID=your_project_id_here
WATSONX_URL=https://us-south.ml.cloud.ibm.com
GRANITE_MODEL_ID=ibm/granite-13b-chat-v2

# Watson NLU
WATSON_NLU_API_KEY=your_nlu_api_key_here
WATSON_NLU_URL=https://api.us-south.natural-language-understanding.watson.cloud.ibm.com/instances/your_instance_id
WATSON_NLU_VERSION=2021-08-01

# IBM Bob (Code Explanation)
BOB_API_KEY=your_bob_api_key_here
BOB_SERVICE_URL=https://code-explanation-service.ibm.com

# ========== DATABASE ==========
DATABASE_URL=postgresql://user:password@localhost:5432/ai_code_intelligence

# ========== SERVER ==========
BACKEND_PORT=8000
FRONTEND_PORT=3000
ENVIRONMENT=development
```

### Get IBM Credentials

1. **Sign up** on [IBM Cloud](https://cloud.ibm.com)
2. **Create Watsonx project** for IBM Granite
3. **Create Watson NLU service**
4. **Get API keys** from each service
5. **Copy to .env**

---

## 💻 Usage

### Via Web Interface

1. **Open** http://localhost:3000
2. **Select** programming language (Python, JavaScript, etc.)
3. **Paste or upload** your code
4. **Click** "Analyze Code"
5. **View** results:
   - 📝 Documentation
   - ♻️ Refactored code
   - 📊 Architecture diagram
   - 🔍 Analysis & keywords

### Example Use Cases

#### 1. Generate Documentation
```python
# Input: Your messy function
def calc(x, y):
    z = x + y
    return z

# Output: Professional docstring
def calc(x: int, y: int) -> int:
    """
    Calculate the sum of two numbers.
    
    Args:
        x (int): First number
        y (int): Second number
    
    Returns:
        int: Sum of x and y
    
    Example:
        >>> calc(5, 3)
        8
    """
    z = x + y
    return z
```

#### 2. Explain Complex Code
Input: Recursive algorithm → Output: Step-by-step breakdown

#### 3. Refactor for Performance
Input: N+1 query loop → Output: Optimized batch query with explanation

---

## 📡 API Documentation

### Base URL
```
http://localhost:8000
```

### Endpoints

#### 1. Generate Documentation
```bash
POST /api/granite/document
Content-Type: application/json

{
  "code": "def hello(name): return f'Hello {name}'",
  "language": "python",
  "file_name": "greeting.py"
}

Response:
{
  "status": "success",
  "documentation": "def hello(name: str) -> str:\n    \"\"\"Generate greeting message...\"\"\""
}
```

#### 2. Refactor Code
```bash
POST /api/granite/refactor
Content-Type: application/json

{
  "code": "your code here",
  "language": "javascript"
}

Response:
{
  "status": "success",
  "refactored_code": "optimized code..."
}
```

#### 3. Explain Code
```bash
POST /api/bob/explain
Content-Type: application/json

{
  "code": "your code here",
  "language": "python"
}

Response:
{
  "status": "success",
  "explanation": [
    "Step 1: Initialize variables",
    "Step 2: Loop through array",
    "Step 3: Return result"
  ]
}
```

#### 4. Generate Architecture
```bash
POST /api/bob/architecture
Content-Type: application/json

{
  "code": "your code here",
  "language": "java"
}

Response:
{
  "status": "success",
  "diagram": "graph LR\n  A[Input] --> B[Processing]\n  B --> C[Output]"
}
```

#### 5. Analyze with Watson
```bash
POST /api/watson/analyze
Content-Type: application/json

{
  "code": "your code comments here"
}

Response:
{
  "status": "success",
  "sentiment": {"score": 0.8, "label": "positive"},
  "keywords": ["function", "optimization", "efficient"]
}
```

#### 6. Full Analysis (All Services)
```bash
POST /api/analyze-full
Content-Type: application/json

{
  "code": "your code here",
  "language": "python"
}

Response:
{
  "status": "success",
  "documentation": "...",
  "refactored_code": "...",
  "explanation": [...],
  "architecture": "...",
  "analysis": {...}
}
```

#### 7. Health Check
```bash
GET /health

Response:
{
  "status": "ok",
  "services": ["granite", "bob", "watson"]
}
```

### Error Responses

```json
{
  "status": "error",
  "message": "Failed to connect to Granite service",
  "error_code": "SERVICE_UNAVAILABLE"
}
```

---

## 📁 Project Structure

```
ai-code-intelligence/
├── backend/
│   ├── services/
│   │   ├── granite_service.py      # IBM Granite LLM
│   │   ├── bob_service.py          # IBM Bob explanations
│   │   ├── watson_service.py       # Watson NLU
│   │   └── prompts.py              # Prompt templates
│   ├── routes/
│   │   ├── granite_routes.py
│   │   ├── bob_routes.py
│   │   └── watson_routes.py
│   ├── config.py                   # Configuration
│   ├── main.py                     # FastAPI app
│   ├── requirements.txt
│   └── test_services.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CodeUpload.tsx
│   │   │   ├── ResultsDisplay.tsx
│   │   │   └── DiagramViewer.tsx
│   │   ├── pages/
│   │   │   ├── Home.tsx
│   │   │   └── Analysis.tsx
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── package.json
│   └── tsconfig.json
├── .env.example                    # Environment template
├── .gitignore
├── README.md
└── docker-compose.yml              # Docker setup
```

---

## 🔨 Development

### Running Tests

```bash
# Backend tests
cd backend
pytest test_services.py -v

# Frontend tests
cd frontend
npm test
```

### Code Quality

```bash
# Linting (Backend)
pylint backend/

# Formatting (Backend)
black backend/

# Linting (Frontend)
cd frontend
npm run lint

# Format (Frontend)
npm run format
```

### Adding New Features

1. **Create service** (e.g., `new_service.py`)
2. **Add API route** (e.g., `/api/new-endpoint`)
3. **Create React component** for UI
4. **Test locally** before pushing
5. **Update documentation**

---

## 🌐 Deployment

### Deploy Backend to IBM Cloud

```bash
# Install IBM Cloud CLI
curl -fsSL https://clis.cloud.ibm.com/install/linux | bash

# Login
ibmcloud login -u your_email@example.com

# Deploy
ibmcloud cf push ai-code-intelligence-backend

# View logs
ibmcloud cf logs ai-code-intelligence-backend --recent
```

### Deploy Frontend to Vercel

```bash
# Install Vercel CLI
npm i -g vercel

# Deploy
vercel

# Set environment variables in Vercel dashboard
# REACT_APP_API_URL=https://backend-url.ibm.cloud
```

### Docker Deployment

```bash
# Build images
docker-compose build

# Run services
docker-compose up -d

# View logs
docker-compose logs -f
```

---

## 🐛 Troubleshooting

### Issue: 401 Unauthorized

**Solution:** Check `.env` file - IBM API keys may be expired or incorrect
```bash
# Regenerate keys from IBM Cloud Dashboard
# Update .env file
```

### Issue: Connection Refused

**Solution:** Ensure backend is running
```bash
# Terminal 1
python backend/main.py

# Should show: "Uvicorn running on http://0.0.0.0:8000"
```

### Issue: CORS Error in Frontend

**Solution:** Update CORS settings in `backend/main.py`
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Issue: Watson API Timeout

**Solution:** Increase timeout in `watson_service.py`
```python
response = requests.post(..., timeout=60)  # Increase from 30
```

### Issue: Module Not Found

**Solution:** Install dependencies
```bash
# Backend
pip install -r requirements.txt

# Frontend
cd frontend && npm install
```

### Issue: Database Connection Error

**Solution:** Verify DATABASE_URL in `.env`
```bash
# Test connection
psql $DATABASE_URL -c "SELECT 1"
```

---

## 🤝 Contributing

We welcome contributions! Follow these steps:

### 1. Fork Repository
```bash
git clone https://github.com/yourusername/ai-code-intelligence.git
cd ai-code-intelligence
```

### 2. Create Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 3. Make Changes
- Follow code style (PEP 8 for Python, Prettier for JavaScript)
- Add tests for new features
- Update documentation

### 4. Commit & Push
```bash
git add .
git commit -m "feat: add support for Rust code analysis"
git push origin feature/your-feature-name
```

### 5. Create Pull Request
- Describe changes clearly
- Link related issues
- Request review

---

## 📝 Commit Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add Rust language support
fix: resolve Watson timeout issue
docs: update API documentation
style: format code
test: add unit tests for refactor
chore: update dependencies
```

---

## 🚦 Roadmap

- [ ] GitHub integration (auto-analyze repos)
- [ ] PostgreSQL integration for history
- [ ] User authentication & teams
- [ ] IDE plugins (VS Code, JetBrains)
- [ ] Mobile app (React Native)
- [ ] Real-time collaboration
- [ ] Advanced caching strategy
- [ ] Custom LLM fine-tuning
- [ ] Multi-language support expansion
- [ ] Performance benchmarking

---

## 📧 Contact & Support

- **Issues:** [GitHub Issues](https://github.com/yourusername/ai-code-intelligence/issues)
- **Discussions:** [GitHub Discussions](https://github.com/yourusername/ai-code-intelligence/discussions)
- **Email:** 
- **Discord:** [Join our community](https://discord.gg/yourserver)

---

## 🙏 Acknowledgments

- IBM Watsonx team for Granite LLM
- IBM Bob for code explanation service
- IBM Watson for NLP capabilities
- FastAPI & React communities
- Our amazing contributors ✨

---

## ⭐ Show Your Support

If this project helps you, please consider:
- ⭐ Star the repository
- 🐛 Report bugs
- 💡 Suggest features
- 🤝 Contribute code

---

**Made with ❤️ by the AI Code Intelligence Team**

[⬆ Back to Top](#-ai-code-intelligence-platform)
