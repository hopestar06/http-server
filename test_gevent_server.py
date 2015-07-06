from multiprocessing import Process
import pytest
import __builtin__
import gevent_server
# import gevent_server
import server
import socket
import os


ADDR = ('127.0.0.1', 8000)
_CRLF = b'\r\n'


@pytest.yield_fixture()
def server_setup():
    process = Process(target=gevent_server.start_gserver)
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
    test_body = b'body contents'
    response = server.response_ok(test_body, 'text/html', len(test_body))
    assert response == _CRLF.join([
        b'HTTP/1.1 200 OK',
        b'Content-Type: text/html',
        b'Content-Length: 13',
        test_body,
        b''])


def test_valid_content_type(monkeypatch):
    monkeypatch.setattr(os.path, 'isdir', lambda x: False)
    monkeypatch.setattr(os.path, 'abspath', lambda x: '/abs/path')
    monkeypatch.setattr(os.path, 'dirname', lambda x: 'dirname')

    # This class mocks out the opened file
    class MockOpenResult(object):
        def read(self):
            return 'file.txt content 1 2 3'

    # This class mocks out what happens with 'with open(filename) as f ...'
    class MockOpenResultHelper(object):
        def __enter__(self):
            return MockOpenResult()

        def __exit__(self, *args):
            pass

    monkeypatch.setattr(__builtin__, 'open', lambda x: MockOpenResultHelper())
    (body, cont_type) = server.resolve_uri(b'/path/to/file.txt')
    expected_body = b'file.txt content 1 2 3'
    assert body == expected_body
    assert cont_type == 'txt'


def test_resolve_uri_value_error():
    with pytest.raises(ValueError):
        server.resolve_uri(b'/path/to/../')


def test_valid_root_directory(monkeypatch):
    monkeypatch.setattr(os.path, 'isdir', lambda x: True)
    monkeypatch.setattr(os, 'listdir',
                        lambda x: ['foo1.html', 'foo2.html', 'foo3.html'])
    (body, cont_type) = server.resolve_uri(b'/path/to/dir')
    expected_body = (b'<head>\n<body>\n<ul>\n'
                     b'<li>foo1.html</li>\n'
                     b'<li>foo2.html</li>\n'
                     b'<li>foo3.html</li>\n</ul>\n'
                     b'</body>\n</head>')
    assert body == expected_body
    assert cont_type == 'dir'


def test_response_error_500(server_setup):
    valid = []
    valid.append(b'HTTP/1.1 500 Internal Server Error')
    valid.append(b'Content-Type: text/html; charset=UTF-8' + _CRLF)
    valid = _CRLF.join(valid)

    response = server.response_error(500, 'Internal Server Error')
    assert valid == response


def test_response_error_504(server_setup):
    valid = []
    valid.append(b'HTTP/1.1 504 Gateway Timeout')
    valid.append(b'Content-Type: text/html; charset=UTF-8' + _CRLF)
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


def test_parse_request_not_get():
    request = []
    request.append(b'POST /path/to/URI HTTP/1.1')
    request.append(b'Host: www.google.com')
    request = (b'\r\n').join(request)
    with pytest.raises(TypeError):
        server.parse_request(request)


def test_parse_request_not_http_1_1():
    request = []
    request.append(b'GET /path/to/URI HTTP/1.0')
    request.append(b'Host: www.google.com')
    request = (b'\r\n').join(request)
    with pytest.raises(NotImplementedError):
        server.parse_request(request)


def test_parse_request_no_host():
    request = []
    request.append(b'GET /path/to/URI HTTP/1.0')
    with pytest.raises(Exception):
        server.parse_request(request)
