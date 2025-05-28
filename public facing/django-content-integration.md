# Django CMS Integration Guide for Unified Content Template

## Overview
This guide documents how to integrate the Ethical Capital unified content template with Django CMS, including automatic content length detection, video embedding, and rich content management.

## 1. Database Models

### Core Models (`models.py`)

```python
from django.db import models
from django.utils.html import strip_tags
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import readtime
import re

class Article(models.Model):
    """Main article model with automatic content length detection"""
    
    CONTENT_TYPES = [
        ('tutorial', 'Tutorial'),
        ('analysis', 'Analysis'),
        ('reference', 'Reference'),
        ('news', 'News'),
        ('opinion', 'Opinion'),
    ]
    
    CONTENT_LENGTHS = [
        ('quick', 'Quick (< 3 min)'),
        ('standard', 'Standard (3-10 min)'),
        ('deep', 'Deep (10+ min)'),
    ]
    
    # Basic fields
    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=300, blank=True, 
        help_text="Optional subtitle for hero section")
    slug = models.SlugField(unique=True)
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    
    # Content
    hero_image = models.ImageField(upload_to='articles/heroes/', blank=True,
        help_text="Recommended: 1600x800px. Leave blank for quick articles.")
    tldr = models.TextField(help_text="TL;DR summary - keep it concise")
    content = models.TextField(help_text="Main article content (Markdown + HTML)")
    
    # Metadata
    published = models.BooleanField(default=False)
    published_date = models.DateTimeField(blank=True, null=True)
    modified_date = models.DateTimeField(auto_now=True)
    author = models.ForeignKey('Author', on_delete=models.CASCADE)
    tags = models.ManyToManyField('Tag', blank=True)
    
    # SEO
    meta_description = models.CharField(max_length=160, blank=True,
        help_text="SEO meta description")
    
    # Auto-calculated
    read_time = models.IntegerField(editable=False, default=0)
    content_length = models.CharField(max_length=20, choices=CONTENT_LENGTHS, 
        editable=False, default='standard')
    word_count = models.IntegerField(editable=False, default=0)
    
    class Meta:
        ordering = ['-published_date']
        
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Calculate word count and read time
        plain_text = strip_tags(self.content)
        self.word_count = len(plain_text.split())
        self.read_time = max(1, round(self.word_count / 200))  # 200 words per minute
        
        # Determine content length class
        if self.read_time <= 3:
            self.content_length = 'quick'
        elif self.read_time <= 10:
            self.content_length = 'standard'
        else:
            self.content_length = 'deep'
        
        # Set published date when first published
        if self.published and not self.published_date:
            from django.utils import timezone
            self.published_date = timezone.now()
            
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return f"/insights/{self.slug}"
    
    def get_related_articles(self, limit=4):
        """Get related articles based on tags"""
        return Article.objects.filter(
            published=True,
            tags__in=self.tags.all()
        ).exclude(id=self.id).distinct()[:limit]


class VideoEmbed(models.Model):
    """Video embeds within articles"""
    
    VIDEO_TYPES = [
        ('youtube', 'YouTube'),
        ('vimeo', 'Vimeo'),
        ('wistia', 'Wistia'),
        ('custom', 'Custom/Self-hosted'),
    ]
    
    article = models.ForeignKey(Article, on_delete=models.CASCADE, 
        related_name='videos')
    video_type = models.CharField(max_length=20, choices=VIDEO_TYPES)
    video_id = models.CharField(max_length=100, blank=True,
        help_text="Video ID (e.g., YouTube video ID)")
    video_url = models.URLField(blank=True,
        help_text="Full URL for custom videos")
    caption = models.CharField(max_length=200, blank=True)
    position = models.IntegerField(default=0,
        help_text="Order of appearance in article")
    inline = models.BooleanField(default=False,
        help_text="Check for smaller inline video (480px max width)")
    
    class Meta:
        ordering = ['position']
    
    def __str__(self):
        return f"{self.get_video_type_display()} - {self.caption or 'No caption'}"
    
    def get_embed_code(self):
        """Generate the appropriate embed code"""
        if self.video_type == 'youtube':
            return f'<iframe src="https://www.youtube.com/embed/{self.video_id}" allowfullscreen></iframe>'
        elif self.video_type == 'vimeo':
            return f'<iframe src="https://player.vimeo.com/video/{self.video_id}" allowfullscreen></iframe>'
        elif self.video_type == 'wistia':
            return f'<iframe src="https://fast.wistia.net/embed/iframe/{self.video_id}" allowfullscreen></iframe>'
        elif self.video_type == 'custom' and self.video_url:
            return f'<video controls><source src="{self.video_url}" type="video/mp4"></video>'
        return ''
    
    def clean(self):
        """Validate video data"""
        if self.video_type in ['youtube', 'vimeo', 'wistia'] and not self.video_id:
            raise ValidationError(f'{self.get_video_type_display()} requires a video ID')
        if self.video_type == 'custom' and not self.video_url:
            raise ValidationError('Custom video requires a video URL')


class ContentBlock(models.Model):
    """Reusable content blocks for articles"""
    
    BLOCK_TYPES = [
        ('info', 'Info Box (Blue)'),
        ('warning', 'Warning Box (Orange)'),
        ('success', 'Success Box (Green)'),
        ('quote', 'Quote Block'),
        ('chart', 'Chart/Visualization'),
        ('table', 'Data Table'),
        ('code', 'Code Block'),
        ('faq', 'FAQ Section'),
    ]
    
    article = models.ForeignKey(Article, on_delete=models.CASCADE,
        related_name='content_blocks')
    block_type = models.CharField(max_length=20, choices=BLOCK_TYPES)
    content = models.TextField()
    position = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['position']
    
    def __str__(self):
        return f"{self.get_block_type_display()} at position {self.position}"


class Author(models.Model):
    """Article authors"""
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    bio = models.TextField(blank=True)
    initials = models.CharField(max_length=3,
        help_text="2-3 letter initials for avatar")
    email = models.EmailField(blank=True)
    
    def __str__(self):
        return self.name


class Tag(models.Model):
    """Article tags for categorization"""
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.name
```

