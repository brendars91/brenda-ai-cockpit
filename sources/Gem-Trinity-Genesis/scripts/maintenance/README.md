# Maintenance Scripts

This folder contains host-side maintenance utilities.

## Scripts
- `backup.sh`: archive artifacts, logs, and config
- `restore.sh`: restore from a backup directory
- `docker-prune.sh`: prune unused images/containers/volumes
- `cleanup-logs.sh`: remove old log files in `logs/`

## Example cron entries
```
0 2 * * * /home/ubuntu/gem-trinity-genesis/scripts/maintenance/backup.sh
30 2 * * * /home/ubuntu/gem-trinity-genesis/scripts/maintenance/cleanup-logs.sh
0 3 * * 0 /home/ubuntu/gem-trinity-genesis/scripts/maintenance/docker-prune.sh
```
