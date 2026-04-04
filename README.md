# WhatsApp MCP Server

<!-- mcp-name: io.github.nakulben/whatsapp-mcp -->

Manage WhatsApp Business templates and send messages from **Claude, ChatGPT, Cursor, VS Code Copilot**, or any MCP-compatible client — powered by the Meta Cloud API.

<p align="center">
  <img src="https://img.shields.io/badge/MCP-compatible-blue" alt="MCP Compatible" />
  <img src="https://img.shields.io/badge/Meta_Cloud_API-v24.0-green" alt="Meta API v24.0" />
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

```bash
cp .env.example .env
```

```env
META_ACCESS_TOKEN=your_access_token
META_WABA_ID=your_whatsapp_business_account_id
META_PHONE_NUMBER_ID=your_phone_number_id
META_APP_ID=your_app_id              # Optional, for media uploads
META_API_VERSION=v24.0               # Optional, defaults to v24.0
```

Environment variables are used by **all modes** — local stdio and hosted remote.

> **How to get these?** Go to [Meta for Developers](https://developers.facebook.com/), create or select your app, navigate to WhatsApp > API Setup.

### 3. Connect to Your MCP Client

The server supports **3 transport modes**:

| Transport | Command | Used By |
|---|---|---|
| `stdio` (default) | `python -m whatsapp_mcp` | Claude Desktop, Cursor, VS Code, Windsurf |
| `sse` | `python -m whatsapp_mcp --transport sse` | Legacy remote clients |
| `streamable-http` | `python -m whatsapp_mcp --transport streamable-http` | Claude.ai, ChatGPT, newer MCP clients |

For HTTP transports, you can customize host/port:
```bash
python -m whatsapp_mcp --transport streamable-http --host 0.0.0.0 --port 8000
```

---

#### Claude Desktop (stdio — local)

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

#### Claude.ai Web (remote — streamable-http)

Claude.ai connects to remote MCP servers as [custom connectors](https://support.claude.com/en/articles/11175166-get-started-with-custom-connectors-using-remote-mcp). The connection originates from Anthropic's cloud servers, not from your machine.

1. Host the server with env vars configured, behind HTTPS:
   ```bash
   python -m whatsapp_mcp --transport streamable-http --host 0.0.0.0 --port 8001
   ```
2. Put it behind HTTPS using nginx, Caddy, or a tunnel (ngrok, Cloudflare Tunnel)
3. In Claude.ai: go to [Customize > Connectors](https://claude.ai/customize/connectors) → Add custom connector
4. Enter your server URL (e.g. `https://your-domain.com/mcp/`)
5. Claude supports **authless** or **OAuth-based** servers. For simplest setup, leave auth blank — the server will use the env vars you configured in step 1.

> **Note:** Claude.ai does not support custom request headers. The server must be pre-configured with Meta credentials via environment variables. Each hosted server serves one WhatsApp Business Account.

<details>
<summary>Example nginx config</summary>

```nginx
location /mcp/ {
    proxy_pass http://127.0.0.1:8001/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_read_timeout 86400;
}
```
</details>

#### ChatGPT (remote — Responses API)

ChatGPT supports remote MCP servers via the [Responses API](https://developers.openai.com/api/docs/guides/tools-connectors-mcp). It supports both Streamable HTTP and SSE transports.

**Option 1 — Server pre-configured with env vars (simplest):**

```python
from openai import OpenAI
client = OpenAI()
resp = client.responses.create(
    model="gpt-4.1",
    tools=[{
        "type": "mcp",
        "server_label": "whatsapp",
        "server_url": "https://your-domain.com/mcp/",
        "require_approval": "never",
    }],
    input="List all my approved templates",
)
```

**Option 2 — Per-request credentials via Bearer token:**

Encode your Meta credentials as base64 JSON and pass them in the `authorization` field.
OpenAI forwards this value as the `Authorization` header to your MCP server:

```bash
# Create the token
echo -n '{"access_token":"EAA...","phone_number_id":"123","waba_id":"456"}' | base64
# Output: eyJhY2Nlc3NfdG9rZW4iOiJFQUEuLi4iLCJwaG9uZV9udW1iZXJfaWQiOiIxMjMiLCJ3YWJhX2lkIjoiNDU2In0=
```

```python
resp = client.responses.create(
    model="gpt-4.1",
    tools=[{
        "type": "mcp",
        "server_label": "whatsapp",
        "server_url": "https://your-domain.com/mcp/",
        "authorization": "eyJhY2Nlc3NfdG9rZW4iOiJFQUEuLi4iLCJwaG9uZV9udW1iZXJfaWQiOiIxMjMiLCJ3YWJhX2lkIjoiNDU2In0=",
        "require_approval": "never",
    }],
    input="List all my approved templates",
)
```

> **Note:** ChatGPT only supports remote MCP servers (no local stdio). Your server must be publicly accessible over HTTPS.

#### Cursor (stdio)

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

#### VS Code Copilot (stdio)

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

#### Per-Request Credentials (direct HTTP / curl / scripts)

For programmatic access or custom MCP clients, you can pass per-request credentials instead of relying on server env vars. Two methods are supported:

**Method 1 — Bearer token (recommended):**

Base64-encode a JSON object with your Meta credentials:

```bash
# Create the token
TOKEN=$(echo -n '{"access_token":"EAA...","phone_number_id":"123","waba_id":"456"}' | base64)

# Use it
curl -H "Authorization: Bearer $TOKEN" https://your-server.com/mcp/ ...
```

Required fields: `access_token`, `phone_number_id`, `waba_id`. Optional: `app_id`, `api_version`.

**Method 2 — X-Meta-* headers:**

| Header | Required | Description |
|---|---|---|
| `X-Meta-Access-Token` | Yes | Your Meta access token |
| `X-Meta-Phone-Number-Id` | Yes | Your WhatsApp phone number ID |
| `X-Meta-Business-Account-Id` | Yes | Your WhatsApp Business Account ID |
| `X-Meta-App-Id` | No | Your Meta app ID (for media uploads) |
| `X-Meta-Api-Version` | No | API version (defaults to v24.0) |

If neither Bearer token nor X-Meta-* headers are present, the server falls back to environment variables.

## Usage Examples

Once connected, just talk to your AI assistant:

> "Create a marketing template called `summer_sale` with a header image, body text about 50% off, and a Shop Now button"

> "List all my approved templates"

> "Send the `order_confirmation` template to +919876543210 with order number ORD-456"

> "Validate this template before I submit it: ..."

> "Check the status of template ID 123456789"

## Supported Template Types

Meta's API has **2 template categories**(excluding Authentication). Within each category, templates can have different **structural variants** — each with its own component layout and validation rules.

### Marketing Templates

| Structural Variant | Create | Send | Key Components |
|---|---|---|---|
| Text / Image / Video / Document | ✅ | ✅ | Header (optional) + Body + Footer + Buttons |
| Carousel | ✅ | ✅ | Cards with per-card header, body, buttons |
| Catalog | ✅ | ✅ | Body + `CATALOG` button |
| Limited-Time Offer (LTO) | ✅ | ✅ | Body + `limited_time_offer` component + copy code button |
| Coupon Code | ✅ | ✅ | Body + `copy_code` button |
| Multi-Product Message (MPM) | ✅ | ✅ | Body + `product_list` action with sections |
| Single-Product Message (SPM) | ✅ | ✅ | Body + `product` action |
| Product Card Carousel | ✅ | ✅ | Body + product cards with buttons |
| Call Permission | ✅ | — | Body + `call_permission` button |

### Utility Templates

| Structural Variant | Create | Send | Key Components |
|---|---|---|---|
| Text / Image / Video / Document | ✅ | ✅ | Header (optional) + Body + Footer + Buttons |
| Order Details | ✅ | ✅ | Body + `order_details` button with payment payload |
| Order Status | ✅ | ✅ | Body + order status parameters |

> **How routing works:** When you call `create_template`, the server inspects the components to auto-detect the structural variant (e.g., presence of `cards[]` → Carousel, `CATALOG` button → Catalog) and applies the correct validator. You just pass `category: "MARKETING"` or `"UTILITY"` — the variant is determined from the component structure.

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
│   ├── middleware.py         # ASGI middleware for per-request credentials
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

Built by [Jina Connect](https://jinaconnect.jinacode.systems/) — the WhatsApp Business CX platform.
