import inspect
import typing

BASE_JSON_TYPES = (str, int, float, dict, list, bool)


def to_snake_case(s):
    return "".join((('_' + i) if i.isupper() else i for i in s)).lower()


def camel_case_helper(s):
    nu = False
    for i in s:
        if nu:
            yield i.upper()
            nu = False
        elif i == '_':
            nu = True
        else:
            yield i


def to_camel_case(s):
    return ''.join(camel_case_helper(s))


def is_json_object(o):
    return o is None or isinstance(o, BASE_JSON_TYPES)


def is_json_type(o):
    return issubclass(o, BASE_JSON_TYPES)


def is_mpd_object(o):
    return o is not None and ((isinstance(o, tuple) and len(o) == 2 and isinstance(o[0], str)
                               and isinstance(o[1], bytes)) or isinstance(o, str))


def get_type_and_depth(type_, storage=None):
    rtd = 0
    while isinstance(type_, typing.GenericMeta) and type_.__extra__ == list:
        type_ = type_.__args__[0]
        rtd += 1

    if storage is not None and isinstance(type_, str):
        type_ = storage.get(type_)

    return type_, rtd


def get_type_wrapper(depth, var_name, func_name):
    tm = '[%s for %s in %%s]'
    r = '%s%%s)' % func_name
    for i in range(depth):
        i = 'i%s' % i
        r = tm % (r % i, i)
    return r % var_name


def compile_type_wrapper(depth, var_name, func_name):
    return compile(get_type_wrapper(depth, var_name, func_name), '<generated>', 'eval')


def build_args_kwargs(args, kwargs, info, defaults):
    b = info.bind(*args, **kwargs)
    args = []

    for name, v in info.parameters.items():
        if v.kind != inspect.Parameter.POSITIONAL_ONLY:
            break
        args.append((name, b.arguments[name]))

    while args and args[-1][1] == defaults[args[-1][0]]:
        args.pop()

    return tuple((v for k, v in args)), {name: v for name, v in b.arguments.items() if v != defaults[name]}


def has_id_field(o):
    for i in o.__na_fields__.values():
        if getattr(i, '__na_id__', False):
            return True
    return False
