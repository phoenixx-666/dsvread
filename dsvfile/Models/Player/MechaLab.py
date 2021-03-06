from ...Fields import ArrayField
from . import Model, Int32Field, ModelField
from .. import Int32KVP


class MechaLab(Model):
    version = Int32Field()
    itemPoints = ArrayField(ModelField(Int32KVP))
