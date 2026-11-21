# Setup Guide — StyleAI

This guide details the complete, step-by-step process to set up the **Face Shape Based Hairstyle Recommendation System (StyleAI)** development environment from scratch.

---

## 1. System Requirements & Prerequisites

Ensure the following tools are installed on your machine:

| Requirement | Minimum Version | Recommended | Notes |
|---|---|---|---|
| **Python** | 3.11+ | 3.12 | Python 3.12 is recommended for OpenCV & MediaPipe compatibility |
| **MongoDB** | 7.0+ | 8.x | Community Server running locally or via Docker |
| **Git** | 2.x | Latest | For repository version control |
| **Replicate API Token** | N/A | Optional / Recommended | Required for cloud virtual try-on with `openai/gpt-image-2.5-flare` |
| **Gemini API Key** | N/A | Optional | For AI styling advice and face-shape rationale |

---

## 2. Step-by-Step Setup

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd "Face Shape Based Hairstyle Recommendation System"
```

---

### Step 2: Create a Python Virtual Environment

Create a dedicated virtual environment using Python 3.12:

**On Windows (PowerShell / Command Prompt):**
```powershell
python -m venv venv
```

**On macOS / Linux:**
```bash
python3 -m venv venv
```

---

### Step 3: Activate the Virtual Environment

**On Windows (PowerShell):**
```powershell
.\venv\Scripts\Activate.ps1
```
*(If PowerShell blocks script execution, run: `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`)*

**On Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

**On macOS / Linux:**
```bash
source venv/bin/activate
```

Verify your active Python version:
```bash
python --version
```

---

### Step 4: Install Dependencies

Upgrade `pip` and install all required packages from `requirements.txt`:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 5: Configure Environment Variables (`.env`)

Copy the template configuration file:

**On Windows (PowerShell):**
```powershell
Copy-Item .env.example .env
```

**On macOS / Linux:**
```bash
cp .env.example .env
```

Open `.env` in your code editor and configure your environment:

```ini
# Flask Core
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=generate-a-strong-random-secret-key-here
PORT=5000

# MongoDB Database Connection
MONGO_URI=mongodb://localhost:27017/faceshape

# JWT Authentication
JWT_SECRET=generate-a-strong-jwt-secret-key-here
JWT_EXPIRY_HOURS=24

# Virtual Try-On Provider (Replicate OpenAI GPT-Image-2.5-Flare)
TRYON_PROVIDER=replicate
REPLICATE_API_TOKEN=r8_your_replicate_api_token_here
REPLICATE_MODEL=openai/gpt-image-2.5-flare
REPLICATE_QUALITY=low

# Alternative Virtual Try-On Provider (ComfyUI)
COMFYUI_API_URL=http://127.0.0.1:8188
COMFYUI_API_KEY=
COMFYUI_WORKFLOW_PATH=workflow/sd1.5.json
COMFYUI_TIMEOUT=180
COMFYUI_POLL_INTERVAL=1.0

# Generative AI (Google Gemini Advice)
GEMINI_API_KEY=your_google_gemini_api_key_here

# File Storage Limits
UPLOAD_FOLDER=server/uploads
MAX_CONTENT_LENGTH=10485760
RATELIMIT_DEFAULT=200/hour
```

---

### Step 6: Start MongoDB

Make sure MongoDB is running on port `27017`:

**Local Service (Windows):**
```powershell
# Check MongoDB service status
Get-Service MongoDB
# Start service if stopped
Start-Service MongoDB
```

**Local Service (macOS via Homebrew):**
```bash
brew services start mongodb-community
```

**Local Service (Linux systemd):**
```bash
sudo systemctl start mongod
```

**Via Docker (Alternative):**
```bash
docker run -d --name mongodb -p 27017:27017 -v mongo_data:/data/db mongo:7
```

---

### Step 7: Seed the Database (Hairstyles & Initial User)

Populate the MongoDB database with hairstyles across all 6 face shapes and create an initial test user account:

**Option A: Seed both hairstyles and initial user together:**
```bash
python database/seed_hairstyles.py --force --with-user
```

**Option B: Seed initial user separately:**
```bash
python database/seed_user.py --force
```

Default credentials created:
- **Email**: `user@example.com`
- **Password**: `user1234`

Expected output:
```
[SUCCESS] Seeded 18 metadata-rich hairstyles into MongoDB
[SUCCESS] Indexes created for MongoDB hairstyle catalog
[SUCCESS] Initial user created successfully!
          Email:    user@example.com
          Password: user1234
```

---

### Step 8: Verify Setup with Automated Tests

Run the test suite to verify all modules and providers are operational:

```bash
pytest tests/test_replicate_provider.py tests/test_comfyui.py -v
```

All tests should pass.

---

## Next Step

Your environment is fully set up! Refer to **[RUN.md](RUN.md)** for instructions on starting the development server, background tasks, and accessing the web portal.
