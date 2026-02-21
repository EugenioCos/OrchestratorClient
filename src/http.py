import os, json

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


class Http:
    """
    Http helper that builds requests and parses responses.
    The Cloudflare Access headers are optional – they are added only
    when the corresponding environment variables are defined.
    """

    # ------------------------------------------------------------------
    # Lettura (opzionale) delle credenziali Cloudflare Access.
    # Se non sono impostate, continuiamo comunque.
    # ------------------------------------------------------------------
    CLIENT_ID = os.getenv("ACCESS_CLIENT_ID")
    CLIENT_SECRET = os.getenv("ACCESS_CLIENT_SECRET")
    # NOTE: non solleviamo più eccezioni qui; i controlli saranno fatti
    #       solo al momento della costruzione dell'header.

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
            "Connection: keep-alive",
        ]
        # Add cookie if we already received one
        if self.cookie is not None:
            header.append(f"Cookie: {self.cookie}")
        # Add Cloudflare Access headers only when they are defined
        if self.CLIENT_ID:
            header.append(f"CF-Access-Client-Id: {self.CLIENT_ID}")
        if self.CLIENT_SECRET:
            header.append(f"CF-Access-Client-Secret: {self.CLIENT_SECRET}")
        return header

