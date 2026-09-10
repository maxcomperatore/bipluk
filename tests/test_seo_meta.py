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

if __name__ == '__main__':
    test_seo()
    test_pwa_manifest()
    test_gsc_targeted_routes()
