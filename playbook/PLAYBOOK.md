# Secure WP Care: 30-Day Launch Playbook

**The business:** small businesses pay you monthly to keep their WordPress sites secure,
updated and backed up. Claude does the heavy lifting; you're the accountable expert.
**Goal:** about 30 sites at about $65/month on average, which is about $2,000/month.

---

## Week 1: Build your lab (all free)

- [ ] Install **LocalWP** (localwp.com) and create 3 practice WordPress sites on your PC
- [ ] On each site, install: **Wordfence** (security), **UpdraftPlus** (backups)
- [ ] Install **MainWP** dashboard on one site and connect the other two (manage all from one screen)
- [ ] Make a backup, break a site on purpose (delete a plugin folder), then **restore it**
- [ ] Practice hardening: hide WordPress version, turn off file editing, enable two-step login for admins
- [ ] Create a free **UptimeRobot** account and add a monitor for any live site you own
- [ ] Run the health check tool on **your own** sites:
      `python3 health_check/site_check.py yoursite.com`

**Learn with Claude (copy these prompts):**
- "Teach me WordPress security hardening one step at a time. Quiz me after each step."
- "Explain what each finding in this report means and how I'd fix it on a real site: [paste report text]"
- "Walk me through cleaning a hacked WordPress site, from backup to verifying it's clean."

## Week 2: Set up your business

- [ ] Pick a name (or use "Secure WP Care") and get a domain (~$12/year)
- [ ] Set up email on that domain **with SPF, DKIM and DMARC done right** (your own proof you know this)
- [ ] One-page website: what you do, the 3 plans below, "Get a free website health check" button
- [ ] Write your client agreement using the checklist below (have Claude draft it, then read every line)
- [ ] Make a prospect tracker (Google Sheet) with these columns:
      `Business | Website | Email | Grade | Top issue | Date emailed | Follow-up date | Status`

## Weeks 3–4: Start selling (no sales calls)

- [ ] Collect 50 local business websites (Google Maps: plumbers, dentists, salons, contractors, restaurants
      around Conway and Little Rock) into `prospects.csv`
- [ ] Run the health check on all of them; keep only grades C, D and F
- [ ] Email **30 a week** with their report attached (template below), and follow up once after 5 days
- [ ] Email **10 small web design agencies or freelance designers** a week (partner template below)
- [ ] Post Fiverr/Upwork gigs: "WordPress maintenance, updates and security" and "Hacked WordPress site cleanup"
- [ ] Ask friends and family who own businesses; offer 2 pilot clients their first month free
- [ ] Goal by day 30: **2 pilot clients** and a few real conversations by email

---

## Your plans and prices

| Plan | Price | What's included |
|---|---|---|
| **Agency white-label** | $30–40 per site/month | Same as Essential, under the agency's brand; they talk to the client |
| **Essential** | $79/month | Weekly updates (tested), daily backups, uptime monitoring, monthly report |
| **Secure** | $99/month | Essential + firewall, malware scans, hardening, 1 hour of fixes per month |
| **Hacked site cleanup** | $150–300 one-time | Clean, restore, harden; then offer a monthly plan |
| **Email Lockdown add-on** | $150–300 one-time | SPF, DKIM, DMARC set up and moved to enforcement |

---

## Email templates (Claude can personalize each one)

**Cold email to a local business**

> **Subject:** Quick check on [website]
>
> Hi [Name], I'm a cybersecurity student in Conway and I run free website health checks for local
> businesses. Yours turned up [number] things worth fixing (report attached), including [top issue in
> plain words].
>
> I handle updates, backups and security monitoring for $79/month, and the first month is free if
> you'd like to try it. Happy to answer any questions by email.
>
> [Your name] · [your business email] · [your mailing address]
>
> Not interested? Reply "no thanks" and I won't email again.

**Follow-up (5 days later, once only)**

> Hi [Name], just making sure the report reached you. The [top issue] is the one I'd fix first.
> I'm glad to answer questions by email.
>
> [Your name]

**Agency / web designer partner**

> **Subject:** White-label WordPress maintenance for your clients
>
> Hi [Name], I handle WordPress updates, backups and security monitoring under your brand, so your
> clients see you, not me. $35 per site per month, monthly report included.
>
> Want to try it free on 2 of your client sites for 30 days?
>
> [Your name] · [site] · [mailing address]

**Cold email law (CAN-SPAM):** use your real name, an honest subject line, a physical mailing address
(a P.O. box works), and stop emailing anyone who says no.

---

## New client onboarding checklist

- [ ] Signed agreement (below) and first payment
- [ ] Client creates a **separate admin account for you**. Never ask for their password; never send
      passwords by text or email (use a password manager's share feature)
- [ ] Take a full backup **before touching anything**
- [ ] Connect the site to MainWP, Wordfence, UpdraftPlus, UptimeRobot
- [ ] Baseline report: what you found on day one (makes your value visible)
- [ ] Updates: test on a staging copy first when the host offers one

## Client agreement checklist (have Claude draft it; this isn't legal advice)

- [ ] What's included and what isn't (redesigns, new features and content edits are extra)
- [ ] Price, billing date, how to cancel (30 days' notice)
- [ ] Response time in writing (for example, "within 12 hours"; no 24/7 promise)
- [ ] Written permission for you to update, scan and back up the site
- [ ] Backup policy and how restores work
- [ ] Limit of liability (capped at fees paid in the last 3 months is common)
- [ ] Their responsibilities: keep hosting paid, don't install random plugins without asking

---

## Money and protection

- Set aside **25% of every payment** for taxes (you're self-employed for this income)
- Track income and expenses in a simple spreadsheet from day one
- At about **10 clients**: get professional liability (errors & omissions) insurance and consider an LLC

## Rules you don't break

1. Public checks only before permission. **Never scan or test a site without written permission.**
2. Backup before every change.
3. Never paste client passwords, keys or customer data into any AI tool.
4. AI drafts, you decide: read every email, agreement and fix before it goes out.
5. Don't promise "you'll never get hacked." Promise monitoring, fast response and backups.
