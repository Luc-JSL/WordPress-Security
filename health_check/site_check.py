#!/usr/bin/env python3
"""Secure WP Care: passive website health check for prospecting.

Only looks at what any visitor's browser already sees:
  - the homepage (one request over HTTPS, one over HTTP to see if it redirects)
  - the TLS certificate the site presents on port 443
  - public DNS records (MX, SPF, DMARC) via DNS-over-HTTPS

It never probes login pages, guesses URLs, or scans for vulnerabilities.
Anything deeper needs the site owner's written permission.

Usage:
  python3 site_check.py example.com
  python3 site_check.py --csv prospects.csv --out reports --from-name "Jordan Sledge" --from-email you@example.com
"""
import argparse
import csv
import html
import json
import re
import socket
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

USER_AGENT = "SecureWPCare-HealthCheck/1.0 (passive public check)"
TIMEOUT = 15
MAX_BODY = 2_000_000
# Oldest PHP branch still getting security fixes. Update when a branch reaches end of life.
MIN_SUPPORTED_PHP = (8, 2)
DOH_URL = "https://dns.google/resolve"
WP_VERSION_API = "https://api.wordpress.org/core/version-check/1.7/"

SEVERITY_ORDER = {"critical": 0, "high": 1, "medium": 2, "low": 3}
SEVERITY_POINTS = {"critical": 30, "high": 20, "medium": 10, "low": 4}


@dataclass
class Finding:
    severity: str
    title: str
    meaning: str
    fix: str


@dataclass
class SiteResult:
    domain: str
    business: str = ""
    reachable: bool = False
    final_url: str = ""
    is_wordpress: bool = False
    wp_version: str = ""
    wp_version_source: str = ""
    latest_wp: str = ""
    plugins: list = field(default_factory=list)
    php_version: str = ""
    cert_days_left: int | None = None
    findings: list = field(default_factory=list)
    error: str = ""

    @property
    def score(self) -> int:
        return max(0, 100 - sum(SEVERITY_POINTS[f.severity] for f in self.findings))

    @property
    def grade(self) -> str:
        s = self.score
        return "A" if s >= 90 else "B" if s >= 80 else "C" if s >= 70 else "D" if s >= 60 else "F"


# ---------- network helpers ----------

def normalize_domain(raw: str) -> str:
    raw = raw.strip()
    if "://" not in raw:
        raw = "http://" + raw
    host = urllib.parse.urlparse(raw).hostname or ""
    return host.lower().rstrip(".")


def fetch(url: str):
    """GET a URL, following redirects. Returns (final_url, status, headers, body_text) or raises."""
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        body = resp.read(MAX_BODY).decode(resp.headers.get_content_charset() or "utf-8", "replace")
        return resp.geturl(), resp.status, dict(resp.headers.items()), body


