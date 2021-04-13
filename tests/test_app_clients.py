import logging
import random

import pytest
from las.client import Client

from . import service, util


@pytest.mark.parametrize('name_and_description', util.name_and_description_combinations())
def test_create_app_client(client: Client, name_and_description):
    response = client.create_app_client(**name_and_description)
    assert 'appClientId' in response, 'Missing appClientId in response'


def test_list_app_clients(client: Client):
    response = client.list_app_clients()
    logging.info(response)
    assert 'appClients' in response, 'Missing appClients in response'


@pytest.mark.parametrize('max_results,next_token', [
    (random.randint(1, 100), None),
    (random.randint(1, 100), 'foo'),
    (None, None),
])
def test_list_app_clients_with_pagination(client: Client, max_results, next_token):
    response = client.list_app_clients(max_results=max_results, next_token=next_token)
    assert 'appClients' in response, 'Missing appClients in response'
    assert 'nextToken' in response, 'Missing nextToken in response'


@pytest.mark.skip(reason='DELETE does not work for the mocked API')
def test_delete_app_client(client: Client):
    app_client_id = service.create_app_client_id()
    response = client.delete_app_client(app_client_id)
    assert 'appClientId' in response, 'Missing appClientId in response'
    assert 'content' in response, 'Missing content in response'

