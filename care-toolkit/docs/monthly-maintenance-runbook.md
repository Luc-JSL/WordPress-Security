# Monthly maintenance runbook

Allow 20 to 40 minutes per site the first few times; the script brings it down to about 10 once the routine is familiar. Do it at a quiet hour for the client's business.

## Before touching production

1. Check the vulnerability alerts for this site's plugins. A plugin with a published vulnerability and a fix moves to the top of the list; a plugin with a published vulnerability and no fix is deactivated today and the client is told.
2. Confirm last night's off-site backup exists and is the expected size. If it does not, stop and fix backups first.
3. If a staging copy exists, run the whole routine there and click through the home page, one product or service page, the contact form and checkout if there is one.

## On production

Run the script (see the README) or do the same steps by hand:

```bash
wp core verify-checksums                 # core files unchanged
wp plugin list --update=available        # what will change
wp theme list --update=available
wp db export backup-before-update.sql    # database backup
wp plugin update --all
wp theme update --all
wp core update && wp core update-db
wp core verify-checksums                 # again, after updating
wp plugin list --status=inactive         # candidates for deletion
```

Then:

4. Load the home page, the contact form and any form that sends email; submit a test and confirm it arrives.
5. Check the error log for new PHP warnings since the update (`wp-content/debug.log` if logging is on, or the host's log viewer).
6. Review the activity log for logins or admin changes you do not recognize. Anything unrecognized moves this to the incident runbook.
7. Remove plugins and themes that have been inactive for two consecutive months after confirming with the client.
8. Check the certificate expiry date and the domain expiry date.
9. Run a page-speed check on the home page and note the score; a sudden drop usually means a plugin update.

## If an update breaks the site

- Roll the single plugin back with `wp plugin install <slug> --version=<previous> --force`, or restore `wp-content/plugins/<slug>` from the backup.
- Database changes from a plugin update are not reversible by rollback alone; restore `backup-before-update.sql` only if the plugin's data is corrupted, and tell the client what was lost between the backup and now.
- Write the plugin and version in the report so the next month's run knows to wait for a fix.

## Close out

10. Fill in `docs/client-report-template.md` and send it by the 5th of the month.
11. Record the run in your tracker: date, site, updates applied, anything deferred and why.
