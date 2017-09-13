from .abstract import ObjectBase
from .object import FieldBase, ObjectMeta
from .tools import get_type_and_depth, compile_type_wrapper, is_json_type, has_id_field


class DataField(FieldBase):
    def __init__(self, type_=None, optional=False, one_of=None, default=None, real_name=None):
        type_, depth = get_type_and_depth(type_)
        self._code = compile_type_wrapper(depth, 'data', 'type(')

        self.type = type_
        self.optional = optional
        self.one_of = one_of
        self.default = default
        self.name = real_name
        self.__na_allowed_encodings__ = ('json', ) if depth or issubclass(type_, (list, dict))\
            else ('json', 'multipart')

        if not is_json_type(type_):
            raise TypeError("DataField`s type must be basic type")

    def __na_on_class_init__(self, cls, kwargs, field_name):
        if self.name is None:
            self.name = field_name

    def __na_on_instance_init__(self, cls, args, kwargs):
        if self.default is not None:
            return self.default
        if self.name in kwargs:
            return kwargs[self.name]
        if not self.optional:
            raise KeyError("Missing required '%s' in %s init" % (self.name, cls.__name__))
        return None

    def __na_data_to_object__(self, cls, data):
        value = data.get(self.name)
        if value is None:
            if self.default is not None:
                value = self.default
            elif not self.optional:
                raise KeyError("Missing required '%s' in %s init" % (self.name, cls.__name__))
            else:
                return None

        value = eval(self._code, {
            'data': value,
            'type': self._data_to_object
        })

        if self.one_of is not None and value not in self.one_of:
            raise ValueError("%s must be one of %s in %s init" % (self.name, self.one_of, cls.__name__))
        return value

    def __na_object_to_data__(self, obj, use_id):
        obj = getattr(obj, self.name, None)
        if not self.optional and obj is None:
            raise KeyError("Missing required '%s' in %s.to_api()" % (self.name, type(obj).__name__))

        if self.one_of is not None and obj not in self.one_of:
            raise ValueError("%s must be one of %s in %s.to_api()" % (self.name, self.one_of, type(obj).__name__))

        return eval(self._code, {
            'data': obj,
            'type': self._object_to_data
        })

    def _data_to_object(self, data):
        if isinstance(data, self.type):
            return data
        raise TypeError("Cannot convert %s to json" % type(data).__name__)

    def _object_to_data(self, obj):
        if isinstance(obj, self.type):
            return obj
        raise TypeError("Cannot convert %s to json" % type(obj).__name__)


class ObjectField(FieldBase):
    def __init__(self, type_=None, optional=False, one_of=None, default=None, real_name=None):
        type_, depth = get_type_and_depth(type_)
        self._code = compile_type_wrapper(depth, 'data', 'type(use_id, ')

        self.type = type_
        self.optional = optional
        self.one_of = one_of
        self.default = default
        self.name = real_name
        self._module = None

        if not isinstance(type_, str) and not has_id_field(type_):
            self.__na_allowed_encodings__ = tuple((i for i in type_.__na_allowed_encodings__ if i != 'multipart'))

        if not isinstance(type_, str) and not issubclass(type_, ObjectBase):
            raise TypeError("ObjectField`s type must be Object")

    def __na_on_class_init__(self, cls, kwargs, field_name):
        if self.name is None:
            self.name = field_name
        self._module = cls.__module__

    def __na_on_instance_init__(self, cls, args, kwargs):
        if self.default is not None:
            return self.default
        if self.name in kwargs:
            return kwargs[self.name]
        if not self.optional:
            raise KeyError("Missing required '%s' in %s init" % (self.name, cls.__name__))
        return None

    def __na_data_to_object__(self, cls, data):
        value = data.get(self.name)
        if value is None:
            if self.default is not None:
                value = self.default
            elif not self.optional:
                raise KeyError("Missing required '%s' in %s init" % (self.name, cls.__name__))
            else:
                return None

        value = eval(self._code, {
            'data': value,
            'type': self._data_to_object,
            'use_id': None,
        })

        if self.one_of is not None and value not in self.one_of:
            raise ValueError("%s must be one of %s in %s init" % (self.name, self.one_of, cls.__name__))
        return value

    def __na_object_to_data__(self, obj, use_id):
        obj = getattr(obj, self.name, None)
        if not self.optional and obj is None:
            raise KeyError("Missing required '%s' in %s.to_api()" % (self.name, type(obj).__name__))

        if self.one_of is not None and obj not in self.one_of:
            raise ValueError("%s must be one of %s in %s.to_api()" % (self.name, self.one_of, type(obj).__name__))

        return eval(self._code, {
            'data': obj,
            'type': self._object_to_data,
            'use_id': use_id,
        })

    def _data_to_object(self, _, data):
        if isinstance(self.type, str):
            self.type = ObjectMeta.by_name(self._module, self.type)
            if not has_id_field(self.type):
                self.__na_allowed_encodings__ = tuple((i for i in self.type.__na_allowed_encodings__
                                                       if i != 'multipart'))

        return self.type.__na_from_api__(data)

    def _object_to_data(self, use_id, obj):
        if isinstance(self.type, str):
            self.type = ObjectMeta.by_name(self._module, self.type)
            if not has_id_field(self.type):
                self.__na_allowed_encodings__ = tuple((i for i in self.type.__na_allowed_encodings__
                                                       if i != 'multipart'))

        if isinstance(obj, self.type):
            return obj.__na_to_api__(use_id)
        raise TypeError("Cannot convert %s to json" % type(obj).__name__)


class IdField(DataField):
    __na_id__ = True

    def __init__(self, type_=None, default=None, real_name=None):
        super().__init__(type_, False, None, default, real_name)