def cert_days_left(host: str) -> int:
    ctx = ssl.create_default_context()
    with socket.create_connection((host, 443), timeout=TIMEOUT) as sock:
        with ctx.wrap_socket(sock, server_hostname=host) as tls:
            not_after = tls.getpeercert()["notAfter"]
    return int((ssl.cert_time_to_seconds(not_after) - time.time()) // 86400)


def doh_txt(name: str, rtype: str = "TXT") -> list:
    """Look up DNS records over HTTPS. Returns record data strings (TXT quotes removed)."""
    url = f"{DOH_URL}?{urllib.parse.urlencode({'name': name, 'type': rtype})}"
    _, _, _, body = fetch(url)
    return parse_doh_answers(json.loads(body))


_latest_wp_cache: list = []


def latest_wordpress_version() -> str:
    if not _latest_wp_cache:
        try:
            _, _, _, body = fetch(WP_VERSION_API)
            _latest_wp_cache.append(json.loads(body)["offers"][0]["current"])
        except Exception:
            _latest_wp_cache.append("")
    return _latest_wp_cache[0]


# ---------- pure parsing helpers (tested offline) ----------

def parse_doh_answers(data: dict) -> list:
    out = []
    for ans in data.get("Answer", []) or []:
        value = ans.get("data", "")
        # TXT records can be split into several quoted strings; join them.
        parts = re.findall(r'"([^"]*)"', value)
        out.append("".join(parts) if parts else value)
    return out


def detect_wordpress(page: str) -> bool:
    return any(marker in page for marker in ("/wp-content/", "/wp-includes/", "wp-json"))


def find_wp_version(page: str) -> tuple:
    """Returns (version, source). Prefers the generator meta tag, falls back to core asset ?ver=."""
    for tag in re.findall(r"<meta[^>]+>", page, flags=re.I):
        if re.search(r'name=["\']generator["\']', tag, flags=re.I):
            m = re.search(r'content=["\']WordPress\s*([\d.]+)', tag, flags=re.I)
            if m:
                return m.group(1), "generator tag"
    m = re.search(r'/wp-includes/[^"\'\s>]+\?ver=(\d+\.\d+(?:\.\d+)?)', page)
    if m:
        return m.group(1), "core file version (likely)"
    return "", ""


def find_plugins(page: str) -> list:
    return sorted(set(re.findall(r"/wp-content/plugins/([a-z0-9][a-z0-9_-]*)/", page, flags=re.I)))


def version_tuple(v: str) -> tuple:
    return tuple(int(x) for x in re.findall(r"\d+", v)[:3]) if v else ()


def compare_wp(found: str, latest: str):
    """Returns 'current', 'patch' (same branch, missing fixes) or 'major' (older branch)."""
    f, l = version_tuple(found), version_tuple(latest)
    if not f or not l:
        return None
    if f[:2] < l[:2]:
        return "major"
    if f < l:
        return "patch"
    return "current"


def php_from_headers(headers: dict) -> str:
    for key, value in headers.items():
        if key.lower() == "x-powered-by":
            m = re.search(r"PHP/(\d+\.\d+(?:\.\d+)?)", value)
            if m:
                return m.group(1)
    return ""


def header_lookup(headers: dict, name: str) -> str:
    for key, value in headers.items():
        if key.lower() == name.lower():
            return value
    return ""


# ---------- analysis ----------

def analyze_page(result: SiteResult, headers: dict, page: str, latest_wp: str) -> None:
    """Adds findings based on the homepage HTML and response headers."""
    result.is_wordpress = detect_wordpress(page)
    if result.is_wordpress:
        result.wp_version, result.wp_version_source = find_wp_version(page)
        result.plugins = find_plugins(page)
        result.latest_wp = latest_wp
        status = compare_wp(result.wp_version, latest_wp)
        if status == "major":
            result.findings.append(Finding(
                "high", f"WordPress is out of date ({result.wp_version}; current is {latest_wp})",
                "Older WordPress versions have publicly known security holes that attackers scan for automatically.",
                "Update WordPress core after taking a full backup and testing on a staging copy."))
        elif status == "patch":
            result.findings.append(Finding(
                "medium", f"WordPress is missing security updates ({result.wp_version}; current is {latest_wp})",
                "Minor releases usually contain security fixes.",
                "Apply the latest minor update (safe to automate with backups in place)."))
        if result.wp_version_source == "generator tag":
            result.findings.append(Finding(
                "low", "Site advertises its WordPress version publicly",
                "Showing the exact version makes it easier for automated attacks to pick targets.",
                "Hide the version number (a one-line setting in most security plugins)."))

    php = php_from_headers(headers)
    if php:
        result.php_version = php
        if version_tuple(php)[:2] < MIN_SUPPORTED_PHP:
            result.findings.append(Finding(
                "high", f"Server runs PHP {php}, which no longer gets security fixes",
                "The language the site runs on is past end of life, so new security holes will never be patched.",
                "Upgrade PHP in the hosting control panel after testing the site on the new version."))
        else:
            result.findings.append(Finding(
                "low", "Server advertises its PHP version",
                "Version details help attackers choose exploits.",
                "Turn off the X-Powered-By header (hosting setting or security plugin)."))

    if result.final_url.startswith("https://"):
        if not header_lookup(headers, "strict-transport-security"):
            result.findings.append(Finding(
                "low", "Missing HSTS security header",
                "Browsers aren't told to always use the secure version of the site.",
                "Enable HSTS once HTTPS works everywhere on the site."))
    missing = [h for h in ("x-content-type-options", "referrer-policy") if not header_lookup(headers, h)]
    framing = header_lookup(headers, "x-frame-options") or (
        "frame-ancestors" in header_lookup(headers, "content-security-policy"))
    if not framing:
        missing.append("x-frame-options")
    if missing:
        result.findings.append(Finding(
            "low", "Basic browser security headers are missing (" + ", ".join(missing) + ")",
            "These headers block common tricks like clickjacking and content sniffing.",
            "Add them through the host, a CDN like Cloudflare, or a security plugin."))


def analyze_email(result: SiteResult, mx: list, root_txt: list, dmarc_txt: list) -> None:
    if not mx:
        return  # domain doesn't receive email, so email spoofing checks don't apply
    if not any(t.lower().startswith("v=spf1") for t in root_txt):
        result.findings.append(Finding(
            "medium", "No SPF record for email",
            "Email providers can't tell which servers are allowed to send mail for this business.",
            "Publish an SPF record listing the services that send your email."))
    dmarc = next((t for t in dmarc_txt if t.lower().startswith("v=dmarc1")), "")
    if not dmarc:
        result.findings.append(Finding(
            "high", "No DMARC record: anyone can send email pretending to be this business",
            "Scammers can send fake invoices or payment requests that look like they came from you.",
            "Publish a DMARC record (start in monitoring mode, then move to blocking)."))
    else:
        m = re.search(r"\bp\s*=\s*(\w+)", dmarc, flags=re.I)
        if m and m.group(1).lower() == "none":
            result.findings.append(Finding(
                "medium", "DMARC is in watch-only mode (p=none)",
                "Fake emails using this domain are reported but still delivered.",
                "Review the reports, then move the policy to quarantine or reject."))


def check_site(raw: str, business: str = "") -> SiteResult:
    result = SiteResult(domain=normalize_domain(raw), business=business)
    host = result.domain
    if not host:
        result.error = "Could not read a domain from the input"
        return result

    try:
        result.final_url, _, headers, page = fetch(f"https://{host}")
        result.reachable = True
    except Exception as exc:
        headers, page = {}, ""
        result.findings.append(Finding(
            "critical", "Secure (HTTPS) version of the site did not load",
            "Visitors may see browser warnings, and Google ranks insecure sites lower.",
            "Install or repair the SSL certificate and make the site load over HTTPS."))
        try:
            result.final_url, _, headers, page = fetch(f"http://{host}")
            result.reachable = True
        except Exception:
            result.error = f"Site unreachable: {exc}"
            return result

    if result.reachable and result.final_url.startswith("https://"):
        try:
            http_final, _, _, _ = fetch(f"http://{host}")  # does plain HTTP upgrade to HTTPS?
            if not http_final.startswith("https://"):
                result.findings.append(Finding(
                    "medium", "Plain HTTP version doesn't redirect to HTTPS",
                    "Some visitors land on the unencrypted version of the site.",
                    "Add a site-wide redirect from http:// to https://."))
        except Exception:
            pass
        try:
            result.cert_days_left = cert_days_left(urllib.parse.urlparse(result.final_url).hostname)
            if result.cert_days_left < 0:
                result.findings.append(Finding("critical", "SSL certificate has expired",
                                               "Visitors get a full-screen security warning.",
                                               "Renew the certificate now and turn on auto-renewal."))
            elif result.cert_days_left < 14:
                result.findings.append(Finding("high", f"SSL certificate expires in {result.cert_days_left} days",
                                               "If it lapses, visitors get a security warning.",
                                               "Renew it and turn on auto-renewal."))
        except ssl.SSLError:
            result.findings.append(Finding("critical", "SSL certificate is invalid",
                                           "Browsers show a security warning to visitors.",
                                           "Replace the certificate with a valid one (free via Let's Encrypt)."))
        except Exception:
            pass

    analyze_page(result, headers, page, latest_wordpress_version() if detect_wordpress(page) else "")

    try:
        analyze_email(result, doh_txt(host, "MX"), doh_txt(host, "TXT"), doh_txt(f"_dmarc.{host}", "TXT"))
    except Exception:
        pass  # DNS lookup failed; skip email checks rather than guess

    result.findings.sort(key=lambda f: SEVERITY_ORDER[f.severity])
    return result


# ---------- reporting ----------

SEVERITY_COLOR = {"critical": "#b42318", "high": "#c4320a", "medium": "#b54708", "low": "#475467"}


def render_report(r: SiteResult, from_name: str = "", from_email: str = "") -> str:
    e = html.escape
    who = e(r.business or r.domain)
    rows = "".join(
        f"<tr><td><span class='sev' style='background:{SEVERITY_COLOR[f.severity]}'>{f.severity.upper()}</span></td>"
        f"<td><strong>{e(f.title)}</strong><br><span class='muted'>{e(f.meaning)}</span></td>"
        f"<td>{e(f.fix)}</td></tr>"
        for f in r.findings) or "<tr><td colspan='3'>No issues found in the public checks. Nice work.</td></tr>"
    facts = [("Website", r.final_url or r.domain),
             ("Runs WordPress", "Yes" if r.is_wordpress else "Not detected")]
    if r.wp_version:
        facts.append(("WordPress version", f"{r.wp_version} (latest: {r.latest_wp or 'unknown'})"))
    if r.php_version:
        facts.append(("PHP version (shown publicly)", r.php_version))
    if r.cert_days_left is not None:
        facts.append(("SSL certificate", f"valid, {r.cert_days_left} days left" if r.cert_days_left >= 0 else "expired"))
    if r.plugins:
        facts.append(("Plugins visible in page code", ", ".join(r.plugins[:12])))
    fact_rows = "".join(f"<tr><th>{e(k)}</th><td>{e(v)}</td></tr>" for k, v in facts)
    contact = ""
    if from_name or from_email:
        contact = (f"<p class='cta'>Questions? Reply to <strong>{e(from_name)}</strong>"
                   f"{' at ' + e(from_email) if from_email else ''}. "
                   "I can fix these and keep the site updated, backed up and monitored every month.</p>")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>Website Health Check: {who}</title>
<style>
 body{{font-family:Helvetica,Arial,sans-serif;color:#1d2939;max-width:760px;margin:32px auto;padding:0 20px;line-height:1.45}}
 h1{{font-size:24px;margin:0 0 4px}} .muted{{color:#667085;font-size:13px}}
 .grade{{display:flex;align-items:center;gap:16px;margin:20px 0;padding:16px;border:1px solid #e4e7ec;border-radius:10px}}
 .letter{{font-size:44px;font-weight:700;color:#1f3a5f;width:64px;text-align:center}}
 table{{width:100%;border-collapse:collapse;margin:12px 0;font-size:14px}}
 th,td{{text-align:left;vertical-align:top;padding:8px;border-bottom:1px solid #e4e7ec}}
 th{{width:34%;color:#475467;font-weight:600}}
 .sev{{color:#fff;font-size:11px;font-weight:700;padding:2px 6px;border-radius:4px}}
 .cta{{margin-top:20px;padding:14px;background:#f2f6fc;border-radius:8px}}
 .fine{{font-size:12px;color:#667085;margin-top:24px}}
</style></head><body>
<h1>Website Health Check: {who}</h1>
<div class="muted">Checked {date.today().isoformat()} &middot; public information only</div>
<div class="grade"><div class="letter">{r.grade}</div>
<div><strong>Score: {r.score}/100</strong><br><span class="muted">{len(r.findings)} item(s) worth attention</span></div></div>
<table>{fact_rows}</table>
<h2 style="font-size:18px">What we found</h2>
<table><tr><th style="width:12%">Level</th><th style="width:50%">Issue and what it means</th><th>How to fix it</th></tr>{rows}</table>
{contact}
<p class="fine">This check only looked at public information any visitor can see: the homepage, its security
certificate and public DNS records. No login pages were accessed and no security scanning was performed.
A full review requires the owner's permission.</p>
</body></html>"""


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "site"


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sites", nargs="*", help="domains or URLs to check")
    ap.add_argument("--csv", help="prospect CSV with columns: business,website[,contact_email]")
    ap.add_argument("--out", default="reports", help="folder for HTML reports and summary.csv")
    ap.add_argument("--from-name", default="", help="your name, shown on the report")
    ap.add_argument("--from-email", default="", help="your email, shown on the report")
    ap.add_argument("--delay", type=float, default=2.0, help="seconds to wait between sites")
    args = ap.parse_args(argv)

    targets = [(s, "", "") for s in args.sites]
    if args.csv:
        with open(args.csv, newline="", encoding="utf-8") as fh:
            for row in csv.DictReader(fh):
                if row.get("website"):
                    targets.append((row["website"], row.get("business", ""), row.get("contact_email", "")))
    if not targets:
        ap.error("give at least one site, or --csv")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    summary_rows = []
    for i, (site, business, contact) in enumerate(targets):
        if i:
            time.sleep(args.delay)
        r = check_site(site, business)
        if r.error:
            print(f"[skip] {site}: {r.error}")
            summary_rows.append({"business": business, "domain": r.domain, "contact_email": contact,
                                 "wordpress": "", "wp_version": "", "grade": "", "score": "",
                                 "top_issue": r.error, "report": ""})
            continue
        report = out / f"{slug(business or r.domain)}.html"
        report.write_text(render_report(r, args.from_name, args.from_email), encoding="utf-8")
        top = r.findings[0].title if r.findings else "No issues found"
        print(f"[{r.grade} {r.score:>3}] {r.domain:<35} WordPress={'yes' if r.is_wordpress else 'no':<3} {top}")
        summary_rows.append({"business": business, "domain": r.domain, "contact_email": contact,
                             "wordpress": "yes" if r.is_wordpress else "no", "wp_version": r.wp_version,
                             "grade": r.grade, "score": r.score, "top_issue": top, "report": report.name})

    with open(out / "summary.csv", "w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"\nReports saved in {out.resolve()}  (summary.csv lists every site)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
