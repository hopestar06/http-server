from __future__ import unicode_literals
import socket
import os


_CRLF = b'\r\n'
_GET = b'GET'
_PROTOCOL = b'HTTP/1.1'
_HOST_PREFIX = b'Host:'
_WS = b' '

_RESPONSE_TEMPLATE = _CRLF.join([
    b'HTTP/1.1 {response_code} {response_reason}',
    b'Content-Type: {c_type}',
    b'Content-Length: {c_length}',
    b''])

_RESPONSE_ERROR_TEMPLATE = _CRLF.join([
    b'HTTP/1.1 {response_code} {response_reason}',
    b'Content-Type: text/html; charset=UTF-8',
    b''])


_HTML_START_TEMPLATE = b'<head>\n<body>\n<ul>'

_HTML_END_TEMPLATE = b'\n</ul>\n</body>\n</head>'


def root_dir():
    return os.path.dirname(os.path.abspath(__file__))


def response_ok(body, cont_type, c_length):
        response = create_header(200, b'OK', cont_type, c_length)
        response += body
        response += _CRLF
        return response


def response_error(response_code, response_reason):
    """ Return 500 Internal Server Error"""
    return _RESPONSE_ERROR_TEMPLATE.format(response_code=response_code,
                                           response_reason=response_reason)


def resolve_uri(uri):
    if '..' in uri:
        raise ValueError(b'Bad Request')
    body = b''
    path = root_dir() + uri
    try:
        if os.path.isdir(path):
            cont_type = b'dir'
            dir_contents = os.listdir(path)
            body = (_HTML_START_TEMPLATE +
                    create_contents_list(dir_contents) +
                    _HTML_END_TEMPLATE)
        else:
            cont_type = path.split('.')[-1]
            print 'starting get_file_content'
            body = body + get_file_content(path)
        return body, cont_type
    except:
        raise IOError


def parse_request(request):
    lines = request.split(_CRLF)

    # Validate the header line
    header = lines[0]
    header_pieces = header.split(_WS)
    if header_pieces[0] != _GET:
        raise TypeError(b'Method Not Allowed')
    elif header_pieces[2] != _PROTOCOL:
        raise NotImplementedError(b'HTTP Version Not Supported')
    # Validate the host line
    if len(lines) < 2:
        raise Exception(b'Bad Request')
    else:
        host_line = lines[1]
        host_line_pieces = host_line.split(_WS)
        if host_line_pieces[0] != _HOST_PREFIX:
            raise Exception(b'Bad Request')

    # Check for a blank line at the end
    if lines[2] != b'':
        raise SyntaxError(b'Bad Request')

    return header_pieces[1]


def create_contents_list(alist):
    result = b''
    for item in alist:
        result = result + '\n' + '<li>' + item + '</li>'
    return result


def get_file_content(filename):
    return get_file_handler(filename)


def get_file_size(filename):
    path = root_dir() + filename
    return len(get_file_handler(path))


def get_file_handler(filename):
    with open(filename) as f:
        print f
        return f.read()


# Creates HTML header
def create_header(r_code, r_reason, c_type, c_length):
    ct = get_content_type(c_type)
    return _RESPONSE_TEMPLATE.format(response_code=r_code,
                                     response_reason=r_reason,
                                     c_type=ct,
                                     c_length=c_length)


# Helper fuction: Returns the appropriate content-type
# for use in HTML header
def get_content_type(c_type):
    if c_type == 'txt':
        c_type = 'text/plain'
    elif c_type == 'html':
        c_type = 'text/html'
    elif c_type == 'png':
        c_type = 'image/png'
    elif c_type == 'jpg':
        c_type = 'image/jpeg'
    return c_type


def start_server():
    ADDR = ('127.0.0.1', 8000)

    s = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

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
                    break
            try:
                uri = parse_request(result)
                body, c_type = resolve_uri(uri)
                c_length = get_file_size(uri)
            except TypeError:
                response_error(405, 'Method Not allowed')
            except NotImplementedError:
                response_error(505, 'HTTP version not supported')
            except SyntaxError:
                response_error(400, 'Bad Request')
            except IOError:
                response_error(404, 'Not Found')
            except Exception:
                response_error(400, 'Bad Request')
            conn.sendall(response_ok(body, c_type, c_length))
            conn.close()
            break
        except KeyboardInterrupt:
            break

if __name__ == '__main__':
    start_server()
