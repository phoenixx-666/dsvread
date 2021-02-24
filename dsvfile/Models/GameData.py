from ..Fields import Int64Field, BoolField, ModelField, StringField, ArrayField, ConditionalField
from ..Func import ge
from . import Model, Int32Field
from .GameDesc import GameDesc
from .GamePrefsData import GamePrefsData
from .GameHistoryData import GameHistoryData
from .GameStatData import GameStatData
from .Player import Player
from .GalacticTransport import GalacticTransport
from .Planets import PlanetFactory
from .DysonSphere import DysonSphereSwitch


"""
GameData
{
    int32 version = 2
    string gameName
    GameDesc
    int64 gameTick
    GamePrefsData preferences (version >= 1)
    GameHistoryData
    uint8_bool hidePlayerModel (version >= 2)
    uint8_bool disableController (version >= 2)
    GameStatData statistics
    int32 planetId
    Player mainPlayer
    int32 factoryCount
    GalacticTransport
    PlanetFactory[factoryCount]
    int32 galaxyStarCount: Must equal GameDesc::starCount or the game will crash.
    [galaxyStarCount] {
        int32 dysonSphereDataIsAvailableFlag: Must be 0 or 1 or the game will crash.
        DysonSphere (dysonSphereDataIsAvailableFlag == 1)
    }
}
"""


class GameData(Model):
    version = Int32Field()
    gameName = StringField()
    gameDesc = ModelField(GameDesc)
    gameTick = Int64Field()
    gamePrefsData = ConditionalField(lambda: ModelField(GamePrefsData), arg_fields='version', condition_func=ge(1))
    gameHistoryData = ModelField(GameHistoryData)
    hidePlayerModel = ConditionalField(BoolField, arg_fields='version', condition_func=ge(2))
    disableController = ConditionalField(BoolField, arg_fields='version', condition_func=ge(2))
    gameStatData = ModelField(GameStatData)
    planetId = Int32Field()
    mainPlayer = ModelField(Player)
    factoryCount = Int32Field()
    galacticTransport = ModelField(GalacticTransport)
    planetFactory = ArrayField(lambda: ModelField(PlanetFactory), length_field='factoryCount')
    galaxyStarCount = Int32Field()
    dysonSpheres = ArrayField(lambda: ModelField(DysonSphereSwitch), length_field='galaxyStarCount')