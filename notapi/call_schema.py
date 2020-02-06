from marshmallow import INCLUDE, Schema, ValidationError, fields, validates

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
        if event not in SUPPORTED_EVENTS:
            raise ValidationError(f"event {event} not supported")

    @validates("phone_from")
    @validates("phone_to")
    def is_phone_valid(self, phone):
        valid = (0 < len(phone) <= 50) and phone.isnumeric()

        if not valid:
            raise ValidationError(f"phone number {phone} not valid")

    @validates("direction")
    def is_valid_direction(self, direction):
        if direction not in ("in", "out"):
            raise ValidationError(f"direction {direction} not supported")
