from flasgger import Swagger
from flask import Flask
from flask.blueprints import Blueprint
from util.format import format

import config
import routes
import logging
from werkzeug.exceptions import HTTPException

server = Flask(__name__)
server.debug = config.DEBUG

server.config["SWAGGER"] = {
    "swagger_version": "2.0",
    "title": "Application",
    "specs": [
        {
            "version": "0.0.1",
            "title": "Application",
            "endpoint": "spec",
            "route": "/application/spec",
            "rule_filter": lambda rule: True,
        }
    ],
    "static_url_path": "/apidocs",
}
Swagger(server)

@server.errorhandler(Exception)
def handle_error(e):
    logging.error(e)
    return format.badRequest(message=str(e))

for blueprint in vars(routes).values():
    if isinstance(blueprint, Blueprint):
        server.register_blueprint(blueprint, url_prefix='/v1/oneai')

if __name__ == "__main__":
    from waitress import serve
    serve(server, host=config.HOST, port=config.PORT)