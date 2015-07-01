import server
import socket
import pytest
from multiprocessing import Process

ADDR = ('127.0.0.1', 8020)
_CRLF = b'\r\n'

@pytest.yield_fixture()
def server_setup():
    process = Process(target=server.start_server)
    process.daemon = True
    process.start()
    yield process


@pytest.fixture()
def client_setup():
    client = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP
    )
    client.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    client.connect(ADDR)
    return client


def test_response_ok(server_setup):
    assert '200 OK' in server.response_ok()


def test_response_error_500(server_setup):
    valid = []
    valid.append(b'HTTP/1.1 500 Internal Server Error')
    valid.append(b'Content-Type: text/html; charset=UTF-8'+ _CRLF)
    valid = _CRLF.join(valid)

    response = server.response_error(500, 'Internal Server Error')
    assert valid == response


def test_response_error_504(server_setup):
    valid = []
    valid.append(b'HTTP/1.1 504 Gateway Timeout')
    valid.append(b'Content-Type: text/html; charset=UTF-8'+ _CRLF)
    valid = _CRLF.join(valid)
    response = server.response_error(504, 'Gateway Timeout')
    assert valid == response


def test_parse_request_valid_request():
    request = []
    request.append(b'GET /path/to/URI HTTP/1.1')
    request.append(b'Host: www.google.com')
    request.append(b'')
    request = (b'\r\n').join(request)
    response = server.parse_request(request)
    assert response == b'/path/to/URI'


def test_parse_request_not_GET():
    request = []
    request.append(b'POST /path/to/URI HTTP/1.1')
    request.append(b'Host: www.google.com')
    request = (b'\r\n').join(request)
    with pytest.raises(TypeError):
        server.parse_request(request)


def test_parse_request_not_HTTP_1_1():
    request = []
    request.append(b'GET /path/to/URI HTTP/1.0')
    request.append(b'Host: www.google.com')
    request = (b'\r\n').join(request)
    with pytest.raises(ValueError):
        server.parse_request(request)


def test_parse_request_no_Host():
    request = []
    request.append(b'GET /path/to/URI HTTP/1.0')
    with pytest.raises(Exception):
        server.parse_request(request)
