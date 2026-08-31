# Sanitized screenshot checklist

No screenshots are checked in yet. Do not capture authenticated screens until a manager exists and the database contains only fake, clearly labeled portfolio data.

Add PNG or WebP images to `docs/images/` and verify each image visually before committing it.

- [ ] Login page after confirming no demo credentials appear
- [ ] Dashboard at desktop and narrow mobile widths
- [ ] Products page with a low-stock filter and fake catalog data
- [ ] Inventory-count draft, save, and submission confirmation
- [ ] Manager user administration with fake names and example-domain emails
- [ ] Browser storage view confirming no token in local or session storage
- [ ] Network response showing a Secure, HTTP-only cookie without exposing its value

Every screenshot must exclude real employee emails, store-sensitive inventory, AWS account or resource identifiers, public IP addresses, tokens, secrets, passwords, certificates, and local machine paths. Crop browser chrome or bookmarks that disclose personal information.
