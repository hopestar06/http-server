from __future__ import unicode_literals
import socket


_CRLF = b'\r\n'
_GET = b'GET'
_PROTOCOL = b'HTTP/1.1'
_HOST_PREFIX = b'Host:'
_WS = b' '

_RESPONSE_TEMPLATE = _CRLF.join([
    b'HTTP/1.1 {response_code} {response_reason}',
    b'Content-Type: text/html; charset=UTF-8',
    b''])


def response_ok():
    return _RESPONSE_TEMPLATE.format(response_code=b'200',
                                     response_reason=b'OK')


def response_error(response_code, response_reason):
    """ Return 500 Internal Server Error"""
    return _RESPONSE_TEMPLATE.format(response_code=response_code,
                                     response_reason=response_reason)


def parse_request(request):
    lines = request.split(_CRLF)

    # Validate the header line
    header = lines[0]
    header_pieces = header.split(_WS)
    if header_pieces[0] != _GET:
        raise TypeError(b'Method Not Allowed')
    elif header_pieces[2] != _PROTOCOL:
        raise ValueError(b'HTTP Version Not Supported')
    # Validate the host line
    host_line = lines[1]
    host_line_pieces = host_line.split(_WS)
    if host_line_pieces[0] != _HOST_PREFIX:
        raise Exception(b'Bad Request')

    # Check for a blank line at the end
    if lines[2] != b'':
        raise SyntaxError(b'Bad Request')

    return header[1]


def start_server():
    ADDR = ('127.0.0.1', 8000)

    s = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP)

    s.bind(ADDR)
    s.listen(1)
    while True:
        result = b''
        try:
            conn, addr = s.accept()
            while True:
                msg = conn.recv(1024)
                result += msg
                if len(msg) < 1024:
                    print result
            try:
                parse_request(result)
            except TypeError:
                response_error(405, 'Method Not allowed')
            except ValueError:
                response_error(505, 'HTTP version not supported')
            except Exception:
                response_error(400, 'Bad Request')
            except SyntaxError:
                response_error(400, 'Bad Request')
            conn.sendall(response_ok())
            conn.close()
            break
        except KeyboardInterrupt:
            break

if __name__ == '__main__':
    start_server()
