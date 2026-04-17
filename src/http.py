import os, json

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class Http:
    """Utility class to build and parse simple HTTP messages over a raw socket.

    It reads environment variables for Cloudflare Access credentials and
    provides methods to construct request headers, parse status lines, headers
    and bodies, and manage the authentication cookie.
    """

    def __init__(self, host):
        """Create an Http helper for *host*.

        The *host* is used when building the ``Host`` header.
        """
        self.host = host
        self.cookie = None
        self.USE_REMOTE = False
        if self.USE_REMOTE:
            CLIENT_ID = os.getenv("ACCESS_CLIENT_ID")
            if not CLIENT_ID:
                raise Exception("ACCESS_CLIENT_ID environment variable not set")
            CLIENT_SECRET = os.getenv("ACCESS_CLIENT_SECRET")
            if not CLIENT_SECRET:
                raise Exception("ACCESS_CLIENT_SECRET environment variable not set")
            host = os.getenv("HOST")
            if not host:
                raise Exception("HOST environment variable not set")

    def set_cookie(self, set_cookie):
        """Extract and store the authentication cookie from a ``Set-Cookie`` header.

        Raises an exception if the header is missing or does not contain an
        ``Authorization`` token.
        """
        if set_cookie is None:
            raise Exception("Invalid response")
        if "Authorization" not in set_cookie:
            raise Exception("Not authorized")
        cookie = set_cookie.split(';')[0]
        self.cookie = cookie

    def read_status(self, reader):
        """Read the HTTP status line from *reader* and return it stripped."""
        status_line = reader.readline().strip()
        return status_line

    def read_header(self, reader):
        """Read HTTP headers from *reader* until an empty line and return a dict."""
        response_headers = {}
        while True:
            line = reader.readline().strip()
            if line == "":
                break
            name, _, value = line.partition(":")
            response_headers[name.strip()] = value.strip()
        return response_headers

    def read_response(self, reader):
        """Read a full HTTP response, raising on 403 and returning the body line."""
        if "403" in self.read_status(reader):
            raise Exception("Authorization denied")
        self.read_header(reader)
        return reader.readline()

    def create_header(self, body_size, method):
        """Build a list of HTTP header lines for a request.

        Parameters:
            body_size: Length of the request body in bytes.
            method: HTTP method string (e.g., ``"POST"``).
        """
        request_line = f"{method} / HTTP/1.1"
        header = [
            request_line,
            f"Host: {self.host}",
            "User-Agent: python-socket-client/1.0",
            "Content-Type: application/json; charset=utf-8",
            f"Content-Length: {body_size}",
            "Connection: keep-alive"
        ]
        if self.USE_REMOTE:
            if self.cookie is not None:
                header.append(f"Cookie: {self.cookie}")
            header.extend([f"CF-Access-Client-Id: {self.CLIENT_ID}", f"CF-Access-Client-Secret: {self.CLIENT_SECRET}"])
        return header
