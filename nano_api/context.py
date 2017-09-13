import io

from nano_api.abstract import g_context

try:
    import requests as _rq
except ImportError:
    _rq = None


class ApiContext:
    def __enter__(self):
        g_context.local.append(self)

    def __exit__(self, exc_type, exc_val, exc_tb):
        g_context.local.pop()

    def execute(self, allowed, method, args):
        raise NotImplementedError("ApiContext is abstract, you must override method `execute`")


class RequestsContext(ApiContext):
    def __init__(self, url, request=None, raise_for_status=False, path=()):
        self._url = url
        self._rfs = raise_for_status
        self._p = path

        if callable(request):
            self._rq = request
        elif _rq is not None:
            self._rq = _rq.request
        else:
            raise RuntimeError("Module `requests` is not installed so you must pass `request` argument")

    def execute(self, allowed, method, args):
        if 'json' in allowed:
            r = self._rq('POST', self._url.format(method=method), json=args)
        elif 'multipart' in allowed:
            r = self._rq('POST', self._url.format(method=method),
                         data={k: v for k, v in args.items() if not isinstance(v, io.IOBase)},
                         files={k: v for k, v in args.items() if isinstance(v, io.IOBase)})
        else:
            raise RuntimeError("Cant handle request %s (allowed %s)" % (method, allowed))

        if self._rfs:
            r.raise_for_status()

        r = r.json()
        for i in self._p:
            r = r[i]
        return r
