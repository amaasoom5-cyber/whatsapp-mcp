# Roadmap

## v0.1.0 — Template Management & Sending (Current)

- [x] 8 MCP tools (6 template + 2 sending)
- [x] 12 template type validators (create)
- [x] 11 template type validators (send)
- [x] Async Meta Graph API client (httpx)
- [x] Pydantic payload validation with friendly errors
- [x] Claude Desktop, Cursor, VS Code Copilot support
- [x] 47 tests passing

## v0.2.0 — Session Messaging & Contacts

- [ ] `send_text_message` — Send free-form text in 24h session window
- [ ] `send_media_message` — Send images, videos, documents
- [ ] `send_interactive_message` — Lists, buttons, product messages
- [ ] `list_contacts` — List contacts from the phone number
- [ ] `get_contact_profile` — Get contact info and chat history

## v0.3.0 — Webhooks & Media

- [ ] Webhook listener for incoming messages
- [ ] Message status webhooks (sent, delivered, read)
- [ ] Media download from incoming messages
- [ ] Template approval/rejection webhook notifications

## Future

- [ ] PyPI package (`pip install whatsapp-mcp`)
- [ ] Docker image
- [ ] SSE transport (in addition to stdio)
- [ ] Multi-provider support (Gupshup, 360dialog)
- [ ] Template analytics tool
- [ ] Conversation-aware context (chat history as MCP resources)
