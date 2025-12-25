# Production Deployment Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Deploy testhome-visualizer to production with security hardening and Cloudflare Tunnel.

**Architecture:** Cloudflare Tunnel → Gunicorn → Django + WhiteNoise static serving. All traffic proxied through Cloudflare for SSL/CDN.

**Tech Stack:** Django 5.2, Gunicorn, WhiteNoise, cloudflared, systemd

**Domain:** trustedhearthandhome.com

---

## Task 1: Environment-Based Configuration

**Files:**
- Modify: `pools_project/settings.py`
- Modify: `.env`
- Create: `.env.example`

**Step 1: Generate new SECRET_KEY**

Run:
```bash
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output for Step 2.

**Step 2: Update .env with production values**

Edit `.env`:
```bash
# Production Configuration
DEBUG=False
SECRET_KEY=<paste-generated-key-here>
DJANGO_PORT=8000

# Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=contractors_dev
DB_USER=contractors_user
DB_PASSWORD=<your-db-password>
DB_HOST=localhost
DB_PORT=5432

# Domain Configuration
ALLOWED_HOSTS=trustedhearthandhome.com,www.trustedhearthandhome.com,localhost,127.0.0.1
CORS_ORIGINS=https://trustedhearthandhome.com,https://www.trustedhearthandhome.com
CSRF_TRUSTED=https://trustedhearthandhome.com,https://www.trustedhearthandhome.com
```

**Step 3: Update settings.py for environment-based config**

Replace hardcoded values in `pools_project/settings.py`:

```python
# Line 31 - Replace hardcoded SECRET_KEY
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-CHANGE-ME-IN-PRODUCTION')

# Line 34 - Replace hardcoded DEBUG
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Line 36 - Replace hardcoded ALLOWED_HOSTS
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')
```

**Step 4: Create .env.example template**

Create `.env.example`:
```bash
# Copy this to .env and fill in values

# Security (REQUIRED - generate with: python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
SECRET_KEY=

# Debug mode (set to False in production)
DEBUG=False

# Database
DB_ENGINE=django.db.backends.postgresql
DB_NAME=contractors_dev
DB_USER=contractors_user
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=5432

# Domain (comma-separated)
ALLOWED_HOSTS=trustedhearthandhome.com,www.trustedhearthandhome.com,localhost
CORS_ORIGINS=https://trustedhearthandhome.com,https://www.trustedhearthandhome.com
CSRF_TRUSTED=https://trustedhearthandhome.com,https://www.trustedhearthandhome.com
```

**Step 5: Verify configuration loads correctly**

Run:
```bash
source venv/bin/activate
python3 manage.py check
```

Expected: `System check identified no issues`

**Step 6: Commit**

```bash
git add pools_project/settings.py .env.example
git commit -m "feat: add environment-based configuration for production"
```

---

## Task 2: Security Headers and HTTPS Settings

**Files:**
- Modify: `pools_project/settings.py`

**Step 1: Add security middleware and settings**

Add after line 70 (after XFrameOptionsMiddleware) in `pools_project/settings.py`:

```python
# Security settings for production
if not DEBUG:
    # HTTPS enforcement
    SECURE_SSL_REDIRECT = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

    # HSTS (tell browsers to always use HTTPS)
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

    # Cookie security
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True

    # Additional security headers
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'DENY'
```

**Step 2: Update CORS settings for production**

Replace CORS_ALLOWED_ORIGINS (lines 181-188):

```python
# CORS settings
CORS_ALLOWED_ORIGINS = [origin.strip() for origin in os.environ.get(
    'CORS_ORIGINS',
    'http://localhost:3000,http://127.0.0.1:3000'
).split(',')]

# In production, also add the main domain
if not DEBUG:
    CORS_ALLOWED_ORIGINS.extend([
        'https://trustedhearthandhome.com',
        'https://www.trustedhearthandhome.com',
    ])

CORS_ALLOW_CREDENTIALS = True
```

**Step 3: Add CSRF trusted origins**

Add after CORS settings:

```python
# CSRF trusted origins for production
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.environ.get(
    'CSRF_TRUSTED',
    'http://localhost:3000'
).split(',')]
```

**Step 4: Verify settings**

Run:
```bash
DEBUG=False python3 manage.py check --deploy
```

Expected: May show some warnings, but no errors. Common warnings about CONN_MAX_AGE are OK.

**Step 5: Commit**

```bash
git add pools_project/settings.py
git commit -m "feat: add production security headers and HTTPS enforcement"
```

---

## Task 3: Static Files with WhiteNoise

**Files:**
- Modify: `requirements.txt`
- Modify: `pools_project/settings.py`

**Step 1: Add WhiteNoise to requirements**

Add to `requirements.txt`:
```
whitenoise==6.6.0
```

**Step 2: Install WhiteNoise**

Run:
```bash
source venv/bin/activate
pip install whitenoise==6.6.0
```

**Step 3: Add WhiteNoise middleware**

In `pools_project/settings.py`, add after SecurityMiddleware (line 63):

```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this line
    'django.contrib.sessions.middleware.SessionMiddleware',
    # ... rest of middleware
]
```

**Step 4: Configure WhiteNoise settings**

Add after STATICFILES_DIRS:

```python
# WhiteNoise configuration for production static files
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

