# Cloudflare Tunnel Configuration

Back to index: [INDEX.md](INDEX.md)

This guide maps the local AETHER frontend and API access through a single public hostname.

## Target Host

- Hostname: `aether.ordl.org`
- Recommended tunnel name: `ordl-aether`

## 1. Create Tunnel

```bash
cloudflared tunnel login
cloudflared tunnel create ordl-aether
```

## 2. Configure DNS Route

```bash
cloudflared tunnel route dns ordl-aether aether.ordl.org
```

## 3. Configure Ingress

Create `~/.cloudflared/config.yml`:

```yaml
tunnel: ordl-aether
credentials-file: /path/to/ordl-aether.json

ingress:
  - hostname: aether.ordl.org
    service: http://localhost:3000
  - service: http_status:404
```

The frontend proxies `/api/*`, `/health`, `/status`, and `/docs` to backend port `8000`, so a single hostname can represent both UI and API routes.

## 4. Run Tunnel

```bash
cloudflared tunnel run ordl-aether
```

## Related Documents

- [Runtime README](../aether-system/README.md)
- [Setup Guide](../aether-system/SETUP.md)
