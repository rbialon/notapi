from concurrent.futures import ThreadPoolExecutor
from os import environ
from xml.dom.minidom import Document

import requests
from flask import Blueprint, Response, abort, request

from .call_schema import CallSchema, EVENT_ANSWER, EVENT_HANGUP, EVENT_NEWCALL

call_handler = Blueprint("call_handler", __name__)
executor = ThreadPoolExecutor(max_workers=1)
call_schema = CallSchema()

PHONE_PREFIX = environ.get("PHONE_PREFIX")
UNTERMSTRICH_URL = environ.get("UNTERMSTRICH_URL")


@call_handler.route('/call', methods=["POST"])
def call():
    errors = call_schema.validate(request.form)
    if errors:
        abort(400, str(errors))

    event = request.form.get("event")
    direction = request.form.get("direction")

    phone = None
    dial = None

    if direction == "in":
        phone = request.form.get("from")
        dial = get_dial(request.form.get("to"))
    elif direction == "out":
        phone = request.form.get("to")
        dial = get_dial(request.form.get("from"))

    active_call = direction == "out"

    response = None
    mimetype = None

    if event == EVENT_NEWCALL:
        executor.submit(untermstrich_call, phone, dial, active_call)

        response = xml_response(phone, request.url)
        mimetype = "application/xml"
    elif event == EVENT_ANSWER:
        executor.submit(untermstrich_answer, phone, dial, active_call)
    elif event == EVENT_HANGUP:
        executor.submit(untermstrich_hangup, phone, dial, active_call)

    return Response(status=200, response=response, mimetype=mimetype)


def get_dial(number: str) -> str:
    return number.split(PHONE_PREFIX)[-1]


def xml_response(phone: str, url: str) -> str:
    doc = Document()
    response = doc.createElement("Response")
    response.setAttribute("onAnswer", url)
    response.setAttribute("onHangup", url)
    doc.appendChild(response)

    return doc.toxml(encoding="UTF-8")


# TODO: Add untermstrich basic authentication

def untermstrich_call(phone: str, dial: str, active_call: bool) -> None:
    url = f"{UNTERMSTRICH_URL}/rest/calls/call?phone={phone}&dial={dial}&active_call={active_call}"
    requests.post(url)


def untermstrich_answer(phone: str, dial: str, active_call: str) -> None:
    url = f"{UNTERMSTRICH_URL}/rest/calls/call?phone={phone}&dial={dial}&active_call={active_call}&received=true"
    requests.post(url)


def untermstrich_hangup(phone: str, dial: str, active_call: bool) -> None:
    url = f"{UNTERMSTRICH_URL}/rest/calls/call?phone={phone}&dial={dial}&active_call={active_call}&disconnected=true&set_to=true"
    requests.post(url)
