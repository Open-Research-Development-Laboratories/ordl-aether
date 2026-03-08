# AETHER Setup Guide

Complete guide to setting up and running your NASA-inspired AI system.

## 🚀 Quick Start (Docker - Recommended)

### Prerequisites
- Docker & Docker Compose installed
- 4GB+ RAM available
- 10GB free disk space

### 1. Clone and Configure

```bash
# Clone the repository
git clone https://github.com/yourusername/aether-system.git
cd aether-system

# Copy environment file
cp .env.example .env

# Edit .env and add your NASA API key (optional but recommended)
# Get free key at: https://api.nasa.gov
nano .env
```

### 2. Start the System

```bash
# Build and start
docker-compose up -d

# Wait for initialization (first run takes ~5 minutes to download models)
docker logs -f aether-system

# When you see "✅ AETHER System is running!", you're ready!
```

### 3. Access the Dashboard

- **Dashboard**: http://localhost
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🛠️ Manual Setup (Development)

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py
```

Backend will start at http://localhost:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will start at http://localhost:3000

## 📁 Project Structure

```
aether-system/
├── backend/                 # Python FastAPI backend
│   ├── core/               # Core system components
│   ├── modules/            # AI processing modules
│   ├── knowledge/          # Database and storage
│   ├── api/                # REST API routes
│   └── main.py             # Application entry point
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # Reusable components
│   │   ├── pages/          # Page components
│   │   └── App.jsx         # Main app
│   └── package.json
├── docker/                 # Docker configuration
├── data/                   # Data storage (created on run)
├── ai_models/              # AI model cache (created on run)
├── docker-compose.yml      # Docker orchestration
├── Dockerfile              # Container definition
└── README.md
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DEBUG` | Enable debug mode | `false` |
| `PORT` | Backend port | `8000` |
| `NASA_API_KEY` | NASA API access | `DEMO_KEY` |
| `DATABASE_URL` | SQLite database path | `sqlite:///./data/aether.db` |

### Module Configuration

Each AI module can be configured via the API. See `/api/v1/status` for current configuration.

## 📊 Usage Guide

### 1. Image Analysis

1. Go to **Image Analysis** page
2. Drag & drop an image or click to select
3. Click "Analyze Image"
4. View classifications, object detections, and embeddings

**Supported formats**: PNG, JPG, GIF (max 50MB)

### 2. Text Intelligence

1. Go to **Text Intelligence** page
2. Paste text (article, report, etc.)
3. Click "Analyze Text"
4. View summary, entities, sentiment, and keywords

**Best for**: Articles, reports, documents up to 1000 words

### 3. Anomaly Detection

1. Go to **Anomaly Detection** page
2. Enter comma-separated numbers
3. Click "Detect Anomalies"
4. View chart and anomaly details

**Example**: `10, 12, 11, 45, 12, 100, 11, 12`

### 4. Knowledge Base

1. Go to **Knowledge Base** page
2. Search previous analyses
3. View stored insights

## 🔌 API Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System health check |
| `/status` | GET | Full system status |
| `/analyze/image` | POST | Analyze image |
| `/analyze/text` | POST | Analyze text |
| `/analyze/anomalies` | POST | Detect anomalies |
| `/knowledge/search` | POST | Search knowledge base |

### Example API Call

```bash
# Analyze text
curl -X POST http://localhost:8000/api/v1/analyze/text \
  -H "Content-Type: application/json" \
  -d '{
    "data_type": "text",
    "content": "Your text here...",
    "context": {"tasks": ["summarize", "sentiment"]}
  }'
```

## 🚀 Deployment

### Deploy to Render (Free)

1. Push code to GitHub
2. Create new Web Service on Render
3. Connect GitHub repo
4. Use Docker configuration
5. Deploy!

### Deploy to Railway (Free)

1. Push code to GitHub
2. Create new project on Railway
3. Deploy from GitHub
4. Add environment variables
5. Deploy!

## 🔄 Updating

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

## 🐛 Troubleshooting

### Issue: Models not loading
**Solution**: First run downloads ~2GB of AI models. Wait for completion.

### Issue: Out of memory
**Solution**: Reduce `MAX_WORKERS` in config or use smaller models.

### Issue: Port conflicts
**Solution**: Change ports in `docker-compose.yml` or `.env`

## 📈 Performance Tips

1. **Use GPU**: Install CUDA for 10x faster AI processing
2. **Enable Redis**: Uncomment in `docker-compose.yml` for caching
3. **Pre-load models**: Keep system running to avoid reload delays

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Make changes
4. Submit pull request

## 📜 License

MIT License - See LICENSE file

---

**Need help?** Open an issue on GitHub or contact [your-email]