**Step 5: Build React frontend and collect static**

Run:
```bash
cd frontend && npm run build && cd ..
python3 manage.py collectstatic --noinput
```

Expected: Static files collected to `staticfiles/`

**Step 6: Verify static files work**

Run:
```bash
DEBUG=False python3 manage.py runserver 8000
# In another terminal:
curl -I http://localhost:8000/static/js/main.*.js
```

Expected: HTTP 200 response

**Step 7: Commit**

```bash
git add requirements.txt pools_project/settings.py
git commit -m "feat: add WhiteNoise for production static file serving"
```

---

## Task 4: Gunicorn Production Server

**Files:**
- Modify: `requirements.txt`
- Create: `gunicorn.conf.py`

**Step 1: Add Gunicorn to requirements**

Add to `requirements.txt`:
```
gunicorn==21.2.0
```

**Step 2: Install Gunicorn**

Run:
```bash
source venv/bin/activate
pip install gunicorn==21.2.0
```

**Step 3: Create Gunicorn configuration**

Create `gunicorn.conf.py`:

```python
"""Gunicorn configuration for production."""
import multiprocessing

# Bind to localhost (Cloudflare Tunnel will connect here)
bind = "127.0.0.1:8000"

# Workers: 2 * CPU cores + 1
workers = multiprocessing.cpu_count() * 2 + 1

# Worker class
worker_class = "sync"

# Timeout (increase for AI processing)
timeout = 180

# Logging
accesslog = "/home/astre/command-center/testhome/testhome-visualizer/logs/gunicorn-access.log"
errorlog = "/home/astre/command-center/testhome/testhome-visualizer/logs/gunicorn-error.log"
loglevel = "info"

# Process naming
proc_name = "visualizer"

# Reload on code changes (disable in production)
reload = False

# Preload app for faster worker spawning
preload_app = True
```

**Step 4: Test Gunicorn**

Run:
```bash
source venv/bin/activate
gunicorn pools_project.wsgi:application -c gunicorn.conf.py
```

Expected: Gunicorn starts with multiple workers, no errors

Test in another terminal:
```bash
curl http://localhost:8000/api/health/ 2>/dev/null || curl http://localhost:8000/api/
```

Expected: API responds

**Step 5: Stop Gunicorn (Ctrl+C) and commit**

```bash
git add requirements.txt gunicorn.conf.py
git commit -m "feat: add Gunicorn production server configuration"
```

---

## Task 5: Systemd Service

**Files:**
- Create: `systemd/visualizer.service`
- Create: `scripts/start-production.sh`

**Step 1: Create systemd service file**

Create directory and file:
```bash
mkdir -p systemd
```

Create `systemd/visualizer.service`:

```ini
[Unit]
Description=TrustHome Visualizer (Django + Gunicorn)
After=network.target postgresql.service
Requires=postgresql.service

[Service]
Type=notify
User=astre
Group=astre
WorkingDirectory=/home/astre/command-center/testhome/testhome-visualizer
Environment="PATH=/home/astre/command-center/testhome/testhome-visualizer/venv/bin"
EnvironmentFile=/home/astre/command-center/testhome/testhome-visualizer/.env
ExecStart=/home/astre/command-center/testhome/testhome-visualizer/venv/bin/gunicorn \
    --config gunicorn.conf.py \
    pools_project.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=always
RestartSec=5
KillMode=mixed
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
```

**Step 2: Create start script for manual testing**

Create `scripts/start-production.sh`:

```bash
#!/bin/bash
# Start production server manually (for testing)

set -e
cd /home/astre/command-center/testhome/testhome-visualizer
source venv/bin/activate
source .env

echo "Building frontend..."
cd frontend && npm run build && cd ..

echo "Collecting static files..."
python3 manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn --config gunicorn.conf.py pools_project.wsgi:application
```

Make executable:
```bash
chmod +x scripts/start-production.sh
```

**Step 3: Install systemd service (requires sudo)**

Run:
```bash
sudo cp systemd/visualizer.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable visualizer
```

**Step 4: Start and verify service**

Run:
```bash
sudo systemctl start visualizer
sudo systemctl status visualizer
```

Expected: Active (running), green status

**Step 5: Commit**

```bash
git add systemd/ scripts/start-production.sh
git commit -m "feat: add systemd service for production deployment"
```

---

