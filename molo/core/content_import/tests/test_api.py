import json

import pytest
import responses
from django.conf import settings

from unittest import TestCase
from molo.core.content_import import api


@pytest.mark.django_db
class ApiTestCase(TestCase):
    @responses.activate
    def test_get_repos(self):
        responses.add(
            responses.GET,
            '%s/repos.json' % settings.UNICORE_DISTRIBUTE_API,
            content_type='application/json',
            body=json.dumps([{
                'name': 'foo',
            }, {
                'name': 'bar'
            }]),
            status=200)

        self.assertEqual(api.get_repos(), ['foo', 'bar'])
