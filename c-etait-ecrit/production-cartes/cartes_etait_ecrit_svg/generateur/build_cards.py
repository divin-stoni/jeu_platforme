#!/usr/bin/env python3
# C'ÉTAIT ÉCRIT : générateur des cartes SVG (63 x 88 mm, viewBox 630 x 880)
# Usage : python3 build_cards.py <dossier_images> <csv_cartes> <csv_prompts> <dossier_sortie>
import sys, os, re, glob, io, base64, random, unicodedata
import pandas as pd
from PIL import Image, ImageFont

IMG_DIR, CSV_C, CSV_P, OUT = sys.argv[1:5]
FIX = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img_fixed')
W, H = 630, 880
MID, GOLD, CREAM, RED, GREEN, BLUE, YEL, PUR = '#14213d', '#d4a017', '#fbf1d4', '#d62828', '#2a9d4a', '#2a6fdb', '#f2c80f', '#6b3fa0'
FF = 'font-family="DejaVu Sans, Verdana, Arial, sans-serif"'
FD = '/usr/share/fonts/truetype/dejavu/'
_fc = {}
def font(size, bold=False, ital=False):
    k = (size, bold, ital)
    if k not in _fc:
        n = 'DejaVuSans' + ('-Bold' if bold else '') + ('-Oblique' if ital and not bold else '')
        if bold and ital: n = 'DejaVuSans-BoldOblique'
        _fc[k] = ImageFont.truetype(FD + n + '.ttf', size)
    return _fc[k]
def tw(s, size, bold=False, ital=False): return font(size, bold, ital).getlength(s)
def esc(s): return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
def wrap(text, size, maxw, bold=False, ital=False):
    out, cur = [], ''
    for w in text.split():
        t = (cur + ' ' + w).strip()
        if tw(t, size, bold, ital) <= maxw or not cur: cur = t
        else: out.append(cur); cur = w
    if cur: out.append(cur)
    return out
_u = [0]
def uid(p='c'): _u[0] += 1; return f'{p}{_u[0]}'
def T(x, y, s, size=28, fill=MID, bold=False, anchor='start', ital=False, extra=''):
    return (f'<text x="{x}" y="{y}" {FF} font-size="{size}" fill="{fill}" text-anchor="{anchor}"'
            f'{" font-weight=\"bold\"" if bold else ""}{" font-style=\"italic\"" if ital else ""} {extra}>{esc(s)}</text>')
def block(lines, x, y, size, lh, fill=MID, bold=False, anchor='start', ital=False):
    return ''.join(T(x, y + i * lh, l, size, fill, bold, anchor, ital) for i, l in enumerate(lines))
def fit_title(s, maxw, size=36, mn=24, bold=True):
    while size > mn and tw(s, size, bold) > maxw: size -= 1
    return size

# ---------- images ----------
_cache = {}
def data_uri(path, maxdim=1100):
    if path in _cache: return _cache[path]
    im = Image.open(path).convert('RGB')
    if max(im.size) > maxdim: im.thumbnail((maxdim, maxdim), Image.LANCZOS)
    b = io.BytesIO(); im.save(b, 'JPEG', quality=84, optimize=True)
    u = 'data:image/jpeg;base64,' + base64.b64encode(b.getvalue()).decode()
    _cache[path] = u; return u
def image(x, y, w, h, path, rx=0, fit='slice', zoom=None):
    cid = uid('cp')
    pa = f'xMidYMid {fit}'
    clip = f'<clipPath id="{cid}"><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}"/></clipPath>'
    if zoom:
        iw, ih = w * zoom, h * zoom
        return clip + f'<image xlink:href="{data_uri(path)}" x="{x-(iw-w)/2}" y="{y-(ih-h)/2}" width="{iw}" height="{ih}" preserveAspectRatio="{pa}" clip-path="url(#{cid})"/>'
    return clip + f'<image xlink:href="{data_uri(path)}" x="{x}" y="{y}" width="{w}" height="{h}" preserveAspectRatio="{pa}" clip-path="url(#{cid})"/>'

# ---------- icônes ----------
def pawn(cx, cy, s, fill=CREAM, sw=5):
    return (f'<g transform="translate({cx},{cy}) scale({s/100})" stroke="{MID}" stroke-width="{sw}" stroke-linejoin="round" fill="{fill}">'
            f'<circle cx="0" cy="-32" r="17"/><path d="M-11 -17 L11 -17 L21 28 L-21 28Z"/><rect x="-30" y="28" width="60" height="15" rx="6"/></g>')
def hourglass(cx, cy, s, col=GOLD):
    return (f'<g transform="translate({cx},{cy}) scale({s/100})" stroke="{MID}" stroke-width="6" stroke-linejoin="round">'
            f'<path d="M-30 -44 L30 -44 L4 0 L30 44 L-30 44 L-4 0Z" fill="{CREAM}"/><path d="M-20 -36 L20 -36 L0 -6Z M-24 38 L24 38 L0 8Z" fill="{col}" stroke="none"/>'
            f'<rect x="-36" y="-52" width="72" height="10" rx="4" fill="{col}"/><rect x="-36" y="42" width="72" height="10" rx="4" fill="{col}"/></g>')
