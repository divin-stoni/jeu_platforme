#!/usr/bin/env python3
"""Contrôle de cohérence C'ÉTAIT ÉCRIT (v0.6).
Usage : python3 check_coherence.py DOSSIER
Lit le texte de tous les .svg, .pdf (nécessite pdftotext) et .docx du dossier
et signale (1) les valeurs périmées, (2) les faits de référence absents.
Code de sortie 0 = aucune alerte bloquante."""
import sys, os, re, zipfile, subprocess, xml.etree.ElementTree as ET
def svg_text(p):
    try: root=ET.parse(p).getroot()
    except Exception as e: return f"[SVG illisible: {e}]"
    out=[]
    for el in root.iter():
        if el.tag.split('}')[-1]=='text':
            t=re.sub(r'\s+',' ',''.join(el.itertext())).strip()
            if t: out.append(t)
    return '\n'.join(out)
def pdf_text(p):
    try: return subprocess.run(['pdftotext','-layout',p,'-'],capture_output=True,text=True).stdout
    except Exception: return '[pdftotext absent]'
def docx_text(p):
    try:
        x=zipfile.ZipFile(p).read('word/document.xml').decode('utf8')
        return re.sub(r'<[^>]+>',' ',x)
    except Exception as e: return f"[DOCX illisible: {e}]"
# (motif, explication, bloquant)
STALE=[
 (r'Rival part de la case 3|ou 3 à 7 joueurs|CASE 2 \(CASE 3|case 1, 2 ou 3','Départ du Rival à 3 (périmé). v0.6.1 : tous les héros en case 2.',True),
 (r'DÉPART : CASE [13]\b|départ [13]\)','Départ 1 ou 3 encore imprimé. v0.6.1 : case 2 pour tous.',True),
 (r'«[ ]*$','Guillemet ouvrant en fin de ligne (SVG) : à reflower.',False),
 (r'case 30\b','Arrivée à la case 30 (v0.1/v0.2). Référence v0.6 : case 33.',True),
 (r'8, 15 et 22','Reliques posées sur 8/15/22 (v0.2). v0.6 : jetons cachés sur 8, 11, 15, 19, 26, 30.',True),
 (r'dès 10 ans','Âge 10 ans. Référence : dès 12 ans.',True),
 (r'prototype v0\.[12]\b','Version de prototype v0.1 ou v0.2 encore imprimée.',True),
 (r'page 9 des cartes','Renvoi à la « page 9 des cartes » (le Dossier est en page 7 de 8).',True),
 (r'FLASH-BACK\s*:\s*interdit','Genre Flash-back (supprimé en v0.5, remplacé par Rediffusion).',True),
 (r'3 cases\s+d.avance','Vedette à 3 cases d’avance (v0.2). v0.6 : 2 cases.',True),
 (r'Après la 5e manche','Genre toutes les 5 manches (v0.1). v0.6 : toutes les 3 manches.',True),
 (r'20 Événements','Compte d’Événements périmé. v0.6 : 25 (29 avec le Dossier).',True),
 (r'mildness|babyoil|baby\s+oil|aceite para|20 FL OZ|locks in up to','Texte de flacon de commerce reconnaissable (risque marque / habillage commercial). À remplacer par un visuel original.',True),
 (r'Une seule Relique','Slogan « une seule Relique » alors qu’il y a 3 Reliques : à trancher (voir rapport, décision D13).',False),
 (r'à retourner après la 3e manche','Dos de Genre : vérifier la cohérence avec l’alternance A/B (règle D9).',False),
 (r'pose B sous A','Consigne « pose B sous A » : incompatible avec l’alternance A/B (règle D9).',True),
 (r'Dure jusqu.au prochain Genre','Vérifier la carte Rediffusion : elle doit durer 1 manche (décision D10).',False),
]
REQUIRED=[
 (r'case 33','La case 33 doit être citée (arrivée).'),
 (r'dès 12 ans','« dès 12 ans » doit apparaître (plateau ou règles).'),
 (r'jamais la même carte|Jamais la même carte','Règle de Mémoire à mentionner.'),
 (r'alternance','L’alternance des Genres A/B doit être écrite.'),
]
def main(d):
    texts={}
    for root,_,files in os.walk(d):
        for f in files:
            p=os.path.join(root,f); e=f.lower().rsplit('.',1)[-1]
            if e=='svg': texts[p]=svg_text(p)
            elif e=='pdf': texts[p]=pdf_text(p)
            elif e=='docx' and not f.startswith('DIGO') and not re.search(r'IA-\d|RAPPORT',f): texts[p]=docx_text(p)
    blocking=0; alerts=0
    print(f"{len(texts)} fichiers lus dans {d}\n")
    for pat,why,blk in STALE:
        hits=[os.path.relpath(p,d) for p,t in texts.items() if re.search(pat,t,re.I|re.M)]
        if hits:
            alerts+=1; blocking+=blk
            print(('BLOQUANT ' if blk else 'À VÉRIFIER ')+f"· {why}")
            for h in hits[:6]: print('    -',h)
            if len(hits)>6: print(f'    … et {len(hits)-6} autres')
    alltxt='\n'.join(texts.values())
    for pat,why in REQUIRED:
        if not re.search(pat,alltxt):
            alerts+=1; blocking+=1; print('MANQUANT · '+why)
    print(f"\n{alerts} alerte(s), dont {blocking} bloquante(s).")
    return 0 if blocking==0 else 1
if __name__=='__main__': sys.exit(main(sys.argv[1] if len(sys.argv)>1 else '.'))
