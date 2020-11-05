import pathlib
from typing import Iterable
import pytest
from las.client import BaseClient
from . import util

pytestmark = pytest.mark.integration


def test_create_document(
    monkeypatch,
    client: BaseClient,
    document_paths: Iterable[str],
    document_mime_types: Iterable[str],
    content,
):
    monkeypatch.setattr(pathlib.Path, 'read_bytes', lambda _: content)

    for document_path, document_mime_type in zip(document_paths, document_mime_types):
        consent_id = util.consent_id()
        content = pathlib.Path(document_path).read_bytes()
        post_documents_response = client.create_document(content, document_mime_type, consent_id)

        assert 'documentId' in post_documents_response, 'Missing documentId in response'
        assert 'consentId' in post_documents_response, 'Missing consentId in response'
        assert 'contentType' in post_documents_response, 'Missing contentType in response'


@pytest.mark.parametrize('batch_id,consent_id', [
    (None, None),
    (util.batch_id(), None),
    (None, util.consent_id()),
    (util.batch_id(), util.consent_id()),
])
def test_get_documents(client: BaseClient, batch_id, consent_id):
    response = client.list_documents(consent_id=consent_id, batch_id=batch_id)
    assert 'documents' in response, 'Missing documents in response'


def test_get_document(client: BaseClient):
    document_id = util.document_id()
    response = client.get_document(document_id)
    assert 'documentId' in response, 'Missing documentId in response'
    assert 'consentId' in response, 'Missing consentId in response'
    assert 'contentType' in response, 'Missing contentType in response'
    assert 'feedback' in response, 'Missing feedback in response'


def test_update_document(client: BaseClient):
    document_id = util.document_id()
    feedback = [
        {'label': 'total_amount', 'value': '54.50'},
        {'label': 'purchase_date', 'value': '2007-07-30'}
    ]

    post_document_id_response = client.update_document(document_id, feedback)

    assert 'feedback' in post_document_id_response, 'Missing feedback in response'
    assert 'documentId' in post_document_id_response, 'Missing documentId in response'
    assert 'consentId' in post_document_id_response, 'Missing consentId in response'


@pytest.mark.parametrize('consent_id', [None, util.consent_id()])
@pytest.mark.skip(reason='DELETE does not work for the mocked API')
def test_delete_documents(client: BaseClient, consent_id):
    delete_documents_response = client.delete_documents(consent_id)

    assert 'documentIds' in delete_documents_response, 'Missing documentIds in response'
