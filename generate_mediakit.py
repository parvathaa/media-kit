"""
generate_mediakit.py
────────────────────
Reads stats.json → injects values into mediakit_template.html → exports a PDF.

Usage (VS Code terminal):
    python generate_mediakit.py

Output:
    0xpvee_mediakit.pdf   (in the same directory)

Workflow for periodic updates:
    1. Edit stats.json with your latest Instagram Insights numbers.
    2. Run this script.
    3. A fresh PDF is created automatically.
"""

import json
import re
from pathlib import Path
from datetime import datetime

# ── weasyprint for HTML → PDF ──────────────────────────────────────────────
try:
    from weasyprint import HTML, CSS
except ImportError:
    raise SystemExit(
        "weasyprint not installed.\n"
        "Run:  pip install weasyprint"
    )

# ── Paths ──────────────────────────────────────────────────────────────────
BASE   = Path(__file__).parent
STATS  = BASE / "stats.json"
TMPL   = BASE / "mediakit_template.html"
OUTPUT = BASE / "0xpvee_mediakit.pdf"

# ── Load stats ─────────────────────────────────────────────────────────────
with STATS.open() as f:
    stats = json.load(f)

# ── Load HTML template ─────────────────────────────────────────────────────
html = TMPL.read_text(encoding="utf-8")

# ── Helper: replace element text by id ────────────────────────────────────
def set_id(source: str, element_id: str, value: str) -> str:
    """Replace the inner text of the first element with the given id."""
    pattern = rf'(<[^>]+\bid="{re.escape(element_id)}"[^>]*>)[^<]*(</)'
    replacement = rf'\g<1>{value}\2'
    result, n = re.subn(pattern, replacement, source, count=1)
    if n == 0:
        print(f"  [warn] id '{element_id}' not found in template — skipping")
    return result

# ── Inject all dynamic values ──────────────────────────────────────────────
aud = stats.get("audience", {})

# Header "Updated" timestamp
now_str = datetime.now().strftime("%B %Y")
html = set_id(html, "last-updated",   f"Updated: {now_str}")
html = set_id(html, "footer-date",    now_str)

# Top stat cards
html = set_id(html, "stat-followers", stats.get("followers", "—"))
html = set_id(html, "stat-net-new",   f"{stats.get('net_new_followers_60d','—')} in 60d")
html = set_id(html, "stat-views",     stats.get("total_views_60d", "—"))
html = set_id(html, "stat-reached",   stats.get("accounts_reached_60d", "—"))
html = set_id(html, "stat-nonfollower", stats.get("reach_breakdown", ""))
html = set_id(html, "stat-reels",     stats.get("reels_views_60d", "—"))

# Audience demographics
gender = aud.get("gender", {})
html = set_id(html, "aud-men",   gender.get("men",   "—"))
html = set_id(html, "aud-women", gender.get("women", "—"))

# ── Export PDF ─────────────────────────────────────────────────────────────
print(f"  Building PDF from template …")

# Embed Google Fonts locally via base CSS (weasyprint needs network or local fonts)
extra_css = CSS(string="""
  @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');
""")

HTML(string=html, base_url=str(BASE)).write_pdf(
    str(OUTPUT),
)

print(f"  ✓ PDF saved → {OUTPUT}")
print(f"  ✓ Stats timestamp: {now_str}")
