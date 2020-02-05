from marshmallow import INCLUDE, Schema, fields, validates

EVENT_NEWCALL = "newCall"
EVENT_ANSWER = "answer"
EVENT_HANGUP = "hangup"
SUPPORTED_EVENTS = (EVENT_NEWCALL, EVENT_ANSWER, EVENT_HANGUP)


class CallSchema(Schema):
    class Meta:
        unknown = INCLUDE
        
    event = fields.Str(required=True)
    phone_from = fields.Str(required=True, data_key="from")
    phone_to = fields.Str(required=True, data_key="to")
    direction = fields.Str(required=True)

    @validates("event")
    def is_event_supported(self, event):
        return event in SUPPORTED_EVENTS

    @validates("direction")
    def is_valid_direction(self, direction):
        return direction in ("in", "out")
