import os
import time
from xml.dom import minidom

import pytest
import responses

import app
from notapi.call_handler import UNTERMSTRICH_PATH

URL_PREFIX = os.environ.get("URL_PREFIX")
CALL_URL = f"{URL_PREFIX}/call"

PHONE_PREFIX = os.environ.get("PHONE_PREFIX")
DIAL = "10"
VALID_LOCAL_PHONE_NUMBER = PHONE_PREFIX + DIAL
INVALID_LOCAL_PHONE_NUMBER = PHONE_PREFIX[::-1] + DIAL
EXTERNAL_PHONE_NUMBER = "00495550123"

UNTERMSTRICH_URL = os.environ.get("UNTERMSTRICH_URL") + f"/{UNTERMSTRICH_PATH}"


@pytest.fixture
def client():
    app.app.config["TESTING"] = True
    return app.app.test_client()


@pytest.fixture()
def untermstrich_response():
    with responses.RequestsMock() as response:
        response.add(responses.POST, UNTERMSTRICH_URL)
        yield response


def test_document_root_404(client):
    response = client.get("/")
    assert response.status_code == 404


def test_invalid_call(client):
    response = client.post(CALL_URL)
    assert response.status_code == 400


def test_valid_new_call(client, untermstrich_response):
    data = {
        "event": "newCall",
        "direction": "out",
        "from": VALID_LOCAL_PHONE_NUMBER,
        "to": EXTERNAL_PHONE_NUMBER
    }
    response = client.post(CALL_URL, data=data)
    assert response.status_code == 200
    assert response.mimetype == "application/xml"

    # Check for well-formed XML
    xml = minidom.parseString(response.data)
    assert xml.hasChildNodes()
    element = xml.firstChild
    assert element.tagName == "Response"
    assert element.hasAttribute("onAnswer")
    assert element.getAttribute("onAnswer") == f"http://localhost/{URL_PREFIX}/call"
    assert element.hasAttribute("onHangup")
    assert element.getAttribute("onHangup") == f"http://localhost/{URL_PREFIX}/call"

    # Allow asynchronous call to untermstrich to occur
    time.sleep(.1)

    assert len(untermstrich_response.calls) == 1
    untermstrich_request = untermstrich_response.calls[0].request

    assert f"dial={DIAL}" in untermstrich_request.url
    assert f"phone={EXTERNAL_PHONE_NUMBER}" in untermstrich_request.url
    assert f"active_call=true" in untermstrich_request.url


def test_invalid_new_call(client):
    data = {
        "event": "newCall",
        "direction": "out",
        "from": VALID_LOCAL_PHONE_NUMBER,
    }
    response = client.post(CALL_URL, data=data)
    assert response.status_code == 400


def test_valid_answer(client, untermstrich_response):
    data = {
        "event": "answer",
        "direction": "out",
        "from": VALID_LOCAL_PHONE_NUMBER,
        "to": EXTERNAL_PHONE_NUMBER
    }
    response = client.post(CALL_URL, data=data)
    assert response.status_code == 200

    # Allow asynchronous call to untermstrich to occur
    time.sleep(.1)

    assert len(untermstrich_response.calls) == 1
    untermstrich_request = untermstrich_response.calls[0].request

    assert f"dial={DIAL}" in untermstrich_request.url
    assert f"phone={EXTERNAL_PHONE_NUMBER}" in untermstrich_request.url
    assert f"active_call=true" in untermstrich_request.url
    assert f"received=true" in untermstrich_request.url


def test_invalid_answer(client):
    data = {
        "event": "answer",
        "direction": "out",
        "from": VALID_LOCAL_PHONE_NUMBER,
    }
    response = client.post(CALL_URL, data=data)
    assert response.status_code == 400


def test_valid_hangup(client, untermstrich_response):
    data = {
        "event": "hangup",
        "direction": "out",
        "from": VALID_LOCAL_PHONE_NUMBER,
        "to": EXTERNAL_PHONE_NUMBER
    }
    response = client.post(CALL_URL, data=data)
    assert response.status_code == 200

    # Allow asynchronous call to untermstrich to occur
    time.sleep(.1)

    assert len(untermstrich_response.calls) == 1
    untermstrich_request = untermstrich_response.calls[0].request

    assert f"dial={DIAL}" in untermstrich_request.url
    assert f"phone={EXTERNAL_PHONE_NUMBER}" in untermstrich_request.url
    assert f"active_call=true" in untermstrich_request.url
    assert f"disconnected=true" in untermstrich_request.url
    assert f"set_to=true" in untermstrich_request.url


def test_invalid_hangup(client):
    data = {
        "event": "hangup",
        "direction": "out",
        "from": VALID_LOCAL_PHONE_NUMBER,
    }
    response = client.post(CALL_URL, data=data)
    assert response.status_code == 400
