from collections.abc import Mapping
from struct import unpack, pack


__all__ = ['IncorrectHeaderException', 'Field', 'FieldMap', 'FixedHeaderField', 'UInt8Field', 'Int16Field',
           'Int32Field', 'Int64Field', 'UInt32Field', 'UInt64Field', 'FloatField', 'DoubleField', 'EnumField',
           'BoolField', 'StringField', 'ByteStringField', 'ArrayField', 'ModelField', 'ConditionalField',
           'ConditionalBlockStart', 'ConditionalBlockEnd']


class IncorrectHeaderException(IOError):
    pass


class Field(object):
    __field_counter = 0
    type_name = NotImplemented
    hidden = False
    store_value = write_value = True
    always_read = False

    def __init__(self):
        self.initialization_order = Field.__field_counter
        Field.__field_counter += 1

    def read(self, input_stream, model):
        raise NotImplementedError

    def write(self, value, output_stream, model):
        raise NotImplementedError


class FieldMap(Mapping):
    _dict = {}

    def __init__(self, dict):
        self._dict = dict

    def __getitem__(self, item):
        return self._dict.__getitem__(item)

    def __iter__(self):
        return self._dict.__iter__()

    def __len__(self):
        return len(self._dict)

    def __getattribute__(self, name):
        if name != '_dict' and name in self._dict:
            return self._dict[name]
        return super().__getattribute__(name)

    def __setattr__(self, name, value):
        if name != '_dict' and name in self._dict:
            raise AttributeError("can't set attribute")
        super().__setattr__(name, value)


class FixedHeaderField(Field):
    type_name = 'header'

    def __init__(self, header, encoding='ISO 8859-1'):
        self.header = header
        self.encoding = encoding
        super().__init__()

    def read(self, input_stream, model):
        if input_stream.read(len(self.header)).decode(self.encoding) != self.header:
            raise IncorrectHeaderException
        return self.header

    def write(self, value, output_stream, model):
        output_stream.write(self.header.encode(self.encoding))


class FixedSizeNumberField(Field):
    size = None
    fmt = None

    def read(self, input_stream, model):
        return unpack(self.fmt, input_stream.read(self.size))[0]

    def write(self, value, output_stream, model):
        output_stream.write(pack(self.fmt, value))


class UInt8Field(FixedSizeNumberField):
    type_name = 'uint8'
    size = 1
    fmt = '<B'


class Int16Field(FixedSizeNumberField):
    type_name = 'int16'
    size = 2
    fmt = '<h'


class Int32Field(FixedSizeNumberField):
    type_name = 'int32'
    size = 4
    fmt = '<l'


class Int64Field(FixedSizeNumberField):
    type_name = 'int64'
    size = 8
    fmt = '<q'


class UInt32Field(FixedSizeNumberField):
    type_name = 'uint32'
    size = 4
    fmt = '<L'


class UInt64Field(FixedSizeNumberField):
    type_name = 'uint64'
    size = 8
    fmt = '<Q'


class FloatField(FixedSizeNumberField):
    type_name = 'float'
    size = 4
    fmt = '<f'


class DoubleField(FixedSizeNumberField):
    type_name = 'double'
    size = 8
    fmt = '<d'


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

    def read(self, input_stream, model):
        return self.field.read(input_stream, model)

    def write(self, value, output_stream, model):
        self.field.write(value, output_stream, model)


class BoolField(EnumField):
    enum_values = ('False', 'True')
    base_type = UInt8Field


class StringField(Field):
    type_name = 'string'

    def __init__(self, encoding='utf-8'):
        self.encoding = encoding
        super().__init__()

    def read(self, input_stream, model):
        length = input_stream.read(1)[0]
        return input_stream.read(length).decode(self.encoding)

    def write(self, value, output_stream, model):
        value = value.encode(self.encoding)
        output_stream.write(pack('B', len(value)) + value)


