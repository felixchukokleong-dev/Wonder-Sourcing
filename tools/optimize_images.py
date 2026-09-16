"""Turn source photos into web-ready responsive WebP for this site.

This is the tool to use for the real photography (factory floor, inspection,
loaded containers, showroom). It handles the things that actually cause
problems with photos:
  - EXIF rotation (phone photos are often stored sideways with an orientation
    flag; without exif_transpose they render rotated on the web)
  - EXIF stripping (removes GPS coordinates and camera serials - a real
    privacy leak on photos shot inside suppliers' factories)
  - resizing to the widths the markup actually uses, so pages stay light

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
QUALITY = 84
EXTS = ('*.jpg', '*.jpeg', '*.png', '*.webp', '*.tif', '*.tiff', '*.heic')

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
        print('''<img src="%s-%d.webp"
     srcset="%s"
     sizes="(max-width:760px) 92vw, 560px"
     width="%d" height="%d" loading="lazy" decoding="async"
     alt="Describe the photo for someone who cannot see it">'''
              % (base, min(widths),
                 ', '.join('%s-%d.webp %dw' % (base, x, x) for x in sorted(widths)),
                 big[1], big[2]))
    print('\nEvery image needs a real alt text. Decorative only? Use alt="".')

if __name__ == '__main__':
    main()
