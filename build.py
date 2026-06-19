#!/usr/bin/env python3
"""Build the donate page from a single source of truth.

`address.txt` holds the Zcash unified address. Everything else is derived from
it so the QR code, the address shown on the page, and the `zcash:` link can
never drift apart:

    zcash-qr.svg   scannable QR of the address with a centered Zcash mark
    favicon.svg    the same Zcash mark, on its own
    index.html     the donation page, with the address injected

Usage:
    python -m pip install segno      # required
    python build.py                  # writes the three files above
    python build.py --verify         # also decode the QR back to the address
                                     # (needs: pip install opencv-python-headless numpy)
"""
import math
import sys

# Gruvbox palette (matching cosmo.red / aslmath), with Zcash gold as the accent.
BG = "#282828"      # page background / dark QR modules
CREAM = "#fbf1c7"   # QR card background (quiet zone)
GOLD = "#fabd2f"    # Zcash-gold accent / logo disc

ADDRESS = open("address.txt", encoding="utf-8").read().strip()


def zcash_mark(cx, cy, r, fill):
    """SVG for the Zcash mark (a bold 'Z' with a central vertical bar),
    sized to a logo disc of radius `r` centred at (cx, cy)."""
    w, h, t = 0.47 * r, 0.52 * r, 0.15 * r  # half-width, half-height, stroke

    def rect(x0, y0, x1, y1):
        return (f'<rect x="{x0:.3f}" y="{y0:.3f}" '
                f'width="{x1 - x0:.3f}" height="{y1 - y0:.3f}"/>')

    top = rect(cx - w, cy - h, cx + w, cy - h + t)
    bottom = rect(cx - w, cy + h - t, cx + w, cy + h)
    vbar = rect(cx - t / 2, cy - h, cx + t / 2, cy + h)
    # diagonal stroke, top-right -> bottom-left
    p1 = (cx + w, cy - h + t)
    p2 = (cx - w, cy + h - t)
    dx, dy = p2[0] - p1[0], p2[1] - p1[1]
    length = math.hypot(dx, dy)
    ox, oy = -dy / length * t / 2, dx / length * t / 2
    pts = [(p1[0] + ox, p1[1] + oy), (p1[0] - ox, p1[1] - oy),
           (p2[0] - ox, p2[1] - oy), (p2[0] + ox, p2[1] + oy)]
    diag = ('<polygon points="'
            + " ".join(f"{x:.3f},{y:.3f}" for x, y in pts) + '"/>')
    return f'<g fill="{fill}">{top}{bottom}{vbar}{diag}</g>'


