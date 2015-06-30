from __future__ import unicode_literals
import socket

ADDR = ('127.0.0.1', 8018)

client = socket.socket(
    socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP
)

client.connect(ADDR)
msg = "do you hear me?"

try:
    client.sendall(msg)
    while True:
        part = client.recv(1024)
        client.shutdown(socket.SHUT_WR)
        print part
        if len(part) < 1024:
            client.close()
            break
except Exception as e:
    print e
