import json

from django.http import HttpResponse
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder


FORMAT_TYPES = {
    'application/json': lambda response: json.dumps(response, cls=DjangoJSONEncoder),
    'text/json':        lambda response: json.dumps(response, cls=DjangoJSONEncoder),
}


try:
    from functools import wraps
except ImportError:
    def wraps(wrapped, assigned=('__module__', '__name__', '__doc__'),
              updated=('__dict__',)):
        def inner(wrapper):
            for attr in assigned:
                setattr(wrapper, attr, getattr(wrapped, attr))
            for attr in updated:
                getattr(wrapper, attr).update(getattr(wrapped, attr, {}))
            return wrapper
        return inner

def ajax_request(func):
    """
    Based on https://github.com/skorokithakis/django-annoying
    Not support YAML, but work with functions in Class Based views

    If view returned serializable dict, returns respons in JSON format

    example:

        @ajax_request
        def my_view(request):
            news = News.objects.all()
            news_titles = [entry.title for entry in news]
            return {'news_titles': news_titles}
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        format_type = 'application/json'
        response = func(*args, **kwargs)
        if not isinstance(response, HttpResponse):
            if hasattr(settings, 'FORMAT_TYPES'):
                format_type_handler = settings.FORMAT_TYPES[format_type]
                if hasattr(format_type_handler, '__call__'):
                    data = format_type_handler(response)
                elif isinstance(format_type_handler, basestring):
                    mod_name, func_name = format_type_handler.rsplit('.', 1)
                    module = __import__(mod_name, fromlist=[func_name])
                    function = getattr(module, func_name)
                    data = function(response)
            else:
                data = FORMAT_TYPES[format_type](response)
            response = HttpResponse(data, content_type=format_type)
            response['content-length'] = len(data)
        return response
    return wrapper
