from Field import Int32Field, ReaderField, ArrayField
from Reader import Reader
from Readers.Int32KVP import Int32KVP


class MechaLab(Reader):
    version = Int32Field()
    itemPoints = ArrayField(lambda: ReaderField(Int32KVP))
