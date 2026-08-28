# Security Operations

Production startup fails unless the database URL, a unique 32+ character authentication secret, secure cookies, and one HTTPS frontend origin are configured. Credentials use HTTP-only, Secure, SameSite cookies scoped to `/api`; credentialed CORS accepts one configured origin and rejects wildcards. API docs are off by default in production.

Five failed logins within five minutes trigger a temporary one-minute cooldown for that client/email pair. Errors are generic and successful authentication clears failures. This protection is process-local; use a shared Redis-backed limiter before running multiple backend replicas.

Password changes require the current password. Manager resets require manager authorization. Both increment the user's authentication version, invalidating issued cookies when the next request is made. Deactivating a user immediately prevents authentication. Passwords, hashes, tokens, cookies, secrets, and request bodies are excluded from audit metadata.

Rotate `AUTH_SECRET_KEY` by scheduling a maintenance window, replacing it in the secret store, and restarting every backend instance; all sessions will be invalidated. Rotate the database password separately and update both PostgreSQL and the application secret atomically. Never place real secrets in Compose files, Git, logs, tickets, or screenshots.

Review manager-only audit events regularly. Limit host/network access, terminate TLS at a trusted reverse proxy, patch images, run vulnerability scans, and test backups. Production and development must never share a database because demo credentials and synthetic inventory are intentionally public.