DOTS = {1: [(0, 0)], 2: [(-1, -1), (1, 1)], 3: [(-1, -1), (0, 0), (1, 1)], 4: [(-1, -1), (1, -1), (-1, 1), (1, 1)],
        5: [(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)], 6: [(-1, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (1, 1)]}
def die(cx, cy, s, n):
    d = ''.join(f'<circle cx="{cx+dx*s*0.26}" cy="{cy+dy*s*0.26}" r="{s*0.075}" fill="{MID}"/>' for dx, dy in DOTS[n])
    return f'<rect x="{cx-s/2}" y="{cy-s/2}" width="{s}" height="{s}" rx="{s*0.2}" fill="{CREAM}" stroke="{MID}" stroke-width="3.5"/>' + d
def check(cx, cy, r):
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{GREEN}" stroke="{CREAM}" stroke-width="5"/>'
            f'<path d="M{cx-r*.45} {cy+r*.02} L{cx-r*.1} {cy+r*.38} L{cx+r*.5} {cy-r*.36}" fill="none" stroke="#fff" stroke-width="{r*.24}" stroke-linecap="round" stroke-linejoin="round"/>')
def cross(cx, cy, r):
    k = r * .38
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{RED}" stroke="{CREAM}" stroke-width="5"/>'
            f'<path d="M{cx-k} {cy-k} L{cx+k} {cy+k} M{cx+k} {cy-k} L{cx-k} {cy+k}" stroke="#fff" stroke-width="{r*.24}" stroke-linecap="round"/>')
def mirror(cx, cy, s):
    return (f'<g transform="translate({cx},{cy}) scale({s/100})" stroke="{MID}" stroke-width="6" stroke-linejoin="round">'
            f'<rect x="-8" y="14" width="16" height="38" rx="7" fill="{GOLD}"/><ellipse cx="0" cy="-12" rx="30" ry="36" fill="{GOLD}"/>'
            f'<ellipse cx="0" cy="-12" rx="21" ry="27" fill="#bfe3f2"/><path d="M-10 -26 L2 -34" stroke="#fff" stroke-width="5" stroke-linecap="round"/></g>')
def ticket(cx, cy, s):
    return (f'<g transform="translate({cx},{cy}) scale({s/100})" stroke="{MID}" stroke-width="6" stroke-linejoin="round">'
            f'<path d="M-42 -26 L42 -26 L42 -8 L36 -3 L42 3 L42 26 L-42 26 L-42 8 L-36 3 L-42 -3Z" fill="{GOLD}"/>'
            f'<path d="M-6 -26 L2 -12 L-6 0 L4 12 L-4 26" fill="none" stroke="{CREAM}" stroke-width="5"/></g>')
def reel(cx, cy, s):
    h = ''.join(f'<circle cx="{18*__import__("math").cos(a)}" cy="{18*__import__("math").sin(a)}" r="8" fill="{MID}"/>' for a in [i * 1.2566 + .3 for i in range(5)])
    return (f'<g transform="translate({cx},{cy}) scale({s/100})" stroke="{MID}" stroke-width="6"><circle r="42" fill="{GOLD}"/>{h}<circle r="5" fill="{MID}"/></g>')
def bolt(cx, cy, s):
    return (f'<g transform="translate({cx},{cy}) scale({s/100})" stroke="{MID}" stroke-width="6" stroke-linejoin="round">'
            f'<path d="M10 -50 L-26 6 L-4 6 L-14 50 L28 -8 L4 -8Z" fill="{YEL}"/></g>')
def tri(cx, cy, s, d, fill='#fff'):
    p = {'r': f'{cx-s/2},{cy-s/2} {cx+s/2},{cy} {cx-s/2},{cy+s/2}', 'l': f'{cx+s/2},{cy-s/2} {cx-s/2},{cy} {cx+s/2},{cy+s/2}',
         'd': f'{cx-s/2},{cy-s/2} {cx+s/2},{cy-s/2} {cx},{cy+s/2}'}[d]
    return f'<polygon points="{p}" fill="{fill}"/>'
def fist(cx, cy, s, col):
    return (f'<g transform="translate({cx},{cy}) scale({s/100})" fill="{col}" stroke="{MID}" stroke-width="6" stroke-linejoin="round">'
            f'<rect x="-30" y="-26" width="60" height="58" rx="14"/><path d="M-30 -8 H30 M-10 -26 V-8 M10 -26 V-8" fill="none"/><rect x="-22" y="30" width="44" height="18" rx="6"/></g>')
def shield(cx, cy, s, col):
    return (f'<g transform="translate({cx},{cy}) scale({s/100})" stroke="{MID}" stroke-width="6" stroke-linejoin="round">'
            f'<path d="M0 -46 L36 -32 L34 8 Q30 34 0 48 Q-30 34 -34 8 L-36 -32Z" fill="{col}"/>'
            f'<polygon points="0,-20 6,-6 21,-5 10,5 13,20 0,12 -13,20 -10,5 -21,-5 -6,-6" fill="{GOLD}" stroke-width="3"/></g>')
def mask(cx, cy, s, col):
    return (f'<g transform="translate({cx},{cy}) scale({s/100})" stroke="{MID}" stroke-width="6" stroke-linejoin="round" stroke-linecap="round">'
            f'<path d="M-36 -40 Q0 -30 36 -40 L34 8 Q28 42 0 50 Q-28 42 -34 8Z" fill="{col}"/>'
            f'<path d="M-22 -8 Q-14 -18 -6 -8 M6 -8 Q14 -18 22 -8" fill="none"/><path d="M-18 16 Q0 36 18 16" fill="none"/></g>')
