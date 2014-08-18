import socket

from io import BytesIO

try:
    from BaseHTTPServer import BaseHTTPRequestHandler
except ImportError:
    from http.server import BaseHTTPRequestHandler


class HTTPRequest(BaseHTTPRequestHandler):
    def __init__(self, request_text):
        self.rfile = BytesIO(request_text)
        self.raw_requestline = self.rfile.readline()
        self.error_code = self.error_message = None
        self.parse_request()

    def send_error(self, code, message):
        self.error_code = code
        self.error_message = message


class HTTPServer(object):
    def __init__(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = self.host = self.port = None
        self.bound = False

    @property
    def url(self):
        return "http://{0}:{1}/".format(self.host, self.port)

    def bind(self, host="127.0.0.1", port=0):
        try:
            self.socket.bind((host, port))
        except socket.error as err:
            raise OSError(err)

        self.socket.listen(1)
        self.bound = True
        self.host, self.port = self.socket.getsockname()

    def open(self, timeout=30):
        self.socket.settimeout(timeout)

        try:
            conn, addr = self.socket.accept()
            conn.settimeout(None)
        except socket.timeout:
            raise OSError("Socket accept timed out")

        try:
            req_data = conn.recv(1024)
        except socket.error:
            raise OSError("Failed to read data from socket")

        req = HTTPRequest(req_data)

        conn.send(b"HTTP/1.1 200 OK\r\n")
        conn.send(b"Server: Livestreamer\r\n")
        conn.send(b"\r\n")
        self.conn = conn

        return req

    def write(self, data):
        if not self.conn:
            raise IOError("No connection")

        self.conn.sendall(data)

    def close(self, client_only=False):
        if self.conn:
            self.conn.close()

        if not client_only:
            self.socket.close()

