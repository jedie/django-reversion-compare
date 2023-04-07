from django import template
from django.urls import reverse
from django.utils.safestring import mark_safe

from reversion_compare_project.models import SimpleModel


register = template.Library()


@register.simple_tag
def demo_links():
    pks = SimpleModel.objects.values_list('pk', flat=True)[:3]
    links = []
    for pk in pks:
        url = reverse('test_view', kwargs={'pk': pk})
        links.append(f'<li><a href="{url}">{url}</a></li>')
    links = ''.join(links)
    return mark_safe(f'<ul>{links}</ul>')
