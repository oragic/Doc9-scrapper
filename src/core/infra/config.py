import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    base_url: str
    username: str
    password: str
    ca_path: str
    cert_path: str
    level: str


def load_config() -> AppConfig:
    """
    Load application configuration from environment variables.

    Required variables:
        APP_BASE_URL   – e.g. https://localhost:3000
        APP_USERNAME
        APP_PASSWORD
        APP_LEVEL      – easy | hard | extreme  (default: extreme)

    Optional (default to files next to main.py):
        APP_CA_PATH    – path to CA certificate
        APP_CERT_PATH  – path to client certificate/key PEM
    """
    this_file = os.path.abspath(__file__)          
    infra_dir = os.path.dirname(this_file)          
    default_cert_dir = os.path.join(infra_dir, "certs")

    base_url = os.environ.get("APP_BASE_URL")
    username = os.environ.get("APP_USERNAME")
    password = os.environ.get("APP_PASSWORD")

    missing = [k for k, v in {"APP_BASE_URL": base_url, "APP_USERNAME": username, "APP_PASSWORD": password}.items() if not v]
    if missing:
        raise EnvironmentError(f"Missing required environment variables: {', '.join(missing)}")

    return AppConfig(
        base_url=base_url,
        username=username,
        password=password,
        ca_path=os.environ.get("APP_CA_PATH", os.path.join(default_cert_dir, "ca.crt")),
        cert_path=os.environ.get("APP_CERT_PATH", os.path.join(default_cert_dir, "client.pem")),
        level=os.environ.get("APP_LEVEL", "extreme"),
    )