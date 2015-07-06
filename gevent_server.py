from __future__ import unicode_literals
import server
import socket
import os
import sys
import mimetypes


def echo(socket, address):
    result = b''
    body = ''
    c_type = ''
    c_length = ''
    while True:
        while True:
            data = socket.recv(1024)
            result += data
            if len(data) < 1024:
                break
        if data:
            try:
                uri = server.parse_request(result)
                body, c_type = server.resolve_uri(uri)
                c_length = server.get_file_size(uri)
            except TypeError:
                socket.sendall(server.response_error(405, 'Method Not allowed'))
            except ValueError:
                socket.sendall(server.response_error(505, 'HTTP version not supported'))
            except SyntaxError:
                socket.sendall(server.response_error(400, 'Bad Request2'))
            except IOError:
                socket.sendall(server.response_error(404, 'Not Found'))
            except Exception:
                socket.sendall(server.response_error(400, 'Bad Request1'))
            socket.sendall(server.response_ok(body, c_type, c_length))
        else:
            socket.close()
            break


def start_gserver():
    from gevent.server import StreamServer
    from gevent.monkey import patch_all
    patch_all()
    serv = StreamServer(('127.0.0.1', 10000), echo)
    print('Starting server on port1000')
    serv.serve_forever()


if __name__ == '__main__':
    start_gserver()
