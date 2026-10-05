"""Turn source photos into web-ready responsive WebP for this site.

This is the tool to use for the real photography (factory floor, inspection,
loaded containers, showroom). It handles the things that actually cause
problems with photos:
  - EXIF rotation (phone photos are often stored sideways with an orientation
    flag; without exif_transpose they render rotated on the web)
  - EXIF stripping (removes GPS coordinates and camera serials - a real
    privacy leak on photos shot inside suppliers' factories)
  - resizing to the widths the markup actually uses, so pages stay light
  - centre-cropping to a single 4:5 ratio, so gallery rails line up

Usage
    python3 tools/optimize_images.py ~/Pictures/factory-shots --name factory-audit
    python3 tools/optimize_images.py photo.jpg --name qc-inspection
    python3 tools/optimize_images.py ~/Photos --out images/ --widths 640,1280

Then reference it with the markup pattern printed at the end (or copy the
pattern from tools/IMAGE-GUIDE.md).
"""
import argparse, os, sys, glob
from PIL import Image, ImageOps

WIDTHS = [540, 1080]
# Quality 72, not the 84 that suited the flat-colour stat cards. Real
# photography of a showroom has gradients, shadow noise and high-frequency
# chair frames, where WebP needs to spend a lot of bits; at 84 this folder of
# 18 photos came out LARGER than the source JPEGs (2876 KB -> 3161 KB). At 72
# it is 2155 KB and visually indistinguishable at these sizes.
QUALITY = 72
EXTS = ('*.jpg', '*.jpeg', '*.png', '*.webp', '*.tif', '*.tiff', '*.heic')

# Every image on this site is 4:5. Source photos arrive at all sorts of
# ratios (the last batch spanned 0.57 to 0.85) and because the galleries are
# horizontal scroll rails with fixed-width cards, mixed ratios leave the cards
# with ragged bottoms. 4:5 is the existing stat-card format, so normalising to
# it makes the photo rail and the stat rail above it read as one set.
ASPECT = (4, 5)


def crop_to_aspect(im, anchor=0.5):
    """Centre-crop to ASPECT. anchor is the fraction of the excess height
    kept above the window: 0.5 centred, lower biases up, higher biases down."""
    w, h = im.size
    target = ASPECT[0] / ASPECT[1]
    if w / h > target:                       # too wide -> trim the sides
        nw = round(h * target)
        x = (w - nw) // 2
        im = im.crop((x, 0, x + nw, h))
    elif w / h < target:                     # too tall -> trim top/bottom
        nh = round(w / target)
        top = max(0, min(h - nh, round((h - nh) * anchor)))
        im = im.crop((0, top, w, top + nh))
    return im

def collect(src):
    if os.path.isfile(src):
        return [src]
    out = []
    for e in EXTS:
        out += sorted(glob.glob(os.path.join(src, '**', e), recursive=True))
        out += sorted(glob.glob(os.path.join(src, '**', e.upper()), recursive=True))
    seen, uniq = set(), []
    for p in out:
        if p not in seen:
            seen.add(p); uniq.append(p)
    return uniq

def slug(name):
    return ''.join(c if c.isalnum() or c in '-_' else '-' for c in name.lower()).strip('-')

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('source', help='image file or directory of images')
    ap.add_argument('--out', default='images', help='output directory (default: images)')
    ap.add_argument('--widths', default=','.join(map(str, WIDTHS)))
    ap.add_argument('--quality', type=int, default=QUALITY)
    ap.add_argument('--name', help='base filename for a single source image')
    ap.add_argument('--no-crop', action='store_true',
                    help='keep the source ratio instead of normalising to %d:%d'
                         % ASPECT)
    ap.add_argument('--anchor', type=float, default=0.5,
                    help='vertical crop bias for tall sources: 0.5 centred, '
                         '0.35 keeps the top (portrait shots), 0.65 keeps the '
                         'bottom (warehouse stacks). Default 0.5')
    a = ap.parse_args()

    widths = [int(w) for w in a.widths.split(',') if w.strip()]
    srcs = collect(a.source)
    if not srcs:
        sys.exit('No images found in %s' % a.source)
    os.makedirs(a.out, exist_ok=True)

    print('%-40s %8s %10s  %s' % ('output', 'width', 'size', 'vs source'))
    print('-' * 82)
    before_total = after_total = 0
    emitted = []
    for p in srcs:
        try:
            im = Image.open(p)
            im = ImageOps.exif_transpose(im)          # honour phone orientation
            if im.mode not in ('RGB', 'RGBA'):
                im = im.convert('RGB')
            elif im.mode == 'RGBA':
                im = im.convert('RGB')                 # WebP on-page; no alpha needed
        except Exception as e:
            print('  SKIP %-36s %s' % (os.path.basename(p), e))
            continue
        base = slug(a.name or os.path.splitext(os.path.basename(p))[0])
        if not a.no_crop:
            im = crop_to_aspect(im, a.anchor)      # normalise to 4:5
        before = os.path.getsize(p); before_total += before
        for w in sorted(widths):
            if w > im.size[0]:
                out_w = im.size[0]
            else:
                out_w = w
            h = round(im.size[1] * out_w / im.size[0])
            r = im if out_w == im.size[0] else im.resize((out_w, h), Image.LANCZOS)
            dest = os.path.join(a.out, '%s-%d.webp' % (base, w))
            r.save(dest, 'WEBP', quality=a.quality, method=6)  # no exif= => metadata stripped
            sz = os.path.getsize(dest); after_total += sz
            pct = ('-%.0f%%' % (100 - 100 * sz / before)) if before else ''
            print('%-40s %8d %9.1fK  %7s' % (dest, out_w, sz / 1024, pct))
            emitted.append((dest, out_w, h))

    print('\ntotal: %.1f KB -> %.1f KB' % (before_total / 1024, after_total / 1024))
    print('\n--- markup pattern (set alt text to describe the photo) ---')
    if emitted:
        big = max(emitted, key=lambda t: t[1])
        base = os.path.relpath(big[0]).rsplit('-', 1)[0]
        if base.startswith('..'):          # --out pointed outside the project
            base = os.path.abspath(big[0]).rsplit('-', 1)[0]
        print('''<img src="%s-%d.webp"
     srcset="%s"
     sizes="(max-width:760px) 92vw, 560px"
     width="%d" height="%d" loading="lazy" decoding="async"
     style="width:100%%;height:auto;aspect-ratio:%d/%d;object-fit:cover;display:block;"
     alt="Describe the photo for someone who cannot see it">'''
              % (base, min(widths),
                 ', '.join('%s-%d.webp %dw' % (base, x, x) for x in sorted(widths)),
                 big[1], big[2], ASPECT[0], ASPECT[1]))
    print('\nEvery image needs a real alt text. Decorative only? Use alt="".')

if __name__ == '__main__':
    main()
