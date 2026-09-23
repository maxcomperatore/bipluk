import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from starlette.testclient import TestClient
from main import app

def test_seo():
    client = TestClient(app)
    res = client.get('/', headers={'Accept-Encoding': 'gzip'})
    assert res.status_code == 200, f"Status code was {res.status_code}"
    
    html = res.text
    checks = [
        'name="twitter:card" content="summary_large_image"',
        'name="twitter:site" content="@bipluk"',
        'name="twitter:creator" content="@bipluk"',
        'rel="apple-touch-icon" sizes="180x180"',
        'rel="icon" href="/favicon.ico"',
        'property="og:locale" content="en_US"',
        'name="theme-color" content="#09090b"',
        'rel="manifest" href="/site.webmanifest"',
        'og_image.png'
    ]
    for check in checks:
        assert check in html, f"Missing check: {check}"
        print(f"PASS: {check}")
        
    print("\nAll SEO meta checks passed successfully!")

def test_pwa_manifest():
    client = TestClient(app)
    res = client.get('/site.webmanifest')
    assert res.status_code == 200, f"Manifest status was {res.status_code}"
    data = res.json()
    assert data.get('theme_color') == '#09090b'
    assert data.get('background_color') == '#09090b'
    
    icons = data.get('icons', [])
    assert len(icons) >= 4, f"Expected at least 4 icons, found {len(icons)}"
    
    purposes = {icon.get('purpose', 'any') for icon in icons}
    assert 'maskable' in purposes, "Missing maskable icon for Android!"
    
    sizes = {icon.get('sizes') for icon in icons}
    assert '192x192' in sizes, "Missing 192x192 icon for Android!"
    assert '512x512' in sizes, "Missing 512x512 icon for Android!"
    
    for icon in icons:
        src = icon['src']
        r = client.get(src)
        assert r.status_code == 200, f"Failed to fetch {src}: status {r.status_code}"
        assert len(r.content) > 0, f"Empty file: {src}"
        print(f"PASS PWA ICON: {src} ({icon.get('sizes')}, purpose: {icon.get('purpose')})")
        
    print("\nAll PWA manifest and Android icon checks passed successfully!")

def test_gsc_targeted_routes():
    client = TestClient(app)
    
    # 1. sysex-librarian-windows route
    res = client.get('/sysex-librarian-windows')
    assert res.status_code == 200
    assert "Snoize SysEx Librarian for Windows & Mac" in res.text
    assert '"@type": "FAQPage"' in res.text
    assert "Is there a Snoize SysEx Librarian for Windows?" in res.text
    
    # 2. snoize-for-windows alias
    res_snoize = client.get('/snoize-for-windows')
    assert res_snoize.status_code == 200

    # 3. sysex-librarian-alternatives
    res_alt = client.get('/sysex-librarian-alternatives')
    assert res_alt.status_code == 200
    assert "Knob Cloud" in res_alt.text
    assert '"@type": "FAQPage"' in res_alt.text
    
    # 4. Resources
    res_res = client.get('/resources')
    assert res_res.status_code == 200
    assert "Free MIDI & SysEx Tools, Guides & Resources" in res_res.text

def test_pricing_page():
    client = TestClient(app)
    
    # 1. /pricing route returns 200
    res = client.get('/pricing')
    assert res.status_code == 200, f"Expected 200 from /pricing, got {res.status_code}"
    html = res.text

    # 2. /pricing/ route returns 200
    res_slash = client.get('/pricing/')
    assert res_slash.status_code == 200, f"Expected 200 from /pricing/, got {res_slash.status_code}"

    # 3. SEO Metadata checks
    assert '<link rel="canonical" href="https://bipluk.com/pricing">' in html
    assert 'content="https://bipluk.com/pricing"' in html
    assert 'Bipluk Pricing &amp; Plans' in html or 'Bipluk Pricing & Plans' in html
    assert 'name="twitter:card" content="summary_large_image"' in html
    assert 'name="theme-color" content="#09090b"' in html

    # 4. JSON-LD Rich Results checks for Google SERP
    assert '"@type": "SoftwareApplication"' in html
    assert '"@type": "BreadcrumbList"' in html
    assert '"@type": "FAQPage"' in html
    assert '"name": "bipluk Free"' in html
    assert '"name": "bipluk+ Lifetime"' in html
    assert '"name": "bipluk Studio Commercial"' in html

    # 5. Full Tier Breakdowns
    assert "Free Forever" in html
    assert "bipluk+ Lifetime" in html
    assert "Studio / Commercial" in html

    # 6. Feature Comparison Matrix
    assert "Feature Comparison Matrix" in html
    assert "Cloud Vault &amp; Patch Storage" in html or "Cloud Vault & Patch Storage" in html
    assert "Hardware Engine &amp; Web MIDI" in html or "Hardware Engine & Web MIDI" in html
    assert "Synthesizer Decoders &amp; Parsers" in html or "Synthesizer Decoders & Parsers" in html

    # 7. Refund & Cancellation Policies
    assert "Refund &amp; Cancellation Policy" in html or "Refund & Cancellation Policy" in html
    assert "Zero Subscriptions · Zero Automatic Renewals · Nothing to Cancel" in html
    assert "White-Glove Dump Recovery Guarantee" in html

    # 8. Sitemap inclusion
    res_sitemap = client.get('/sitemap.xml')
    assert res_sitemap.status_code == 200
    assert 'https://bipluk.com/pricing</loc>' in res_sitemap.text

if __name__ == '__main__':
    test_seo()
    test_pwa_manifest()
    test_gsc_targeted_routes()
    test_pricing_page()
