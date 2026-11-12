# Formes à contour irrégulier (SVG) — C'ÉTAIT ÉCRIT

Au lieu de tuiles carrées, chaque pièce est UN SEUL tracé organique (bande, bloc, masse, L, T, courbe) avec une texture dedans.
Les pièces se superposent librement ; chaque contour a son ombre portée, son ombre intérieure et son trait de bord.

- formes/ : une feuille par style (11 formes chacune), textures liées par chemin relatif (../textures/). Garde les dossiers ensemble.
- autonomes/ : mêmes fichiers avec textures intégrées (un seul fichier, à partager ou ouvrir n'importe où).
- exemple_assemblage.svg : reprend ton croquis (masse centrale, bandes, blocs, abysses en bas).
- formes_contours.json : tracés et dimensions de chaque forme, pour l'IA qui construira le parcours.
- textures/ : les JPG 512 px utilisés.

Styles : herbe tempérée, litière de forêt, humus de jungle, herbe de savane, terre rouge, terre brune, pavé gris / savane / moussu, dalle d'ardoise, abysse clair / moyen / profond (contour de falaise rocheuse plus épais).

## Modifier (Inkscape, Affinity, Figma, navigateur)
- Forme : sélectionne le tracé (`path`) et déplace ses nœuds (environ 40 à 70 nœuds par forme). Tout le reste suit.
- Texture : change le remplissage `url(#t_...)` ou remplace le JPG dans textures/.
- Irrégularité fine : dans `<filter>`, l'attribut `scale` de `feDisplacementMap` (0 = contour lisse, plus grand = plus rugueux).
- Épaisseur et couleur du bord : `stroke` et `stroke-width` du tracé.
- Les ombres sont des filtres SVG : à l'export PNG, utilise Inkscape ou un navigateur, pas un convertisseur basique.

## Arbres et formes d'abysse
- sprites/ : les 11 arbres/buissons et les 7 formes d'abysse (PNG transparents, ombre incluse).
- arbres_et_formes_abysse.svg (dans formes/ et autonomes/) : tous les sprites rangés par biome, chacun est une image déplaçable et redimensionnable.
- exemple_assemblage_complet.svg : l'exemple avec arbres posés sur chaque biome et créatures dans les abysses.
Les arbres restent des images (PNG) dans le SVG, pas des tracés vectoriels : on peut les déplacer, tourner, agrandir, mais pas modifier leurs feuilles.
