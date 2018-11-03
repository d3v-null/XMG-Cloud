import re

import pytest
from flaky import flaky

from .conftest import flaky_filter


# Mark all test cases in this class as flaky, so that if errors occur they
# can be retried. This is useful when databases are temporarily unavailable.
@flaky(rerun_filter=flaky_filter)
# Tell pytest to use both the app and model fixtures for all test cases.
# This ensures that configuration is properly applied and that all database
# resources created during tests are cleaned up. These fixtures are defined
# in conftest.py
@pytest.mark.usefixtures('app', 'model')
class TestCrudActions(object):

    def test_list(self, app, model):
        for i in range(1, 12):
            model.create({'title': u'Layer {0}'.format(i)})

        with app.test_client() as atc:
            resp = atc.get('/layers/')

        assert resp.status == '200 OK'

        body = resp.data.decode('utf-8')
        assert 'Layer 1' in body, "Should show layers"
        assert len(re.findall('<h4>Layer', body)) == 10, (
            "Should not show more than 10 layers")
        assert 'More' in body, "Should have more than one page"

    def test_add(self, app):
        data = {
            'title': 'Test Layer',
        }

        with app.test_client() as atc:
            resp = atc.post('/layers/add', data=data, follow_redirects=True)

        assert resp.status == '200 OK'
        body = resp.data.decode('utf-8')
        assert 'Test Layer' in body

    def test_edit(self, app, model):
        existing = model.create({'title': "Temp Title"})

        with app.test_client() as atc:
            resp = atc.post(
                '/layers/%s/edit' % existing['id'],
                data={'title': 'Updated Title'},
                follow_redirects=True)

        assert resp.status == '200 OK'
        body = resp.data.decode('utf-8')
        assert 'Updated Title' in body
        assert 'Temp Title' not in body

    def test_delete(self, app, model):
        existing = model.create({'title': "Temp Title"})

        with app.test_client() as atc:
            resp = atc.get(
                '/layers/%s/delete' % existing['id'],
                follow_redirects=True)

        assert resp.status == '200 OK'
        assert not model.read(existing['id'])
