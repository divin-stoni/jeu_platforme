# Cartes C’ÉTAIT ÉCRIT — version vcodex

Cette version est une copie de `cartes_etait_ecrit_v3_svg`.

## Contrôles level design

- 102 entrées du CSV correspondent à 102 cartes logiques ; les 103 SVG incluent deux faces du jeton Porte (recto rouge et verso bleu).
- Aucun code, nom ou catégorie de carte ne manque.
- Répartition identique par cartes logiques : 7 Héros, 21 Actions, 27 Événements, 13 Rebondissements, 9 Genres, 6 Procès-verbaux, 8 Abysses, 10 Jetons et 1 Légende.
- Les descriptions SVG contiennent les noms et règles de la source CSV.

## Correction vcodex

Les 22 SVG concernés contenaient plusieurs fois le même identifiant XML pour
les logos `logo-coup`, `logo-garde` ou `logo-ruse`. Les identifiants répétés ont
été rendus uniques (`-2`, `-3`) sans modifier les textes, les images, les
couleurs, les dimensions ou les règles.

## Vérification graphique structurelle

- Cartes : 63 × 88 mm, viewBox 630 × 880.
- Jetons : 30 × 30 mm, viewBox 600 × 600.
- Tous les textes sont convertis en tracés comme dans la v3.
- Les références locales d’images restent valides.

La version v3 originale est conservée intacte.
