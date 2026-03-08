# Cloudflare Tunnel (aether.ordl.org)

Recommended tunnel name: `ordl-aether`

## 1) Create tunnel

```bash
cloudflared tunnel login
cloudflared tunnel create ordl-aether
```

## 2) DNS route

```bash
cloudflared tunnel route dns ordl-aether aether.ordl.org
```

## 3) Config

Create `~/.cloudflared/config.yml`:

```yaml
tunnel: ordl-aether
credentials-file: /path/to/ordl-aether.json

ingress:
  - hostname: aether.ordl.org
    service: http://localhost:3000
  - service: http_status:404
```

The frontend dev server proxies `/api/*`, `/health`, `/status`, and `/docs` to backend `:8000`,
so a single hostname can serve both UI and API.

## 4) Run tunnel

```bash
cloudflared tunnel run ordl-aether
```
