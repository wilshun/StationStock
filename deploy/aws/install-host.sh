#!/bin/bash
set -euo pipefail

deployment_dir=/opt/stationstock
env_file="${deployment_dir}/.env.aws"

dnf install -y docker git awscli openssl
install -d -m 0755 /usr/local/lib/docker/cli-plugins
curl --fail --location --silent --show-error \
  https://github.com/docker/compose/releases/download/v5.4.0/docker-compose-linux-x86_64 \
  --output /usr/local/lib/docker/cli-plugins/docker-compose
curl --fail --location --silent --show-error \
  https://github.com/docker/buildx/releases/download/v0.36.1/buildx-v0.36.1.linux-amd64 \
  --output /usr/local/lib/docker/cli-plugins/docker-buildx
chmod 0755 /usr/local/lib/docker/cli-plugins/docker-compose /usr/local/lib/docker/cli-plugins/docker-buildx
systemctl enable --now docker
docker compose version
docker buildx version

install -d -m 0700 /var/lib/stationstock/backups
chmod 0755 "${deployment_dir}/deploy/aws/backup-to-s3.sh"

if [[ ! -f "${env_file}" ]]; then
  umask 077
  postgres_password="$(openssl rand -hex 32)"
  auth_secret="$(openssl rand -hex 48)"
  cat >"${env_file}" <<EOF
ENVIRONMENT=production
DOMAIN=stationstocklh.duckdns.org
ACME_EMAIL=admin@example.com
POSTGRES_DB=stationstock
POSTGRES_USER=stationstock
POSTGRES_PASSWORD=${postgres_password}
AUTH_SECRET_KEY=${auth_secret}
AUTH_COOKIE_NAME=stationstock_access_token
AUTH_COOKIE_SECURE=true
AUTH_COOKIE_SAMESITE=lax
ACCESS_TOKEN_EXPIRE_MINUTES=15
ALLOWED_FRONTEND_ORIGIN=https://stationstocklh.duckdns.org
API_DOCS_ENABLED=false
NEXT_PUBLIC_API_BASE_URL=https://stationstocklh.duckdns.org/api/v1
LOGIN_MAX_ATTEMPTS=5
LOGIN_WINDOW_SECONDS=300
LOGIN_COOLDOWN_SECONDS=60
S3_BACKUP_BUCKET=stationstock-prod-backups-000000000000-us-east-1
AWS_REGION=us-east-1
EOF
  chmod 0600 "${env_file}"
fi

install -m 0644 "${deployment_dir}/deploy/aws/stationstock.service" /etc/systemd/system/stationstock.service
install -m 0644 "${deployment_dir}/deploy/aws/stationstock-backup.service" /etc/systemd/system/stationstock-backup.service
install -m 0644 "${deployment_dir}/deploy/aws/stationstock-backup.timer" /etc/systemd/system/stationstock-backup.timer
systemctl daemon-reload

docker compose --env-file "${env_file}" -f "${deployment_dir}/deploy/aws/docker-compose.aws.yml" config --quiet
systemctl enable --now stationstock.service
systemctl enable --now stationstock-backup.timer
