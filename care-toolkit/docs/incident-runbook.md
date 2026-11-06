# Incident runbook: a site you maintain is compromised

Signs: unfamiliar admin accounts, spam pages or redirects, Google's "This site may be hacked" label, the host suspending the account, `wp core verify-checksums` reporting modified files, outbound spam from the server.

Tell the client within the hour, in plain language, with what you know and what you are doing. Keep a timestamped log from the first minute; it becomes the write-up.

## 1. Contain

- Put the site in maintenance mode or ask the host to restrict it to your IP.
- Change the passwords for every WordPress administrator, the hosting panel, SFTP/SSH, the database user, and rotate the keys and salts in `wp-config.php` (that logs everyone out).
- Revoke application passwords and API keys. Remove any account you did not create.
- If the host offers a malware scan or a cleaning service in the plan, start it now; it runs while you work.

## 2. Preserve

- Take a full copy of the site and database as it is, before cleaning, and store it off the server. You will need it to find the entry point, and the client may need it for an insurer or a lawyer.
- Save the server access and error logs covering the last 30 days.

## 3. Find the entry point

- Compare the modified-file list (`wp core verify-checksums`, plus a diff of `wp-content` against last month's clean backup) with the access logs around the first modification time.
- The usual causes, in order: a plugin or theme with a known vulnerability that was not updated, a weak or reused admin password, a nulled premium plugin, a neighboring site on the same hosting account, or a leaked SFTP credential.
- If you cannot find the entry point in an hour, say so and bring in a professional cleanup service; the client pays once for a clean site rather than three times for repeated reinfections.

## 4. Clean or restore

- Preferred: restore the most recent backup from before the first sign of compromise, then apply every update and the hardening checklist before taking it live.
- If no clean backup exists: reinstall WordPress core and every plugin and theme from fresh downloads, keep only `wp-content/uploads` (checked for PHP files) and the database, inspect the database for injected admin users, spam posts and `siteurl` or `home` changes, and remove scheduled tasks you did not create.
- Delete anything you cannot account for. Do not try to repair a modified core file by hand.

## 5. Verify and reopen

- `wp core verify-checksums` is clean, the vulnerability scanner reports nothing, no unknown users, forms and checkout work.
- Request a review in Google Search Console if the site was flagged; check the domain against blocklists.
- Rotate the client's email and payment-processor passwords if the site stored or touched them.

## 6. Write it up

One page for the client: what happened, when, how it got in, what was done, what changed to prevent it, and what you need from them (for example, approving the removal of a plugin). Add the lesson to your onboarding checklist if it was missing there.