## 2. Django Admin Configuration

### Enhanced Admin with Video Support (`admin.py`)

```python
from django.contrib import admin
from django.utils.html import format_html
from django_summernote.admin import SummernoteModelAdmin
from .models import Article, Author, Tag, VideoEmbed, ContentBlock

class VideoEmbedInline(admin.TabularInline):
    """Inline video management within articles"""
    model = VideoEmbed
    extra = 1
    fields = ['video_type', 'video_id', 'video_url', 'caption', 'inline', 'position']
    
    def get_formset(self, request, obj=None, **kwargs):
        formset = super().get_formset(request, obj, **kwargs)
        # Add help text dynamically
        formset.form.base_fields['video_id'].help_text = """
        YouTube: Use video ID from URL (e.g., dQw4w9WgXcQ from youtube.com/watch?v=dQw4w9WgXcQ)<br>
        Vimeo: Use video ID from URL (e.g., 123456789 from vimeo.com/123456789)<br>
        Wistia: Use video ID from embed code
        """
        return formset


class ContentBlockInline(admin.StackedInline):
    """Inline content blocks"""
    model = ContentBlock
    extra = 0
    fields = ['block_type', 'content', 'position']
    classes = ['collapse']


@admin.register(Article)
class ArticleAdmin(SummernoteModelAdmin):
    """Enhanced article admin with video embedding"""
    
    summernote_fields = ('content',)
    inlines = [VideoEmbedInline, ContentBlockInline]
    
    list_display = ['title', 'content_type', 'author', 'read_time_display', 
                    'content_length_badge', 'published', 'published_date']
    list_filter = ['published', 'content_type', 'content_length', 'author', 
                   'published_date', 'tags']
    search_fields = ['title', 'content', 'tldr']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['read_time', 'content_length', 'word_count', 
                       'preview_button', 'video_shortcuts']
    date_hierarchy = 'published_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'subtitle', 'slug', 'content_type', 'author')
        }),
        ('Hero Section', {
            'fields': ('hero_image',),
            'description': 'Leave blank for quick articles (< 3 min read)'
        }),
        ('Content', {
            'fields': ('tldr', 'content', 'video_shortcuts')
        }),
        ('Metadata & SEO', {
            'fields': ('tags', 'meta_description', 'read_time', 
                       'content_length', 'word_count'),
            'classes': ('collapse',)
        }),
        ('Publishing', {
            'fields': ('published', 'published_date', 'preview_button')
        }),
    )
    
    def read_time_display(self, obj):
        return f"{obj.read_time} min"
    read_time_display.short_description = "Read Time"
    
    def content_length_badge(self, obj):
        colors = {
            'quick': '#22C55E',
            'standard': '#3B82F6', 
            'deep': '#553C9A'
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            colors.get(obj.content_length, '#718096'),
            obj.get_content_length_display()
        )
    content_length_badge.short_description = "Length"
    
    def preview_button(self, obj):
        if obj.pk:
            return format_html(
                '<a class="button" href="/admin/preview/article/{}" target="_blank">'
                'Preview Article</a>',
                obj.pk
            )
        return "Save article first to preview"
    preview_button.short_description = "Preview"
    
    def video_shortcuts(self, obj):
        """Helper to show video embedding syntax"""
        return format_html('''
        <div style="background: #f3f4f6; padding: 12px; border-radius: 4px; 
                    font-family: monospace; font-size: 12px;">
            <strong>Video Embedding Shortcuts:</strong><br><br>
            In your content, use these placeholders:<br>
            <code>[video-1]</code> - First video<br>
            <code>[video-2]</code> - Second video<br>
            <code>[video-inline-1]</code> - First video as inline<br><br>
            Add videos in the "Video Embeds" section below.
        </div>
        ''')
    video_shortcuts.short_description = "Video Embedding"
    
    def save_model(self, request, obj, form, change):
        """Process video placeholders after saving"""
        super().save_model(request, obj, form, change)
        
        # Process video placeholders in content
        if obj.videos.exists():
            content = obj.content
            videos = list(obj.videos.all())
            
            # Replace placeholders with actual embed code
            for i, video in enumerate(videos, 1):
                # Full-width video
                full_placeholder = f'[video-{i}]'
                if full_placeholder in content:
                    embed_html = f'''
<div class="video-embed">
    <div class="video-wrapper">
        {video.get_embed_code()}
    </div>
    <div class="video-caption">{video.caption}</div>
</div>'''
                    content = content.replace(full_placeholder, embed_html)
                
                # Inline video
                inline_placeholder = f'[video-inline-{i}]'
                if inline_placeholder in content:
                    embed_html = f'''
<div class="video-inline">
    <div class="video-wrapper">
        {video.get_embed_code()}
    </div>
    <div class="video-caption">{video.caption}</div>
</div>'''
                    content = content.replace(inline_placeholder, embed_html)
            
            # Save processed content
            if content != obj.content:
                obj.content = content
                obj.save(update_fields=['content'])
    
    class Media:
        css = {
            'all': ('admin/css/article_admin.css',)
        }
        js = ('admin/js/article_admin.js',)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'title', 'initials', 'email']
    search_fields = ['name', 'email']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']
```

