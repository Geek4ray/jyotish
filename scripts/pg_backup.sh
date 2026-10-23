#!/bin/sh
# A pg_dump of the service's database, kept for RETENTION_DAYS (default 14) under BACKUP_DIR (default
# /data/backups). The database is JYOTISH_DATABASE_URL (the SQLAlchemy URL the service uses; its
# "+psycopg" is dropped for pg_dump). Needs pg_dump at least the server's major version (the image
# has PostgreSQL 17's client, which dumps a 16 server).
#
#   scripts/pg_backup.sh            one dump now, then the old ones pruned
#   scripts/pg_backup.sh --nightly  the same at 03:00 UTC every night, for ever (the compose backup service)
set -eu

backup() {
    url=$(printf '%s' "${JYOTISH_DATABASE_URL:?set JYOTISH_DATABASE_URL}" | sed 's#^postgresql+psycopg://#postgresql://#; s#^postgres://#postgresql://#')
    case "$url" in postgresql://*) ;; *) echo "pg_backup: JYOTISH_DATABASE_URL is not a Postgres URL" >&2; exit 2;; esac
    dir="${BACKUP_DIR:-/data/backups}"
    keep="${RETENTION_DAYS:-14}"
    mkdir -p "$dir"
    file="$dir/jyotish-$(date -u +%Y%m%dT%H%MZ).dump"
    pg_dump --format=custom --no-owner --file="$file.partial" "$url"
    mv "$file.partial" "$file"
    find "$dir" -name 'jyotish-*.dump' -type f -mtime +"$keep" -delete
    echo "pg_backup: wrote $file ($(du -h "$file" | cut -f1)); kept $(find "$dir" -name 'jyotish-*.dump' | wc -l | tr -d ' ') dump(s), none older than $keep days"
}

if [ "${1:-}" = "--nightly" ]; then
    while true; do
        now=$(date -u +%s)
        next=$(date -u -d "tomorrow 03:00" +%s)
        today=$(date -u -d "today 03:00" +%s)
        [ "$today" -gt "$now" ] && next=$today
        sleep $((next - now))
        backup || echo "pg_backup: the dump failed; the next try is tomorrow" >&2
    done
else
    backup
fi
