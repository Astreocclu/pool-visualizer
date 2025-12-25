# Cloudflare Tunnel Setup

This directory contains the configuration for Cloudflare Tunnel, which provides secure HTTPS access to the testhome-visualizer application without exposing ports or requiring a public IP.

## Architecture

```
Internet → Cloudflare Edge → Cloudflare Tunnel → localhost:8000 (Gunicorn)
```

## Manual Setup Steps

Since Cloudflare Tunnel requires interactive authentication, these steps must be performed manually:

### 1. Install cloudflared

```bash
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb
rm cloudflared.deb
```

Verify installation:
```bash
cloudflared --version
```

### 2. Authenticate with Cloudflare

```bash
cloudflared tunnel login
```

This opens a browser window. Log in to your Cloudflare account and authorize the tunnel.

### 3. Create the Tunnel

```bash
cloudflared tunnel create visualizer
```

**IMPORTANT:** Note the tunnel ID from the output. You'll need it for the next step.

Example output:
```
Created tunnel visualizer with id a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

### 4. Update config.yml

Edit `config.yml` and replace both instances of `TUNNEL_ID` with the actual tunnel ID:

```yaml
tunnel: a1b2c3d4-e5f6-7890-abcd-ef1234567890
credentials-file: /home/astre/.cloudflared/a1b2c3d4-e5f6-7890-abcd-ef1234567890.json
```

### 5. Configure DNS

Route your domain through the tunnel:

```bash
cloudflared tunnel route dns visualizer trustedhearthandhome.com
cloudflared tunnel route dns visualizer www.trustedhearthandhome.com
```

This creates CNAME records in Cloudflare DNS pointing to the tunnel.

### 6. Test Manually

Before installing as a service, test the tunnel:

```bash
cloudflared tunnel --config /home/astre/command-center/testhome/testhome-visualizer/cloudflared/config.yml run
```

In another terminal, verify it works:

```bash
curl -I https://trustedhearthandhome.com
```

You should get a 200 response from your Django application.

### 7. Install as systemd Service

Once testing is successful, install as a system service:

```bash
sudo cloudflared service install --config /home/astre/command-center/testhome/testhome-visualizer/cloudflared/config.yml
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

Verify the service is running:

```bash
sudo systemctl status cloudflared
```

## Troubleshooting

### Tunnel Not Connecting

Check logs:
```bash
sudo journalctl -u cloudflared -f
```

### DNS Not Resolving

Verify CNAME records in Cloudflare dashboard:
```bash
dig trustedhearthandhome.com
```

Should show CNAME pointing to `*.cfargotunnel.com`

### 502 Bad Gateway

Ensure Gunicorn is running:
```bash
sudo systemctl status visualizer
curl http://localhost:8000/api/
```

## Security Notes

- The tunnel runs over an encrypted connection to Cloudflare's edge
- No inbound ports need to be opened on the server
- All traffic is proxied through Cloudflare's CDN
- SSL/TLS is terminated at Cloudflare (free certificate)
- Credentials are stored in `~/.cloudflared/` (keep secure!)

## References

- [Cloudflare Tunnel Documentation](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/)
- [cloudflared CLI Reference](https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/tunnel-guide/)
