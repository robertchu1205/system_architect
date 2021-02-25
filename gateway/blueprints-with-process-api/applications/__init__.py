"""Initialize Flask app."""
import sys
# import json_logging
from flask import Flask

def create_app():
    """Create Flask application."""
    # app = Flask(__name__, instance_relative_config=False)
    app = Flask(__name__, template_folder='templates')

    # json_logging.ENABLE_JSON_LOGGING = True
    # json_logging.init_flask()
    # json_logging.init_request_instrument(app)

    with app.app_context():
        # Import parts of our application
        from .metrics import metrics
        from .predict import predict
        from .showconfig import showconfig
        from .setconfig import setconfig

        # Register Blueprints
        app.register_blueprint(metrics.metrics_bp, url_prefix='/metrics')
        app.register_blueprint(metrics.metrics_bp, url_prefix='/metrics/')
        app.register_blueprint(predict.predict_bp, url_prefix='/predict')
        app.register_blueprint(predict.predict_bp, url_prefix='/predict/')
        app.register_blueprint(predict.predict_bp, url_prefix='/predict/result')
        app.register_blueprint(predict.predict_bp, url_prefix='/predict/result/')
        app.register_blueprint(showconfig.showconfig_bp, url_prefix='/showconfig')
        app.register_blueprint(showconfig.showconfig_bp, url_prefix='/showconfig/')
        app.register_blueprint(setconfig.config_bp, url_prefix='/config')
        app.register_blueprint(setconfig.config_bp, url_prefix='/config/')

        return app