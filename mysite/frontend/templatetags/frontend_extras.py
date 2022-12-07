from django import template
register = template.Library()
from urllib.parse import urlparse

@register.filter(name='spliturl')
def spliturl(url):
    o = urlparse(url)
    path = o.path
    return path.split('/')

@register.filter(name='index')
def index(indexable, i):
    print('findex', indexable)
    if len(indexable) < i:
        return ''
    return indexable[i]