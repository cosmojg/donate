# donate

A simple, static page for accepting [Zcash](https://z.cash/) donations, in the
same minimalist style as [cosmo.red](https://cosmo.red).

Live at **https://donate.cosmo.red**.

## Address

```
u1qlrh06j0mlta7xdarj6yjxj7wyt3z0lhkt4kuudhlmlc8nd3mr7tau4tqquy73tsexuhh4c2jxld0wvlgf7953a8u54fd9t92s7jtr6gnrpfguwj6ua323snf3xrym9d79w6p8yny7yfx9sdshqpaty7rgn49r6hn7wvm7zfyuu0lr08
```

## Build

[`address.txt`](address.txt) is the single source of truth. The QR code, the
favicon, and the address shown on the page are all generated from it, so they
can never drift apart:

```sh
python -m pip install segno
python build.py            # writes index.html, zcash-qr.svg, favicon.svg
```

Optionally, decode the generated QR back to the address to prove it is correct:

```sh
python -m pip install opencv-python-headless numpy
python build.py --verify
```

No build step is required to deploy — it is plain HTML, CSS, and SVG served as
static files (e.g. via GitHub Pages).