ACT = {'COUP': fist, 'GARDE': shield, 'RUSE': mask}
ACC = {'COUP': RED, 'GARDE': GREEN, 'RUSE': BLUE}

# ---------- pastilles / badges ----------
def badge(spec):
    """retourne (svg local, largeur, hauteur) ; origine en haut à gauche"""
    h = 56
    m = re.fullmatch(r'(ALL)?([+−])(\d+)', spec)
    if m:
        allf, sg, n = m.groups(); col = GREEN if sg == '+' else RED
        ic = ''; x = 16
        if allf:
            ic = ''.join(pawn(x + 10 + i * 20, 34, 40, '#fff', 4) for i in range(3)); x += 66
        arr = tri(x + 10, h / 2, 20, 'r' if sg == '+' else 'l'); x += 28
        txt = T(x, 40, f'{sg}{n}', 36, '#fff', True)
        w = x + tw(f'{sg}{n}', 36, True) + 16
        return f'<rect width="{w}" height="{h}" rx="28" fill="{col}" stroke="{MID}" stroke-width="4"/>{ic}{arr}{txt}', w, h
    m = re.fullmatch(r'T(\d+)', spec)
    if m:
        s = f'{m.group(1)} s'; w = 62 + tw(s, 32, True) + 14
        return f'<rect width="{w}" height="{h}" rx="28" fill="{MID}" stroke="{GOLD}" stroke-width="4"/>{hourglass(32, 28, 40)}{T(58, 40, s, 32, CREAM, True)}', w, h
    m = re.fullmatch(r'M(\+\d+)?', spec)
    if m:
        s = m.group(1) or ''; w = 62 + (tw(s, 34, True) + 12 if s else 0)
        return f'<rect width="{w}" height="{h}" rx="28" fill="{MID}" stroke="{GOLD}" stroke-width="4"/>{mirror(32, 30, 44)}{T(58, 41, s, 34, GOLD, True) if s else ""}', w, h
    m = re.fullmatch(r'D(\d+)', spec)
    if m:
        fs = [int(c) for c in m.group(1)]; w = 18 + len(fs) * 46
        return f'<rect width="{w}" height="{h}" rx="14" fill="{MID}" stroke="{GOLD}" stroke-width="4"/>' + ''.join(die(32 + i * 46, 28, 36, f) for i, f in enumerate(fs)), w, h
    m = re.fullmatch(r'≤(\d+)', spec)
    if m:
        s = f'≤{m.group(1)}'; w = tw(s, 34, True) + 32
        return f'<rect width="{w}" height="{h}" rx="28" fill="{MID}" stroke="{GOLD}" stroke-width="4"/>{T(16, 41, s, 34, CREAM, True)}', w, h
    return '', 0, h

def place_badges(rect, specs):
    x, y, w, h = rect; o = ''; right = x + w - 10; row = 0
    for sp in specs:
        if sp in ('OK', 'KO'):
            o += (check if sp == 'OK' else cross)(x + 40, y + 40, 30); continue
        g, bw, bh = badge(sp)
        if not g: continue
        if sp.startswith('M'): o += f'<g transform="translate({x+w-10-bw},{y+h-10-bh})">{g}</g>'; continue
        if right - bw < x + 84 and right != x + w - 10:   # ne tient pas : nouvelle ligne
            row += 1; right = x + w - 10
        right -= bw; o += f'<g transform="translate({right},{y+10+row*64})">{g}</g>'; right -= 8
    return o

# ---------- découpage des cases ----------
def rects(mp, x, y, w):
    g = 8
    if mp in ('B', 'B+P'):
        h = w * 30 / 63; return [(x, y, w, h), (x, y + h + g, w, h)], 2 * h + g
    if mp == 'D':
        h = w * 30 / 63; hw = (w - g) / 2
        return [(x, y, w, h), (x, y + h + g, hw, h), (x + hw + g, y + h + g, hw, h)], 2 * h + g
    if mp == 'C':
        h = w * 20 / 63; return [(x, y + i * (h + g), w, h) for i in range(3)], 3 * h + 2 * g
    h = w * 60 / 63; return [(x, y, w, h)], h

