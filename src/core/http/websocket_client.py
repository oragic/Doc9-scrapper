import ssl


class WebSocketClient:
    """
    Infrastructure WebSocket client.
    Holds mTLS configuration so callers can build an ssl.SSLContext from it.
    The actual connect/send/recv is done inline in the service to keep
    fine-grained control over the protocol flow.
    """

    def __init__(self, ca_path: str, cert_path: str):
        self.ca_path = ca_path
        self.cert_path = cert_path

    def build_ssl_context(self) -> ssl.SSLContext:
        ctx = ssl.create_default_context(cafile=self.ca_path)
        ctx.load_cert_chain(self.cert_path)
        return ctx