## 3. URL Configuration

### URLs (`urls.py`)

```python
from django.urls import path
from . import views

app_name = 'insights'

urlpatterns = [
    # Article list and filtering
    path('', views.ArticleListView.as_view(), name='article_list'),
    path('type/<str:content_type>/', views.ArticleListView.as_view(), name='article_by_type'),
    path('tag/<slug:tag>/', views.ArticleListView.as_view(), name='article_by_tag'),
    
    # Article detail
    path('<slug:slug>/', views.ArticleDetailView.as_view(), name='article_detail'),
    
    # Preview for admin
    path('preview/<int:pk>/', views.ArticlePreviewView.as_view(), name='article_preview'),
    
    # API endpoints for dynamic content
    path('api/articles/', views.ArticleAPIView.as_view(), name='article_api'),
]
```

## 4. Views

### View Classes (`views.py`)

```python
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from django.db.models import Q
from .models import Article, Tag

class ArticleListView(ListView):
    """List view with filtering support"""
    model = Article
    template_name = 'insights/article_list.html'
    context_object_name = 'articles'
    paginate_by = 20
    
    def get_queryset(self):
        queryset = Article.objects.filter(published=True)
        
        # Filter by type
        content_type = self.kwargs.get('content_type') or self.request.GET.get('type')
        if content_type:
            queryset = queryset.filter(content_type=content_type)
        
        # Filter by tag
        tag_slug = self.kwargs.get('tag')
        if tag_slug:
            queryset = queryset.filter(tags__slug=tag_slug)
        
        # Filter by length
        length = self.request.GET.get('length')
        if length:
            queryset = queryset.filter(content_length=length)
        
        # Search
        search = self.request.GET.get('q')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(content__icontains=search) |
                Q(tldr__icontains=search)
            )
        
        return queryset.order_by('-published_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['content_types'] = Article.CONTENT_TYPES
        context['popular_tags'] = Tag.objects.annotate(
            article_count=models.Count('article')
        ).order_by('-article_count')[:10]
        return context


class ArticleDetailView(DetailView):
    """Article detail view with dynamic content class"""
    model = Article
    template_name = 'insights/article_detail.html'
    context_object_name = 'article'
    
    def get_queryset(self):
        return Article.objects.filter(published=True)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Add content class for template
        context['content_class'] = f'content-{self.object.content_length}'
        
        # Get related articles
        context['related_articles'] = self.object.get_related_articles()
        
        # Process videos
        context['videos'] = self.object.videos.all()
        
        return context


@method_decorator(staff_member_required, name='dispatch')
class ArticlePreviewView(DetailView):
    """Preview view for admin users"""
    model = Article
    template_name = 'insights/article_detail.html'
    context_object_name = 'article'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['content_class'] = f'content-{self.object.content_length}'
        context['is_preview'] = True
        return context


class ArticleAPIView(View):
    """API endpoint for dynamic content loading"""
    
    def get(self, request):
        articles = Article.objects.filter(published=True)[:10]
        data = [{
            'title': article.title,
            'url': article.get_absolute_url(),
            'type': article.get_content_type_display(),
            'read_time': article.read_time,
            'published': article.published_date.isoformat() if article.published_date else None,
        } for article in articles]
        return JsonResponse({'articles': data})
```