OV = {  # surcouches par case (0 = haut / première ; D : 1 = gauche, 2 = droite)
 'EV01': {0: ['+2'], 1: ['M+1']}, 'EV02': {1: ['D246'], 2: ['D135', '−2']}, 'EV03': {0: ['+1'], 1: ['M+1', 'T10']},
 'EV04': {0: ['T3']}, 'EV05': {0: ['+2']}, 'EV06': {0: ['≤4']}, 'EV07': {0: ['+2'], 1: ['M']},
 'EV08': {1: ['OK'], 2: ['KO', '−3']}, 'EV09': {0: ['−3']}, 'EV10': {1: ['OK'], 2: ['KO', '−1']}, 'EV11': {1: ['+4']},
 'EV12': {0: ['+3', 'ALL+1']}, 'EV13': {0: ['+2'], 1: ['M+1']}, 'EV14': {0: ['ALL−1']}, 'EV15': {0: ['−2']},
 'EV16': {0: ['≤6']}, 'EV17': {0: ['−2']}, 'EV19': {1: ['−3']}, 'EV20': {1: ['+4']}, 'EV21': {1: ['OK', '+2'], 2: ['KO']},
 'EV22': {0: ['−3']}, 'EV23': {0: ['+2']}, 'EV24': {0: ['T5'], 1: ['OK', '+3'], 2: ['KO', '−2']},
 'EV25': {1: ['D246', '+3'], 2: ['D135', '−1']}, 'EV26': {1: ['+1']},
 'RB01': {0: ['−2'], 1: ['M', 'T10']}, 'RB02': {0: ['−3'], 1: ['M']}, 'RB03': {1: ['OK'], 2: ['KO', '−3']},
 'RB06': {1: ['OK'], 2: ['KO', '+2']}, 'RB09': {1: ['D12', '−4'], 2: ['D3456', '−1']}, 'RB10': {1: ['OK'], 2: ['KO', '−2']},
 'RB11': {0: ['−2'], 1: ['M', 'T3']}, 'RB12': {0: ['ALL+1']}, 'RB13': {0: ['T10'], 1: ['OK', '−1'], 2: ['KO', '−3']},
 'GN02': {0: ['+2']}, 'GN06': {0: ['−5']}, 'GN07': {0: ['−4']}, 'GN08': {0: ['T10']}, 'GN09': {0: ['−3', 'T5']},
 'HC4': {0: ['+6']},
}
HERO_X = {'HR2': ['−1'], 'HR3': ['−1'], 'HR4': ['≤3'], 'HR5': ['−2'], 'HR6': ['T10']}
LISERE = {'EV24': GREEN, 'EV25': BLUE, 'EV26': RED, 'EV27': '#6b7280', 'RB13': '#6b7280', 'GN05': '#6b7280'}
STAMP = {'PV2': (RED, 'REMPLACÉ', 'x'), 'PV3': (BLUE, 'EN ATTENTE DE RETRAIT', 'h'), 'PV4': (GREEN, 'EN PAUSE', 'p'), 'PV5': ('#6b7280', 'CORRIGÉ LUNDI', 'e')}

def case_block(code, mp, imgs, x, y, w):
    rs, bh = rects(mp, x, y, w); o = ''
    for i, r in enumerate(rs):
        if i < len(imgs):
            o += image(*r, imgs[i], rx=6)
        else:
            o += f'<rect x="{r[0]}" y="{r[1]}" width="{r[2]}" height="{r[3]}" rx="6" fill="#e5dcc0" stroke="{MID}" stroke-dasharray="10 8" stroke-width="3"/>'
        o += f'<rect x="{r[0]}" y="{r[1]}" width="{r[2]}" height="{r[3]}" rx="6" fill="none" stroke="{MID}" stroke-width="4"/>'
    pic = ''.join(place_badges(rs[i], sp) for i, sp in OV.get(code, {}).items() if i < len(rs))
    if mp == 'C':
        for i in range(2):
            ycn = rs[i][1] + rs[i][3] + 4; pic += tri(x + w / 2, ycn, 34, 'd', GOLD).replace('<polygon', f'<polygon stroke="{MID}" stroke-width="4"')
    return o, pic, bh

def wrap_fit(text, maxw, maxlines, size=29, mn=22, bold=False):
    while True:
        ls = wrap(text, size, maxw, bold)
        if len(ls) <= maxlines or size <= mn: return ls, size
        size -= 1

def svg_wrap(code, body, desc, w=W, h=H, mm=(63, 88), defs=''):
    return (f'<?xml version="1.0" encoding="UTF-8"?>\n<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
            f'width="{mm[0]}mm" height="{mm[1]}mm" viewBox="0 0 {w} {h}">\n<title>{esc(code)}</title><desc>{esc(desc)}</desc><defs>{defs}</defs>\n{body}\n</svg>\n')

# ---------- cadres ----------
def card_event(r, mp, imgs, dossier):
    code = r.code; lis = LISERE.get(code)
    body = ''
    if dossier:
        body += (f'<g id="cadre"><rect width="{W}" height="{H}" rx="26" fill="#e3cf94"/><path d="M0 40 Q0 14 26 14 L190 14 L214 36 L{W} 36 L{W} {H-26} Q{W} {H} {W-26} {H} L26 {H} Q0 {H} 0 {H-26}Z" fill="#ead9a4"/>'
                 f'<rect x="22" y="48" width="{W-44}" height="{H-70}" rx="12" fill="#fffdf4" stroke="{lis}" stroke-width="12"/>'
                 f'<circle cx="566" cy="846" r="52" fill="none" stroke="#8b5e3c" stroke-width="8" opacity=".25"/><path d="M522 818 A52 52 0 0 1 598 812" fill="none" stroke="#8b5e3c" stroke-width="4" opacity=".28"/></g>')
        px, pw, y0 = 48, 534, 120
    else:
        holes = ''.join(f'<rect x="{xx}" y="{yy}" width="20" height="30" rx="6" fill="{CREAM}" stroke="{MID}" stroke-width="2.5"/>' for xx in (18, 592) for yy in range(30, 850, 46))
        body += (f'<g id="cadre"><rect width="{W}" height="{H}" rx="26" fill="{GOLD}"/>{holes}'
                 f'<rect x="56" y="18" width="518" height="{H-36}" rx="14" fill="#fffaf0" stroke="{MID}" stroke-width="5"/></g>')
        px, pw, y0 = 70, 490, 104
    ig, pic, bh = case_block(code, mp, imgs, px, y0, pw)
    body += f'<g id="image">{ig}</g>'
    # en-tête
    tsz = fit_title(r.nom, pw - 110, 36)
    head = T(px, y0 - 24, r.nom, tsz, MID, True)
    m = re.match(r'Acte (I+)', str(r.groupe))
    if m:
        n = len(m.group(1)); head += ''.join(f'<circle cx="{px+pw-60+i*24}" cy="{y0-38}" r="9" fill="{GOLD if i < n else "none"}" stroke="{MID}" stroke-width="3"/>' for i in range(3))
    if dossier: head += f'<rect x="{px}" y="{y0-12}" width="{pw}" height="4" fill="{lis}"/>'
    ty = y0 + bh + 22
    ls, sz = wrap_fit(r.regle_fr, pw - 6, 5, 29, 22, True)
    txt = block(ls, px + pw / 2, ty + 34, sz, sz * 1.28, MID, True, 'middle')
    body += f'<g id="pictos">{pic}</g><g id="sous-titre">{head}{txt}</g>'
    return body

