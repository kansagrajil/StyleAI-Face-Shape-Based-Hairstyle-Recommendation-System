# Run Guide — StyleAI

This guide details how to run the **StyleAI Face Shape Based Hairstyle Recommendation System** locally, manage background services, switch between Virtual Try-On providers, and run the test suite.

---

## 1. Quick Start

Ensure your virtual environment is activated and MongoDB is running:

```powershell
# 1. Activate virtual environment (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# 2. Run the application
python wsgi.py
```

Open your browser and navigate to:
👉 **[http://localhost:5000](http://localhost:5000)**

### Default Login Credentials
If you seeded the initial user:
- **Email**: `user@example.com`
- **Password**: `user1234`

To seed or reset this user at any time:
```bash
python database/seed_user.py --force
```

---


## 2. Running the Server

### Development Server (Hot Reloading)

To run the server with debug mode and live code reloading enabled:

```bash
python wsgi.py
```

*Default address:* `http://localhost:5000` (or `http://127.0.0.1:5000`)

To specify a custom port:
```powershell
$env:PORT="8080"; python wsgi.py
```

### Production WSGI Server

#### On Windows (using Waitress):
```powershell
pip install waitress
waitress-serve --listen=0.0.0.0:5000 wsgi:app
```

#### On Linux / macOS (using Gunicorn):
```bash
gunicorn --bind 0.0.0.0:5000 wsgi:app --workers 4 --timeout 120
```

---

## 3. Configuring Virtual Try-On Providers

StyleAI supports two state-of-the-art Generative AI engines for hairstyle try-on. You can switch between them at any time in your [`.env`](.env) file without changing code:

### Option A: Replicate (`openai/gpt-image-2.5-flare`) [Default]

Image-to-Image hairstyle modification with high identity preservation:

1. In `.env`:
   ```ini
   TRYON_PROVIDER=replicate
   REPLICATE_API_TOKEN=r8_your_api_token_here
   REPLICATE_MODEL=openai/gpt-image-2.5-flare
   REPLICATE_QUALITY=low
   ```
2. The server will automatically use Replicate for all try-on requests.

---

### Option B: ComfyUI (Local SD1.5 Workflow)

Runs completely locally using the workflow located at `workflow/sd1.5.json`:

1. Launch your local ComfyUI server:
   ```bash
   python main.py --port 8188 --listen 127.0.0.1
   ```
2. In `.env`:
   ```ini
   TRYON_PROVIDER=comfyui
   COMFYUI_API_URL=http://127.0.0.1:8188
   COMFYUI_WORKFLOW_PATH=workflow/sd1.5.json
   COMFYUI_TIMEOUT=180
   ```
3. Restart the StyleAI server.

---

## 4. Running the Test Suite

Execute automated unit and integration tests with `pytest`:

```bash
# Run all provider tests (ComfyUI & Replicate)
pytest tests/test_replicate_provider.py tests/test_comfyui.py -v

# Run complete test suite
pytest
```

---

## 5. Docker (Full Stack Alternative)

To run the complete stack (Flask Backend, Nginx, MongoDB) inside Docker containers:

```bash
docker-compose up --build
```

Access the application at:
👉 **`http://localhost`** (Port 80 via Nginx reverse proxy)

To stop the containers:
```bash
docker-compose down
```

---

## 6. Troubleshooting

| Issue | Cause | Solution |
|---|---|---|
| `ServerSelectionTimeoutError` | MongoDB is not running | Run `Start-Service MongoDB` (Windows) or `docker run -d -p 27017:27017 mongo:7` |
| `Address already in use` (Port 5000) | Another process is using port 5000 | Set `$env:PORT="5050"` or kill existing process: `Stop-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess -Force` |
| `ReplicateConfigError` | Missing Replicate API Token | Add `REPLICATE_API_TOKEN=...` in your `.env` file |
| `ExecutionPolicy` error on Windows | PowerShell execution restricted | Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` |
| `DLL load failed` on Windows | AppLocker policy blocking TF/native DLLs | StyleAI has automatic OpenCV & rule-based fallbacks built-in |
