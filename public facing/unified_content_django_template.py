{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 # models.py\
from django.db import models\
from django.utils.html import strip_tags\
import readtime\
\
class Article(models.Model):\
    CONTENT_TYPES = [\
        ('tutorial', 'Tutorial'),\
        ('analysis', 'Analysis'),\
        ('reference', 'Reference'),\
        ('news', 'News'),\
    ]\
    \
    # Basic fields\
    title = models.CharField(max_length=200)\
    subtitle = models.CharField(max_length=300, blank=True)\
    slug = models.SlugField(unique=True)\
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)\
    \
    # Content\
    hero_image = models.ImageField(upload_to='articles/heroes/', blank=True)\
    tldr = models.TextField(help_text="TL;DR summary")\
    content = models.TextField(help_text="Main article content (Markdown + HTML)")\
    \
    # Metadata\
    published_date = models.DateTimeField(auto_now_add=True)\
    modified_date = models.DateTimeField(auto_now=True)\
    author = models.ForeignKey('Author', on_delete=models.CASCADE)\
    tags = models.ManyToManyField('Tag')\
    \
    # Auto-calculated\
    read_time = models.IntegerField(editable=False, default=0)\
    content_length = models.CharField(max_length=20, editable=False, default='standard')\
    \
    def save(self, *args, **kwargs):\
        # Calculate read time\
        plain_text = strip_tags(self.content)\
        self.read_time = readtime.of_text(plain_text).minutes\
        \
        # Determine content length class\
        if self.read_time <= 3:\
            self.content_length = 'quick'\
        elif self.read_time <= 10:\
            self.content_length = 'standard'\
        else:\
            self.content_length = 'deep'\
            \
        super().save(*args, **kwargs)\
    \
    def get_absolute_url(self):\
        return f"/insights/\{self.slug\}"\
\
class Author(models.Model):\
    name = models.CharField(max_length=100)\
    title = models.CharField(max_length=100)\
    bio = models.TextField(blank=True)\
    initials = models.CharField(max_length=3)\
    \
class Tag(models.Model):\
    name = models.CharField(max_length=50)\
    slug = models.SlugField(unique=True)}