def card_rebond(r, mp, imgs):
    code = r.code; rnd = random.Random(code); pts = []
    step = 18
    for x in range(0, W, step): pts.append((x, rnd.uniform(0, 9)))
    for y in range(0, H, step): pts.append((W - rnd.uniform(0, 9), y))
    for x in range(W, 0, -step): pts.append((x, H - rnd.uniform(0, 9)))
    for y in range(H, 0, -step): pts.append((rnd.uniform(0, 9), y))
    poly = ' '.join(f'{a:.1f},{b:.1f}' for a, b in pts)
    cre = ''.join(f'<path d="M{rnd.randint(0,W)} 0 L{rnd.randint(0,W)} {rnd.randint(300,H)} L{rnd.randint(0,W)} {H}" fill="none" stroke="{"#fff" if i%2 else "#9a9276"}" stroke-width="2" opacity=".35"/>' for i in range(7))
    body = f'<g id="cadre"><rect width="{W}" height="{H}" fill="#d9d3c0"/><polygon points="{poly}" fill="#ece7d6" stroke="#8d866c" stroke-width="3"/>{cre}</g>'
    px, pw, y0 = 54, 522, 112
    ig, pic, bh = case_block(code, mp, imgs, px, y0, pw)
    body += f'<g id="image">{ig}</g>'
    lab = str(r.groupe)
    head = T(px, 66, lab, 26, '#6b665a', True) + f'<path d="M{px-6} 58 Q{px+60} 52 {px+tw(lab,26,True)+8} 60 M{px-4} 64 Q{px+80} 70 {px+tw(lab,26,True)+6} 54" stroke="{RED}" stroke-width="7" fill="none" stroke-linecap="round"/>'
    tsz = fit_title(r.nom, pw - 90, 38); head += T(px, y0 - 14, r.nom, tsz, MID, True)
    pic += bolt(px + pw - 28, 62, 64)
    ty = y0 + bh + 22; ls, sz = wrap_fit(r.regle_fr, pw - 6, 5, 29, 22, True)
    txt = block(ls, px + pw / 2, ty + 34, sz, sz * 1.28, MID, True, 'middle')
    return body + f'<g id="pictos">{pic}</g><g id="sous-titre">{head}{txt}</g>'

def card_hero(r, imgs):
    code = r.code; x, w = 20, 590
    body = f'<g id="cadre"><rect width="{W}" height="{H}" rx="26" fill="{MID}"/><rect x="6" y="6" width="{W-12}" height="{H-12}" rx="22" fill="none" stroke="{GOLD}" stroke-width="6"/></g>'
    three = len(imgs) >= 3
    hs = [(20, 250)] + ([(352, 190), (548, 190)] if three else [(352, 250)])
    ig = ''
    for i, (yy, hh) in enumerate(hs):
        if i < len(imgs): ig += image(x, yy, w, hh, imgs[i], rx=6)
        ig += f'<rect x="{x}" y="{yy}" width="{w}" height="{hh}" rx="6" fill="none" stroke="{GOLD}" stroke-width="3"/>'
    body += f'<g id="image">{ig}</g>'
    rib = f'<rect x="{x}" y="276" width="{w}" height="70" rx="6" fill="{CREAM}" stroke="{GOLD}" stroke-width="3"/>'
    tsz = fit_title(r.nom, w - 30, 30); rib += T(x + w / 2, 308, r.nom, tsz, MID, True, 'middle')
    if r.citation_fr: rib += T(x + w / 2, 334, '« ' + r.citation_fr.rstrip('.') + ' »', fit_title('« ' + r.citation_fr + ' »', w - 30, 22, 16, False), '#5b5646', False, 'middle', True)
    ty = 750 if three else 628
    ls, sz = wrap_fit(r.regle_fr, w - 20, 3 if three else 4, 28 if three else 31, 21, True)
    txt = block(ls, x + w / 2, ty + 26, sz, sz * 1.25, CREAM, True, 'middle')
    # pictos : fréquence + départ + extras
    py = 566 if three else 802
    pic = ''; cx = x + 8
    if code == 'HR2': pic += reel(cx + 28, py + 28, 56)
    else: pic += ticket(cx + 30, py + 28, 64) + T(cx + 76, py + 42, '×1', 32, GOLD, True)
    cx += 150
    for sp in HERO_X.get(code, []):
        g, bw, bh = badge(sp)
        if g: pic += f'<g transform="translate({cx},{py})">{g}</g>'; cx += bw + 10
    dep = (f'<rect x="{x+w-132}" y="{py}" width="132" height="56" rx="28" fill="{GOLD}" stroke="{CREAM}" stroke-width="4"/>'
           f'{pawn(x+w-100, py+30, 44, CREAM, 4)}{T(x+w-62, py+41, "2", 36, MID, True)}')
    body += f'<g id="pictos">{pic}{dep}</g><g id="sous-titre">{rib}{txt}</g>'
    return body

