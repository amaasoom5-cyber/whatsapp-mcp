# WhatsApp MCP Server

Manage WhatsApp Business templates and send messages from **Claude, Cursor, VS Code Copilot**, or any MCP-compatible client — powered by the Meta Cloud API.

<p align="center">
  <img src="https://img.shields.io/badge/MCP-compatible-blue" alt="MCP Compatible" />
  <img src="https://img.shields.io/badge/Meta_Cloud_API-v21.0-green" alt="Meta API v21.0" />
  <img src="https://img.shields.io/badge/license-MIT-blue" alt="MIT License" />
  <img src="https://img.shields.io/badge/python-3.10+-yellow" alt="Python 3.10+" />
</p>

## What It Does

| Tool | Description |
|------|-------------|
| `validate_template` | Validate a template payload before submitting to Meta |
| `create_template` | Submit a template for Meta approval |
| `list_templates` | List templates with optional filters (status, category, name) |
| `get_template_detail` | Get full details of a template by ID |
| `check_template_status` | Quick status check for a template |
| `delete_template` | Delete a template by name |
| `send_template_message` | Send an approved template to a phone number |
| `send_bulk_template_messages` | Send an approved template to multiple phone numbers |

**8 tools** covering the full template lifecycle: create → validate → approve → send.

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/nakulben/whatsapp-mcp.git
cd whatsapp-mcp
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Credentials

Copy `.env.example` to `.env` and fill in your Meta credentials:

```bash
cp .env.example .env
```

```env
META_ACCESS_TOKEN=your_access_token
META_WABA_ID=your_whatsapp_business_account_id
META_PHONE_NUMBER_ID=your_phone_number_id
META_APP_ID=your_app_id              # Required for media uploads
META_API_VERSION=v21.0               # Optional, defaults to v21.0
```

> **How to get these?** Go to [Meta for Developers](https://developers.facebook.com/), create or select your app, navigate to WhatsApp > API Setup.

### 3. Connect to Your MCP Client

#### Claude Desktop

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "whatsapp": {
      "command": "/path/to/whatsapp-mcp/venv/bin/python",
      "args": ["-m", "whatsapp_mcp"],
      "env": {
        "META_ACCESS_TOKEN": "your_access_token",
        "META_WABA_ID": "your_waba_id",
        "META_PHONE_NUMBER_ID": "your_phone_number_id",
        "META_APP_ID": "your_app_id"
      }
    }
  }
}
```

#### Cursor

Add to `.cursor/mcp.json` in your project:

```json
{
  "mcpServers": {
    "whatsapp": {
      "command": "/path/to/whatsapp-mcp/venv/bin/python",
      "args": ["-m", "whatsapp_mcp"]
    }
  }
}
```

#### VS Code Copilot

Add to `.vscode/mcp.json`:

```json
{
  "servers": {
    "whatsapp": {
      "type": "stdio",
      "command": "/path/to/whatsapp-mcp/venv/bin/python",
      "args": ["-m", "whatsapp_mcp"]
    }
  }
}
```

## Usage Examples

Once connected, just talk to your AI assistant:

> "Create a marketing template called `summer_sale` with a header image, body text about 50% off, and a Shop Now button"

> "List all my approved templates"

> "Send the `order_confirmation` template to +919876543210 with order number ORD-456"

> "Validate this template before I submit it: ..."

> "Check the status of template ID 123456789"

## Supported Template Types

| Type | Create | Send |
|------|--------|------|
| Marketing | ✅ | ✅ |
| Utility | ✅ | ✅ |
| Carousel | ✅ | ✅ |
| Catalog | ✅ | ✅ |
| Limited-Time Offer (LTO) | ✅ | ✅ |
| Coupon Code | ✅ | ✅ |
| Order Details | ✅ | ✅ |
| Order Status | ✅ | ✅ |
| Multi-Product Message (MPM) | ✅ | ✅ |
| Single-Product Message (SPM) | ✅ | ✅ |
| Product Card Carousel | ✅ | ✅ |
| Call Permission | ✅ | — |

## Running Tests

```bash
pip install pytest pytest-asyncio
python -m pytest tests/ -v
```

## Project Structure

```
whatsapp-mcp/
├── whatsapp_mcp/
│   ├── __init__.py          # Package version
│   ├── __main__.py          # Entry point (python -m whatsapp_mcp)
│   ├── config.py            # Environment config loader
│   ├── meta_api.py          # Async Meta Graph API client
│   ├── server.py            # MCP server with 8 tools
│   ├── models/              # Pydantic data models
│   │   ├── body.py          # Body component
│   │   ├── header.py        # Header component (text/image/video/document)
│   │   ├── footer.py        # Footer component
│   │   ├── buttons.py       # Button types (URL, phone, quick reply, etc.)
│   │   ├── buttons_component.py
│   │   ├── enums.py         # Template categories, types, formats
│   │   └── order_models.py  # Order-related models (checkout templates)
│   └── validators/
│       ├── create/          # 12 template creation validators
│       └── send/            # 11 template send validators
├── tests/
│   ├── test_validators.py   # Validator tests
│   ├── test_meta_api.py     # API client tests (mocked HTTP)
│   └── test_tools.py        # MCP tool registration & helper tests
├── .env.example
├── requirements.txt
├── LICENSE                  # MIT
└── ROADMAP.md
```

## Requirements

- Python 3.10+
- Meta WhatsApp Business Account
- System User access token with `whatsapp_business_messaging` and `whatsapp_business_management` permissions

### Dependencies

| Package | Purpose |
|---------|---------|
| `mcp` | Model Context Protocol SDK |
| `httpx` | Async HTTP client for Meta API |
| `pydantic` | Payload validation |
| `python-dotenv` | Environment config |

## Roadmap

See [ROADMAP.md](ROADMAP.md) for planned features.

## License

MIT — see [LICENSE](LICENSE).

---

Built by [Jina Connect](https://jinaconnect.com) — the WhatsApp Business CX platform.
