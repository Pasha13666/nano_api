from .abstract import FieldBase, ObjectBase, InputType


class ObjectMeta(type):
    __na_fields__ = {}
    __na_object_storage__ = {}

    def __new__(mcs, name, bases, dct: dict, allowed_encodings=None, **kwargs):
        if kwargs.get('na_ignored', False):
            return super().__new__(mcs, name, bases, dct)

        fields = {k: v for k, v in dct.items() if isinstance(v, FieldBase)}
        if allowed_encodings is None:
            allowed_encodings = set(InputType.__na_allowed_encodings__)
            for i in fields.values():
                allowed_encodings &= set(i.__na_allowed_encodings__)

            allowed_encodings = tuple(allowed_encodings)

        dct['__na_allowed_encodings__'] = allowed_encodings
        dct['__na_fields__'] = fields
        obj = super().__new__(mcs, name, bases, dct)
        mcs.__na_object_storage__[(dct.get('__module__'), name)] = obj

        for key, value in dct.items():
            if isinstance(value, FieldBase):
                value.__na_on_class_init__(obj, kwargs, key)

        return obj

    def __call__(cls, *args, **kwargs):
        obj = cls.__new__(cls)

        for k, v in cls.__na_fields__.items():
            setattr(obj, k, v.__na_on_instance_init__(cls, args, kwargs))

        cls.__init__(obj, *args, **kwargs)
        return obj

    @classmethod
    def __prepare__(mcs, name, bases, **kwargs):
        return {}

    @classmethod
    def by_name(mcs, mod, name):
        return mcs.__na_object_storage__.get((mod, name))


class Object(ObjectBase, metaclass=ObjectMeta, na_ignored=True):
    def __na_to_api__(self, use_id):
        data = {}

        for k, v in type(self).__na_fields__.items():
            if use_id and hasattr(v, '__na_id__'):
                return v.__na_object_to_data__(self, use_id)
            data[k] = v.__na_object_to_data__(self, use_id)

        return data

    @classmethod
    def __na_from_api__(cls, data):
        obj = cls.__new__(cls)
        for k, v in cls.__na_fields__.items():
            setattr(obj, k, v.__na_data_to_object__(cls, data))

        o = getattr(obj, '__na_init_data__', None)
        if o is not None:
            o(obj, data)

        return obj
