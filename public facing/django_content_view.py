{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 # views.py\
from django.shortcuts import render, get_object_or_404\
from django.views.generic import ListView, DetailView\
from .models import Article\
\
class ArticleDetailView(DetailView):\
    model = Article\
    template_name = 'insights/article.html'\
    context_object_name = 'article'\
    \
    def get_context_data(self, **kwargs):\
        context = super().get_context_data(**kwargs)\
        \
        # Get related articles\
        context['related_articles'] = Article.objects.filter(\
            tags__in=self.object.tags.all()\
        ).exclude(id=self.object.id).distinct()[:4]\
        \
        # Add content class for template\
        context['content_class'] = f'content-\{self.object.content_length\}'\
        \
        return context\
\
class ArticleListView(ListView):\
    model = Article\
    template_name = 'insights/article_list.html'\
    context_object_name = 'articles'\
    paginate_by = 20\
    \
    def get_queryset(self):\
        queryset = Article.objects.all()\
        \
        # Filter by type if provided\
        content_type = self.request.GET.get('type')\
        if content_type:\
            queryset = queryset.filter(content_type=content_type)\
            \
        # Filter by length if provided\
        length = self.request.GET.get('length')\
        if length:\
            queryset = queryset.filter(content_length=length)\
            \
        return queryset.order_by('-published_date')}