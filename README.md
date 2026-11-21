# StyleAI — Face Shape Based Hairstyle Recommendation System

AI-powered face shape analysis and personalized hairstyle recommendations using deep learning, computer vision, and generative AI.

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, JavaScript (ES6+) |
| Backend | Python 3.11+, Flask 3.x |
| Computer Vision | OpenCV 4.x, MediaPipe 0.10+ |
| Machine Learning | TensorFlow 2.x / Keras |
| Generative AI | Google Gemini API |
| Database | MongoDB 7.x (PyMongo) |
| Deployment | Docker, Nginx, Gunicorn |

## Quick Start

For detailed step-by-step instructions, see:
- 📖 **[SETUP.md](SETUP.md)** — Complete environment setup and database seeding
- 🚀 **[RUN.md](RUN.md)** — Running locally, switching Virtual Try-On providers (Replicate / ComfyUI), and testing

### Prerequisites
- Python 3.11+
- MongoDB 7.x (running locally or via Docker)
- Google Gemini API key (optional, for AI advice)

### Setup

```bash
# Clone and enter the project
cd "Face Shape Based Hairstyle Recommendation System"

# Create virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Copy environment config
cp .env.example .env
# Edit .env with your MongoDB URI and API keys

# Seed the hairstyle database and initial test user (user@example.com / user1234)
python database/seed_hairstyles.py --force --with-user

# Run the development server
python wsgi.py
```


Open **http://localhost:5000** in your browser.

### Docker (Full Stack)

```bash
cd docker
docker-compose up --build
```

Open **http://localhost** (port 80 via Nginx).

## Project Structure

```
├── client/              # Frontend (HTML/CSS/JS)
│   ├── css/             # Design system + components
│   ├── js/              # API client, modules
│   └── pages/           # HTML pages
├── server/              # Flask backend
│   ├── routes/          # API endpoints
│   ├── services/        # Business logic
│   ├── models/          # Data schemas
│   ├── middleware/       # JWT auth
│   └── utils/           # Helpers
├── ml/                  # ML training pipeline
│   └── train/           # Preprocessing, training, evaluation
├── database/            # Seed scripts
├── docker/              # Docker + Nginx config
└── tests/               # Test suite
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Login |
| GET | `/api/auth/profile` | Get profile |
| POST | `/api/analyze` | Upload & analyze face |
| GET | `/api/recommend` | Get recommendations |
| GET | `/api/hairstyles` | Browse catalog |
| POST | `/api/tryon` | Virtual try-on |
| GET | `/api/history` | Analysis history |

## License

MIT
