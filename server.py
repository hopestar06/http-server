from __future__ import unicode_literals
import socket


def response_ok():
    header = 'HTTP/1.1 200 OK\nContent-Type: text/html'
    body = '<html><body>200 OK</body></html>'
    return header + body


def response_error():
    response = 'HTTP/1.1 500 Internal Server Error\n'
    return response


def start_server():
    ADDR = ('127.0.0.1', 8000)

    s = socket.socket(
        socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_IP)

    s.bind(ADDR)
    s.listen(1)
    result = ''
    while True:
        try:
            conn, addr = s.accept()
            while True:
                msg = conn.recv(1024)
                result += msg
                if len(msg) < 1024:
                    print result
                    conn.sendall(response_ok())
                    conn.close()
                    break
        except KeyboardInterrupt:
            break

if __name__ == '__main__':
    start_server()
