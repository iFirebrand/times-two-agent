import logging
import os

import dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix
from theoriq.extra.flask import init_logging
from theoriq.extra.flask.logging import list_routes

import app_v1alpha2

def create_app():
    dotenv.load_dotenv()
    app = Flask(__name__, static_folder=None)
    
    # Enable CORS
    CORS(app, resources={
        r"/*": {
            "origins": ["*"],  # Allow all origins during development
            "methods": ["GET", "POST", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Handle proxy headers
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    init_logging(app, logging.INFO)
    app.register_blueprint(app_v1alpha2.deployed_agent_blueprint())
    app.register_blueprint(app_v1alpha2.configurable_agent_blueprint())

    @app.route('/deployed', methods=['POST'])
    def handle_request():
        data = request.get_json()
        # Your agent logic here
        return jsonify({"result": "success"})

    @app.route('/deployed/public-key', methods=['GET'])
    def get_public_key():
        # Read the agent's public key from environment
        public_key = os.getenv('AGENT_PUBLIC_KEY', "0x" + "0" * 64)
        return jsonify({"publicKey": public_key})

    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({"status": "healthy"})

    # Add request/response logging
    @app.before_request
    def log_request_info():
        logging.info('Headers: %s', dict(request.headers))
        logging.info('Body: %s', request.get_data())

    @app.after_request
    def after_request(response):
        logging.info('Response: %s', response.get_data())
        return response

    # Add error handlers
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error"}), 500

    list_routes(app)
    return app

app = create_app()

def main():
    port = int(os.environ.get('PORT', 8888))
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    main()
