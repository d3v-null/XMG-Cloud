"""conftest.py is used to define common test fixtures for pytest."""

import pytest
from google.cloud.exceptions import ServiceUnavailable

from retrying import retry

from . import config, layers

from oauth2client.client import HttpAccessTokenRefreshError

if True:
    import dev_appserver
    dev_appserver.fix_sys_path()

    from google.appengine.datastore import datastore_stub_util
    from google.appengine.ext import ndb
    from google.appengine.ext import testbed


@pytest.yield_fixture
def app(request):
    """This fixtures provides a Flask app instance configured for testing.

    Because it's parametric, it will cause every test that uses this fixture
    to run three times: one time for each backend (datastore, cloudsql, and
    mongodb).

    It also ensures the tests run within a request context, allowing
    any calls to flask.request, flask.current_app, etc. to work."""
    app = layers.create_app(
        config,
        testing=True)

    with app.test_request_context():
        yield app


@pytest.yield_fixture
def model(monkeypatch, app):
    """This fixture provides a modified version of the app's model that tracks
    all created items and deletes them at the end of the test.

    Any tests that directly or indirectly interact with the database should use
    this to ensure that resources are properly cleaned up.

    Monkeypatch is provided by pytest and used to patch the model's create
    method.

    The app fixture is needed to provide the configuration and context needed
    to get the proper model object.

    Note: Originally this fixture provided access to multiple models
    """

    # First, create an instance of the Testbed class.
    ds_testbed = testbed.Testbed()
    # Then activate the testbed, which prepares the service stubs for use.
    ds_testbed.activate()
    # Create a consistency policy that will simulate the High Replication
    # consistency model.
    policy = datastore_stub_util.PseudoRandomHRConsistencyPolicy(
        probability=1)
    # Initialize the datastore stub with this policy.
    ds_testbed.init_datastore_v3_stub(consistency_policy=policy)
    # Initialize memcache stub too, since ndb also uses memcache
    ds_testbed.init_memcache_stub()
    # Clear in-context cache before each test.
    ndb.get_context().clear_cache()

    # Ensure no layers exist before running. This typically helps if tests
    # somehow left the database in a bad state.
    delete_all_layers(layers.model)

    yield layers.model

    # Delete all layers that we created during tests.
    delete_all_layers(layers.model)

    ds_testbed.deactivate()



# The backend data stores can sometimes be flaky. It's useful to retry this
# a few times before giving up.
# @retry(
#     stop_max_attempt_number=3,
#     wait_exponential_multiplier=100,
#     wait_exponential_max=2000)
def delete_all_layers(model):
    while True:
        layers, _ = model.list(limit=50)
        if not layers:
            break
        for layer in layers:
            model.delete(layer['id'])


def flaky_filter(info, *args):
    """Used by flaky to determine when to re-run a test case."""
    _, e, _ = info
    return isinstance(e, (ServiceUnavailable, HttpAccessTokenRefreshError))
