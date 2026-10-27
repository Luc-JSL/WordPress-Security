# WordPress-Security
This is my first form of security+ I am going to secure businesses Word Press websites.

## Secure WP Care

A WordPress security and care business: small businesses pay monthly to keep their WordPress
sites secure, updated and backed up. Built to start as a side business with no sales calls,
grow past $2,000/month, and turn a cybersecurity degree into income.

## What's in here

| Folder | What it is |
|---|---|
| [`health_check/`](health_check/) | Passive website health check tool. Point it at a business's site and it produces a one-page report you attach to your first email. Public information only. |
| [`playbook/`](playbook/) | The 30-day launch playbook (Markdown and PDF), a sample report, and the script that builds the PDF |
| [`skills/`](skills/) | The 11 Claude Code skills this business uses, why each one, what was checked, and install commands |
| [`docs/`](docs/) | The business plan: why this idea won, pricing, sales channels, realistic odds and sources |

## Quick start

```bash
cd health_check
python3 -m unittest -v test_site_check.py      # offline tests
python3 site_check.py yoursite.com --from-name "Your Name" --from-email you@yourdomain.com
```

Then follow [`playbook/PLAYBOOK.md`](playbook/PLAYBOOK.md), Week 1.

## Rules this business runs on

1. Public checks only before permission. Never scan or test a site without written permission.
2. Backup before every change.
3. Never paste client passwords, keys or customer data into any AI tool.
4. AI drafts, you decide.
5. Promise monitoring, fast response and backups, never "you'll never get hacked."
