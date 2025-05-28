# views.py - Server-side rendering for maximum speed
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
from django.db.models import Prefetch, F, Q
from django.utils.decorators import method_decorator
import json
import asyncio
from channels.db import database_sync_to_async

class QuickReviewView(TemplateView):
    """Main dashboard - server-rendered for instant load"""
    template_name = 'tick/quick_review.html'
    
    def get_context_data(self, ticker=None, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get ticker from URL or use last viewed
        if not ticker:
            ticker = self.request.session.get('last_ticker', 'AAPL')
        
        # Single query with all relationships
        security = Security.objects.select_related(
            'latest_presentation',
            'sector',
            'industry'
        ).prefetch_related(
            Prefetch('notes', 
                queryset=Note.objects.order_by('-created_at')[:5],
                to_attr='recent_notes'
            ),
            Prefetch('ai_insights',
                queryset=AIInsight.objects.filter(
                    insight_type__in=['risk_change', 'ethics', 'peer_comp']
                ).order_by('-created_at')[:3],
                to_attr='recent_insights'
            ),
            Prefetch('tick_scores',
                queryset=TickScore.objects.order_by('-created_at')[:1],
                to_attr='latest_tick'
            )
        ).get(ticker=ticker)
        
        # Get universe list from cache or build it
        universe_key = f'universe_{self.request.user.id}'
        universe = cache.get(universe_key)
        if not universe:
            universe = list(Security.objects.filter(
                status='universe'
            ).values('ticker', 'name', 'tick_score').order_by('ticker'))
            cache.set(universe_key, universe, 3600)  # 1 hour cache
        
        context.update({
            'security': security,
            'universe': universe,
            'observe_count': cache.get('observe_count', 0),
            'last_ticker': ticker,
        })
        
        # Store in session for next visit
        self.request.session['last_ticker'] = ticker
        
        return context

class DeepAnalysisView(TemplateView):
    """Presentation analysis mode"""
    template_name = 'tick/deep_analysis.html'
    
    def get_context_data(self, ticker, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get security with minimal queries
        security = Security.objects.select_related(
            'latest_presentation'
        ).get(ticker=ticker)
        
        # Start new session
        session = AnalysisSession.objects.create(
            security=security,
            presentation=security.latest_presentation,
            analyst=self.request.user,
            initial_tick=security.tick_score or 0
        )
        
        # Get any existing notes for this presentation
        existing_notes = SlideNote.objects.filter(
            session__security=security,
            session__presentation=security.latest_presentation
        ).order_by('slide_number', '-created_at').distinct('slide_number')
        
        context.update({
            'security': security,
            'session': session,
            'presentation': security.latest_presentation,
            'existing_notes': existing_notes,
            'ai_tick_guess': self._get_ai_tick_guess(security),
        })
        
        return context
    
    def _get_ai_tick_guess(self, security):
        """Quick AI guess at tick score - cached"""
        cache_key = f'ai_tick_{security.ticker}'
        guess = cache.get(cache_key)
        if not guess:
            # Simple heuristic for now, replace with actual AI
            guess = min(100, max(-100, 
                int(security.tick_score or 0) + 
                (10 if security.revenue_growth > 0.1 else -5)
            ))
            cache.set(cache_key, guess, 86400)  # 24 hour cache
        return guess

# Fast AJAX endpoints
@method_decorator(csrf_exempt, name='dispatch')
class UpdateTickAPI(View):
    """Lightning-fast tick updates"""
    
    def post(self, request, ticker):
        data = json.loads(request.body)
        new_score = int(data['score'])
        
        # Update in single query
        Security.objects.filter(ticker=ticker).update(
            tick_score=new_score,
            tick_last_updated=timezone.now()
        )
        
        # Create history record
        TickScore.objects.create(
            security_id=Security.objects.get(ticker=ticker).id,
            score=new_score,
            scorer=request.user,
            notes=data.get('notes', '')
        )
        
        # Invalidate caches
        cache.delete(f'universe_{request.user.id}')
        
        return JsonResponse({'status': 'ok', 'score': new_score})

@method_decorator(csrf_exempt, name='dispatch')
class SaveNoteAPI(View):
    """Save notes with minimal latency"""
    
    def post(self, request):
        data = json.loads(request.body)
        
        # Bulk create for speed
        note = SlideNote.objects.create(
            session_id=data['session_id'],
            slide_number=data['slide_number'],
            slide_title=data.get('slide_title', ''),
            note_text=data['text']
        )
        
        return JsonResponse({
            'status': 'ok', 
            'note_id': note.id,
            'timestamp': note.created_at.isoformat()
        })

class RandomTickerAPI(View):
    """Get random ticker needing review"""
    
    def get(self, request):
        # Prioritize securities needing review
        ticker = Security.objects.filter(
            Q(tick_last_updated__lt=timezone.now() - timedelta(days=90)) |
            Q(tick_score__isnull=True),
            status='universe'
        ).order_by('?').values_list('ticker', flat=True).first()
        
        if not ticker:
            # Fallback to any random
            ticker = Security.objects.filter(
                status='universe'
            ).order_by('?').values_list('ticker', flat=True).first()
        
        return JsonResponse({'ticker': ticker})

# WebSocket for real-time dictation
from channels.generic.websocket import AsyncWebsocketConsumer
import whisper

class DictationConsumer(AsyncWebsocketConsumer):
    """WebSocket for continuous dictation"""
    
    async def connect(self):
        await self.accept()
        self.whisper_model = await self.load_whisper()
    
    async def receive(self, bytes_data=None, text_data=None):
        if bytes_data:
            # Process audio chunk
            transcription = await self.transcribe_audio(bytes_data)
            await self.send(text_data=json.dumps({
                'type': 'transcription',
                'text': transcription
            }))
    
    @database_sync_to_async
    def load_whisper(self):
        # Cache the model in memory
        if not hasattr(self.channel_layer, 'whisper_model'):
            self.channel_layer.whisper_model = whisper.load_model("base")
        return self.channel_layer.whisper_model
    
    async def transcribe_audio(self, audio_bytes):
        # Run CPU-bound transcription in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self._transcribe_sync,
            audio_bytes
        )
    
    def _transcribe_sync(self, audio_bytes):
        # Save to temp file (Whisper requirement)
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.wav') as tmp:
            tmp.write(audio_bytes)
            tmp.flush()
            result = self.channel_layer.whisper_model.transcribe(tmp.name)
            return result['text']

# urls.py
from django.urls import path
from . import views

urlpatterns = [
    # Main views - server rendered
    path('', views.QuickReviewView.as_view(), name='home'),
    path('review/<str:ticker>/', views.QuickReviewView.as_view(), name='review'),
    path('analyze/<str:ticker>/', views.DeepAnalysisView.as_view(), name='analyze'),
    
    # Fast AJAX endpoints
    path('api/tick/<str:ticker>/', views.UpdateTickAPI.as_view(), name='update_tick'),
    path('api/note/', views.SaveNoteAPI.as_view(), name='save_note'),
    path('api/random/', views.RandomTickerAPI.as_view(), name='random_ticker'),
    path('api/search/', views.SearchAPI.as_view(), name='search'),
    
    # WebSocket for dictation
    path('ws/dictate/', consumers.DictationConsumer.as_asgi(), name='dictate'),
]

# models.py - Optimized for speed
class Security(models.Model):
    ticker = models.CharField(max_length=10, unique=True, db_index=True)
    name = models.CharField(max_length=200)
    tick_score = models.IntegerField(null=True, db_index=True)
    tick_last_updated = models.DateTimeField(null=True, db_index=True)
    status = models.CharField(max_length=20, default='universe', db_index=True)
    
    # Denormalized for speed
    latest_presentation = models.ForeignKey(
        'InvestorPresentation', 
        null=True, 
        on_delete=models.SET_NULL,
        related_name='+'
    )
    revenue_growth = models.FloatField(null=True)  # Cached metric
    fcf_yield = models.FloatField(null=True)  # Cached metric
    
    class Meta:
        indexes = [
            models.Index(fields=['ticker']),
            models.Index(fields=['status', 'tick_score']),
            models.Index(fields=['tick_last_updated']),
            models.Index(fields=['status', '-tick_last_updated']),  # For review needed
        ]

# settings.py - Performance settings
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'tickdb',
        'CONN_MAX_AGE': 600,  # Persistent connections
        'OPTIONS': {
            'connect_timeout': 10,
        }
    }
}

# Cache configuration
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {'max_connections': 50},
            'SOCKET_CONNECT_TIMEOUT': 5,
            'SOCKET_TIMEOUT': 5,
        }
    }
}

# Session in Redis for speed
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Middleware optimization
MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',  # Cache pages
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Serve static files fast
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    # Skip CSRF for API endpoints
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',  # Fetch from cache
]

# Static files served by WhiteNoise
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Template caching
TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'OPTIONS': {
        'loaders': [
            ('django.template.loaders.cached.Loader', [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ]),
        ],
    },
}]