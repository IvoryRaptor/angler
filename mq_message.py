from protobuf3.message import Message
from protobuf3.fields import StringField, MessageField, BytesField


class Address(Message):
    pass


class MQMessage(Message):
    pass

Address.add_field('matrix', StringField(field_number=1, optional=True))
Address.add_field('device', StringField(field_number=2, optional=True))
MQMessage.add_field('source', MessageField(field_number=1, optional=True, message_cls=Address))
MQMessage.add_field('destination', MessageField(field_number=2, optional=True, message_cls=Address))
MQMessage.add_field('resource', StringField(field_number=3, optional=True))
MQMessage.add_field('action', StringField(field_number=4, optional=True))
MQMessage.add_field('payload', BytesField(field_number=5, optional=True))
