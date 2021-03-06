from ...Fields import FloatField, DoubleField
from ...Fields.Enums import EItem
from . import Model, Int32Field


class ShipData(Model):
    version = Int32Field()
    stage = Int32Field()
    planetA = Int32Field()
    planetB = Int32Field()
    uPos_x = DoubleField()
    uPos_y = DoubleField()
    uPos_z = DoubleField()
    uVel_x = FloatField()
    uVel_y = FloatField()
    uVel_z = FloatField()
    uSpeed = FloatField()
    warpState = FloatField()
    uRot_x = FloatField()
    uRot_y = FloatField()
    uRot_z = FloatField()
    uRot_w = FloatField()
    uAngularVel_x = FloatField()
    uAngularVel_y = FloatField()
    uAngularVel_z = FloatField()
    uAngularSpeed = FloatField()
    pPosTemp_x = DoubleField()
    pPosTemp_y = DoubleField()
    pPosTemp_z = DoubleField()
    pRotTemp_x = FloatField()
    pRotTemp_y = FloatField()
    pRotTemp_z = FloatField()
    pRotTemp_w = FloatField()
    otherGId = Int32Field()
    direction = Int32Field()
    t = FloatField()
    itemId = EItem()
    itemCount = Int32Field()
    gene = Int32Field()
    shipIndex = Int32Field()
    warperCnt = Int32Field()