## 5. Templates

### Base Article Template (`templates/insights/article_detail.html`)

```django
{% extends "base.html" %}
{% load markdown_extras static %}

{% block body_class %}{{ content_class }}{% endblock %}

{% block title %}{{ article.title }} | Ethical Capital{% endblock %}

{% block meta_description %}{{ article.meta_description|default:article.tldr }}{% endblock %}

{% block content %}
<!-- Include the unified template styles here -->
<link rel="stylesheet" href="{% static 'css/unified-content.css' %}">

<!-- Breadcrumb -->
<div class="breadcrumb">
    <a href="/">Home</a>
    <span>/</span>
    <a href="{% url 'insights:article_list' %}">Insights</a>
    <span>/</span>
    <a href="{% url 'insights:article_by_type' article.content_type %}">
        {{ article.get_content_type_display }}
    </a>
</div>

<!-- Hero Section (conditional) -->
{% if article.hero_image %}
<div class="hero">
    <img src="{{ article.hero_image.url }}" alt="{{ article.title }}" class="hero-image">
    <div class="hero-overlay">
        <div class="hero-content">
            <h1>{{ article.title }}</h1>
            {% if article.subtitle %}
            <p class="subtitle">{{ article.subtitle }}</p>
            {% endif %}
        </div>
    </div>
</div>
{% else %}
<!-- Article Header (when no hero) -->
<div class="article-header">
    <div class="article-header-content">
        <div class="article-meta">
            <div class="meta-item">
                <span class="content-type">{{ article.get_content_type_display|upper }}</span>
            </div>
            <div class="meta-item">
                <span>📖</span>
                <span>{{ article.read_time }} min read</span>
            </div>
            <div class="meta-item">
                <span>📅</span>
                <span>{{ article.published_date|date:"M d, Y" }}</span>
            </div>
            {% if article.tags.exists %}
            <div class="meta-item">
                <span>🏷️</span>
                <span>
                    {% for tag in article.tags.all %}
                    <a href="{% url 'insights:article_by_tag' tag.slug %}">{{ tag.name }}</a>{% if not forloop.last %}, {% endif %}
                    {% endfor %}
                </span>
            </div>
            {% endif %}
        </div>
        <h1>{{ article.title }}</h1>
    </div>
</div>
{% endif %}

<!-- Preview Banner (for admin preview) -->
{% if is_preview %}
<div class="preview-banner" style="background: #F59E0B; color: white; padding: 12px; text-align: center; font-weight: 600;">
    PREVIEW MODE - This article is not yet published
</div>
{% endif %}

<!-- Main Layout -->
<div class="main-layout">
    <!-- TOC would go here for deep content -->
    {% if article.content_length == 'deep' %}
    <aside class="toc">
        <div class="toc-sticky">
            <h3>Contents</h3>
            <!-- TOC generated from content headings -->
            {{ article.content|toc }}
        </div>
    </aside>
    {% endif %}

    <!-- Main Content -->
    <article class="content">
        <!-- TL;DR Box -->
        <div class="tldr-box">
            <h3>TL;DR</h3>
            <p>{{ article.tldr }}</p>
        </div>

        <!-- Article Body with processed video embeds -->
        {{ article.content|markdown|safe }}
        
        <!-- Next Steps CTA -->
        {% if article.content_type == 'tutorial' %}
        <div class="next-steps">
            <h3>Need Help?</h3>
            <p>Our team is here to assist you with any questions.</p>
            <a href="/contact" class="btn-primary">Contact Support</a>
        </div>
        {% else %}
        <div class="next-steps">
            <h3>Want to learn more?</h3>
            <p>Explore our investment process and see how we put these insights into practice.</p>
            <a href="/process" class="btn-primary">Our Process</a>
        </div>
        {% endif %}
    </article>

    <!-- Sidebar (conditional based on content length) -->
    {% if article.content_length != 'quick' %}
    <aside class="sidebar">
        <div class="sidebar-section">
            <h3>About the Author</h3>
            <div class="author-box">
                <div class="author-avatar">{{ article.author.initials }}</div>
                <div class="author-info">
                    <h4>{{ article.author.name }}</h4>
                    <p>{{ article.author.title }}</p>
                </div>
            </div>
            {% if article.author.bio %}
            <p style="margin-top: 12px; font-size: 12px; color: var(--ec-text-muted);">
                {{ article.author.bio }}
            </p>
            {% endif %}
        </div>
        
        {% if related_articles %}
        <div class="sidebar-section">
            <h3>Related Reading</h3>
            <ul class="related-list">
                {% for related in related_articles %}
                <li>
                    <a href="{{ related.get_absolute_url }}">{{ related.title }}</a>
                    <div class="related-meta">
                        {{ related.get_content_type_display }} • {{ related.read_time }} min read
                    </div>
                </li>
                {% endfor %}
            </ul>
        </div>
        {% endif %}
        
        {% include 'includes/newsletter_signup.html' %}
    </aside>
    {% endif %}
</div>
{% endblock %}

{% block extra_js %}
<script>
    // Initialize any interactive elements
    document.addEventListener('DOMContentLoaded', function() {
        // FAQ toggles
        document.querySelectorAll('.faq-question').forEach(question => {
            question.addEventListener('click', () => {
                question.parentElement.classList.toggle('open');
            });
        });
        
        // Table of contents highlighting for deep content
        {% if article.content_length == 'deep' %}
        const headings = document.querySelectorAll('h2[id], h3[id]');
        const tocLinks = document.querySelectorAll('.toc-list a');
        
        window.addEventListener('scroll', () => {
            let current = '';
            headings.forEach(heading => {
                const rect = heading.getBoundingClientRect();
                if (rect.top <= 100) {
                    current = heading.getAttribute('id');
                }
            });
            
            tocLinks.forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === '#' + current) {
                    link.classList.add('active');
                }
            });
        });
        {% endif %}
    });
</script>
{% endblock %}
```

