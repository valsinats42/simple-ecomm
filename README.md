# Simple Ecomm

A small Django 6 + Django Ninja ecommerce API demo with products, categories, image uploads, admin support, and basic bearer-token protection for write endpoints.

## Tech Stack

- Python 3.14
- Django 6
- Django Ninja
- SQLite for local development
- Pillow for image validation
- WhiteNoise for static files
- Gunicorn for simple production serving

## Local Development

Install dependencies:

```bash
uv sync
```

Run database migrations:

```bash
uv run backend/manage.py migrate
```

Create an admin user:

```bash
uv run backend/manage.py createsuperuser
```

Start the development server:

```bash
uv run backend/manage.py runserver
```

Useful local URLs:

- Django admin: `http://127.0.0.1:8000/admin/`
- Swagger API docs: `http://127.0.0.1:8000/api/v1/docs`
- Products API: `http://127.0.0.1:8000/api/v1/products`
- Categories API: `http://127.0.0.1:8000/api/v1/categories`

Run tests:

```bash
uv run backend/manage.py test api
```

## API Key

The project uses a single API for accessing all of the write endpoints.
A demo API key hash is defined in `backend/simpleecomm/settings.py`.
The demo plaintext key is `secret`.

Use it as a bearer token for protected endpoints:

```bash
curl \
  -H "Authorization: Bearer secret" \
  http://127.0.0.1:8000/api/v1/products
```

Generate a SHA-256 hash for a different local key:

```bash
echo -n "your-api-key" | python -c 'import sys, hashlib; print(hashlib.sha256(sys.stdin.read().encode()).hexdigest())'
```

For production, do not use the demo key. Set `API_KEY_SHA256` from the environment or from production-only settings.

## Static and Media Files

Current paths:

- Static files: `backend/static`
- Uploaded media: `backend/uploads`

Collect static files:

```bash
uv run backend/manage.py collectstatic
```

During local development, Django serves media files when `DEBUG = True`. In production, serve uploaded media through Nginx, object storage, or another dedicated file-serving layer.

## Simple Production Setup: MariaDB + Gunicorn

This is intentionally minimal. For a real deployment, also review HTTPS, secure cookies, logging, backups, process monitoring, and Django's deployment checklist.

### 1. Check Production Dependencies

The project already includes the MariaDB/MySQL driver and Gunicorn in its normal dependency list.

If `mysqlclient` build fails, install your OS MariaDB development headers first. On Debian/Ubuntu that is usually:

```bash
sudo apt install build-essential pkg-config default-libmysqlclient-dev
```

### 2. Create the MariaDB Database

If you want to run MariaDB in a local container for testing the production-style setup, use Docker or Podman:

```bash
docker run --name simple-ecomm-mariadb \
  -e MARIADB_ROOT_PASSWORD=change-root-password \
  -e MARIADB_DATABASE=simple_ecomm \
  -e MARIADB_USER=simple_ecomm \
  -e MARIADB_PASSWORD=change-this-password \
  -p 3306:3306 \
  -v simple-ecomm-mariadb:/var/lib/mysql \
  -d mariadb:latest
```

If you are using a MariaDB server installed directly on the host, create the database and user manually.

Example SQL:

```sql
CREATE DATABASE simple_ecomm CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'simple_ecomm'@'localhost' IDENTIFIED BY 'change-this-password';
GRANT ALL PRIVILEGES ON simple_ecomm.* TO 'simple_ecomm'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Configure Production Settings

The current `settings.py` is local-development oriented. For production, set at least:

```python
import os

SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]
DEBUG = False
ALLOWED_HOSTS = ["example.com", "127.0.0.1"]

API_KEY_SHA256 = os.environ["API_KEY_SHA256"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ["DB_NAME"],
        "USER": os.environ["DB_USER"],
        "PASSWORD": os.environ["DB_PASSWORD"],
        "HOST": os.environ.get("DB_HOST", "127.0.0.1"),
        "PORT": os.environ.get("DB_PORT", "3306"),
        "OPTIONS": {
            "charset": "utf8mb4",
        },
    }
}
```

Set environment variables:

```bash
export DJANGO_SECRET_KEY="change-this-to-a-long-random-secret"
export API_KEY_SHA256="sha256-hash-of-your-production-api-key"
export DB_NAME="simple_ecomm"
export DB_USER="simple_ecomm"
export DB_PASSWORD="change-this-password"
export DB_HOST="127.0.0.1"
export DB_PORT="3306"
```

### 4. Migrate and Collect Static

```bash
uv run python backend/manage.py migrate
uv run python backend/manage.py collectstatic --noinput
```

### 5. Run Gunicorn

From the repository root:

```bash
uv run gunicorn simpleecomm.wsgi:application \
  --chdir backend \
  --bind 127.0.0.1:8000 \
  --workers 3
```

### 6. Optional systemd Service

Example `/etc/systemd/system/simple-ecomm.service`:

```ini
[Unit]
Description=Simple Ecomm Django app
After=network.target mariadb.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/srv/simple-ecomm
Environment="DJANGO_SECRET_KEY=change-this-to-a-long-random-secret"
Environment="API_KEY_SHA256=sha256-hash-of-your-production-api-key"
Environment="DB_NAME=simple_ecomm"
Environment="DB_USER=simple_ecomm"
Environment="DB_PASSWORD=change-this-password"
Environment="DB_HOST=127.0.0.1"
Environment="DB_PORT=3306"
ExecStart=/srv/simple-ecomm/.venv/bin/gunicorn simpleecomm.wsgi:application --chdir backend --bind 127.0.0.1:8000 --workers 3
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable simple-ecomm
sudo systemctl start simple-ecomm
```

### 7. Nginx Frontend

Gunicorn should serve Django only. Put Nginx in front of it for static/media files and reverse proxying:

```nginx
server {
    listen 80;
    server_name example.com;

    location /static/ {
        alias /srv/simple-ecomm/backend/static/;
    }

    location /media/ {
        alias /srv/simple-ecomm/backend/uploads/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

For HTTPS, use Certbot or your preferred TLS setup.
