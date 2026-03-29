# DOC9 Scraper

Automation tool for testing authenticated login flows (easy / hard / extreme).

---

## Requirements

- Python 3.11+
- Virtual environment (recommended)

---

## Setup

**1. Clone and enter the project**
```bash
cd doc9
```

**2. Create and activate the virtual environment**
```bash
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` with your values:
```env
APP_BASE_URL=https://localhost:3000
APP_USERNAME=your_username
APP_PASSWORD=your_password
APP_LEVEL=extreme        # easy | hard | extreme
```

**5. Place certificates**

Copy `ca.crt` and `client.pem` into:
```
src/core/infra/certs/
```

---

## Running

```bash
python -m src.main
```

---

## Project Structure

```
src/
├── core/
│   ├── auth/
│   │   └── crypto.py          # Challenge generation, POW solver, AES decryption
│   ├── http/
│   │   ├── client.py          # HTTP client (httpx wrapper)
│   │   └── websocket_client.py
│   └── infra/
│       ├── certs/             # ca.crt, client.pem
│       └── config.py          # Loads settings from .env
└── services/
    └── scraper_service.py     # Orchestrates the login flows
```