from __future__ import unicode_literals
import socket
import os
import sys
import mimetypes
import server
from gevent.server import StreamServer
from gevent.monkey import patch_all


def echo(socket, address):
    result = b''
    body = ''
    c_type = ''
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
            socket.sendall(server.response_ok(body, c_type))
        else:
            socket.close()
            break



if __name__ == '__main__':
    patch_all()
    serv = StreamServer(('127.0.0.1', 10000), echo)
    print ('Starting server on port 10000')
    serv.serve_forever()

'''
    
      try:
                uri = server.parse_request(result)
                body, c_type = server.resolve_uri(uri)
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
            socket.sendall(server.response_ok(body, c_type))
            socket.close()
            break
'''