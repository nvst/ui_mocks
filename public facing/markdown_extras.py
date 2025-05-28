# templatetags/markdown_extras.py
from django import template
from django.template.defaultfilters import stringfilter
import markdown

register = template.Library()

@register.filter
@stringfilter
def markdown(value):
    return markdown.markdown(value, extensions=[
        'markdown.extensions.fenced_code',
        'markdown.extensions.codehilite',
        'markdown.extensions.tables',
        'markdown.extensions.toc',
        'markdown.extensions.footnotes',
        'markdown.extensions.attr_list',
    ])