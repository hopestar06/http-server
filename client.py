from __future__ import unicode_literals
import socket

ADDR = ('127.0.0.1', 10000)

client = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP
)

client.connect(ADDR)
request = []
request.append(b'GET /webroot/a_web_page.html HTTP/1.1')
request.append(b'Host: www.google.com')
request.append(b'')
request = (b'\r\n').join(request)

try:
    client.sendall(request)
    while True:
        part = client.recv(1024)
        client.shutdown(socket.SHUT_WR)
        print part
        if len(part) < 1024:
            client.close()
            break
except Exception as e:
    print e
