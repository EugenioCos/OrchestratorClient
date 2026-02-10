import os, json

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Http:

    CLIENT_ID = os.getenv("ACCESS_CLIENT_ID")
    if not CLIENT_ID:
        raise Exception("ACCESS_CLIENT_ID environment variable not set")
    CLIENT_SECRET = os.getenv("ACCESS_CLIENT_SECRET")
    if not CLIENT_SECRET:
        raise Exception("ACCESS_CLIENT_SECRET environment variable not set")

    def __init__(self, host):
        self.host = host
        self.cookie = None

    def set_cookie(self, set_cookie):
        if set_cookie is None:
            raise Exception("Invalid response")
        if "Authorization" not in set_cookie:
            raise Exception("Not authorized")
        cookie = set_cookie.split(';')[0]
        self.cookie = cookie

    def read_status(self, reader):
        status_line = reader.readline().strip()
        return status_line

    def read_header(self, reader):
        response_headers = {}
        while True:
            line = reader.readline().strip()
            if line == "":
                break
            name, _, value = line.partition(":")
            response_headers[name.strip()] = value.strip()
        return response_headers

    def read_response(self, reader):
        if "403" in self.read_status(reader):
            raise Exception("Authorization denied")
        self.read_header(reader)
        return reader.readline()

    def create_header(self, body_size, method):
        request_line = f"{method} / HTTP/1.1"
        header = [
            request_line,
            f"Host: {self.host}",
            "User-Agent: python-socket-client/1.0",
            "Content-Type: application/json; charset=utf-8",
            f"Content-Length: {body_size}",
            "Connection: keep-alive"
        ]
        if self.cookie is not None:
            header.append(f"Cookie: {self.cookie}")
        header.extend([f"CF-Access-Client-Id: {self.CLIENT_ID}", f"CF-Access-Client-Secret: {self.CLIENT_SECRET}"])
        return header
