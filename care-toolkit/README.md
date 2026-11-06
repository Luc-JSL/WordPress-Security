# WordPress care toolkit

Checklists, runbooks, config snippets and a maintenance script for keeping small-business WordPress sites patched, backed up and locked down. Written while studying cybersecurity and running a monthly care plan for sites I administer.

Everything here is for sites you own or have written permission to maintain. The script needs shell access to the server and WP-CLI, which you only have on sites you administer. Nothing in this repository tests, probes or scans anyone else's site.

## What is inside

| Path | What it is |
|---|---|
| `docs/hardening-checklist.md` | The baseline every site gets at onboarding: accounts, updates, backups, HTTPS, headers, file permissions, logging |
| `docs/monthly-maintenance-runbook.md` | The monthly routine, step by step, with the WP-CLI commands and the order that avoids breaking a live site |
| `docs/incident-runbook.md` | What to do when a site you maintain is compromised, from isolating it to the write-up afterwards |
| `docs/client-report-template.md` | The one-page monthly report a client receives |
| `config/wp-config-hardening.php` | Constants to add to `wp-config.php` |
| `config/security-headers.apache.conf`, `config/security-headers.nginx.conf` | Security response headers for the two common web servers |
| `scripts/wp-maintenance.sh` | Backup, update and verify a site with WP-CLI, printing a summary you can paste into the report |

## How a care plan uses it

1. Onboarding: work through the hardening checklist once and record what changed.
2. Monthly: run `scripts/wp-maintenance.sh` on a staging copy first, then on production, then fill in the client report.
3. When something goes wrong: follow the incident runbook, and write down what happened and what prevents it next time.

## Requirements for the script

- SSH access to the server and a user that can read the WordPress directory
- [WP-CLI](https://wp-cli.org/) 2.x on the server
- `tar`, `gzip` and about twice the site's size in free disk for the backup

## Running the maintenance script

```bash
WP_PATH=/var/www/example.com BACKUP_DIR=/var/backups/example.com ./scripts/wp-maintenance.sh
```

Add `DRY_RUN=1` to see which updates would be applied without applying them.

## Why these choices

- Backups happen before any update, every time, because a failed plugin update on a live site is the most common way a care plan loses a client's trust.
- Core checksums are verified after updates so modified core files, which are a common sign of a compromise, are caught the same day.
- Updates run on staging first when a staging copy exists; the script does not create one, it only refuses to skip the question.
- Security headers are shipped as server config rather than a plugin, because a plugin can be disabled by the next person who logs in.

