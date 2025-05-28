# nginx.conf - Reverse proxy with caching
server {
    listen 80;
    server_name tickreview.yourcompany.com;
    
    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
    gzip_min_length 1000;
    
    # Static files - served directly by nginx
    location /static/ {
        alias /var/www/tickreview/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Media files (PDFs, etc)
    location /media/ {
        alias /var/www/tickreview/media/;
        expires 1d;
    }
    
    # Cache API responses
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_cache api_cache;
        proxy_cache_valid 200 1m;
        proxy_cache_key "$request_uri|$request_body";
        proxy_cache_methods POST GET;
    }
    
    # WebSocket for dictation
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
    
    # Django app
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

# gunicorn.conf.py - Production WSGI server
bind = "127.0.0.1:8000"
workers = 4  # 2 * CPU cores + 1
worker_class = "uvicorn.workers.UvicornWorker"  # For async support
worker_connections = 1000
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

# Preload app for faster worker startup
preload_app = True

# docker-compose.yml - Complete stack
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: tickdb
      POSTGRES_USER: tickuser
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    command: >
      postgres
      -c shared_buffers=256MB
      -c effective_cache_size=1GB
      -c maintenance_work_mem=64MB
      -c checkpoint_completion_target=0.9
      -c wal_buffers=16MB
      -c random_page_cost=1.1
      -c effective_io_concurrency=200
      -c work_mem=4MB
      -c min_wal_size=1GB
      -c max_wal_size=4GB
    
  redis:
    image: redis:7-alpine
    command: >
      redis-server
      --maxmemory 512mb
      --maxmemory-policy allkeys-lru
      --save ""
      --appendonly no
    
  app:
    build: .
    depends_on:
      - db
      - redis
    environment:
      DATABASE_URL: postgres://tickuser:${DB_PASSWORD}@db/tickdb
      REDIS_URL: redis://redis:6379/0
    volumes:
      - static:/app/static
      - media:/app/media
    command: gunicorn config.wsgi:application -c gunicorn.conf.py
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/conf.d/default.conf
      - static:/var/www/tickreview/static
      - media:/var/www/tickreview/media
    depends_on:
      - app

volumes:
  postgres_data:
  static:
  media:

# production_settings.py - Django optimizations
from .settings import *

DEBUG = False
ALLOWED_HOSTS = ['tickreview.yourcompany.com']

# Database connection pooling
DATABASES['default']['CONN_MAX_AGE'] = 600
DATABASES['default']['OPTIONS'] = {
    'connect_timeout': 10,
    'options': '-c statement_timeout=30000'  # 30 second query timeout
}

# Aggressive caching
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            'CONNECTION_POOL_KWARGS': {'max_connections': 50},
            'PARSER_CLASS': 'redis.connection.HiredisParser',
        }
    }
}

# Cache entire views
CACHE_MIDDLEWARE_SECONDS = 60
CACHE_MIDDLEWARE_KEY_PREFIX = 'tickreview'

# Security
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Static files with compression
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
WHITENOISE_COMPRESSION_QUALITY = 80

# Template caching
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]

# Logging - only errors in production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/tickreview/error.log',
            'maxBytes': 10 * 1024 * 1024,  # 10MB
            'backupCount': 10,
        },
    },
    'root': {
        'handlers': ['file'],
        'level': 'ERROR',
    },
}

# management/commands/warmup_cache.py
from django.core.management.base import BaseCommand
from django.core.cache import cache
from tick.models import Security

class Command(BaseCommand):
    """Pre-warm cache on deploy"""
    
    def handle(self, *args, **options):
        # Cache universe list
        universe = list(Security.objects.filter(
            status='universe'
        ).values('ticker', 'name', 'tick_score').order_by('ticker'))
        
        cache.set('universe_global', universe, 3600)
        
        # Cache high-frequency securities
        for security in Security.objects.filter(status='universe')[:100]:
            cache.set(f'security_{security.ticker}', {
                'ticker': security.ticker,
                'name': security.name,
                'tick_score': security.tick_score,
                'metrics': security.get_key_metrics()
            }, 3600)
        
        self.stdout.write('Cache warmed up!')

# Database indexes for speed
class Migration(migrations.Migration):
    operations = [
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY idx_security_ticker_status ON tick_security(ticker, status);",
            reverse_sql="DROP INDEX idx_security_ticker_status;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY idx_tick_updated ON tick_security(tick_last_updated DESC NULLS LAST);",
            reverse_sql="DROP INDEX idx_tick_updated;"
        ),
        migrations.RunSQL(
            "CREATE INDEX CONCURRENTLY idx_notes_recent ON tick_note(security_id, created_at DESC);",
            reverse_sql="DROP INDEX idx_notes_recent;"
        ),
        migrations.RunSQL(
            "CLUSTER tick_security USING idx_security_ticker_status;",
            reverse_sql="ALTER TABLE tick_security SET WITHOUT CLUSTER;"
        ),
    ]