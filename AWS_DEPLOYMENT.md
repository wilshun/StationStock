# StationStock AWS Deployment

This deployment keeps the application on one Amazon Linux 2023 `t3.small` EC2 instance in `us-east-1`. Docker Compose runs Caddy, Next.js, FastAPI, and PostgreSQL. PostgreSQL is private and persists on the encrypted 30 GiB gp3 root EBS volume. Daily custom-format database backups are encrypted and uploaded to a private S3 bucket through the EC2 instance role. Systems Manager Session Manager replaces public SSH.

No demo seed command is part of startup. The backend applies Alembic migrations and starts with zero users and zero store records. Stop before running the interactive first-manager command.

## Files and secrets

Copy `.env.aws.example` to `/opt/stationstock/.env.aws` on the instance, set mode `0600`, and replace every placeholder. The real file is ignored by Git. Generate the database password and auth secret locally or on the instance with a cryptographically secure generator; never paste either into Git, user data, shell history, logs, or SSM command parameters.

Use one user-controlled DNS name for both the web application and API, for example `inventory.example.com`. Set `DOMAIN`, `ALLOWED_FRONTEND_ORIGIN`, and `NEXT_PUBLIC_API_BASE_URL` to that exact HTTPS origin (`NEXT_PUBLIC_API_BASE_URL` ends in `/api/v1`). Add `ACME_EMAIL` to `.env.aws` for Caddy certificate notices.

## AWS resources

The approval checkpoint must name and price every resource before creation. The intended set is:

- one `t3.small` Amazon Linux 2023 EC2 instance with no key pair and no public SSH;
- one encrypted 30 GiB gp3 root EBS volume, delete-on-termination enabled;
- one security group allowing inbound TCP 80 and TCP/UDP 443 from the internet, with no inbound 22 or 5432;
- one Elastic IP for stable DNS;
- one EC2 IAM role and instance profile with `AmazonSSMManagedInstanceCore` plus bucket-scoped backup permissions;
- one globally unique private S3 bucket with public access blocked, SSE-S3 default encryption, versioning, and lifecycle expiration;
- DNS records at the user's existing DNS provider (or Route 53 only if separately approved).

The default VPC and a public subnet are preferred to avoid NAT Gateway and custom-VPC costs. The instance requires outbound internet access for SSM, OS packages, container images, Caddy ACME, and S3.

## Host installation

Before using the JSON policy templates, replace the documented `000000000000` account placeholder and example bucket name with the approved deployment values. Keep account-specific copies outside Git.

After the infrastructure and DNS are approved and created, connect only through Systems Manager. Install Git, Docker, the Docker Compose plugin, AWS CLI v2, and PostgreSQL client tools. Clone the reviewed commit into `/opt/stationstock`, create `/var/lib/stationstock/backups` with root-only permissions, install the three systemd units and timer from `deploy/aws`, and enable Docker.

Validate before starting:

```sh
docker compose --env-file /opt/stationstock/.env.aws -f /opt/stationstock/deploy/aws/docker-compose.aws.yml config --quiet
```

Start and inspect:

```sh
sudo systemctl enable --now stationstock.service
docker compose --env-file /opt/stationstock/.env.aws -f /opt/stationstock/deploy/aws/docker-compose.aws.yml ps
curl --fail https://inventory.example.com/api/health
```

Verify the database is empty before bootstrap:

```sh
docker compose --env-file /opt/stationstock/.env.aws -f /opt/stationstock/deploy/aws/docker-compose.aws.yml exec -T postgres \
  psql -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Atc \
  "select 'users=' || count(*) from users union all select 'categories=' || count(*) from categories union all select 'vendors=' || count(*) from vendors union all select 'products=' || count(*) from products union all select 'inventory_counts=' || count(*) from inventory_counts union all select 'inventory_count_items=' || count(*) from inventory_count_items;"
```

The expected value for every row is zero. Confirm `/docs`, `/redoc`, and `/openapi.json` return 404; the session cookie is `Secure` and `HttpOnly`; CORS allows only the configured HTTPS origin; and the production demo seed exits with `Development seed commands are disabled in production`.

## Backups

Install `stationstock-backup.service` and `stationstock-backup.timer`, then enable the timer:

```sh
sudo systemctl enable --now stationstock-backup.timer
sudo systemctl start stationstock-backup.service
sudo journalctl -u stationstock-backup.service --no-pager
aws s3api list-objects-v2 --bucket "$S3_BACKUP_BUCKET" --prefix daily/ --max-items 5
```

The script verifies the PostgreSQL custom-format archive before upload, requests SSE-S3 encryption, and removes its temporary local and container copies. S3 bucket policy and lifecycle settings provide the durable retention boundary. Rehearse restore only into a separate empty test database and obtain explicit approval before any production restore.

## First manager: intentional stop point

Do not run this during deployment validation. Return it to the owner only after the empty production state, HTTPS, security controls, and backups are verified:

```sh
docker compose --env-file /opt/stationstock/.env.aws -f /opt/stationstock/deploy/aws/docker-compose.aws.yml run --rm backend \
  python -m app.scripts.create_manager --name "Manager Name" --email "manager@example.com"
```

The password prompt is interactive and does not put the password in shell history. The command refuses to create a second manager.
