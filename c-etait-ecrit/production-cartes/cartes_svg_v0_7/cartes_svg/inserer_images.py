#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Remplit les emplacements d'image des cartes SVG.
Usage : python3 inserer_images.py [dossier_sortie]   (défaut : sortie/)
Place tes images dans images/ sous la forme CODE_N.png (ou .jpg, .webp), ex. EV01_1.png, EV01_2.png.
N est le numéro de l'emplacement (le petit chiffre en haut à gauche de chaque emplacement).
Les SVG d'origine ne sont jamais modifiés. Une image absente laisse l'emplacement vide."""
import os, re, sys, base64
ici = os.path.dirname(os.path.abspath(__file__))
sortie = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ici, 'sortie')
MIME = {'.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.webp': 'image/webp'}
SLOT = re.compile(r'<g class="slot" id="slot-(\d+)" data-image="([^"]+)" data-x="([\d.]+)" data-y="([\d.]+)" data-w="([\d.]+)" data-h="([\d.]+)" data-shape="(\w+)">(<g class="ph">.*?</g>)', re.S)
def trouve(chemin):
    base = os.path.splitext(os.path.join(ici, chemin))[0]
    for ext in MIME:
        if os.path.exists(base + ext): return base + ext
total = 0
for sub in ('monde', 'fr'):
    os.makedirs(os.path.join(sortie, sub), exist_ok=True)
    for nom in sorted(os.listdir(os.path.join(ici, sub))):
        if not nom.endswith('.svg'): continue
        s = open(os.path.join(ici, sub, nom), encoding='utf-8').read()
        def rep(m):
            global total
            f = trouve(m.group(2))
            if not f: return m.group(0)
            i, x, y, w, h, shape, ph = m.group(1), *map(float, m.groups()[2:6]), m.group(7), m.group(8)
            b64 = base64.b64encode(open(f, 'rb').read()).decode()
            cid = 'clip-%s-%s' % (nom[:-4], i)
            clip = ('<clipPath id="%s"><circle cx="%.1f" cy="%.1f" r="%.1f"/></clipPath>' % (cid, x + w / 2, y + h / 2, min(w, h) / 2)) if shape == 'circle' else ('<clipPath id="%s"><rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="5"/></clipPath>' % (cid, x, y, w, h))
            img = '%s<image href="data:%s;base64,%s" x="%.1f" y="%.1f" width="%.1f" height="%.1f" preserveAspectRatio="xMidYMid slice" clip-path="url(#%s)"/>' % (clip, MIME[os.path.splitext(f)[1]], b64, x, y, w, h, cid)
            total += 1
            return m.group(0).replace(ph, img)
        s2 = SLOT.sub(rep, s)
        open(os.path.join(sortie, sub, nom), 'w', encoding='utf-8').write(s2)
print('images insérées :', total, '| sortie :', sortie)
