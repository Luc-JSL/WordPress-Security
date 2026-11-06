#!/usr/bin/env bash
# Monthly maintenance for a WordPress site you administer: back up, update, verify, summarize.
#
# Usage:
#   WP_PATH=/var/www/example.com BACKUP_DIR=/var/backups/example.com ./wp-maintenance.sh
#   DRY_RUN=1 ...   shows available updates and exits without changing anything
#
# Requirements: shell access to the server, WP-CLI (wp) on the PATH, tar and gzip.
# The script refuses to run without a backup location, and stops at the first error.

set -euo pipefail

WP_PATH="${WP_PATH:?Set WP_PATH to the WordPress root directory}"
BACKUP_DIR="${BACKUP_DIR:?Set BACKUP_DIR to a directory outside the web root}"
DRY_RUN="${DRY_RUN:-0}"
STAMP="$(date +%Y%m%d-%H%M%S)"
SITE="$(basename "$WP_PATH")"

wp_() { wp --path="$WP_PATH" --skip-plugins=none "$@"; }

echo "== $SITE  $(date)"
echo "WordPress $(wp_ core version)  PHP $(wp_ eval 'echo PHP_VERSION;')"

echo
echo "== Available updates"
wp_ plugin list --update=available --fields=name,version,update_version --format=table || true
wp_ theme list --update=available --fields=name,version,update_version --format=table || true
if wp_ core check-update --format=csv | grep -q .; then wp_ core check-update; else echo "core: up to date"; fi

if [[ "$DRY_RUN" == "1" ]]; then
  echo
  echo "DRY_RUN=1: no changes made."
  exit 0
fi

echo
echo "== Backup to $BACKUP_DIR"
mkdir -p "$BACKUP_DIR"
wp_ db export "$BACKUP_DIR/$SITE-$STAMP.sql"
gzip "$BACKUP_DIR/$SITE-$STAMP.sql"
tar -czf "$BACKUP_DIR/$SITE-$STAMP-wp-content.tar.gz" -C "$WP_PATH" wp-content
ls -lh "$BACKUP_DIR"/"$SITE-$STAMP"*

echo
echo "== Core checksums before updating"
wp_ core verify-checksums || echo "WARNING: modified core files found before the update; see the incident runbook."

echo
echo "== Updating"
wp_ plugin update --all
wp_ theme update --all
wp_ core update
wp_ core update-db

echo
echo "== Core checksums after updating"
wp_ core verify-checksums

echo
echo "== Housekeeping"
echo "Inactive plugins (candidates for removal):"
wp_ plugin list --status=inactive --fields=name,version --format=table || true
echo "Administrators:"
wp_ user list --role=administrator --fields=user_login,user_email,user_registered --format=table
echo "Transients cleared: $(wp_ transient delete --all 2>/dev/null | tail -1)"

echo
echo "== Done. Now load the home page and submit the contact form by hand."
echo "Backup files: $BACKUP_DIR/$SITE-$STAMP*"
