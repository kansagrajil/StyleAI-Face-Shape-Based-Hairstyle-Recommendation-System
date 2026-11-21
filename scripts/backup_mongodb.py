"""
Automated MongoDB Backup & Retention Management Script.
Performs gzipped mongodump backups and enforces a 7-day retention rotation policy.
"""

import os
import sys
import time
import subprocess
from datetime import datetime, timezone

BACKUP_DIR = os.getenv('BACKUP_DIR', 'backups')
RETENTION_DAYS = int(os.getenv('RETENTION_DAYS', 7))
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/faceshape')


def run_backup():
    """Execute compressed MongoDB backup."""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    backup_file = os.path.join(BACKUP_DIR, f'faceshape_backup_{timestamp}.gz')

    print(f"[{datetime.now().isoformat()}] Starting MongoDB backup to {backup_file}...")

    cmd = [
        'mongodump',
        f'--uri={MONGO_URI}',
        f'--archive={backup_file}',
        '--gzip'
    ]

    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0:
            print(f"[{datetime.now().isoformat()}] Backup completed successfully!")
            cleanup_old_backups()
            return True
        else:
            print(f"Backup failed: {res.stderr}")
            return False
    except Exception as e:
        print(f"Error executing mongodump: {e}")
        return False


def cleanup_old_backups():
    """Remove backup archives older than RETENTION_DAYS."""
    now = time.time()
    cutoff = now - (RETENTION_DAYS * 86400)

    for filename in os.listdir(BACKUP_DIR):
        if filename.startswith('faceshape_backup_') and filename.endswith('.gz'):
            filepath = os.path.join(BACKUP_DIR, filename)
            stat = os.stat(filepath)
            if stat.st_mtime < cutoff:
                print(f"Removing old backup: {filename}")
                try:
                    os.remove(filepath)
                except Exception as e:
                    print(f"Error removing {filename}: {e}")


if __name__ == '__main__':
    success = run_backup()
    sys.exit(0 if success else 1)
