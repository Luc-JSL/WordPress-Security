"""Offline tests: run with `python3 -m unittest test_site_check.py` from this folder."""
import threading
import unittest
from http.server import BaseHTTPRequestHandler, HTTPServer

import site_check as sc

WP_PAGE = """<html><head>
<meta name="generator" content="WordPress 6.4.2" />
<link rel='stylesheet' href='https://shop.test/wp-content/plugins/woocommerce/assets/css/woo.css?ver=8.1' />
<script src='https://shop.test/wp-content/plugins/contact-form-7/includes/js/index.js?ver=5.8'></script>
<script src='https://shop.test/wp-includes/js/jquery/jquery.min.js?ver=3.7.1'></script>
</head><body>Hello</body></html>"""


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        body = WP_PAGE.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("X-Powered-By", "PHP/7.4.33")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args):
        pass


class ParsingTests(unittest.TestCase):
    def test_normalize_domain(self):
        self.assertEqual(sc.normalize_domain("https://WWW.Example.com/about"), "www.example.com")
        self.assertEqual(sc.normalize_domain("example.com"), "example.com")

    def test_generator_tag_any_attribute_order(self):
        self.assertEqual(sc.find_wp_version(WP_PAGE), ("6.4.2", "generator tag"))
        flipped = '<meta content="WordPress 6.6" name="generator">'
        self.assertEqual(sc.find_wp_version(flipped)[0], "6.6")

    def test_core_asset_fallback(self):
        page = "<script src='/wp-includes/js/wp-emoji-release.min.js?ver=6.5.3'></script>"
        self.assertEqual(sc.find_wp_version(page), ("6.5.3", "core file version (likely)"))

    def test_bundled_library_version_is_not_wordpress(self):
        jquery = "<script src='https://x.com/wp-includes/js/jquery/jquery.min.js?ver=3.7.1'></script>"
        self.assertEqual(sc.find_wp_version(jquery), ("", ""))
        block_css = "<link href='/wp-includes/css/dist/block-library/style.min.css?ver=6.6.2'>"
        self.assertEqual(sc.find_wp_version(jquery + block_css)[0], "6.6.2")
        emoji_json = '"concatemoji":"https:\\/\\/x.com\\/wp-includes\\/js\\/wp-emoji-release.min.js?ver=6.6.2"'
        self.assertEqual(sc.find_wp_version(jquery + emoji_json)[0], "6.6.2")

    def test_plugins(self):
        self.assertEqual(sc.find_plugins(WP_PAGE), ["contact-form-7", "woocommerce"])

    def test_compare_versions(self):
        self.assertEqual(sc.compare_wp("6.4.2", "7.1"), "major")
        self.assertEqual(sc.compare_wp("7.1", "7.1.2"), "patch")
        self.assertEqual(sc.compare_wp("7.1.2", "7.1.2"), "current")
        self.assertIsNone(sc.compare_wp("", "7.1"))

    def test_doh_txt_joins_split_strings(self):
        data = {"Answer": [{"data": '"v=spf1 include:_spf.google.com " "~all"'}]}
        self.assertEqual(sc.parse_doh_answers(data), ["v=spf1 include:_spf.google.com ~all"])

    def test_email_findings(self):
        r = sc.SiteResult(domain="shop.test")
        sc.analyze_email(r, ["10 mx.shop.test."], ["google-site-verification=abc"], [])
        titles = " ".join(f.title for f in r.findings)
        self.assertIn("No SPF", titles)
        self.assertIn("No DMARC", titles)

        r2 = sc.SiteResult(domain="shop.test")
        sc.analyze_email(r2, ["10 mx."], ["v=spf1 -all"], ["v=DMARC1; p=none; rua=mailto:x@shop.test"])
        self.assertEqual([f.severity for f in r2.findings], ["medium"])

        r3 = sc.SiteResult(domain="shop.test")
        sc.analyze_email(r3, [], [], [])  # no MX: email checks don't apply
        self.assertEqual(r3.findings, [])


class EndToEndTest(unittest.TestCase):
    def test_local_wordpress_site(self):
        server = HTTPServer(("127.0.0.1", 0), Handler)
        threading.Thread(target=server.serve_forever, daemon=True).start()
        try:
            url = f"http://127.0.0.1:{server.server_port}/"
            final_url, status, headers, page = sc.fetch(url)
            self.assertEqual(status, 200)
            r = sc.SiteResult(domain="shop.test", business="Joe's <Plumbing>", final_url=final_url, reachable=True)
            sc.analyze_page(r, headers, page, latest_wp="7.1.2")
        finally:
            server.shutdown()
            server.server_close()

        self.assertTrue(r.is_wordpress)
        self.assertEqual(r.wp_version, "6.4.2")
        self.assertEqual(r.php_version, "7.4.33")
        severities = sorted(f.severity for f in r.findings)
        self.assertEqual(severities.count("high"), 2)  # outdated WordPress + end-of-life PHP
        self.assertLess(r.score, 70)

        report = sc.render_report(r, "Jordan Sledge", "jordan@example.com")
        self.assertIn("Joe&#x27;s &lt;Plumbing&gt;", report)  # business name is escaped
        self.assertIn("PHP 7.4.33", report)
        self.assertIn("public information only", report)


if __name__ == "__main__":
    unittest.main()