def cycle_cases(cur, x, y, w):
    order = ['COUP', 'RUSE', 'GARDE']; cw = 150; gap = (w - 3 * cw) / 2; o = ''
    for i, a in enumerate(order):
        cx = x + i * (cw + gap); on = a == cur
        o += f'<rect x="{cx}" y="{y}" width="{cw}" height="{cw}" rx="22" fill="{ACC[a] if on else "#fffdf4"}" stroke="{MID}" stroke-width="{7 if on else 4}"/>'
        o += ACT[a](cx + cw / 2, y + cw / 2 + 2, 96, CREAM if on else ACC[a])
        if i < 2:
            ax = cx + cw + gap / 2; o += f'<path d="M{ax-22} {y+cw/2} H{ax+14}" stroke="{MID}" stroke-width="8" stroke-linecap="round"/>' + tri(ax + 18, y + cw / 2, 22, 'r', MID)
    ax0, ax2 = x + 2 * (cw + gap) + cw / 2, x + cw / 2   # retour Garde -> Coup
    yb = y + cw + 34
    o += f'<path d="M{ax0} {y+cw+6} V{yb} H{ax2+0} V{y+cw+22}" fill="none" stroke="{MID}" stroke-width="8" stroke-linejoin="round"/><polygon points="{ax2-11},{y+cw+22} {ax2+11},{y+cw+22} {ax2},{y+cw+6}" fill="{MID}"/>'
    return o

def card_action(r, imgs):
    code = r.code; act = code.split('-')[2]; n = re.search(r'HR(\d)', code).group(1); acc = ACC[act]
    body = (f'<g id="cadre"><rect width="{W}" height="{H}" rx="26" fill="{CREAM}"/><rect x="8" y="8" width="{W-16}" height="{H-16}" rx="20" fill="none" stroke="{acc}" stroke-width="12"/></g>')
    body += f'<g id="image">{image(28, 28, 574, 546, imgs[0], rx=10)}<rect x="28" y="28" width="574" height="546" rx="10" fill="none" stroke="{MID}" stroke-width="5"/></g>'
    pic = f'<circle cx="82" cy="82" r="42" fill="{CREAM}" stroke="{MID}" stroke-width="6"/>' + T(82, 100, n, 54, MID, True, 'middle')
    pic += cycle_cases(act, 52, 598, 526)
    ls, sz = wrap_fit(r.regle_fr, 560, 2, 31, 24, True)
    txt = block(ls, 315, 838 - 36 * (len(ls) - 1), sz, 36, MID, True, 'middle')
    return body + f'<g id="pictos">{pic}</g><g id="sous-titre">{txt}</g>'

def card_genre(r, imgs):
    code = r.code
    dots = ''.join(f'<circle cx="{x}" cy="{y}" r="2.6" fill="#ffffff" opacity=".10"/>' for x in range(8, W, 14) for y in range(8, H, 14))
    stripes = ''.join(f'<polygon points="{36+i*60},72 {66+i*60},72 {96+i*60},22 {66+i*60},22" fill="{CREAM if i%2 else MID}"/>' for i in range(-1, 10))
    body = (f'<g id="cadre"><rect width="{W}" height="{H}" rx="26" fill="{MID}"/>{dots}<rect x="8" y="8" width="{W-16}" height="{H-16}" rx="20" fill="none" stroke="{GOLD}" stroke-width="6"/>'
            f'<clipPath id="stp"><rect x="20" y="22" width="590" height="50" rx="6"/></clipPath><g clip-path="url(#stp)"><rect x="20" y="22" width="590" height="50" fill="{CREAM}"/>{stripes}</g>'
            f'<rect x="20" y="22" width="590" height="50" rx="6" fill="none" stroke="{CREAM}" stroke-width="4"/></g>')
    rs, bh = rects('A', 20, 80, 590)
    body += f'<g id="image">{image(*rs[0], imgs[0], rx=6)}<rect x="{rs[0][0]}" y="{rs[0][1]}" width="{rs[0][2]}" height="{rs[0][3]}" rx="6" fill="none" stroke="{CREAM}" stroke-width="4"/></g>'
    pic = place_badges(rs[0], OV.get(code, {}).get(0, []))
    tag = str(r.groupe).replace('Tas ', '')
    pic += f'<circle cx="578" cy="47" r="20" fill="{GOLD}" stroke="{MID}" stroke-width="4"/>' + T(578, 58, tag, 28, MID, True, 'middle')
    y = 80 + bh + 44
    tsz = fit_title(r.nom, 540, 40)
    ls, sz = wrap_fit(r.regle_fr, 560, 4, 32)
    txt = T(315, y, r.nom, tsz, GOLD, True, 'middle') + block(ls, 315, y + 42, sz, sz * 1.28, CREAM, False, 'middle')
    return body + f'<g id="pictos">{pic}</g><g id="sous-titre">{txt}</g>'

