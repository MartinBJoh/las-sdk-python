import pytest

from las import Invoice
from las.client import FileFormatException
from io import BytesIO


@pytest.fixture(scope='module')
def url(params):
    return params('invoice_url')


@pytest.fixture(scope='module')
def filename(params):
    return params('invoice_filename')


def scan_invoice(client, invoice):
    response = client.scan_invoice(invoice=invoice)
    for detection in response.detections:
        assert 0 <= detection['confidence'] <= 1
        assert detection['value']
        assert detection['label']


def test_scan_invoice_with_url(url, client):
    invoice = Invoice(url=url)
    scan_invoice(client, invoice)


def test_scan_invoice_with_filename(filename, client):
    invoice = Invoice(filename=filename)
    scan_invoice(client, invoice)


def test_scan_invoice_with_junk(client):
    fp = BytesIO(b'junk')
    invoice = Invoice(fp=fp)
    try:
        scan_invoice(client, invoice)
    except FileFormatException:
        assert True
    except:
        assert False


def test_scan_invoice_with_bad_image(client):
    fp = BytesIO(b'\x00' * 6 + b'JFIF')
    invoice = Invoice(fp=fp)
    response = client.scan_invoice(invoice=invoice)
    assert response.detections == []
