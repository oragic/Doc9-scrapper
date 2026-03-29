import httpx


class HttpClient:
    """
    Infrastructure HTTP client wrapping httpx.
    Handles mTLS configuration and exposes simple async methods.
    """

    def __init__(self, ca_path: str, cert_path: str):
        self._ca_path = ca_path
        self._cert_path = cert_path

    def _build_client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            verify=self._ca_path,
            cert=(self._cert_path, self._cert_path),
        )

    async def post(self, url: str, payload: dict) -> dict:
        async with self._build_client() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            return response.json()

    async def post_empty(self, url: str) -> dict:
        """POST with no body (used for init endpoints)."""
        async with self._build_client() as client:
            response = await client.post(url)
            response.raise_for_status()
            return response.json()