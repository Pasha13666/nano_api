import inspect
import types

from .abstract import OutputType, InputType, g_context
from .object import ObjectMeta
from .tools import build_args_kwargs, to_camel_case, get_type_and_depth, compile_type_wrapper


class ApiFunction:
    def __new__(cls, *args, **kwargs):
        if not args or not isinstance(args[0], types.FunctionType):
            return lambda x: ApiFunction(x, *args, **kwargs)
        return super().__new__(cls)

    def __init__(self, fn, name=None):
        if name is None:
            name = fn.__name__

        self._fn = fn
        self.name = name
        self.method_name = to_camel_case(name)
        self._info = inspect.signature(fn)
        self._defaults = {i.name: i.default for i in self._info.parameters.values()}
        self.return_type, depth = get_type_and_depth(self._info.return_annotation)
        self._code = compile_type_wrapper(depth, 'i_end', 'rr(')

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return types.MethodType(self, instance)

    def _exec(self, kwargs, obj):
        method = self.method_name
        if isinstance(obj, tuple) and len(obj) == 2:
            if obj[0] == 'append':
                kwargs.update(obj[1])

            else:
                method = obj[0]
                kwargs = obj[1]
        elif isinstance(obj, dict):
            kwargs = obj

        args = {}
        allowed = set(InputType.__na_allowed_encodings__)
        for k, v in kwargs:
            if v is None:
                continue

            if isinstance(v, InputType):
                args[k] = v.__na_to_api__(True)
                allowed &= set(v.__na_allowed_encodings__)

            elif isinstance(v, (str, int, float, bool, dict, list)):  # ???
                args[k] = v

            else:
                raise TypeError('Argument %s of %s must be InputType or base type, not %s' % (k, self.name,
                                                                                              type(v).__name__))

        return g_context.local[-1].execute(tuple(allowed), method, args)

    def __call__(self, *args, **kwargs):
        args, kwargs = build_args_kwargs(args, kwargs, self._info, self._defaults)
        gen = self._fn(*args, **kwargs)

        if isinstance(gen, types.GeneratorType):
            try:
                res = gen.send(None)
            except StopIteration as e:
                res = e.value

            res = self._exec(kwargs, res)
            try:
                res = gen.send(res)
            except StopIteration as e:
                res = e.value

        else:
            res = self._exec(kwargs, gen)

        if isinstance(self.return_type, str):
            self.return_type = ObjectMeta.by_name(self._fn.__module__, self.return_type)
        if self.return_type is None:
            return res

        return eval(self._code, {
            'i_end': res,
            'rr': self.return_type.__na_from_api__ if issubclass(self.return_type, OutputType) else self.return_type
        })
