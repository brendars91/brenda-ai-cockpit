# Personal Runbook (Gem Trinity Genesis)

Purpose
- Quick recovery steps for personal use without extra complexity.

Key URLs
- Backend (public): `https://covered-bar-identity-bedford.trycloudflare.com`
- Backend (private/Tailscale): `http://100.69.240.73:8000/api/status`
- n8n (private/Tailscale): `http://100.69.240.73:5678`

Daily Check (optional)
```bash
curl -fsS https://covered-bar-identity-bedford.trycloudflare.com/api/status
```

If the frontend stops loading data
1) Check backend via tunnel:
```bash
curl -fsS https://covered-bar-identity-bedford.trycloudflare.com/api/status
```
2) If it fails, restart the tunnel:
```bash
cd /home/ubuntu/gem-trinity-genesis
docker compose restart cloudflared
```
3) If the tunnel URL changed, update Vercel env:
- `NEXT_PUBLIC_API_URL=https://NEW-TUNNEL-URL`
- Redeploy the frontend.

If the backend itself is down
```bash
cd /home/ubuntu/gem-trinity-genesis
docker compose ps
docker compose restart gem-backend
docker logs --tail=100 gem-trinity-backend
```

If disk space grows
```bash
df -h
du -sh /home/ubuntu/gem-trinity-genesis/artifacts
```

Backups
- Daily backup runs at 02:00 UTC via cron.
- Backup location: `/home/ubuntu/backups/gem-trinity/<timestamp>`
- Restore:
```bash
/home/ubuntu/gem-trinity-genesis/scripts/maintenance/restore.sh /home/ubuntu/backups/gem-trinity/<timestamp>
```

Useful commands
```bash
docker compose ps
docker logs --tail=50 cloudflared
docker logs --tail=50 gem-trinity-backend
```
