{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\margl1440\margr1440\vieww11520\viewh8400\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 \{# templates/insights/article.html #\}\
\{% extends "base.html" %\}\
\{% load markdown_extras %\}\
\
\{% block body_class %\}\{\{ content_class \}\}\{% endblock %\}\
\
\{% block content %\}\
<!-- Breadcrumb -->\
<div class="breadcrumb">\
    <a href="/">Home</a>\
    <span>/</span>\
    <a href="\{% url 'article_list' %\}">Insights</a>\
    <span>/</span>\
    \{\{ article.get_content_type_display \}\}\
</div>\
\
<!-- Hero Section (conditional) -->\
\{% if article.hero_image %\}\
<div class="hero">\
    <img src="\{\{ article.hero_image.url \}\}" alt="\{\{ article.title \}\}" class="hero-image">\
    <div class="hero-overlay">\
        <div class="hero-content">\
            <h1>\{\{ article.title \}\}</h1>\
            \{% if article.subtitle %\}\
            <p class="subtitle">\{\{ article.subtitle \}\}</p>\
            \{% endif %\}\
        </div>\
    </div>\
</div>\
\{% else %\}\
<!-- Article Header (when no hero) -->\
<div class="article-header">\
    <div class="article-header-content">\
        <div class="article-meta">\
            <div class="meta-item">\
                <span class="content-type">\{\{ article.get_content_type_display|upper \}\}</span>\
            </div>\
            <div class="meta-item">\
                <span>\uc0\u55357 \u56534 </span>\
                <span>\{\{ article.read_time \}\} min read</span>\
            </div>\
            <div class="meta-item">\
                <span>\uc0\u55357 \u56517 </span>\
                <span>\{\{ article.published_date|date:"M d, Y" \}\}</span>\
            </div>\
            \{% if article.tags.exists %\}\
            <div class="meta-item">\
                <span>\uc0\u55356 \u57335 \u65039 </span>\
                <span>\{% for tag in article.tags.all %\}\{\{ tag.name \}\}\{% if not forloop.last %\}, \{% endif %\}\{% endfor %\}</span>\
            </div>\
            \{% endif %\}\
        </div>\
        <h1>\{\{ article.title \}\}</h1>\
    </div>\
</div>\
\{% endif %\}\
\
<!-- Main Layout -->\
<div class="main-layout">\
    <!-- Main Content -->\
    <article class="content">\
        <!-- TL;DR Box -->\
        <div class="tldr-box">\
            <h3>TL;DR</h3>\
            <p>\{\{ article.tldr \}\}</p>\
        </div>\
\
        <!-- Article Body -->\
        \{\{ article.content|markdown|safe \}\}\
    </article>\
\
    <!-- Sidebar (conditional based on content length) -->\
    \{% if article.content_length != 'quick' %\}\
    <aside class="sidebar">\
        <div class="sidebar-section">\
            <h3>About the Author</h3>\
            <div class="author-box">\
                <div class="author-avatar">\{\{ article.author.initials \}\}</div>\
                <div class="author-info">\
                    <h4>\{\{ article.author.name \}\}</h4>\
                    <p>\{\{ article.author.title \}\}</p>\
                </div>\
            </div>\
            \{% if article.author.bio %\}\
            <p style="margin-top: 12px; font-size: 12px; color: var(--ec-text-muted);">\
                \{\{ article.author.bio \}\}\
            </p>\
            \{% endif %\}\
        </div>\
        \
        \{% if related_articles %\}\
        <div class="sidebar-section">\
            <h3>Related Reading</h3>\
            <ul class="related-list">\
                \{% for related in related_articles %\}\
                <li>\
                    <a href="\{\{ related.get_absolute_url \}\}">\{\{ related.title \}\}</a>\
                    <div class="related-meta">\{\{ related.get_content_type_display \}\} \'95 \{\{ related.read_time \}\} min read</div>\
                </li>\
                \{% endfor %\}\
            </ul>\
        </div>\
        \{% endif %\}\
        \
        <div class="sidebar-section" style="background: var(--ec-purple); color: white;">\
            <h3 style="color: white;">Stay Informed</h3>\
            <p style="font-size: 12px; margin-bottom: 16px;">Get our latest research and insights delivered to your inbox.</p>\
            <form method="post" action="\{% url 'newsletter_signup' %\}" style="display: flex; flex-direction: column; gap: 8px;">\
                \{% csrf_token %\}\
                <input type="email" name="email" placeholder="Your email" required style="padding: 8px; border: none; font-family: inherit; font-size: 12px;">\
                <button type="submit" class="btn-primary" style="background: white; color: var(--ec-purple); width: 100%;">Subscribe</button>\
            </form>\
        </div>\
    </aside>\
    \{% endif %\}\
</div>\
\{% endblock %\}}