import socket, ssl
from http import Http

class Client:

    host = "iaorc.ceugenio.org"
    USE_REMOTE = False

    def __init__(self):
        self.context = None
        self.plain_sock = None
        self.sock = None
        self.reader = None
        self.http = Http(self.host)

    def close(self):
        if self.sock is not None: self.sock.close()

    def connect(self):
        if self.USE_REMOTE:
            plain_sock = socket.create_connection((self.host, 443))
            context = ssl.create_default_context()
            # Disabilitata la verifica del certificato solo per scopi di test!
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            # Wrappiamo il socket con TLS
            self.sock = context.wrap_socket(plain_sock, server_hostname=self.host)
            print(f"[TLS]  Versione: {self.sock.version()}")
        else:
            self.sock = socket.create_connection((None, 5433))
        print(f"[CONN] Connesso a {self.host}")
        self.reader = self.sock.makefile("r", encoding="utf-8", newline="\r\n")
    
    def authenticate(self, data_for_server):
        self.send(data_for_server, "POST")
        if "502" in self.http.read_status(self.reader):
            raise Exception("Server not available")
        response_header = self.http.read_header(self.reader)
        if self.USE_REMOTE:
            set_cookie = response_header.get("set-cookie")
            self.http.set_cookie(set_cookie)
        return self.reader.readline() # http body

    def send(self, body: bytes, method: str):
        header = self.http.create_header(len(body + b'\r\n') if body is not None else 0, method)
        header_section = "\r\n".join(header) + "\r\n\r\n"
        http_message = header_section.encode("utf-8")
        if body is not None: http_message +=  body + b'\r\n'
        self.sock.sendall(http_message)
        print("[SEND] In attesa della risposta…")

    def get_message(self):
        return self.http.read_response(self.reader)