## 6. Static Files

### Admin CSS (`static/admin/css/article_admin.css`)

```css
/* Enhanced admin styles for article editing */
.field-video_shortcuts {
    margin: 20px 0;
}

.field-video_shortcuts .readonly {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    padding: 15px;
}

/* Make Summernote editor larger */
.summernote-div {
    min-height: 500px;
}

/* Video embed inline preview */
.inline-group .tabular tr.has_original td {
    background: #f8f9fa;
}

/* Content block inline styling */
.inline-group.content_blocks-group {
    background: #f8f9fa;
    padding: 10px;
    border-radius: 4px;
}

/* Preview button styling */
.field-preview_button .button {
    background: #553C9A;
    color: white;
    padding: 10px 20px;
    text-decoration: none;
    border-radius: 4px;
    display: inline-block;
}

.field-preview_button .button:hover {
    background: #6B46C1;
}
```

### Admin JavaScript (`static/admin/js/article_admin.js`)

```javascript
(function($) {
    $(document).ready(function() {
        // Auto-update slug from title
        $('#id_title').on('blur', function() {
            var title = $(this).val();
            var slug = $('#id_slug');
            if (!slug.val()) {
                slug.val(title.toLowerCase()
                    .replace(/[^\w ]+/g, '')
                    .replace(/ +/g, '-'));
            }
        });
        
        // Show/hide video URL field based on video type
        $('.field-video_type select').on('change', function() {
            var $row = $(this).closest('tr');
            var videoType = $(this).val();
            
            if (videoType === 'custom') {
                $row.find('.field-video_id').hide();
                $row.find('.field-video_url').show();
            } else {
                $row.find('.field-video_id').show();
                $row.find('.field-video_url').hide();
            }
        }).trigger('change');
        
        // Add video placeholder helper
        $('.add-row a').on('click', function() {
            setTimeout(function() {
                $('.field-video_type select').trigger('change');
            }, 100);
        });
        
        // Character count for TL;DR
        $('#id_tldr').after('<div class="tldr-count" style="margin-top: 5px; color: #666;"></div>');
        $('#id_tldr').on('input', function() {
            var count = $(this).val().length;
            $('.tldr-count').text(count + ' characters (recommended: under 200)');
        }).trigger('input');
    });
})(django.jQuery);
```

