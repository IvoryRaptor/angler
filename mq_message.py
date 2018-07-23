from protobuf3.message import Message
from protobuf3.fields import Int32Field, StringField, Int64Field, BytesField


class MintPayload(Message):
    pass


class MQMessage(Message):
    pass

MintPayload.add_field('partition', Int32Field(field_number=1, optional=True))
MintPayload.add_field('number', StringField(field_number=2, optional=True))
MintPayload.add_field('time', Int64Field(field_number=3, optional=True))
MQMessage.add_field('caller', StringField(field_number=1, optional=True))
MQMessage.add_field('matrix', StringField(field_number=2, optional=True))
MQMessage.add_field('device', StringField(field_number=3, optional=True))
MQMessage.add_field('resource', StringField(field_number=4, optional=True))
MQMessage.add_field('action', StringField(field_number=5, optional=True))
MQMessage.add_field('payload', BytesField(field_number=6, optional=True))
MQMessage.add_field('time', Int64Field(field_number=7, optional=True))
