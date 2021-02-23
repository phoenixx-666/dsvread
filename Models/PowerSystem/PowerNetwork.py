from Fields import Int32Field, ModelField, ArrayField
from Models import Model
from Models.PowerSystem.PowerNetworkNode import PowerNetworkNode

"""
PowerNetwork
{
    int32 version = 0
    int32 id
    int32 numNodes
    int32 numConsumers
    int32 numGenerators
    int32 numAccumulators
    int32 numExchangers
    PowerNetworkStructures::Node[numNodes]
    int32 consumers[numConsumers]
    int32 generators[numGenerators]
    int32 accumulators[numAccumulators]
    int32 exchangers[numExchangers]
}
"""


class PowerNetwork(Model):
    version = Int32Field()
    id = Int32Field()
    numNodes = Int32Field()
    numConsumers = Int32Field()
    numGenerators = Int32Field()
    numAccumulators = Int32Field()
    numExchangers = Int32Field()
    nodes = ArrayField(lambda: ModelField(PowerNetworkNode), length_field='numNodes')
    consumers = ArrayField(Int32Field, length_field='numConsumers')
    generators = ArrayField(Int32Field, length_field='numGenerators')
    accumulators = ArrayField(Int32Field, length_field='numAccumulators')
    exchangers = ArrayField(Int32Field, length_field='numExchangers')