def build_qr():
    import segno
    qr = segno.make(ADDRESS, error="h", micro=False)
    matrix = [list(row) for row in qr.matrix]
    n = len(matrix)

    border = 4              # quiet zone
    total = n + 2 * border
    c = total / 2.0
    r_knock = 7.5           # cream knockout radius (~20% of the symbol)
    r_disc = 6.4            # gold logo disc radius

    # dark modules, merged into horizontal runs to keep the file small
    runs = []
    for y, row in enumerate(matrix):
        x = 0
        while x < n:
            if row[x]:
                x0 = x
                while x < n and row[x]:
                    x += 1
                runs.append((x0 + border, y + border, x - x0))
            else:
                x += 1
    path = "".join(f"M{px} {py}h{w}v1h-{w}z" for px, py, w in runs)

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total} {total}" '
        f'shape-rendering="crispEdges" role="img" '
        f'aria-label="QR code for a Zcash unified address">'
        f'<rect width="{total}" height="{total}" rx="3" fill="{CREAM}"/>'
        f'<path fill="{BG}" d="{path}"/>'
        f'<circle cx="{c}" cy="{c}" r="{r_knock}" fill="{CREAM}"/>'
        f'<circle cx="{c}" cy="{c}" r="{r_disc}" fill="{GOLD}"/>'
        f'<g shape-rendering="geometricPrecision">{zcash_mark(c, c, r_disc, BG)}</g>'
        f'</svg>\n'
    )
    with open("zcash-qr.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"zcash-qr.svg  version={qr.version} modules={n}x{n} bytes={len(svg)}")
    return qr


def build_favicon():
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32" '
        'role="img" aria-label="Zcash">'
        f'<circle cx="16" cy="16" r="16" fill="{GOLD}"/>'
        f'{zcash_mark(16, 16, 13, BG)}'
        '</svg>\n'
    )
    with open("favicon.svg", "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"favicon.svg   bytes={len(svg)}")


def build_html():
    addr = ADDRESS
    html = f"""<!DOCTYPE html>
<html lang="en">

<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>donate</title>
    <meta name="description" content="Support cosmo's work with a Zcash donation.">
    <meta name="color-scheme" content="dark">
    <link rel="icon" href="favicon.svg">
    <style>
        body {{
            font-family: Arial, Helvetica, sans-serif;
            background-color: {BG};
            color: #ebdbb2;
            line-height: 1.5;
        }}
        main {{
            margin: auto;
            max-width: 70ch;
            padding: 2ch;
            text-align: center;
        }}
        h1 {{
            color: {GOLD};
            margin-bottom: 0.25rem;
        }}
        p {{ margin: 0.75rem 0; }}
        .muted {{ color: #a89984; }}
        a {{ color: {GOLD}; text-decoration: none; }}
        a:hover {{ text-decoration: underline; }}
        .qr {{
            display: block;
            width: min(76vw, 300px);
            height: auto;
            margin: 1.5rem auto 1rem;
        }}
        .addr {{
            display: block;
            max-width: 54ch;
            margin: 1rem auto;
            padding: 0.85rem 1rem;
            background-color: #32302f;
            border: 1px solid #504945;
            border-radius: 8px;
            color: #ebdbb2;
            font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
            font-size: 0.8rem;
            line-height: 1.6;
            text-align: left;
            word-break: break-all;
            user-select: all;
        }}
        .actions {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.6rem;
            justify-content: center;
            margin: 1rem 0;
        }}
        button, .btn {{
            font: inherit;
            color: {GOLD};
            background-color: transparent;
            border: 1px solid {GOLD};
            border-radius: 8px;
            padding: 0.5rem 1.2rem;
            cursor: pointer;
            text-decoration: none;
            transition: background-color 0.15s, color 0.15s;
        }}
        button:hover, .btn:hover {{
            background-color: {GOLD};
            color: {BG};
            text-decoration: none;
        }}
        .back {{ margin-top: 2.5rem; }}
        .back a {{ color: #a89984; }}
        ::selection {{ background-color: {GOLD}; color: {BG}; }}
    </style>
</head>

<body>
    <main>
        <h1>donate</h1>
        <p class="muted">Support my work with a <a href="https://z.cash/">Zcash</a> donation.</p>

        <img class="qr" src="zcash-qr.svg" width="300" height="300"
            alt="QR code for cosmo's Zcash unified address">

        <p class="muted">Scan the code, tap to open your wallet, or copy the unified address:</p>

        <code class="addr" id="addr">{addr}</code>

        <div class="actions">
            <button id="copy" type="button" aria-label="Copy Zcash address to clipboard">copy address</button>
            <a class="btn" href="zcash:{addr}">open in wallet</a>
        </div>

        <p class="muted">Thank you. &#9829;</p>

        <p class="back"><a href="https://cosmo.red/">&larr; cosmo.red</a></p>
    </main>

    <script>
        const button = document.getElementById("copy");
        const address = document.getElementById("addr").textContent;
        button.addEventListener("click", async () => {{
            try {{
                await navigator.clipboard.writeText(address);
            }} catch (err) {{
                const range = document.createRange();
                range.selectNode(document.getElementById("addr"));
                const sel = window.getSelection();
                sel.removeAllRanges();
                sel.addRange(range);
                document.execCommand("copy");
                sel.removeAllRanges();
            }}
            const label = button.textContent;
            button.textContent = "copied!";
            setTimeout(() => {{ button.textContent = label; }}, 1500);
        }});
    </script>
</body>

</html>
"""
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print(f"index.html    bytes={len(html)}")
    # consistency guard: the address must appear verbatim, and only the
    # expected number of times (the <code> block and the zcash: link).
    assert html.count(addr) == 2, "address not injected as expected"


def verify(qr):
    """Render the final QR exactly as it appears and decode it back."""
    import numpy as np
    import cv2

    matrix = [list(row) for row in qr.matrix]
    n = len(matrix)
    border = 4
    total = n + 2 * border
    c = total / 2.0
    r_knock, r_disc = 7.5, 6.4
    w, h, t = 0.47 * r_disc, 0.52 * r_disc, 0.15 * r_disc

    s = 12
    img = np.full((total * s, total * s), 235, np.uint8)  # cream
    for y, row in enumerate(matrix):
        for x, v in enumerate(row):
            if v:
                img[(y + border) * s:(y + border + 1) * s,
                    (x + border) * s:(x + border + 1) * s] = 34
    yy, xx = np.mgrid[0:total * s, 0:total * s]
    dist = np.hypot(xx / s - c, yy / s - c)
    img[dist <= r_knock] = 235
    img[dist <= r_disc] = 191
    img[int((c - h) * s):int((c - h + t) * s), int((c - w) * s):int((c + w) * s)] = 34
    img[int((c + h - t) * s):int((c + h) * s), int((c - w) * s):int((c + w) * s)] = 34
    img[int((c - h) * s):int((c + h) * s), int((c - t / 2) * s):int((c + t / 2) * s)] = 34

    data, _, _ = cv2.QRCodeDetector().detectAndDecode(img)
    assert data == ADDRESS, f"QR decoded to {data!r}, expected the address"
    print("verify        QR decodes back to the address ✓")


def main():
    print(f"address       {ADDRESS[:14]}...{ADDRESS[-12:]} ({len(ADDRESS)} chars)")
    qr = build_qr()
    build_favicon()
    build_html()
    if "--verify" in sys.argv:
        verify(qr)


if __name__ == "__main__":
    main()
