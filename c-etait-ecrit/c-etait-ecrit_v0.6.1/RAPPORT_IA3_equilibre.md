# IA-3 Équilibre : rapport de validation (v0.6)

Simulateur : `sim.py` (25 Événements, 16 Rebondissements, 8 Genres, Mémoire, jetons, Vedette, Armures, 7 pouvoirs). Banc d'essai : `experiments.py`, `p07*.py`, `t4run.py`. Données brutes : `resultats/`.
Les joueurs sont simulés (débutant = carte favorite, hasard, expert = lit l'historique et la Mémoire). Ce sont des mesures de modèle, pas de tests humains.

## 0. Calibration (le simulateur reproduit T1)
| Mesure (5 joueurs, hasard) | Rapport | Simulateur |
|---|---|---|
| v0.5 telle qu'écrite, manches | 8,1 | 8,2 |
| Prophéties justes | 47 % | 48 % |
| Sans pouvoirs / sans portes | 7,9 / 8,6 | 7,9 / 8,75 |
| 1 expert vs 4 hasard / 4 débutants | x1,64 / x1,88 | x1,60 / x1,96 |
| 1 débutant vs 4 experts | x0,24 | x0,27 |
| Nuls entre experts | 60 % | 56 % |
Écart connu : 1,6 vol de Relique par partie (rapport : 1,9). Contrat v0.6 complet : 8,6 manches. L'écart vient de l'alternance des Genres (D9, +0,4 manche), pas de D12 ni des 12 étoiles.

## 1. T2 / P09 : équité des sièges (D12) → **NON validé en l'état**
Part de victoire par siège, 1,00 = équitable (joueurs au hasard, IC95 ≈ ±0,02).
| Joueurs | Ordre v0.5 (min–max) | D12 (min–max) |
|---|---|---|
| 4 | 0,91–1,08 | 0,89–1,06 |
| 5 | 0,96–1,08 | 0,94–1,10 |
| 6 | 0,92–1,13 | 0,94–1,13 |
| 7 | 0,90–1,13 | 0,93–1,08 |
D12 relève le dernier siège à 7 joueurs (0,90 → 0,93) mais ne ramène l'écart sous ±5 % nulle part. Cause identifiée : le détenteur de la Plume dans la manche gagnante gagne environ 1,5 fois sa part (+3 immédiat, tour de lecture), quel que soit l'ordre des dés. Le premier Scénariste (siège 0) est le plus pénalisé avec D12 (0,89 à 4 joueurs).
Correctif testé : le premier Scénariste démarre une case plus loin. Résultat : 4 j. 0,96–1,03 ; 5 j. 0,98–1,04 ; 7 j. 0,94–1,07. Mieux, mais à 7 joueurs il reste ±6 %. Le test à +2 cases n'a pas été terminé.

## 2. T4 / P07 : héros avec cartes cachées (D4) → **NON validé**
Écart de part de victoire par héros (5 joueurs, hasard, IC95 ±2,1 pts).
| Configuration | Hurleur | Rival | Maître | Artichaut | Traître | Comique | Stratège |
|---|---|---|---|---|---|---|---|
| Cartes visibles (v0.2), pouvoirs « malins » | −13 | −9 | **+39** | −14 | +7 | −5 | −5 |
| Cartes cachées (D4), « malins » | −9 | −7 | **+26** | −12 | +8 | −4 | −3 |
| Cartes cachées (D4), « naïfs » | −8 | −6 | +17 | +6 | −7 | −2 | −1 |
| D4, SANS pouvoirs | −13 | 0 | +7 | −10 | +7 | +11 | −3 |
Le rapport annonçait le Maître à +1 % sous D4 : le simulateur trouve +17 à +26 %. D4 ramène le Maître de +39 à +26, pas à zéro. Deux causes :
1. **La case de départ pèse environ 10 points par case**, plus que la plupart des pouvoirs (départ 1 : Hurleur et Artichaut ; départ 3 : Maître, Traître, Comique).
2. Le pouvoir du Maître est un « re-choix » : même sans voir de carte, il applique la lecture de la Mémoire (jouer la carte qui ne perd jamais face à deux cartes possibles) une fois, à coup sûr.
À 7 joueurs, le Traître domine (+19 à +25 %) quand il peut voler juste avant le lancer du porteur.
**Paquet de correctifs testé** (IC95 ±2 pts) :
| Joueurs | Hurleur | Rival | Maître | Artichaut | Traître | Comique | Stratège |
|---|---|---|---|---|---|---|---|
| 5 | +6 | −2 | +6 | −1 | −8 | −5 | +4 |
| 7 | +8 | −10 | +7 | −1 | +1 | −5 | 0 |
Paquet : tous les héros démarrent en case 2 ; Maître : « puis recule de 1 » ; Traître : usage au début de la Course seulement, puis recule de 2. Écart maximal ramené de ±25 % à ±10 %.
À surveiller : le Rival reste faible à 7 joueurs (−10 %), non corrigé. Le Comique et le Stratège dépendent de mes hypothèses (rire à 70 %, politique de décision simple).

## 3. T6 : 12 étoiles et Événements vus → **validé**
Événements tirés par partie (toute la table) : 8 étoiles / 12 étoiles.
| Joueurs | 8 étoiles (I / II / III) | 12 étoiles (I / II / III) |
|---|---|---|
| 4 | 8,3 (2,7 / 3,6 / 2,0) | 12,5 (4,0 / 5,0 / 3,5) |
| 5 | 10,4 (3,4 / 4,5 / 2,5) | 15,7 (5,0 / 6,4 / 4,3) |
| 6 | 12,5 | 18,9 |
| 7 | 14,8 | 22,2 |
À 5 joueurs, part des parties où une carte d'Acte III apparaît : 27 % (8 étoiles) → 45 % (12 étoiles). La durée ne change pas (8,6 manches). Les 25 cartes sont vues à fréquence uniforme dans leur Acte. 14 étoiles : 17,7 tirages, Acte III seulement 4,9 : peu de gain.
Cartes les plus fortes (5 j., cases nettes pour le tireur) : E09 Vent favorable (+3, les autres +1), E01 / E10 (+2,75), E17 (+2,7). Les plus faibles : E03 Embuscade (−2,3), E19 Poisse (−2,0), E11 Faille (−1,7 pour un joueur au hasard). Aucune ne justifie une correction avant test humain.

## 4. P10 : variantes de Mémoire / nuls entre experts → **aucune variante testée ne convient**
5 joueurs. 1E = 1 expert contre 4 hasard ; 1D = 1 débutant contre 4 experts.
| Variante | Nuls E-E | 1E vs 4 hasard | 1D vs 4E | Manches (5 experts) | Prophéties |
|---|---|---|---|---|---|
| V0 contrat | 56 % | x1,60 | x0,27 | 7,8 | 53 % |
| V1 égalité : les deux −1 | 59 % | x1,77 | x0,16 | 11,0 | 57 % |
| V2 égalité : le plus avancé −1 | 58 % | x1,81 | x0,18 | 9,7 | 56 % |
| V3 Mémoire sur 2 manches | 40 % | x0,96 | x1,03 | 8,2 | **85 %** |
| V4 (contrôle) égalité : les deux +1 | 55 % | x1,54 | x0,41 | 6,0 | 50 % |
| V6 égalité : le plus proche de la Plume gagne | n/a | x1,66 | x0,16 | 11,7 | 58 % |
| V7 égalités typées | 57 % | x1,58 | x0,26 | 7,9 | 53 % |
V1, V2, V6 allongent la partie de 25 à 50 % sans réduire les nuls. V3 baisse les nuls mais rend la carte jouée quasi forcée : l'expert ne gagne plus rien et le Scénariste prédit 85 % des cartes. V6 : le compteur de nuls n'est pas comparable (les égalités sont tranchées ensuite). Recommandation : garder la Mémoire à 1 manche, traiter ~56 % de nuls entre experts comme un équilibre de haut niveau, et ne pas modifier l'égalité.
Précision : environ 6 000 parties par cas (±3 % relatif sur les ratios).

## 5. Texte des cartes à modifier (à reporter sur les SVG, je n'ai pas relu les fichiers de carte ligne à ligne)
- **Fiches Héros** : « Départ : case 2 » pour les sept.
- **Maître** : « …remplace ta carte jouée par une autre de ta main (pas celle de la manche précédente), puis recule de 1. »
- **Traître** : « Une fois par partie, au début de la Course, prends la Relique d'un joueur (si tu n'en portes pas), puis recule de 2. »
- **Règle des sièges** : à décider après le test ci-dessous.

## 6. Limites et suite
- Les pouvoirs du Stratège, du Comique, de l'Artichaut et du Traître dépendent de règles de décision que j'ai choisies ; un test humain les contredira peut-être.
- Cartes des Rebondissements, jetons, Genres modélisés d'après mes lectures des fichiers de cartes ; le Dossier Gérard et le bénéfice de la question de l'Enquête ne sont pas modélisés.
- À refaire : T2 à 7 joueurs avec bonus de +2 cases, T4 à 7 joueurs en cartes visibles, Rival à 7 joueurs, et confirmation des ordres de grandeur avec des parties physiques.

## 7. Corrections appliquées (v0.6.1)
Paquet de la section 5 appliqué aux cartes, au plateau et aux règles (voir CORRECTIONS_v0.6.1.md). Simulation non relancée après application.
