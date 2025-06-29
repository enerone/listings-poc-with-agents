# Amazon Listings Generator with AI Agents

🚀 **Advanced Amazon listings generator powered by AI agents with SEO analysis and market intelligence**

## Features

### 🤖 AI-Powered Analysis
- **Multi-agent system** with specialized AI agents
- **qwen2.5-coder:32b** model for high-quality Spanish content generation
- **Intelligent language detection** and automatic translation
- **Context-aware optimization** for Amazon marketplace

### 📊 SEO & Market Intelligence
- **Advanced SEO analysis** with keyword optimization
- **Competitive market intelligence** with pricing analysis
- **Search intent analysis** and content gap identification
- **Market positioning** and brand landscape analysis
- **Real-time competitor research** with strategic insights

### 🎯 Specialized Agents
1. **Analyzer Agent** - Main orchestration and content generation
2. **Competitor Researcher** - Market research and competitive analysis
3. **Image Finder** - Smart image discovery from multiple sources
4. **Optimizer** - Amazon compliance and performance optimization
5. **SEO Analyzer** - Advanced keyword and search optimization
6. **Market Intelligence** - Competitive analysis and pricing strategy

### 🖼️ Smart Image Search
- **Real stock photos** from Unsplash and curated collections
- **Automatic categorization** by product type
- **URL validation** to ensure working image links
- **Multiple image sources** with intelligent fallbacks

## Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLite with SQLAlchemy ORM
- **AI Engine**: Ollama (local LLM)
- **Frontend**: HTML/CSS/JavaScript with Jinja2 templates
- **Caching**: Redis (optional)
- **Images**: Unsplash API integration

## Quick Start

### Prerequisites
- Python 3.8+
- [Ollama](https://ollama.ai/) installed and running
- qwen2.5-coder:32b model downloaded

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/enerone/listings-poc-with-agents.git
cd listings-poc-with-agents
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Download and run the AI model**
```bash
ollama serve
ollama pull qwen2.5-coder:32b
```

4. **Configure environment** (optional)
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. **Start the application**
```bash
python run.py
```

6. **Open in browser**
```
http://localhost:8000
```

## Configuration

### Environment Variables (.env)
```env
# Database
DATABASE_URL=sqlite:///./listings.db

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5-coder:32b

# Redis Configuration (optional)
REDIS_URL=redis://localhost:6379

# API Keys (optional)
UNSPLASH_ACCESS_KEY=your_unsplash_key
PEXELS_API_KEY=your_pexels_key

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=False
```

## API Endpoints

### Core Endpoints
- `POST /api/listings/` - Create new listing
- `GET /api/listings/{id}` - Get listing details
- `POST /api/listings/{id}/analyze` - AI analysis with SEO & market intelligence
- `POST /api/listings/{id}/find-images` - Smart image discovery
- `POST /api/listings/{id}/optimize` - Amazon optimization

### Web Interface
- `/` - Home page
- `/create` - Create new listing
- `/listings` - View all listings
- `/listings/{id}` - View specific listing

## Workflow

1. **Create Listing** - Input product title and description
2. **AI Analysis** - Multi-agent analysis with:
   - Language detection and translation
   - SEO keyword optimization
   - Competitor research and market intelligence
   - Content generation in professional Spanish
3. **Image Discovery** - Automatic relevant image search
4. **Amazon Optimization** - Compliance check and performance optimization
5. **Export** - Ready-to-use Amazon listing

## Sample Output

```json
{
  "generated_title": "Auriculares Bluetooth Premium con Cancelación de Ruido - Batería 30h - Resistentes al Agua IPX7",
  "generated_description": "Experimenta audio de calidad superior con estos auriculares...",
  "generated_bullets": [
    "🎵 SONIDO SUPERIOR: Drivers de 40mm con tecnología avanzada",
    "🔋 BATERÍA EXTENDIDA: Hasta 30 horas de reproducción continua",
    "💧 RESISTENTE AL AGUA: Certificación IPX7 para uso deportivo",
    "🎧 CANCELACIÓN DE RUIDO: Tecnología ANC para máxima inmersión",
    "📱 CONECTIVIDAD UNIVERSAL: Bluetooth 5.0 compatible con todos los dispositivos"
  ],
  "keywords": ["auriculares bluetooth", "cancelación ruido", "resistente agua"],
  "seo_analysis": {
    "seo_score": 85,
    "enhanced_keywords": {...},
    "search_intent": "transactional",
    "recommendations": [...]
  },
  "market_intelligence": {
    "competitors_analyzed": 8,
    "pricing_analysis": {...},
    "competitive_insights": [...],
    "market_gaps": {...}
  }
}
```

## Project Structure

```
listings-amazon/
├── app/
│   ├── agents/          # AI agent implementations
│   │   ├── analyzer.py      # Main orchestration agent
│   │   ├── competitor_researcher.py
│   │   ├── image_finder.py
│   │   └── optimizer.py
│   ├── services/        # Core services
│   │   ├── seo_analyzer.py      # Advanced SEO analysis
│   │   ├── market_intelligence.py # Market research
│   │   ├── real_image_service.py # Image management
│   │   ├── ollama_client.py
│   │   └── web_search.py
│   ├── api/            # FastAPI endpoints
│   ├── models/         # Database models
│   ├── schemas/        # Pydantic schemas
│   └── core/           # Configuration and utilities
├── static/             # Frontend assets
├── templates/          # HTML templates
├── requirements.txt
├── run.py             # Application entry point
└── README.md
```

## Features Deep Dive

### 🎯 SEO Analysis
- **Keyword Research**: Automatic extraction and enhancement of relevant keywords
- **Search Intent**: Analysis of user search patterns (informational, commercial, transactional)
- **Content Optimization**: Gap analysis and improvement recommendations
- **Competitive Keywords**: Integration with competitor research for strategic advantage

### 📊 Market Intelligence
- **Pricing Strategy**: Competitive pricing analysis and recommendations
- **Market Positioning**: Brand landscape and positioning opportunities
- **Gap Analysis**: Identification of market opportunities
- **Competitive Insights**: AI-generated strategic recommendations

### 🖼️ Image Intelligence
- **Smart Categorization**: Automatic product type detection
- **Multiple Sources**: Unsplash, Pexels, and curated collections
- **Quality Validation**: URL verification and fallback mechanisms
- **Relevance Scoring**: AI-powered image relevance assessment

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Ollama](https://ollama.ai/) for local LLM infrastructure
- [Qwen2.5-Coder](https://huggingface.co/Qwen/Qwen2.5-Coder-32B) for the AI model
- [Unsplash](https://unsplash.com/) for stock photography
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework

---

**Made with ❤️ for Amazon sellers who want to optimize their listings with AI**