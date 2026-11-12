# Cartes SVG v0.7 : mode d'emploi

92 cartes (84 de base + Dossier Gérard + 8 Abysses), une par fichier, 179 x 249 pt (63 x 88 mm) avec 3 mm de fond perdu (viewBox -8.5 -8.5 196 266). Le rectangle `coupe` (masqué) marque la découpe.

## Les trois couches (contrat d'internationalisation)
Chaque SVG contient des groupes séparés :
- `fond` : bandeau d'acte ou de type, cadre, perforations.
- `scene` : les emplacements d'image (`slot-1`, `slot-2`, `slot-3`), numérotés, plus coche/croix, miroir, cadenas.
- `pictos` : pastilles chiffrées, sablier, dé, Armure, Relique, portée, cible. Seuls les chiffres sont en texte.
- `calque-texte` : nom, règle, citation. **Absent dans `monde/`**, présent dans `fr/`. Zone fixe de 15 % de hauteur (`zone-sous-titre`), taille de police réduite automatiquement.

`monde/` = Édition Monde (aucun mot). `fr/` = même carte avec le sous-titre français. `textes/fr.json` = code, nom, règle, citation de chaque carte : ajouter une langue = ajouter un fichier `textes/xx.json`.
Langues de droite à gauche : le calque texte porte `data-dir`; l'image ne se met jamais en miroir. Le champ `data-marge` de la racine donne la couleur de marge pour l'impression (plus besoin de lire les pixels).

## Mettre les images
1. Génère l'image de chaque emplacement avec `prompts_images_v0_7.csv` (un emplacement par case).
2. Nomme-la `CODE_N.png` dans `images/` : EV01_1.png (case 1), EV01_2.png (case 2)... N est le petit chiffre dans l'emplacement. Cartes à 3 emplacements : types B+P, B, C, D, H.
3. Lance `python3 inserer_images.py` : les cartes remplies sortent dans `sortie/`.

Quand tu auras vectorisé tes images, remplace le contenu de l'emplacement dans l'éditeur SVG par ton dessin (groupe `slot-N`).

## À savoir
- Les pictogrammes sont des gabarits simples, à redessiner dans ton style (poing, masque, sablier, etc.).
- Police : `Helvetica, Arial`. Avant impression, vectorise les textes (Inkscape : Objet > Convertir en chemin).
- Les dos de cartes et les jetons ne sont pas inclus.
- Planche de légende LG1 : grille vide de 15 cases à dessiner en vectoriel.
