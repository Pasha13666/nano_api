import threading
from collections import deque


class FieldBase:
    __na_allowed_encodings__ = ('json', 'multipart')

    def __na_on_class_init__(self, cls, kwargs, field_name):
        pass

    def __na_on_instance_init__(self, cls, args, kwargs):
        pass

    def __na_data_to_object__(self, cls, data):
        pass

    def __na_object_to_data__(self, obj, use_id):
        pass


class InputType:
    __na_allowed_encodings__ = ('json', 'multipart')

    def __na_to_api__(self, use_id):
        pass


class OutputType:
    @classmethod
    def __na_from_api__(cls, data):
        pass


class ObjectBase(InputType, OutputType):
    __na_allowed_encodings__ = ('json', 'multipart')


g_context = threading.local()
g_context.local = deque()