class ByteStringField(Field):
    type_name = 'bytestring'

    def __init__(self, format='HEX', length_field=Int32Field, length_func=None):
        self.format = format
        if isinstance(length_field, str):
            self.length_field = length_field
        elif isinstance(length_field, type):
            self.length_field = length_field()
        else:
            self.length_field = length_field
        self.length_func = length_func
        super().__init__()

    def read(self, input_stream, model):
        if isinstance(self.length_field, str):
            length = model.__getattribute__(self.length_field)
            if self.length_func is not None:
                length = self.length_func(length)
        else:
            length = self.length_field.read(input_stream, model)
        return input_stream.read(length)

    def write(self, value, output_stream, model):
        if isinstance(self.length_field, str):
            length = model.__getattribute__(self.length_field)
            if self.length_func is not None:
                length = self.length_func(length)
            if length != len(value):
                raise ValueError('Value length does not match one specified by {0}'.format(self.length_field))
        else:
            length = len(value)
            self.length_field.write(length, output_stream, model)
        output_stream.write(value)


class ArrayField(Field):
    type_name = 'array'

    def __init__(self, item_field, length_field=Int32Field, length_func=None, index_enum=None):
        self.item_field = item_field() if isinstance(item_field, type) else item_field
        if isinstance(length_field, str):
            self.length_field = length_field
        elif isinstance(length_field, type):
            self.length_field = length_field()
        else:
            self.length_field = length_field
        self.length_func = length_func
        self.index_enum = index_enum() if isinstance(index_enum, type) else index_enum
        super().__init__()

    def read(self, input_stream, model):
        if isinstance(self.length_field, str):
            length = model.__getattribute__(self.length_field)
            if self.length_func is not None:
                length = self.length_func(length)
        else:
            length = self.length_field.read(input_stream, model)
        return [self.item_field.read(input_stream, model) for i in range(length)]

    def write(self, value, output_stream, model):
        if isinstance(self.length_field, str):
            length = model.__getattribute__(self.length_field)
            if self.length_func is not None:
                length = self.length_func(length)
            if length != len(value):
                raise ValueError('Value length does not match one specified by {0}'.format(self.length_field))
        else:
            length = len(value)
            self.length_field.write(length, output_stream, model)
        for item in value:
            self.item_field.write(item, output_stream, model)


class ModelField(Field):
    type_name = 'struct'

    def __init__(self, model_class):
        self.model_class = model_class
        super().__init__()

    def read(self, input_stream, model):
        local_model = self.model_class()
        local_model.read(input_stream)
        return local_model

    def write(self, value, output_stream, model):
        if value:
            value.write(output_stream)


class ConditionMixin(object):
    def _check_condition(self, model):
        if self.condition_func is None:
            return True
        args = [model.__getattribute__(field) for field in self.arg_fields]
        return self.condition_func(*args)


class ConditionalField(Field, ConditionMixin):
    def __init__(self, field, arg_fields=[], condition_func=None):
        self.field = field() if isinstance(field, type) else field
        self.arg_fields = arg_fields if isinstance(arg_fields, (list, tuple)) else [arg_fields]
        self.condition_func = condition_func
        super().__init__()

    def read(self, input_stream, model):
        if self._check_condition(model):
            return self.field.read(input_stream, model)
        return None

    def write(self, value, output_stream, model):
        if self._check_condition(model):
            self.field.write(value, output_stream, model)


class ConditionalBlockStart(Field, ConditionMixin):
    hidden = True
    store_value = write_value = False
    always_read = True

    def __init__(self, arg_fields=[], condition_func=None):
        self.arg_fields = arg_fields if isinstance(arg_fields, (list, tuple)) else [arg_fields]
        self.condition_func = condition_func
        super().__init__()

    def read(self, input_stream, model):
        return self._check_condition(model)

    def write(self, value, output_stream, model):
        pass


class ConditionalBlockEnd(Field):
    hidden = True
    store_value = write_value = False
    always_read = True

    def read(self, input_stream, model):
        return None

    def write(self, value, output_stream, model):
        pass
