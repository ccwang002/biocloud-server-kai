from functools import wraps
from django.http import HttpResponseBadRequest


def ajax_required(f):
    """AJAX request required decorator

    To apply it to a view that only accepts AJAX operations::

        @ajax_required
        def my_view(request):
            ....

    Ref: https://djangosnippets.org/snippets/771/
    """
    @wraps(f)
    def wrap(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest()
        return f(request, *args, **kwargs)
    return wrap
