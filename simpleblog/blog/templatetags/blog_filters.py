from urllib.parse import urlencode

from django.template.defaultfilters import register


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.simple_tag(takes_context=True)
def build_url(context, ordering=None):
    params = {key: value for key, value in context.request.GET.items()}
    if ordering is not None:
        if ordering != params.get('ordering'):
            params['ordering'] = ordering
        else:
            params['ordering'] = '-' + ordering
    return '{}?{}'.format(context.request.path, urlencode(params))
