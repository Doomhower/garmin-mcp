# garmin-mcp
A garmin-mcp server that allows you to get data from your garmin watch via their official api

## Running

```bash
docker compose up -d --build
```

The server listens on port `8091` (streamable HTTP, path `/mcp`). It holds no
API key itself.

## Providing the API key

Each MCP client sends its own Garmin personal API key with every request, in
one of these headers:

- `X-Garmin-Api-Key: <key>` (preferred)
- `Authorization: Bearer <key>`

Bearer tokens obtained from Garmin are cached inside the container per key
(`/tmp/garmin-mcp-tokens`, keyed by a hash of the API key); the key itself is
never stored.

Claude Code:

```bash
claude mcp add --transport http garmin http://localhost:8091/mcp --header "X-Garmin-Api-Key: YOUR_KEY"
```

Generic JSON config (clients that support remote HTTP servers with headers):

```json
{
  "mcpServers": {
    "garmin": {
      "type": "http",
      "url": "http://localhost:8091/mcp",
      "headers": { "X-Garmin-Api-Key": "YOUR_KEY" }
    }
  }
}
```

The key travels in plain text over HTTP, so put the server behind TLS (or keep
it on a private network) if clients connect from other machines.
