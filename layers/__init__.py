"""Models, Views, Controllers for map import layers."""
import json
import logging

from flask import current_app, Flask, redirect, request, session, url_for
import httplib2
from oauth2client.contrib.flask_util import UserOAuth2


# import google.cloud.logging
# from google.cloud import error_reporting
# from google.cloud import logging as google_cloud_logging


oauth2 = UserOAuth2()

def create_app(config, debug=False, testing=False, config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(config)

    app.debug = debug
    app.testing = testing

    if config_overrides:
        app.config.update(config_overrides)

    # Configure logging
    if not app.testing:
        logging.basicConfig(level=logging.INFO)
        # TODO:
        # client = google_cloud_logging.Client(app.config['PROJECT_ID'])
        # # Attaches a Google Stackdriver logging handler to the root logger
        # client.setup_logging(logging.INFO)

    # Initalize the OAuth2 helper.
    oauth2.init_app(
        app,
        scopes=['email', 'profile'],
        authorize_callback=_request_user_info)

    # Add a logout handler.
    @app.route('/logout')
    def logout():
        # Delete the user's profile and the credentials stored by oauth2.
        del session['profile']
        session.modified = True
        oauth2.storage.delete()
        return redirect(request.referrer or '/')

    # Register the Layers CRUD blueprint.
    from .crud import crud
    app.register_blueprint(crud, url_prefix='/layers')

    # Add a default root route.
    # @oauth2.required
    @app.route("/")
    def index():
        # TODO
        return redirect(url_for('crud.list'))

    # TODO:
    # @app.route("/settings")

    # Add an error handler that reports exceptions to Stackdriver Error
    # Reporting. Note that this error handler is only used when debug
    # is False
    @app.errorhandler(500)
    def server_error(exc):
        return """
        An internal error occurred: <pre>{}</pre>
        See logs for full stacktrace.
        """.format(exc), 500
        # TODO:
        # client = error_reporting.Client(app.config['PROJECT_ID'])
        # client.report_exception(
        #     http_context=error_reporting.build_flask_context(request))
        # return """
        # An internal error occurred.
        # """, 500

    return app



def _request_user_info(credentials):
    """
    Makes an HTTP request to the Google+ API to retrieve the user's basic
    profile information, including full name and photo, and stores it in the
    Flask session.
    """
    http = httplib2.Http()
    credentials.authorize(http)
    resp, content = http.request(
        'https://www.googleapis.com/plus/v1/people/me')

    if resp.status != 200:
        current_app.logger.error(
            "Error while obtaining user profile: \n%s: %s", resp, content)
        return None

    session['profile'] = json.loads(content.decode('utf-8'))
