from os import environ

from flask import Flask

from notapi.call_handler import call_handler, executor

URL_PREFIX = environ.get("URL_PREFIX")

app = Flask(__name__)
app.register_blueprint(call_handler, url_prefix=f"/{URL_PREFIX}")

if __name__ == "__main__":
    app.run()
    executor.shutdown()
