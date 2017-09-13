

class CachedProperty:
    def __init__(self, fn):
        self.fn = fn
        self.__doc__ = fn.__doc__
        self._cache = (None, False)

    def __get__(self, instance, owner):
        if instance is None:
            return self

        if not self._cache[1]:
            self._cache = (self.fn(instance), True)
        return self._cache[0]

    @property
    def __isabstractmethod__(self):
        return self.fn.__isabstractmethod__


class StaticProperty:
    def __init__(self, fn):
        self.fn = fn
        self.__doc__ = fn.__doc__

    def __get__(self, instance, owner):
        return self.fn()

    @property
    def __isabstractmethod__(self):
        return self.fn.__isabstractmethod__


class CachedStaticProperty:
    def __init__(self, fn):
        self.fn = fn
        self.__doc__ = fn.__doc__
        self._cache = (None, False)

    def __get__(self, instance, owner):
        if not self._cache[1]:
            self._cache = (self.fn(), True)
        return self._cache[0]

    @property
    def __isabstractmethod__(self):
        return self.fn.__isabstractmethod__
