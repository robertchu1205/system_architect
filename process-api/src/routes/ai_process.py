from flask import Blueprint
from flask_restful import Api

from resources import AiProcessResource

AI_PROCESS_BLUEPRINT = Blueprint("ai_process", __name__)
Api(AI_PROCESS_BLUEPRINT).add_resource(AiProcessResource, "/<string:process_name>")