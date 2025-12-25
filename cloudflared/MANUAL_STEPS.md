# Cloudflare Tunnel - Manual Setup Required

This file documents the manual steps that must be completed to activate Cloudflare Tunnel for testhome-visualizer.

## Status: PENDING USER ACTION

The following steps require interactive authentication and cannot be automated:

---

## Step 1: Install cloudflared

```bash
curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared.deb
rm cloudflared.deb
```

Verify:
```bash
cloudflared --version
```

---

## Step 2: Authenticate with Cloudflare (INTERACTIVE)

```bash
cloudflared tunnel login
```

**This will open a browser window.** You must:
1. Log in to your Cloudflare account
2. Select the domain: `trustedhearthandhome.com`
3. Authorize the tunnel

---

## Step 3: Create the Tunnel

```bash
cloudflared tunnel create visualizer
```

**CRITICAL:** Save the tunnel ID from the output. Example:
```
Created tunnel visualizer with id a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

---

## Step 4: Update config.yml

Edit `/home/astre/command-center/testhome/testhome-visualizer/cloudflared/config.yml`

Replace `TUNNEL_ID` with your actual tunnel ID:

```yaml
tunnel: a1b2c3d4-e5f6-7890-abcd-ef1234567890
credentials-file: /home/astre/.cloudflared/a1b2c3d4-e5f6-7890-abcd-ef1234567890.json
```

---

## Step 5: Configure DNS

```bash
cloudflared tunnel route dns visualizer trustedhearthandhome.com
cloudflared tunnel route dns visualizer www.trustedhearthandhome.com
```

This creates CNAME records in Cloudflare DNS.

---

## Step 6: Test the Tunnel

```bash
cloudflared tunnel --config /home/astre/command-center/testhome/testhome-visualizer/cloudflared/config.yml run
```

In another terminal:
```bash
curl -I https://trustedhearthandhome.com
```

Expected: HTTP 200 response from Django

---

## Step 7: Install as systemd Service

```bash
sudo cloudflared service install --config /home/astre/command-center/testhome/testhome-visualizer/cloudflared/config.yml
sudo systemctl enable cloudflared
sudo systemctl start cloudflared
```

Verify:
```bash
sudo systemctl status cloudflared
```

---

## After Completion

Once all steps are complete, you can delete this file and update the plan to mark Task 6 as COMPLETE.

The tunnel will automatically start on system boot and proxy all traffic through Cloudflare's edge network.

---

## Troubleshooting

If you encounter issues, see `README.md` in this directory for detailed troubleshooting steps.