## 7. Template Tags

### Markdown Processing (`templatetags/markdown_extras.py`)

```python
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
import markdown
from markdown.extensions.toc import TocExtension
import re

register = template.Library()

@register.filter
@stringfilter
def markdown(value):
    """Convert markdown to HTML with extensions"""
    md = markdown.Markdown(extensions=[
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.tables',
        'markdown.extensions.footnotes',
        'markdown.extensions.attr_list',
        'markdown.extensions.toc',
        'markdown.extensions.extra',
    ])
    return mark_safe(md.convert(value))

@register.filter
@stringfilter
def toc(value):
    """Extract table of contents from markdown"""
    md = markdown.Markdown(extensions=[TocExtension(baselevel=2)])
    md.convert(value)
    return mark_safe(md.toc)

@register.filter
def reading_time(word_count):
    """Calculate reading time from word count"""
    minutes = max(1, round(word_count / 200))
    return f"{minutes} min read"
```

## 8. Settings Configuration

### Django Settings (`settings.py`)

```python
# Add to INSTALLED_APPS
INSTALLED_APPS = [
    # ... other apps
    'django_summernote',
    'insights',
]

# Summernote configuration
SUMMERNOTE_CONFIG = {
    'iframe': True,
    'summernote': {
        'width': '100%',
        'height': '600',
        'toolbar': [
            ['style', ['style']],
            ['font', ['bold', 'italic', 'underline', 'clear']],
            ['fontname', ['fontname']],
            ['color', ['color']],
            ['para', ['ul', 'ol', 'paragraph']],
            ['height', ['height']],
            ['table', ['table']],
            ['insert', ['link', 'picture', 'video', 'hr']],
            ['view', ['fullscreen', 'codeview']],
            ['help', ['help']],
        ],
        'codemirror': {
            'theme': 'monokai',
        },
    },
    'attachment_model': 'insights.Attachment',
    'attachment_upload_to': 'attachments/',
    'attachment_filesize_limit': 5 * 1024 * 1024,  # 5MB
}

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Static files
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
```

