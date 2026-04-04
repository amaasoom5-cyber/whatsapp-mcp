# WhatsApp MCP Server

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

The server supports **two credential modes** depending on how you run it:

#### Option A: Environment Variables (local / stdio)

For local use with Claude Desktop, Cursor, VS Code, etc.:

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

#### Option B: HTTP Headers (hosted / remote)

For Claude.ai web, ChatGPT, and other remote clients — each user passes their **own** Meta credentials via request headers. No credentials are stored on the server.

| Header | Required | Description |
|---|---|---|
| `X-Meta-Access-Token` | Yes | Your Meta access token |
| `X-Meta-Phone-Number-Id` | Yes | Your WhatsApp phone number ID |
| `X-Meta-Business-Account-Id` | Yes | Your WhatsApp Business Account ID |
| `X-Meta-App-Id` | No | Your Meta app ID (for media uploads) |
| `X-Meta-Api-Version` | No | API version (defaults to v24.0) |

> **How to get these?** Go to [Meta for Developers](https://developers.facebook.com/), create or select your app, navigate to WhatsApp > API Setup.

### 3. Connect to Your MCP Client

The server supports **3 transport modes**:

| Transport | Command | Credentials | Used By |
|---|---|---|---|
| `stdio` (default) | `python -m whatsapp_mcp` | Env vars | Claude Desktop, Cursor, VS Code, Windsurf |
| `sse` | `python -m whatsapp_mcp --transport sse` | HTTP headers | ChatGPT, remote clients |
| `streamable-http` | `python -m whatsapp_mcp --transport streamable-http` | HTTP headers | Claude.ai web, newer MCP clients |

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

Claude.ai web connects to remote MCP servers over HTTPS. Users provide their **own** Meta credentials via headers — no credentials are stored on the server.

**If a hosted instance is available** (e.g. `https://your-domain.com/mcp/`):

1. In Claude.ai: Settings → MCP Servers → Add Remote Server
2. Enter the server URL and your credentials as custom headers:
   - URL: `https://your-domain.com/mcp/`
   - `X-Meta-Access-Token`: your Meta access token
   - `X-Meta-Phone-Number-Id`: your phone number ID
   - `X-Meta-Business-Account-Id`: your WABA ID

**If self-hosting:**

1. Start the server: `python -m whatsapp_mcp --transport streamable-http --host 0.0.0.0 --port 8001`
2. Put it behind HTTPS using nginx, Caddy, or a tunnel (ngrok, Cloudflare Tunnel)
3. Connect from Claude.ai with your credentials as headers (see above)

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

#### ChatGPT (remote)

1. Start the server: `python -m whatsapp_mcp --transport sse --host 0.0.0.0 --port 8000`
2. Expose to the internet (ngrok, Cloudflare Tunnel, or deploy to a VPS)
3. In ChatGPT: Settings → Developer Mode → Add MCP Server → enter your server URL
4. Add your Meta credentials as custom headers (same `X-Meta-*` headers as above)

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
