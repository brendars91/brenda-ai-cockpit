# Ops Guides

## Cloudflare Tunnel (systemd)
1. Install cloudflared on the host.
2. Create `/etc/default/cloudflared`:
   ```
   CLOUDFLARE_TUNNEL_TOKEN=your-token-here
   ```
3. Copy `ops/systemd/cloudflared.service` to `/etc/systemd/system/`.
4. Enable and start:
   ```
   sudo systemctl daemon-reload
   sudo systemctl enable cloudflared
   sudo systemctl start cloudflared
   ```
5. Check status:
   ```
   sudo systemctl status cloudflared
   ```

## Cron Maintenance
Install the cron jobs from `ops/cron/maintenance.cron`:
```
crontab -e
```
Copy the contents and save.

## Backups
- Backups are stored under `/home/ubuntu/backups/gem-trinity/<timestamp>`.
- Restore with `scripts/maintenance/restore.sh <backup-dir>`.
