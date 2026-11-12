# Classement vérifié du dossier

Ce classement a été établi par lecture et contrôle du contenu des fichiers. Le rapport d’équilibre indiqué dans la conversation et le README n’ont pas servi de source.

## 1. Noyau de travail du jeu

À conserver ensemble comme base opérationnelle :

- `c-etait-ecrit/jeu-actuel/sim.py` : simulateur du jeu ; il s’importe et termine des parties de 4 à 7 joueurs.
- `c-etait-ecrit/jeu-actuel/experiments.py` : campagnes de simulation qui importent le simulateur.
- `c-etait-ecrit/jeu-actuel/regle/check_coherence.py` : contrôle automatique du texte des SVG, PDF et DOCX.
- `c-etait-ecrit/jeu-actuel/regle/regles_et_fiche_test_A4_v0.6.pdf` : règles imprimables v0.6, avec arrivée à la case 33 et 4 à 7 joueurs.
- `c-etait-ecrit/jeu-actuel/regle/regles_et_fiche_test_A4_vcodex.md` et `.docx` : nouvelle règle de test alignée sur les 27 Événements et 13 Rebondissements du paquet vcodex.
- `c-etait-ecrit/jeu-actuel/CORRECTIONS_v0.6.1.md` : corrections appliquées à la base v0.6.1.
- `c-etait-ecrit/jeu-actuel/carte-jetons/CARTES_v0_6_impression.pdf` : planche imprimable des cartes et jetons v0.6.

## 2. Chaîne de production des cartes

Ces fichiers forment une chaîne de travail graphique et éditorial distincte :

- `c-etait-ecrit/production-cartes/cartes_v0_7.csv` : source structurée des cartes, avec codes, règles, citations, effets et pictogrammes.
- `c-etait-ecrit/production-cartes/prompts/` et `c-etait-ecrit/production-cartes/prompts_images_v0_7.csv` : prompts de production d’images.
- `c-etait-ecrit/production-cartes/cartes_etait_ecrit_svg/generateur/build_cards.py` : générateur SVG utilisant le CSV et les images.
- `c-etait-ecrit/production-cartes/cartes_etait_ecrit_svg/` : premier export SVG.
- `c-etait-ecrit/production-cartes/cartes_etait_ecrit_v2_svg/` : export SVG v2.
- `c-etait-ecrit/production-cartes/cartes_etait_ecrit_v3_svg/` : export SVG v3 perfectionné ; son document de changements indique 103 cartes et la conversion des textes en contours.
- `c-etait-ecrit/production-cartes/cartes_svg_v0_7/` : autre arborescence d’export, avec textes, images et mode d’emploi ; à traiter comme une variante de production, pas comme une archive sans examen visuel.
- Les ZIP correspondants sont rangés dans `c-etait-ecrit/production-cartes/` comme livrables compressés des mêmes exports.

## 3. Plateaux et maquettes en concurrence

À garder dans un dossier de variantes tant qu’un plateau final n’est pas explicitement choisi :

- `c-etait-ecrit/variantes-plateau/plateau/plateau_A3_v0_14_quatre_actes.svg`
- `c-etait-ecrit/variantes-plateau/plateau/plateau_A3_v0_15_route_des_quatre_actes.svg`
- `c-etait-ecrit/variantes-plateau/plateau/plateau_option_b_reclasse.svg`
- `c-etait-ecrit/variantes-plateau/Maquette alleger pour simple illustration plateau La Bobine.html`
- `c-etait-ecrit/variantes-plateau/plateau/plateau_A3_v0_11.svg` et son PDF d’impression.
- `c-etait-ecrit/variantes-plateau/apercus_orlando.svg` : aperçu graphique associé au plateau.

Le PDF de règles v0.6 et le texte du plateau v0.11 confirment le même socle de jeu : 4 à 7 joueurs, case 33, actes et genres. Les trois SVG v0.14/v0.15/option B doivent donc rester séparés : leur contenu justifie des variantes, pas une fusion automatique.

## 4. Documents de conception et de décision

À séparer des fichiers directement imprimables :

- `c-etait-ecrit/documentation-conception/C’ÉTAIT ÉCRIT la Bible de cohérence v1.pdf` : document de cohérence fondé sur le jeu v0.6.1 et les supports graphiques.
- `c-etait-ecrit/documentation-conception/C’ÉTAIT ÉCRIT dossier d’internationalisation v2.pdf` et v3 : adaptation éditoriale en planches de manga ; la v3 se présente comme le remplacement de la v2.
- `c-etait-ecrit/documentation-conception/C’ÉTAIT ÉCRIT journal des idées du 9 novembre 2026.pdf` : journal de conception du plateau.
- `c-etait-ecrit/documentation-conception/C’ÉTAIT ÉCRIT · IA-5 Univers et Codex.docx` : audit de cohérence de l’univers, pas une règle imprimable.
- `c-etait-ecrit/documentation-conception/RAPPORT_diagnostic_gameplay_v0.5_vers_v0.6.md` : diagnostic et plan de correction historique.

## 5. Snapshot complet v0.6.1

`c-etait-ecrit/c-etait-ecrit_v0.6.1/` est un paquet complet figé : règles, cartes, plateau, images, simulateur et corrections. Il doit être conservé comme snapshot reproductible, mais ne doit pas être confondu avec le dossier de travail principal.

Les fichiers `sim.py`, `experiments.py` et `CORRECTIONS_v0.6.1.md` du snapshot sont identiques à ceux du dossier principal. `check_coherence.py` est proche, mais pas identique.

Les tilemaps et leur archive sont rangés avec le jeu actuel dans `c-etait-ecrit/jeu-actuel/tilemaps_svg/`.

## 6. Archives historiques

À déplacer éventuellement sous une archive clairement datée, après validation :

- `archives/ancien-prototype/` : prototypes v0.1 à v0.3, règles, plateaux, cartes et diagnostics.
- `archives/versions-anciennes/NEWS/` : doublons et versions v0.1 à v0.6, revues de plateau et documents de rédaction.
- `archives/versions-anciennes/tilemaps_svg_doublon/` : copie ancienne des tilemaps.

Le contenu des PDF confirme leur statut historique : les anciennes règles parlent de la case 30 et des prototypes v0.1/v0.2, alors que les règles v0.6 utilisent la case 33.

## 7. Projet séparé : DIGO

Les DOCX `DIGO_Manga_Script_Tome1_v5.docx` à `Tome5_v5.docx` concernent le manga « Je reviens lundi » et non le matériel directement nécessaire à C’ÉTAIT ÉCRIT. Ils devraient avoir leur propre dossier de projet, même s’ils partagent des personnages ou un univers.

## Contrôles effectués

- 597 SVG parsés sans erreur XML.
- 3 JSON parsés sans erreur.
- 17 ZIP testés sans membre corrompu.
- 38 PDF reconnus par `pdfinfo`.
- 134 références locales dans les SVG vérifiées ; aucune référence manquante.
- 16 scripts Python parsés avec Python 3.14 ; aucune erreur de syntaxe.
- 80 parties simulées sur 4, 5, 6 et 7 joueurs ; aucune partie bloquée.

## Décision de rangement recommandée

Ne pas mélanger les fichiers immédiatement. La structure cible devrait comporter cinq zones : `jeu-actuel/`, `production-cartes/`, `variantes-plateau/`, `documentation-conception/` et `archives/`, avec `DIGO/` séparé. Le déplacement physique doit venir après validation du plateau retenu et des exports de cartes, car plusieurs SVG ont des références relatives aux images.
