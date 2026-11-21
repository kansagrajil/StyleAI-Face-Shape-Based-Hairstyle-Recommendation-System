# Production Deployment Guide & Operations Manual

**System Name**: StyleAI — Face Shape Based Hairstyle Recommendation System  
**Version**: `v1.0`  
**Architecture**: Python Flask WSGI + TensorFlow + MediaPipe + MongoDB 7.0 + Nginx Reverse Proxy  

---

## 1. Environment Configuration & Prerequisites

### Server Requirements
- **OS**: Ubuntu 22.04 LTS / Debian 12 / RHEL 9 (or Docker Engine 24+)
- **CPU**: 2+ vCPUs recommended
- **RAM**: 4GB+ RAM (8GB recommended for TensorFlow inference)
- **Disk**: 20GB+ SSD storage

### Environment File Setup
Copy `.env.example` to `.env` and configure production secrets:

```bash
cp .env.example .env
```

Edit `.env`:
```ini
FLASK_ENV=production
SECRET_KEY=e8a9f4c3b2a1... # Generate with: python -c "import secrets; print(secrets.token_hex(32))"
JWT_SECRET=f7e6d5c4b3a2... # Generate with: python -c "import secrets; print(secrets.token_hex(32))"
MONGO_URI=mongodb://db:27017/faceshape
GEMINI_API_KEY=AIzaSy...
```

---

## 2. Docker Compose Multi-Container Deployment (Recommended)

### Step 1: Clone Repository & Build Containers
```bash
docker-compose build
```

### Step 2: Launch Stack Background Service
```bash
docker-compose up -d
```

### Step 3: Verify Container Health
```bash
docker-compose ps
```

Verify application logs:
```bash
docker-compose logs -f web
```

---

## 3. HTTPS / SSL Certificate Setup (Let's Encrypt / Certbot)

To enable secure HTTPS traffic:

```bash
sudo apt-get update
sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d styleai.yourdomain.com
```

Certbot automatically configures SSL certificates and sets up automatic 90-day renewal.

---

## 4. Manual Deployment on Linux VPS (Gunicorn + Systemd)

If deploying directly on Linux without Docker:

### Step 1: Install System Dependencies
```bash
sudo apt-get update && sudo apt-get install -y python3-pip python3-venv mongodb nginx
```

### Step 2: Setup Python Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt gunicorn
```

### Step 3: Configure Systemd Service (`/etc/systemd/system/styleai.service`)
```ini
[Unit]
Description=StyleAI Flask Application
After=network.target mongodb.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/styleai
Environment="PATH=/var/www/styleai/venv/bin"
EnvironmentFile=/var/www/styleai/.env
ExecStart=/var/www/styleai/venv/bin/gunicorn --workers 4 --threads 2 --bind 127.0.0.1:5000 wsgi:app

[Install]
WantedBy=multi-user.target
```

Enable & start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable styleai
sudo systemctl start styleai
```

---

## 5. Automated MongoDB Backup Strategy

Automated backup is configured via cron using `scripts/backup_mongodb.py`:

Add a daily cron job at 2:00 AM:
```bash
crontab -e
```

Add line:
```cron
0 2 * * * /var/www/styleai/venv/bin/python /var/www/styleai/scripts/backup_mongodb.py >> /var/www/styleai/logs/backup.log 2>&1
```

### Manual Database Restoration
To restore a MongoDB backup archive:
```bash
mongorestore --uri="mongodb://localhost:27017/faceshape" --archive=/path/to/backup.gz --gzip --drop
```

---

## 6. Horizontal Scaling & Monitoring

- **Gunicorn Workers**: Scale worker threads based on available CPU cores:
  $$\text{Workers} = (2 \times \text{CPU Cores}) + 1$$
- **Log Inspection**: Production logs write to `logs/app.log` with automatic 10MB file rotation and 5 backups.
- **Monitoring Health**: `GET /api/admin/analytics` returns live system health and MongoDB connection metrics.
