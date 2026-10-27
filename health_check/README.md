# Website Health Check (Secure WP Care)

A free, passive check you run on a business's website before emailing them. It produces a
one-page report (grade, findings in plain English, how to fix each one) that you attach to
your first email.

## What it checks (public information only)

| Check | How |
|---|---|
| Does the site load over HTTPS, and does `http://` redirect to it? | Loads the homepage, like a browser |
| SSL certificate valid, days until it expires | The certificate any browser sees |
| Runs WordPress? Which version? Is it out of date? | Reads the homepage's page code and compares with wordpress.org |
| Plugins visible in the page code | Same page code |
| PHP version shown in headers (end of life?) | Response headers |
| Basic browser security headers | Response headers |
| Email spoofing protection (SPF, DMARC) | Public DNS records |

**What it never does:** log in, open `/wp-admin` or `/wp-login.php`, guess URLs, or scan for
vulnerabilities. Anything deeper needs the owner's written permission. Keep it that way;
unauthorized scanning can be a crime.

## Setup

Needs Python 3.10 or newer. No extra packages.

## Run it

```bash
# One site
python3 site_check.py example.com --from-name "Jordan Sledge" --from-email you@example.com

# A list of prospects (see prospects_example.csv)
python3 site_check.py --csv prospects.csv --out reports --from-name "Jordan Sledge" --from-email you@example.com
```

Output:
- `reports/<business>.html`: one report per site. Open it in your browser, then
  **Print → Save as PDF** to attach it to your email.
- `reports/summary.csv`: every site with its grade and top issue, ready to sort.

**Only email businesses whose report shows real issues.** A grade of A or B means they don't need you yet.

## Tests

```bash
python3 -m unittest -v test_site_check.py
```

The tests run offline against a fake local WordPress site. Run your first live checks on
**your own sites** to see real output before checking anyone else's.

## Keep it current

`MIN_SUPPORTED_PHP` at the top of `site_check.py` is the oldest PHP branch still getting
security fixes (8.2 as of late 2026). Update it when a branch reaches end of life
(php.net/supported-versions).

## Next tools to build with Claude

1. **Vulnerability watcher** (for paying clients, with permission): compare each client's
   plugin list against Wordfence Intelligence's free vulnerability API and alert you.
2. **Monthly client report**: turn your MainWP dashboard export into a branded PDF.
