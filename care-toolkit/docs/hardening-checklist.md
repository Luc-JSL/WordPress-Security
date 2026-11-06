# Hardening checklist

Work through this once at onboarding and record the date next to each item. Re-check the starred items every month.

## Accounts and access

- [ ] Remove or rename the `admin` username; every account has its own named login.
- [ ] Every administrator uses a password manager and a unique password of 16 or more characters.
- [ ] Two-factor authentication is on for every administrator and editor account.
- [ ] Login attempts are rate limited (a plugin such as Limit Login Attempts Reloaded, or Wordfence's login security, or the host's protection).
- [ ] Roles follow least privilege: people who write posts are Authors or Editors, not Administrators.
- [ ] Inactive accounts (no login in 90 days) are removed or downgraded to Subscriber. *
- [ ] Application passwords and REST API access are reviewed; unused ones are revoked.
- [ ] Hosting control panel, domain registrar and DNS provider accounts also have two-factor authentication.

## Software

- [ ] WordPress core, every plugin and every theme are on the current version. *
- [ ] Unused plugins and themes are deleted, not just deactivated. *
- [ ] Every plugin comes from wordpress.org or a known vendor, and was updated by its author within the last year.
- [ ] Automatic updates are on for minor core releases; major core and plugin updates go through the monthly runbook.
- [ ] PHP is a version the PHP project still supports.

## Backups

- [ ] Daily off-site backups of the database and `wp-content` (host backups count only if they are stored away from the web server).
- [ ] A restore has been tested on a staging copy, and the restore time is written down. *
- [ ] Backup retention covers at least 30 days.

## Transport and headers

- [ ] HTTPS everywhere with a valid certificate that renews automatically; HTTP redirects to HTTPS.
- [ ] `FORCE_SSL_ADMIN` is set (see `config/wp-config-hardening.php`).
- [ ] Security headers from `config/` are deployed: HSTS, `X-Content-Type-Options`, `X-Frame-Options` or a frame-ancestors policy, `Referrer-Policy`, `Permissions-Policy`.
- [ ] A Content-Security-Policy is at least in report-only mode, so inline scripts added by plugins can be seen before enforcement.

## Files and configuration

- [ ] `DISALLOW_FILE_EDIT` is set so the theme and plugin editors are disabled in the dashboard.
- [ ] File permissions: directories 755, files 644, `wp-config.php` 640 or 600, owned by the site's user, not the web server's.
- [ ] Directory listing is off.
- [ ] PHP execution is blocked inside `wp-content/uploads` (see the server configs).
- [ ] The unique keys and salts in `wp-config.php` were regenerated at onboarding.
- [ ] Database table prefix is not `wp_` on new builds (changing it on an existing site is optional and risky).
- [ ] XML-RPC is disabled unless something the client uses needs it (Jetpack and some mobile apps do).

## Monitoring and logging

- [ ] Uptime monitoring with an alert to you, not only the client.
- [ ] File integrity monitoring or a scheduled `wp core verify-checksums`. *
- [ ] Login and admin-action logging (WP Activity Log or the host's logs) retained for 90 days.
- [ ] The site is registered for vulnerability alerts for its installed plugins (Patchstack, Wordfence or WPScan email alerts). *
- [ ] Search Console is connected so Google's "hacked content" and security warnings reach you.

## Paper

- [ ] A signed care agreement that names the sites in scope, what you may change, and who to call at the host.
- [ ] Hosting, domain and DNS logins are in the client's name, with you as a delegated user, so an offboarding never strands them.
- [ ] The onboarding report lists everything above with the date it was done.
