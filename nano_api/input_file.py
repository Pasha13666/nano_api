from .abstract import InputType
import io


class InputFile(InputType):
    __na_allowed_encodings__ = ('multipart',)

    def __init__(self, data):
        if isinstance(data, str):
            self._data = open(data, 'rb')
        elif isinstance(data, (bytes, bytearray)):
            self._data = io.BytesIO(data)
        else:
            self._data = data

    def __na_to_api__(self, use_id):
        return self._data