def stamp(cx, cy, col, label, sym):
    ls = wrap(label, 24, 190, True)
    hh = 36 + 30 * len(ls); ww = 250
    ic = {'x': f'<path d="M-26 -14 L26 14 M26 -14 L-26 14" stroke="{col}" stroke-width="8"/>', 'h': hourglass(0, 0, 54, col).replace(MID, col), 'p': f'<rect x="-22" y="-24" width="14" height="48" fill="{col}"/><rect x="8" y="-24" width="14" height="48" fill="{col}"/>',
          'e': f'<path d="M-24 18 L16 -22 L26 -12 L-14 28Z" fill="none" stroke="{col}" stroke-width="6" stroke-linejoin="round"/>'}[sym]
    return (f'<g transform="translate({cx},{cy}) rotate(-9)" opacity=".92"><rect x="{-ww/2}" y="{-hh/2}" width="{ww}" height="{hh}" rx="10" fill="#ffffff" fill-opacity=".35" stroke="{col}" stroke-width="7"/>'
            f'<rect x="{-ww/2+8}" y="{-hh/2+8}" width="{ww-16}" height="{hh-16}" rx="6" fill="none" stroke="{col}" stroke-width="2.5"/>'
            f'<g transform="translate({-ww/2+46},0)">{ic}</g>' + block(ls, 22, -hh / 2 + 44, 24, 30, col, True, 'middle') + '</g>')

def card_pv(r, imgs):
    code = r.code
    body = (f'<g id="cadre"><rect width="{W}" height="{H}" rx="14" fill="#e9dcb8"/><rect x="14" y="14" width="{W-28}" height="{H-28}" fill="none" stroke="#6e5a34" stroke-width="5"/>'
            f'<rect x="24" y="24" width="{W-48}" height="{H-48}" fill="none" stroke="#6e5a34" stroke-width="1.8"/></g>')
    rs, bh = rects('A', 44, 98, 542)
    body += f'<g id="image">{image(*rs[0], imgs[0])}<rect x="{rs[0][0]}" y="{rs[0][1]}" width="{rs[0][2]}" height="{rs[0][3]}" fill="none" stroke="#2b2418" stroke-width="4"/></g>'
    head = T(44, 70, 'PROCÈS-VERBAL · 1872', 26, '#4a3c20', True) + T(586, 70, r.nom, 26, '#4a3c20', False, 'end')
    y = 98 + bh + 40
    lines = ''.join(f'<line x1="44" y1="{yy}" x2="586" y2="{yy}" stroke="#6e5a34" stroke-width="1" opacity=".45"/>' for yy in range(int(y) + 10, 850, 40))
    cap = wrap(r.regle_fr, 28, 530, True); q = wrap('« ' + r.citation_fr + ' »', 27, 530, False, True)
    txt = block(cap, 44, y, 28, 40, '#2b2418', True) + block(q, 44, y + 40 * len(cap), 27, 40, '#4a3c20', False, 'start', True)
    st = STAMP.get(code); pic = stamp(445, 760, *st) if st else ''
    return body + f'<g id="pictos">{pic}</g><g id="sous-titre">{head}{txt}{lines}</g>'

def card_abysses(r, imgs):
    defs = '<radialGradient id="lum" cx="50%" cy="48%" r="75%"><stop offset="0" stop-color="#2a8f9e"/><stop offset=".55" stop-color="#145561"/><stop offset="1" stop-color="#082a33"/></radialGradient>'
    body = (f'<g id="cadre"><rect width="{W}" height="{H}" rx="26" fill="url(#lum)"/><rect x="8" y="8" width="{W-16}" height="{H-16}" rx="20" fill="none" stroke="{GOLD}" stroke-width="8"/>'
            f'<rect x="22" y="22" width="{W-44}" height="{H-44}" rx="14" fill="none" stroke="{GOLD}" stroke-width="2" opacity=".7"/></g>')
    rs, bh = rects('A', 34, 40, 562)
    body += f'<g id="image">{image(*rs[0], imgs[0], rx=8)}<rect x="{rs[0][0]}" y="{rs[0][1]}" width="{rs[0][2]}" height="{rs[0][3]}" rx="8" fill="none" stroke="{GOLD}" stroke-width="6"/></g>'
    pic = place_badges(rs[0], OV.get(r.code, {}).get(0, []))
    y = 40 + bh + 52
    ls, sz = wrap_fit(r.regle_fr, 540, 4, 34)
    txt = T(315, y, r.nom, fit_title(r.nom, 540, 44), GOLD, True, 'middle') + block(ls, 315, y + 42, sz, sz * 1.28, CREAM, False, 'middle') + T(315, 852, 'HORS-CHAMP', 20, GOLD, True, 'middle', extra='letter-spacing="4"')
    return body + f'<g id="pictos">{pic}</g><g id="sous-titre">{txt}</g>', defs

