import asyncio

from dotenv import load_dotenv

from src.core.http.client import HttpClient
from src.core.http.websocket_client import WebSocketClient
from src.core.infra.config import load_config
from src.services.scraper_service import ScraperService

load_dotenv()


async def main() -> None:
    config = load_config()

    http_client = HttpClient(ca_path=config.ca_path, cert_path=config.cert_path)
    ws_client = WebSocketClient(ca_path=config.ca_path, cert_path=config.cert_path)

    service = ScraperService(
        base_url=config.base_url,
        username=config.username,
        password=config.password,
        http_client=http_client,
        ws_client=ws_client,
    )

    result = await service.run(level=config.level)

    print(f"TOKEN:          {result['token']}")
    print(f"EXECUTION TIME: {result['execution_time_seconds']}s")


if __name__ == "__main__":
    asyncio.run(main())