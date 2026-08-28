# Backup and Restore

Backups contain store and account data. Encrypt them, restrict access, keep a copy outside the server, and never commit them. A practical starting policy is daily backups for 14 days, weekly backups for 8 weeks, and monthly backups for one year, adjusted to business and legal needs.

Create a PostgreSQL custom-format backup:

```sh
docker compose --env-file .env.production -f docker-compose.prod.yml exec postgres sh /opt/stationstock/scripts/backup.sh
```

Copy the resulting `.dump` file from the `stationstock_prod_backups` volume to encrypted storage. Periodically verify it with `pg_restore --list` and rehearse a restore into a separate, empty test database.

Restore (destructive): stop application traffic, take a new backup, confirm the target database twice, and prefer an empty database. Set the exact file beneath `/backups`:

```sh
docker compose --env-file .env.production -f docker-compose.prod.yml exec -e BACKUP_FILE=/backups/stationstock-YYYYMMDDTHHMMSSZ.dump postgres sh /opt/stationstock/scripts/restore.sh
```

The restore uses `--clean --if-exists` and can overwrite existing objects. Afterward, run migrations, start the backend, verify health, sign in, compare record counts, and perform a read-only catalog check.
