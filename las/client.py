import requests
import json
import pathlib
import logging

from base64 import b64encode
from backoff import on_exception, expo
from requests.exceptions import RequestException
from json.decoder import JSONDecodeError
from urllib.parse import urlparse
from typing import List, Dict

from .credentials import Credentials


logger = logging.getLogger('las')


def _fatal_code(e):
    return 400 <= e.response.status_code < 500


def _json_decode(response):
    try:
        response.raise_for_status()
        return response.json()
    except JSONDecodeError as e:
        logger.error('Error in response. Returned {}'.format(response.text))
        raise e
    except Exception as e:
        logger.error('Error in response. Returned {}'.format(response.text))

        if response.status_code == 403 and 'Forbidden' in response.json().values():
            raise InvalidCredentialsException('Credentials provided is not valid.')

        if response.status_code == 429 and 'Too Many Requests' in response.json().values():
            raise TooManyRequestsException('You have reached the limit of requests per second.')

        if response.status_code == 429 and 'Limit Exceeded' in response.json().values():
            raise LimitExceededException('You have reached the limit of total requests per month.')

        raise e


class ClientException(Exception):
    """A ClientException is raised if the client refuses to
    send request due to incorrect usage or bad request data."""
    pass


class InvalidCredentialsException(ClientException):
    """An InvalidCredentialsException is raised if api key, access key id or secret access key is invalid."""
    pass


class TooManyRequestsException(ClientException):
    """A TooManyRequestsException is raised if you have reached the number of requests per second limit
    associated with your credentials."""
    pass


class LimitExceededException(ClientException):
    """A LimitExceededException is raised if you have reached the limit of total requests per month
    associated with your credentials."""
    pass


