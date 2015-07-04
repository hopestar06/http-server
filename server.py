from __future__ import unicode_literals
import socket
import os
import sys
import mimetypes

current_file_path = os.path.abspath(__file__)
root_dir = os.path.dirname(current_file_path)

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


# Given an http body and content type
# Creates and returns a correctly formatted http header with body
def response_ok(body, cont_type):
        c_length = sys.getsizeof(body)
        response = create_header(200, b'OK', cont_type, c_length)
        response += '\r\n' + body
        return response


# Given an http response code and reaponse reason
# Return an http formatted response
def response_error(response_code, response_reason):
    """ Return 500 Internal Server Error"""
    return _RESPONSE_ERROR_TEMPLATE.format(response_code=response_code,
                                     response_reason=response_reason)


# Takes as a argument, a uri.
# If the uri is a directory, return the list of the directory contents
# and the content type.
# If the uri is a file, return the contents of the file
# and the content type
# If uri is invalid or file cannot be opened raises and IOError
def resolve_uri(uri):
    body = b''
    path = root_dir + uri
    try:
        if os.path.isdir(path):
            cont_type = b'text/html'
            dir_contents = os.listdir(path)
            body = ('<head><body><p>' + path +'</p>'+
                    create_contents_list(dir_contents) +
                    '</ul></body></head>')
        elif os.path.isfile(path):
            cont_type, encoding = mimetypes.guess_type(uri)
            #cont_type = path.split('.')[-1]
            body = body + get_file_content(path)
        return body, cont_type
    except:
        raise IOError


# Takes in an http request, parses the request
# Returns the uri contained in the request
# If request is not a 'GET'request or is not
# http-formatted, an error will be raised 
def parse_request(request):
    lines = request.split(_CRLF)

    # Validate the header line
    header = lines[0]
    header_pieces = header.split(_WS)
    if header_pieces[0] != _GET:
        raise TypeError 
        #(b'Method Not Allowed')
    elif header_pieces[2] != _PROTOCOL:
        raise ValueError(b'HTTP Version Not Supported')
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

# Takes as a parameter a list of the contents of a directory
# and returns an html formatted listing of the directory contents
def create_contents_list(alist):
    result = b''
    for item in alist:
        result = result + '<li>' + item + '</li>'
    return result

# Given path of a file, returns the contents of a file
def get_file_content(filename):
    with open(filename) as f:
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
        body = ''
        c_type = ''
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
            except TypeError:
                conn.sendall(response_error(405, 'Method Not allowed'))
            except ValueError:
                conn.sendall(response_error(505, 'HTTP version not supported'))
            except SyntaxError:
                conn.sendall(response_error(400, 'Bad Request2'))
            except IOError:
                conn.sendall(response_error(404, 'Not Found'))
            except Exception:
                conn.sendall(response_error(400, 'Bad Request1'))
            conn.sendall(response_ok(body, c_type))
            conn.close()
            break
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    start_server()
