import numpy as np


class IncorrectHeaderException(IOError):
    pass


class Field(object):
    field_counter = 0
    type_name = NotImplemented
    hidden = False
    store_value = True
    always_read = False

    def __init__(self):
        self.order = Field.field_counter
        Field.field_counter += 1

    def read(self, input_stream, reader):
        raise NotImplementedError


class FixedHeaderField(Field):
    type_name = 'header'

    def __init__(self, header):
        self.header = header
        super().__init__()

    def read(self, input_stream, reader):
        if input_stream.read(len(self.header)).decode('ISO 8859-1') != self.header:
            raise IncorrectHeaderException
        return self.header


class FixedSizeNumberField(Field):
    size = None
    dtype = None

    def read(self, input_stream, reader):
        cls = self.__class__
        return np.frombuffer(input_stream.read(cls.size), dtype=cls.dtype)[0]


class UInt8Field(FixedSizeNumberField):
    type_name = 'uint8'
    size = 1
    dtype = np.uint8


class Int16Field(FixedSizeNumberField):
    type_name = 'int16'
    size = 2
    dtype = np.int16


class Int32Field(FixedSizeNumberField):
    type_name = 'int32'
    size = 4
    dtype = np.int32


class Int64Field(FixedSizeNumberField):
    type_name = 'int64'
    size = 8
    dtype = np.int64


class UInt32Field(FixedSizeNumberField):
    type_name = 'uint32'
    size = 4
    dtype = np.uint32


class UInt64Field(FixedSizeNumberField):
    type_name = 'uint64'
    size = 8
    dtype = np.uint64


class FloatField(FixedSizeNumberField):
    type_name = 'float'
    size = 4
    dtype = np.float32


class DoubleField(FixedSizeNumberField):
    type_name = 'double'
    size = 8
    dtype = np.double


class EnumField(Field):
    type_name = 'enum'
    enum_values = {}
    base_type = Int32Field

    def __init__(self):
        self.field = self.base_type()
        if isinstance(self.enum_values, dict):
            self.enum_values = self.enum_values
        elif isinstance(self.enum_values, (tuple, list)):
            self.enum_values = {i: v for i, v in enumerate(self.enum_values)}
        else:
            raise TypeError()
        super().__init__()

    def read(self, input_stream, reader):
        return self.field.read(input_stream, reader)


class BoolField(EnumField):
    enum_values = ('False', 'True')
    base_type = UInt8Field


class StringField(Field):
    type_name = 'string'

    def __init__(self, encoding='utf-8'):
        self.encoding = encoding
        super().__init__()

    def read(self, input_stream, reader):
        length = input_stream.read(1)[0]
        return input_stream.read(length).decode('utf-8')


class ByteStringField(Field):
    type_name = 'bytestring'

    def __init__(self, format='HEX', length_field=Int32Field, length_function=None):
        self.format = format
        if isinstance(length_field, str):
            self.length_field = length_field
        else:
            self.length_field = length_field()
        self.length_function = length_function
        super().__init__()

    def read(self, input_stream, reader):
        if isinstance(self.length_field, str):
            length = reader.__getattribute__(self.length_field)
        else:
            length = self.length_field.read(input_stream, reader)
        if self.length_function is not None:
            length = self.length_function(length)
        return input_stream.read(length)


class ArrayField(Field):
    type_name = 'array'

    def __init__(self, item_field, length_field=Int32Field, length_function=None):
        self.item_field = item_field()
        if isinstance(length_field, str):
            self.length_field = length_field
        else:
            self.length_field = length_field()
        self.length_function = length_function
        super().__init__()

    def read(self, input_stream, reader):
        if isinstance(self.length_field, str):
            length = reader.__getattribute__(self.length_field)
        else:
            length = self.length_field.read(input_stream, reader)
        if self.length_function is not None:
            length = self.length_function(length)
        return [self.item_field.read(input_stream, reader) for i in range(length)]


class ReaderField(Field):
    type_name = 'struct'

    def __init__(self, reader_class):
        self.reader_class = reader_class
        super().__init__()

    def read(self, input_stream, reader):
        local_reader = self.reader_class()
        local_reader.read(input_stream)
        return local_reader


class ConditionMixin(object):
    def _check_condition(self, reader):
        if self.condition_func is None:
            return True
        args = [reader.field_values[field] for field in self.arg_fields]
        return self.condition_func(*args)


class ConditionalField(Field, ConditionMixin):
    def __init__(self, field, arg_fields=[], condition_func=None):
        self.field = field()
        self.arg_fields = arg_fields if isinstance(arg_fields, (list, tuple)) else [arg_fields]
        self.condition_func = condition_func
        super().__init__()

    def read(self, input_stream, reader):
        if self._check_condition(reader):
            return self.field.read(input_stream, reader)
        return None


class ConditionalBlockStart(Field, ConditionMixin):
    hidden = True
    store_value = False
    always_read = True

    def __init__(self, arg_fields=[], condition_func=None):
        self.arg_fields = arg_fields if isinstance(arg_fields, (list, tuple)) else [arg_fields]
        self.condition_func = condition_func
        super().__init__()

    def read(self, input_stream, reader):
        return self._check_condition(reader)


class ConditionalBlockEnd(Field):
    hidden = True
    store_value = False
    always_read = True

    def read(self, input_stream, reader):
        return None