## 9. Deployment Checklist

### Production Considerations

1. **Image Optimization**
   ```python
   # Install: pip install pillow-heif pillow-avif-plugin
   # Add image optimization to model save
   ```

2. **Caching**
   ```python
   # Cache article queries
   from django.core.cache import cache
   
   def get_cached_article(slug):
       key = f'article_{slug}'
       article = cache.get(key)
       if not article:
           article = Article.objects.get(slug=slug, published=True)
           cache.set(key, article, 3600)  # 1 hour
       return article
   ```

3. **Search**
   ```python
   # Add full-text search with PostgreSQL
   from django.contrib.postgres.search import SearchVector
   
   Article.objects.annotate(
       search=SearchVector('title', 'content', 'tldr')
   ).filter(search='your query')
   ```

4. **SEO Enhancements**
   ```python
   # Add to article model
   og_image = models.ImageField(upload_to='og/', blank=True)
   canonical_url = models.URLField(blank=True)
   
   # Generate sitemap
   class ArticleSitemap(Sitemap):
       changefreq = "weekly"
       priority = 0.8
       
       def items(self):
           return Article.objects.filter(published=True)
   ```

5. **Performance**
   - Use select_related() and prefetch_related() for queries
   - Enable Django template caching
   - Compress static files
   - Use CDN for media files

## 10. Content Migration

### Import Existing Content

```python
# management/commands/import_content.py
from django.core.management.base import BaseCommand
from insights.models import Article, Author
import markdown
import frontmatter

class Command(BaseCommand):
    help = 'Import markdown files as articles'
    
    def add_arguments(self, parser):
        parser.add_argument('directory', type=str)
    
    def handle(self, *args, **options):
        import os
        from pathlib import Path
        
        directory = Path(options['directory'])
        default_author = Author.objects.get_or_create(
            name="Sloane Ortel",
            defaults={
                'title': 'Chief Investment Officer',
                'initials': 'SO'
            }
        )[0]
        
        for md_file in directory.glob('*.md'):
            with open(md_file, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
                
                Article.objects.create(
                    title=post.get('title', md_file.stem),
                    slug=post.get('slug', md_file.stem),
                    content_type=post.get('type', 'analysis'),
                    content=post.content,
                    tldr=post.get('tldr', ''),
                    author=default_author,
                    published=True
                )
                
            self.stdout.write(f"Imported {md_file.name}")
```

## Usage Examples

### Creating an Article with Videos

1. **In Django Admin:**
   - Create new article
   - Fill in basic information
   - In content field, add placeholder: `[video-1]` where you want the video
   - In Video Embeds section below, add your video details
   - Save and preview

2. **Video Types:**
   - YouTube: Just paste the video ID (e.g., `dQw4w9WgXcQ`)
   - Vimeo: Just the numeric ID (e.g., `123456789`)
   - Custom: Full URL to your hosted video

3. **Content Example:**
   ```markdown
   ## Introduction
   
   Here's an overview of our investment process:
   
   [video-1]
   
   ## Deep Dive
   
   For a detailed explanation, watch this:
   
   [video-inline-2]
   
   ### Key Points
   - Point 1
   - Point 2
   ```

This will automatically render with the proper video embed HTML!