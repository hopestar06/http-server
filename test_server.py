import server
import socket
import pytest
from multiprocessing import Process

ADDR = ('127.0.0.1', 8080)


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
    client.connect(ADDR)
    return client


def test_response_ok(server_setup):
    assert '200 OK' in server.response_ok()


def test_response_error(server_setup):
    assert '500 Internal Server Error' in server.response_error()