def card_legend(r, imgs):
    body = f'<g id="cadre"><rect width="{W}" height="{H}" rx="26" fill="{CREAM}"/><rect x="8" y="8" width="{W-16}" height="{H-16}" rx="20" fill="none" stroke="{MID}" stroke-width="8"/></g>'
    body += f'<g id="image">{image(34, 96, 562, 640, imgs[0], rx=8, fit="meet")}</g>'
    ls = wrap(r.regle_fr, 28, 540, True)
    txt = T(315, 70, r.nom, 38, MID, True, 'middle') + block(ls, 315, 790, 28, 36, MID, True, 'middle')
    return body + f'<g id="sous-titre">{txt}</g>'

JZ = {'CL-ROUGE': 1.2, 'CL-BLEU': 1.2, 'CL-VERT': 1.2, 'GR-GRIS': 1.2, 'JT-PLUME': 1.2, 'JT-PROJ': 1.2, 'JT-PORTE': 1.55, 'JT-ARMURE': 1.0, 'JT-LEURRE': 1.0, 'JT-RELIQUE': 1.0}
def card_jeton(r, path, name):
    ring = {'rouge': RED, 'bleu': BLUE, 'vert': GREEN, 'gris': '#6b7280'}.get(str(r.couleur), GOLD)
    body = (f'<g id="cadre"><circle cx="300" cy="300" r="296" fill="{MID}"/><circle cx="300" cy="300" r="284" fill="{ring}"/><circle cx="300" cy="300" r="266" fill="{MID}"/></g>')
    cid = uid('cp'); z = JZ.get(r.code, 1.2); sz = 520 * z
    body += (f'<g id="image"><clipPath id="{cid}"><circle cx="300" cy="300" r="260"/></clipPath><image xlink:href="{data_uri(path)}" x="{300-sz/2}" y="{300-sz/2}" width="{sz}" height="{sz}" '
             f'preserveAspectRatio="xMidYMid slice" clip-path="url(#{cid})"/></g>')
    return body

# ---------- indexation des images ----------
def build_index():
    idx = {}
    for f in sorted(glob.glob(IMG_DIR + '/**/*', recursive=True)):
        if not os.path.isfile(f) or f.endswith('.pjeg') or '/fiche_personnage/' in f: continue
        d = os.path.basename(os.path.dirname(f)).split(' ')[0]; n = os.path.basename(f)
        code = n.split(' ')[0] if '/Actions/' in f else d
        idx.setdefault(code, []).append(f)
    def key(p):
        m = re.search(r'cas[e]?\s*(\d)', os.path.basename(p).lower()); return int(m.group(1)) if m else 0
    for c in idx: idx[c].sort(key=key)
    for f in glob.glob(FIX + '/*.png'): idx[os.path.basename(f)[:-4]] = [f]
    return idx

def slug(s): return re.sub(r'[^A-Za-z0-9]+', '-', unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode()).strip('-')

def main():
    df = pd.read_csv(CSV_C).fillna(''); mp = dict(pd.read_csv(CSV_P).fillna('')[['code', 'mise_en_page']].values)
    idx = build_index(); done = []; miss = []
    for r in df.itertuples():
        code = r.code; imgs = idx.get(code, []); m = mp.get(code, 'A'); defs = ''
        fam = {'Héros': '1_Heros', 'Action': '2_Actions', 'Événement': '3_Evenements', 'Rebondissement': '4_Rebondissements', 'Genre': '5_Genres',
               'Procès-verbal': '6_Proces-verbaux', 'Légende': '7_Legende', 'Abysses': '8_Abysses', 'Jeton': '9_Jetons'}[r.type]
        if not imgs: miss.append(code); continue
        desc = f'{r.nom} | {r.regle_fr} | {r.effet_chiffre}'
        outs = []
        if r.type == 'Héros': b = card_hero(r, imgs)
        elif r.type == 'Action': b = card_action(r, imgs)
        elif r.type == 'Événement': b = card_event(r, m, imgs, r.mode == 'dossier')
        elif r.type == 'Rebondissement':
            b = card_event(r, m, imgs, True) if r.mode == 'dossier' else card_rebond(r, m, imgs)
        elif r.type == 'Genre':
            b = card_genre(r, imgs) if r.mode != 'dossier' else card_event(r, 'A', imgs, True)
        elif r.type == 'Procès-verbal': b = card_pv(r, imgs)
        elif r.type == 'Abysses': b, defs = card_abysses(r, imgs)
        elif r.type == 'Légende': b = card_legend(r, imgs)
        if r.type == 'Jeton':
            for k, p in enumerate(imgs):
                suf = '' if len(imgs) == 1 else ['_recto-rouge', '_verso-bleu'][k]
                s = svg_wrap(code, card_jeton(r, p, r.nom), desc, 600, 600, (30, 30))
                outs.append((f'{code}_{slug(r.nom)}{suf}.svg', s))
        else:
            outs.append((f'{code}_{slug(r.nom)}.svg', svg_wrap(code, b, desc, defs=defs)))
        os.makedirs(f'{OUT}/{fam}', exist_ok=True)
        for fn, s in outs:
            open(f'{OUT}/{fam}/{fn}', 'w', encoding='utf-8').write(s); done.append(f'{fam}/{fn}')
    print(len(done), 'SVG écrits ; sans image :', miss)
main()
