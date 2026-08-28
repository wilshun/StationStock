#!/bin/sh
set -eu
: "${POSTGRES_DB:?POSTGRES_DB is required}"
: "${POSTGRES_USER:?POSTGRES_USER is required}"
: "${BACKUP_FILE:?BACKUP_FILE must name a file under /backups}"
case "$BACKUP_FILE" in /backups/*.dump) ;; *) echo "BACKUP_FILE must be /backups/<name>.dump" >&2; exit 2;; esac
echo "WARNING: this restores into $POSTGRES_DB and may overwrite matching objects."
pg_restore --exit-on-error --clean --if-exists --no-owner --no-acl --username="$POSTGRES_USER" --dbname="$POSTGRES_DB" "$BACKUP_FILE"
