import logging
import random

import pytest
from las.client import Client

from . import service, util


@pytest.mark.parametrize('error_config', [None, service.create_error_config()])
@pytest.mark.parametrize('completed_config', [None, service.create_completed_config()])
@pytest.mark.parametrize('name_and_description', util.name_and_description_combinations(True))
def test_create_workflow(client: Client, name_and_description, error_config, completed_config):
    specification = {'definition': {}}
    response = client.create_workflow(
        specification,
        **name_and_description,
        error_config=error_config,
        completed_config=completed_config
    )
    logging.info(response)
    assert_workflow(response)


def test_list_workflows(client: Client):
    response = client.list_workflows()
    assert 'workflows' in response, 'Missing workflows in response'
    for workflow in response['workflows']:
        assert_workflow(workflow)


@pytest.mark.parametrize('max_results,next_token', [
    (random.randint(1, 100), None),
    (random.randint(1, 100), 'foo'),
    (None, None),
])
def test_list_workflows_with_pagination(client: Client, max_results, next_token):
    response = client.list_workflows(max_results=max_results, next_token=next_token)
    assert 'workflows' in response, 'Missing workflows in response'
    assert 'nextToken' in response, 'Missing nextToken in response'


def test_get_workflow(client: Client):
    workflow_id = service.create_workflow_id()
    response = client.get_workflow(workflow_id)
    logging.info(response)
    assert_workflow(response)


@pytest.mark.parametrize('error_config', [None, service.create_error_config()])
@pytest.mark.parametrize('completed_config', [None, service.create_completed_config()])
@pytest.mark.parametrize('name_and_description', util.name_and_description_combinations(True))
def test_update_workflow(client: Client, name_and_description, error_config, completed_config):
    response = client.update_workflow(
        service.create_workflow_id(),
        error_config=error_config,
        completed_config=completed_config,
        **name_and_description,
    )
    logging.info(response)
    assert_workflow(response)


@pytest.mark.parametrize('status', [
    ['succeeded'],
    ['failed'],
    'running',
    None,
])
def test_list_workflow_executions(client: Client, status):
    workflow_id = service.create_workflow_id()
    response = client.list_workflow_executions(workflow_id, status=status)
    logging.info(response)
    assert 'workflowId' in response, 'Missing workflowId in response'
    assert 'executions' in response, 'Missing executions in response'


@pytest.mark.parametrize('max_results,next_token', [
    (random.randint(1, 100), None),
    (random.randint(1, 100), 'foo'),
    (None, None),
])
def test_list_workflow_executions_with_pagination(client: Client, max_results, next_token):
    workflow_id = service.create_workflow_id()
    response = client.list_workflow_executions(workflow_id=workflow_id, max_results=max_results, next_token=next_token)
    assert 'workflowId' in response, 'Missing workflowId in response'
    assert 'executions' in response, 'Missing executions in response'
    assert 'nextToken' in response, 'Missing nextToken in response'


def test_execute_workflow(client: Client):
    workflow_id = service.create_workflow_id()
    response = client.execute_workflow(workflow_id, content={})
    logging.info(response)
    assert_workflow_execution(response)


@pytest.mark.skip(reason='DELETE does not work for the mocked API')
def test_delete_workflow_execution(client: Client):
    workflow_id = service.create_workflow_id()
    execution_id = service.create_workflow_execution_id()
    response = client.delete_workflow_execution(workflow_id, execution_id)
    logging.info(response)
    assert_workflow_execution(response)


@pytest.mark.skip(reason='DELETE does not work for the mocked API')
def test_delete_workflow(client: Client):
    workflow_id = service.create_workflow_id()
    response = client.delete_workflow(workflow_id)
    logging.info(response)
    assert_workflow(response)


def test_get_workflow_execution(client: Client):
    response = client.get_workflow_execution(service.create_workflow_id(), service.create_workflow_execution_id())
    logging.info(response)
    assert_workflow_execution(response)


def test_update_workflow_execution(client: Client):
    response = client.update_workflow_execution(
        service.create_workflow_id(),
        service.create_workflow_execution_id(),
        service.create_transition_id(),
    )
    logging.info(response)
    assert_workflow_execution(response)


def assert_workflow(response):
    assert 'workflowId' in response, 'Missing workflowId in response'
    assert 'name' in response, 'Missing name in response'
    assert 'description' in response, 'Missing description in response'


def assert_workflow_execution(response):
    assert 'workflowId' in response, 'Missing workflowId in response'
    assert 'executionId' in response, 'Missing executionId in response'
    assert 'startTime' in response, 'Missing startTime in response'
    assert 'endTime' in response, 'Missing endTime in response'
    assert 'transitionExecutions' in response, 'Missing transitionExecutions in response'
