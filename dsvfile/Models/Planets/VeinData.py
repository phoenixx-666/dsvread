from ...Fields import UInt8Field, Int16Field
from ...Fields.Enums import EVeinType16
from . import Model, Int32Field, FloatField


"""
VeinData
{
    uint8 version = 0
    int32 id
    int16 EVeinType (see above)
    int16 modelIndex
    int16 groupIndex
    int32 amount
    int32 productId
    float pos_x
    float pos_y
    float pos_z
    int32 minerCount
    int32 minerId0
    int32 minerId1
    int32 minerId2
    int32 minerId3
}
"""


class VeinData(Model):
    version = UInt8Field()
    id = Int32Field()
    veinType = EVeinType16()
    modelIndex = Int16Field()
    groupIndex = Int16Field()
    amount = Int32Field()
    productId = Int32Field()
    pos_x = FloatField()
    pos_y = FloatField()
    pos_z = FloatField()
    minerCount = Int32Field()
    minerId0 = Int32Field()
    minerId1 = Int32Field()
    minerId2 = Int32Field()
    minerId3 = Int32Field()