## Task 6: Cloudflare Tunnel Setup

**Files:**
- Create: `cloudflared/config.yml`
- Create: `systemd/cloudflared.service`

**Step 1: Install cloudflared**

Run:
```bash
# Download and install cloudflared
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb
rm cloudflared.deb
```

Verify:
```bash
cloudflared --version
```

Expected: `cloudflared version 2024.x.x`

**Step 2: Authenticate with Cloudflare**

Run:
```bash
cloudflared tunnel login
```

This opens a browser. Log in to Cloudflare and authorize the tunnel.

**Step 3: Create the tunnel**

Run:
```bash
cloudflared tunnel create visualizer
```

Expected: Tunnel created, credentials file saved to `~/.cloudflared/<tunnel-id>.json`

Note the tunnel ID from the output.

**Step 4: Create tunnel configuration**

Create directory:
```bash
mkdir -p cloudflared
```

Create `cloudflared/config.yml` (replace TUNNEL_ID with actual ID):

```yaml
# Cloudflare Tunnel Configuration
tunnel: TUNNEL_ID
credentials-file: /home/astre/.cloudflared/TUNNEL_ID.json

ingress:
  # Main domain routes to Django
  - hostname: trustedhearthandhome.com
    service: http://localhost:8000
  - hostname: www.trustedhearthandhome.com
    service: http://localhost:8000

  # Catch-all (required)
  - service: http_status:404
```

**Step 5: Configure DNS in Cloudflare**

Run:
```bash
cloudflared tunnel route dns visualizer trustedhearthandhome.com
cloudflared tunnel route dns visualizer www.trustedhearthandhome.com
```

Expected: CNAME records created in Cloudflare DNS

**Step 6: Test tunnel manually**

Run:
```bash
cloudflared tunnel --config cloudflared/config.yml run
```

In another terminal, verify:
```bash
curl -I https://trustedhearthandhome.com
```

Expected: HTTP 200 response from your Django app

**Step 7: Install cloudflared as service**

Run:
```bash
sudo cloudflared service install --config /home/astre/command-center/testhome/testhome-visualizer/cloudflared/config.yml
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

Verify:
```bash
sudo systemctl status cloudflared
```

Expected: Active (running)

**Step 8: Commit configuration**

```bash
git add cloudflared/config.yml
git commit -m "feat: add Cloudflare Tunnel configuration"
```

---

## Task 7: Rate Limiting on Guest Sessions

**Files:**
- Modify: `api/auth_views.py`

**Step 1: Add rate limiting to GuestSessionView**

In `api/auth_views.py`, add decorator to GuestSessionView.post:

```python
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator

class GuestSessionView(APIView):
    """Create anonymous guest session for beta testing. No login required."""
    permission_classes = [permissions.AllowAny]

    @method_decorator(ratelimit(key='ip', rate='10/h', method='POST', block=True))
    def post(self, request, *args, **kwargs):
        # ... existing code
```

**Step 2: Test rate limiting**

Run development server and test:
```bash
for i in {1..12}; do curl -X POST http://localhost:8000/api/auth/guest/ -s | head -c 50; echo; done
```

Expected: After 10 requests, should get 429 Too Many Requests

**Step 3: Commit**

```bash
git add api/auth_views.py
git commit -m "feat: add rate limiting to guest session creation"
```

---

## Task 8: Final Verification and Deployment

**Step 1: Run full deployment check**

```bash
source venv/bin/activate
DEBUG=False python3 manage.py check --deploy
```

Review and address any warnings.

**Step 2: Verify all services running**

```bash
sudo systemctl status visualizer
sudo systemctl status cloudflared
curl -I https://trustedhearthandhome.com
```

Expected: Both services running, HTTPS working

**Step 3: Test full user flow**

1. Open https://trustedhearthandhome.com in browser
2. Guest session should be created automatically
3. Upload an image and generate visualization
4. Verify result is returned

**Step 4: Monitor logs**

```bash
tail -f logs/gunicorn-error.log
sudo journalctl -u cloudflared -f
```

**Step 5: Final commit and push**

```bash
git add -A
git commit -m "chore: production deployment complete"
git push
```

---

## Rollback Plan

If something goes wrong:

```bash
# Stop services
sudo systemctl stop cloudflared
sudo systemctl stop visualizer

# Revert to development mode
# Edit .env: DEBUG=True
# Start development server
source venv/bin/activate
python3 manage.py runserver 8000
```

---

## Post-Deployment Checklist

- [ ] HTTPS working on trustedhearthandhome.com
- [ ] Guest session creation working
- [ ] Image upload working
- [ ] AI visualization generating
- [ ] Static files loading (CSS, JS)
- [ ] No errors in Gunicorn logs
- [ ] Cloudflare Tunnel stable
- [ ] Rate limiting working on /api/auth/guest/
