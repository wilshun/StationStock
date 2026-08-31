#!/bin/bash
set -euo pipefail

: "${S3_BACKUP_BUCKET:?S3_BACKUP_BUCKET is required}"
: "${AWS_REGION:?AWS_REGION is required}"

deployment_dir="${STATIONSTOCK_DIR:-/opt/stationstock}"
env_file="${STATIONSTOCK_ENV_FILE:-${deployment_dir}/.env.aws}"
compose_file="${deployment_dir}/deploy/aws/docker-compose.aws.yml"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
backup_name="stationstock-${timestamp}.dump"
container_path="/backups/${backup_name}"
local_dir="/var/lib/stationstock/backups"
local_path="${local_dir}/${backup_name}"

umask 077
mkdir -p "${local_dir}"

cleanup() {
  rm -f -- "${local_path}"
  docker compose --env-file "${env_file}" -f "${compose_file}" exec -T postgres rm -f -- "${container_path}" >/dev/null 2>&1 || true
}
trap cleanup EXIT

docker compose --env-file "${env_file}" -f "${compose_file}" exec -T postgres \
  sh -c 'pg_dump --format=custom --no-owner --no-acl --username="$POSTGRES_USER" --dbname="$POSTGRES_DB" --file="$1"' \
  sh "${container_path}"
docker compose --env-file "${env_file}" -f "${compose_file}" cp \
  "postgres:${container_path}" "${local_path}"
docker run --rm -v "${local_path}:/backup.dump:ro" postgres:17 \
  pg_restore --list /backup.dump >/dev/null
aws s3 cp "${local_path}" "s3://${S3_BACKUP_BUCKET}/daily/${backup_name}" \
  --region "${AWS_REGION}" \
  --only-show-errors \
  --sse AES256
echo "Uploaded encrypted backup: s3://${S3_BACKUP_BUCKET}/daily/${backup_name}"
