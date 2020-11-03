import pytest
from las.client import BaseClient
from . import util
import logging


@pytest.mark.parametrize('transition_type,params', [
    ('docker', {'imageUrl': 'python3.8'}),
    ('manual', None),
])
def test_create_transition(client: BaseClient, transition_type, params):
    in_schema = util.json_schema()
    out_schema = util.json_schema()
    response = client.create_transition(transition_type, in_schema, out_schema, params=params)
    logging.info(response)
    assert 'transitionId' in response, 'Missing transitionId in response'


def test_execute_transition(client: BaseClient):
    transition_id = util.transition_id()
    response = client.execute_transition(transition_id)
    logging.info(response)
    assert 'transitionId' in response, 'Missing transitionId in response'
    assert 'executionId' in response, 'Missing executionId in response'
    assert 'status' in response, 'Missing status in response'


@pytest.mark.parametrize('status,output,error', [
    ('succeeded', {'foo': 'bar'}, None),
    ('failed', None, {'message': 'foobar'}),
])
def test_update_transition_execution(client: BaseClient, status, output, error):
    transition_id = util.transition_id()
    execution_id = util.transition_execution_id()
    response = client.update_transition_execution(transition_id, execution_id, status, output=output, error=error)
    logging.info(response)
    assert 'transitionId' in response, 'Missing transitionId in response'
    assert 'executionId' in response, 'Missing executionId in response'
    assert 'status' in response, 'Missing status in response'