class Client:
    """A low level client to invoke api methods from Lucidtech AI Services.

    :param endpoint: Domain endpoint of the api, e.g. https://<prefix>.api.lucidtech.ai/<version>
    :type endpoint: str
    :param credentials: Credentials to use, instance of :py:class:`~las.Credentials`
    :type credentials: Credentials

    """
    def __init__(self, endpoint: str, credentials=None):
        self.endpoint = endpoint
        self.credentials = credentials or Credentials()

    @on_exception(expo, TooManyRequestsException, max_tries=4)
    @on_exception(expo, RequestException, max_tries=3, giveup=_fatal_code)
    def patch_task_id(self, task_id: str, task_result: dict) -> dict:
        """Creates a document handle, calls the POST /documents endpoint.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.post_documents('image/jpeg', consent_id='foobar')

        :param content_type: A mime type for the document handle
        :type content_type: str
        :param consent_id: An identifier to mark the owner of the document handle
        :type consent_id: str
        :return: Document handle id and pre-signed upload url
        :rtype: dict
        :raises InvalidCredentialsException: If the credentials are invalid
        :raises TooManyRequestsException: If limit of requests per second is reached
        :raises LimitExceededException: If limit of total requests per month is reached
        :raises requests.exception.RequestException: If error was raised by requests
        """

        body = json.dumps({
            'taskResult': task_result,
        }).encode()
        uri, headers = self._create_signing_headers(f'/tasks/{task_id}')

        post_documents_response = requests.patch(
            url=uri.geturl(),
            headers=headers,
            data=body
        )

        response = _json_decode(post_documents_response)
        return response

    @on_exception(expo, TooManyRequestsException, max_tries=4)
    @on_exception(expo, RequestException, max_tries=3, giveup=_fatal_code)
    def post_tasks(self, activity_arn: str) -> dict:
        """Creates a document handle, calls the POST /documents endpoint.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.post_documents('image/jpeg', consent_id='foobar')

        :param content_type: A mime type for the document handle
        :type content_type: str
        :param consent_id: An identifier to mark the owner of the document handle
        :type consent_id: str
        :return: Document handle id and pre-signed upload url
        :rtype: dict
        :raises InvalidCredentialsException: If the credentials are invalid
        :raises TooManyRequestsException: If limit of requests per second is reached
        :raises LimitExceededException: If limit of total requests per month is reached
        :raises requests.exception.RequestException: If error was raised by requests
        """

        body = json.dumps({
            'activityArn': activity_arn,
        }).encode()
        uri, headers = self._create_signing_headers('/tasks')

        post_documents_response = requests.post(
            url=uri.geturl(),
            headers=headers,
            data=body
        )

        response = _json_decode(post_documents_response)
        return response

    @on_exception(expo, TooManyRequestsException, max_tries=4)
    @on_exception(expo, RequestException, max_tries=3, giveup=_fatal_code)
    def post_processes(self, state_machine_arn: str, input_data: dict) -> dict:
        """Creates a document handle, calls the POST /documents endpoint.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.post_documents('image/jpeg', consent_id='foobar')

        :param content_type: A mime type for the document handle
        :type content_type: str
        :param consent_id: An identifier to mark the owner of the document handle
        :type consent_id: str
        :return: Document handle id and pre-signed upload url
        :rtype: dict
        :raises InvalidCredentialsException: If the credentials are invalid
        :raises TooManyRequestsException: If limit of requests per second is reached
        :raises LimitExceededException: If limit of total requests per month is reached
        :raises requests.exception.RequestException: If error was raised by requests
        """

        body = json.dumps({
            'stateMachineArn': state_machine_arn,
            'inputData': input_data
        }).encode()
        print(body)
        uri, headers = self._create_signing_headers('/processes')

        post_documents_response = requests.post(
            url=uri.geturl(),
            headers=headers,
            data=body
        )

        response = _json_decode(post_documents_response)
        return response

    @on_exception(expo, TooManyRequestsException, max_tries=4)
    @on_exception(expo, RequestException, max_tries=3, giveup=_fatal_code)
    def post_documents(self, content: bytes, content_type: str, consent_id: str) -> dict:
        """Creates a document handle, calls the POST /documents endpoint.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.post_documents('image/jpeg', consent_id='foobar')

        :param content_type: A mime type for the document handle
        :type content_type: str
        :param consent_id: An identifier to mark the owner of the document handle
        :type consent_id: str
        :return: Document handle id and pre-signed upload url
        :rtype: dict
        :raises InvalidCredentialsException: If the credentials are invalid
        :raises TooManyRequestsException: If limit of requests per second is reached
        :raises LimitExceededException: If limit of total requests per month is reached
        :raises requests.exception.RequestException: If error was raised by requests
        """

        base64_content = b64encode(content).decode()
        body = json.dumps({
            'content': base64_content,
            'contentType': content_type,
            'consentId': consent_id
        }).encode()
        uri, headers = self._create_signing_headers('/documents')

        post_documents_response = requests.post(
            url=uri.geturl(),
            headers=headers,
            data=body
        )

        response = _json_decode(post_documents_response)
        return response

    @staticmethod
    @on_exception(expo, RequestException, max_tries=3, giveup=_fatal_code)
    def put_document(document_path: str, content_type: str, presigned_url: str, use_kms: bool = False) -> str:
        """Convenience method for putting a document to presigned url.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.put_document(document_path='document.jpeg', content_type='image/jpeg',
        >>> presigned_url='<presigned url>')

        :param document_path: Path to document to upload
        :type document_path: str
        :param content_type: Mime type of document to upload. Same as provided to :py:func:`~las.Client.post_documents`
        :type content_type: str
        :param presigned_url: Presigned upload url from :py:func:`~las.Client.post_documents`
        :type presigned_url: str
        :param use_kms: Adds KMS header to the request to S3. Set to true if your API using KMS default encryption on
        the data bucket
        :type use_kms: bool
        :return: Response from put operation
        :rtype: str
        :raises requests.exception.RequestException: If error was raised by requests
        """

        body = pathlib.Path(document_path).read_bytes()
        headers = {'Content-Type': content_type}
        if use_kms:
            headers.update({'x-amz-server-side-encryption': 'aws:kms'})

        put_document_response = requests.put(presigned_url, data=body, headers=headers)
        put_document_response.raise_for_status()
        return put_document_response.content.decode()

    @on_exception(expo, TooManyRequestsException, max_tries=4)
    @on_exception(expo, RequestException, max_tries=3, giveup=_fatal_code)
    def post_predictions(self, document_id: str, model_name: str) -> dict:
        """Run inference and create a prediction, calls the POST /predictions endpoint.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.post_predictions(document_id='<document id>', model_name='invoice')

        :param document_id: The document id to run inference and create a prediction on
        :type document_id: str
        :param model_name: The name of the model to use for inference
        :type model_name: str
        :return: Prediction on document
        :rtype: dict
        :raises InvalidCredentialsException: If the credentials are invalid
        :raises TooManyRequestsException: If limit of requests per second is reached
        :raises LimitExceededException: If limit of total requests per month is reached
        :raises requests.exception.RequestException: If error was raised by requests
        """

        body = json.dumps({'documentId': document_id, 'modelName': model_name}).encode()
        uri, headers = self._create_signing_headers('POST', '/predictions', body)

        post_predictions_response = requests.post(
            url=uri.geturl(),
            headers=headers,
            data=body
        )

        response = _json_decode(post_predictions_response)
        return response

    @on_exception(expo, TooManyRequestsException, max_tries=4)
    @on_exception(expo, RequestException, max_tries=3, giveup=_fatal_code)
    def get_document_id(self, document_id: str) -> dict:
        """Get document from the REST API, calls the GET /documents/{documentId} endpoint.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.get_document_id(document_id='<document id>')

        :param document_id: The document id to run inference and create a prediction on
        :type document_id: str
        :return: Document response from REST API
        :rtype: dict
        :raises InvalidCredentialsException: If the credentials are invalid
        :raises TooManyRequestsException: If limit of requests per second is reached
        :raises LimitExceededException: If limit of total requests per month is reached
        :raises requests.exception.RequestException: If error was raised by requests
        """

        uri, headers = self._create_signing_headers(f'/documents/{document_id}')

        get_document_id_response = requests.get(
            url=uri.geturl(),
            headers=headers
        )

        response = _json_decode(get_document_id_response)
        return response

    @on_exception(expo, TooManyRequestsException, max_tries=4)
    @on_exception(expo, RequestException, max_tries=3, giveup=_fatal_code)
    def post_document_id(self, document_id: str, feedback: List[Dict[str, str]]) -> dict:
        """Post feedback to the REST API, calls the POST /documents/{documentId} endpoint.
        Posting feedback means posting the ground truth data for the particular document.
        This enables the API to learn from past mistakes.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> feedback = [{'label': 'total_amount', 'value': '156.00'}, {'label': 'invoice_date', 'value': '2018-10-23'}]
        >>> client.post_document_id(document_id='<document id>', feedback=feedback)

        :param document_id: The document id to run inference and create a prediction on
        :type document_id: str
        :param feedback: A list of feedback items
        :type feedback: List[Dict[str, str]]
        :return: Feedback response from REST API
        :rtype: dict
        :raises InvalidCredentialsException: If the credentials are invalid
        :raises TooManyRequestsException: If limit of requests per second is reached
        :raises LimitExceededException: If limit of total requests per month is reached
        :raises requests.exception.RequestException: If error was raised by requests
        """

        body = json.dumps({'feedback': feedback}).encode()
        uri, headers = self._create_signing_headers('POST', f'/documents/{document_id}', body)

        post_document_id_response = requests.post(
            url=uri.geturl(),
            headers=headers,
            data=body
        )

        response = _json_decode(post_document_id_response)
        return response

    @on_exception(expo, TooManyRequestsException, max_tries=4)
    @on_exception(expo, RequestException, max_tries=3, giveup=_fatal_code)
    def delete_consent_id(self, consent_id: str) -> dict:
        """Delete documents with this consent_id, calls the DELETE /consent/{consentId} endpoint.

        >>> from las import Client
        >>> client = Client(endpoint='<api endpoint>')
        >>> client.delete_consent_id('<consent id>')

        :param consent_id: Delete documents with this consent_id
        :type consent_id: str
        :return: Delete consent id response from REST API
        :rtype: dict
        :raises InvalidCredentialsException: If the credentials are invalid
        :raises TooManyRequestsException: If limit of requests per second is reached
        :raises LimitExceededException: If limit of total requests per month is reached
        :raises requests.exception.RequestException: If error was raised by requests
        """

        body = json.dumps({}).encode()
        uri, headers = self._create_signing_headers('DELETE', f'/consents/{consent_id}', body)

        delete_consent_id_consent = requests.delete(
            url=uri.geturl(),
            headers=headers,
            data=body
        )

        response = _json_decode(delete_consent_id_consent)
        return response

    def _create_signing_headers(self, path: str):
        uri = urlparse(f'{self.endpoint}{path}')

        auth_headers = {
            'Authorization': f'Bearer {self.credentials.access_token}',
            'X-Api-Key': self.credentials.api_key
        }
        headers = {**auth_headers, 'Content-Type': 'application/json'}
        return uri, headers
