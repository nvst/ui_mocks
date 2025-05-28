# admin.py
from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import Article, Author, Tag

@admin.register(Article)
class ArticleAdmin(SummernoteModelAdmin):
    summernote_fields = ('content',)
    list_display = ['title', 'content_type', 'author', 'read_time', 'content_length', 'published_date']
    list_filter = ['content_type', 'content_length', 'author', 'published_date']
    search_fields = ['title', 'content', 'tldr']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['read_time', 'content_length']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'subtitle', 'slug', 'content_type', 'author')
        }),
        ('Content', {
            'fields': ('hero_image', 'tldr', 'content')
        }),
        ('Metadata', {
            'fields': ('tags', 'read_time', 'content_length'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'title', 'initials']

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}