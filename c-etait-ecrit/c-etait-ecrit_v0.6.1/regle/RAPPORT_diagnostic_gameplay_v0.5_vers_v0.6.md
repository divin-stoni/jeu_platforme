# C’ÉTAIT ÉCRIT : rapport de diagnostic gameplay et plan de correction (v0.5 vers v0.6)

Date : 7 novembre 2026 · Coordinateur : Claude · Matière examinée : `claude.zip` (42 entrées : règles v0.1 et v0.2, bible v1, règles par couches v0.5, plateau A3 v0_10, 3 jeux de cartes SVG, jetons, 5 tomes du manga).

## 0. Verdict en 30 secondes

**Le cœur du jeu fonctionne. Le dossier d’impression, lui, n’est pas cohérent.**

- **Imprimable aujourd’hui pour un test privé à table (seuil A du 16 nov.)** : oui, avec les règles v0.6 livrées avec ce rapport.
- **Imprimable pour vendre ou photographier pour les précommandes (seuil B du 23 nov.)** : non, tant que le flacon de type « huile pour bébé » n’est pas remplacé et que les points P03 à P05 ne sont pas réglés.

| Axe | Note /10 | En une phrase |
| --- | --- | --- |
| Noyau (Coup/Garde/Ruse + Prophétie + Mémoire) | 8 | Simple, lisible, avec une vraie tension. Durée mesurée : environ 8 manches. |
| Profondeur et maîtrise | 6 | L’écart débutant/expert existe, mais il repose sur une seule règle (la Mémoire). Voir T3. |
| Rythme | 8 | Parties courtes, peu de blocages, aucune partie infinie sur 100 000 simulées. |
| Variété réellement vue en partie | 4 | Les 4 Genres « climax » (dont Shonen) n’apparaissent presque jamais. 30 à 60 % des Événements non plus. Voir T5 et T6. |
| Cohérence documentaire | 3 | 3 versions des règles qui se contredisent. Aucune règle complète v0.5 n’existait. Voir section 4. |
| Prêt à imprimer | 4 | Polices non incorporées, pas de fond perdu, cartes sans gouttière, recto-verso incomplet. |
| Risque juridique | 3 (élevé) | Flacon calqué sur un emballage commercial, sur le plateau et sur 3 jetons. |

Ces notes sont des jugements de lecture appuyés sur des mesures simulées. Aucune n’a été validée par une vraie table (voir section 2).

## 1. Ce que j’ai examiné

- `REDACTION/` : règles v0.1 et v0.2 (PDF A4), bible du monde v1, règles par couches v0.5 (docx), 5 tomes du manga (non audités ici, hors gameplay).
- `platforme-final/` : plateau A3 `v0_10` (SVG, 6 Mo, 34 images PNG intégrées).
- `CARTE/carte-page-1/` : cartes v0.5 pages 1 à 5 (héros, cartes action, parchemins, carte du tronc).
- `CARTE/cartes_v0_5_pages-2/` : cartes v0.5 pages 1 à 8 (Événements, Rebondissements, Genres, Dossier, Procès-verbal), recto seul.
- `CARTE/carte-recto-verso/` : dos pour impression recto-verso, jetons, un seul recto.

J’ai rendu le plateau et plusieurs pages en image pour les contrôler à l’œil, extrait tout le texte des SVG et PDF, et reconstitué la carte du plateau (cases, étoiles, jetons).

**Plateau réel (relevé)** : cases 0 à 33 en boucle (la 33 touche la 0). Étoiles d’Événement : 4 et 9 (acte I), 13, 17 et 21 (acte II), 24, 28 et 32 (acte III), soit 8. Jetons cachés « ? » : 8, 11, 15, 19, 26, 30. Café en 23. Flacon en 33.

## 2. Méthode et limites (à lire avant de croire un chiffre)

J’ai écrit un simulateur fidèle au plateau réel et aux cartes v0.5 (`simulateur/sim.py`), et joué environ 100 000 parties virtuelles par variante de règle.

**Ce que le simulateur ne sait pas faire** : mesurer le rire, la clarté, le temps d’explication, le bluff humain. Les rires et cris sont supposés réussis à 70 à 80 %. Les Événements et Rebondissements sont modélisés par leurs effets chiffrés. Les pouvoirs Hurleur, Rival, Maître, Traître, Artichaut sont modélisés ; **Stratège et Comique sont approchés grossièrement, leurs chiffres ne sont pas fiables**. Trois profils de joueurs : *débutant* (carte favorite), *hasard*, *expert* (choisit la carte qui perd le moins contre ses deux voisins, devine selon l’historique, garde ses Armures).

**Aucune partie humaine n’a été jouée.** Ce rapport est un audit plus des tests simulés, pas un test de table. La fiche de test v0.6 sert à combler ce manque.

## 3. Résultats des tests de gameplay

### T1. Durée et rythme (5 joueurs, joueurs au hasard)

| Variante | Manches moy. | p10 / p90 | Victoires avec Relique | Prophéties justes |
| --- | --- | --- | --- | --- |
| **v0.5 telle qu’écrite** | **8,1** | 6 / 10 | 94 % | 47 % |
| 4 / 6 / 7 joueurs | 8,1 / 8,0 / 7,9 | | | |
| Première partie, aucun Genre | 9,2 | 7 / 12 | 96 % | 48 % |
| Sans Mémoire (v0.3) | 8,3 | 6 / 11 | 92 % | 33 % |
| v0.3 complet (recul 2, +2/−1) | 8,7 | 7 / 11 | 83 % | 33 % |
| Sans pouvoirs de héros | 7,9 | | | |
| Sans portes de départ | 8,6 | | | |
| Arrivée « atteindre la 33 » au lieu de « dépasser » | 7,7 | | | |

Lecture : parties courtes, 64 % finies en 8 manches ou moins. Avec 3 à 4 minutes par manche (**estimation, à chronométrer**), on tient les 30 à 40 minutes annoncées. 94 % des victoires passent par une Relique : la voie « 2 Armures » est quasi morte pour un joueur moyen.

### T2. Équité des sièges (8 000 parties)

| Joueurs | Règle actuelle (course par le Scénariste) | Course par le dernier du parcours |
| --- | --- | --- |
| 5 | 0,94 à 1,07 de la part équitable | 0,94 à 1,03 |
| 7 | **0,88 à 1,14** (les derniers sièges perdent 12 %) | 0,95 à 1,04 |

Cause : dans la manche finale, l’ordre des dés avantage ceux qui jouent juste après la Plume. Correctif retenu : décision D12.

### T3. Maîtrise (1 expert, siège 0, contre 4 autres)

| Match | Victoires expert | Rapport à la part équitable (20 %) |
| --- | --- | --- |
| vs 4 débutants prévisibles | 37,6 % | x1,88 |
| vs 4 joueurs au hasard | 32,8 % | x1,64 |
| vs 4 experts | 22,0 % | x1,10 |
| 1 débutant vs 4 experts | 4,8 % | x0,24 |
| 1 hasard vs 4 experts | 8,3 % | x0,41 |
| **Sans la Mémoire**, 1 expert vs 4 hasard | 20,7 % | **x1,03** |

Lecture : la direction confirme vos chiffres de la v0.5 (écart net, débutant seul écrasé) mais l’ampleur est plus faible chez moi (x1,64 contre x2,3 chez vous). **Toute la maîtrise vient de la Mémoire** : sans elle, l’expert ne gagne rien. Mécanisme : si ton voisin de gauche a joué X, il ne peut pas rejouer X. La carte que X bat ne perd donc jamais contre lui. C’est enseignable en une phrase, ce qui est bien pour la couche 3. Mais entre experts, **60 % des duels sont nuls** (33 % entre débutants) : à haut niveau, les duels s’éteignent et le dé et les Événements décident. À surveiller (P10).

### T4. Équilibre des héros (6 000 parties, 5 joueurs, hasard)

| Hypothèse | Maître | Traître | Comique | Hurleur | Artichaut | Rival | Stratège |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Cartes visibles à l’étape Actions (v0.2) | **+24 %** | +5 % | +4 % | −3 % | −4 % | −9 % | −17 % * |
| Cartes cachées jusqu’aux Duels (décision D4) | **+1 %** | +5 % | +10 % * | +1 % | −7 % | +1 % | −11 % * |

\* modèle non fiable. Seul résultat robuste : **le Maître est cassé si les cartes sont retournées avant la Lecture**, car il change sa carte en connaissant tout. Ambiguïté entre la v0.2 (cartes retournées à l’étape 2) et la v0.5 (non dit). Corrigée par D4. Les autres héros se mesureront à table.

### T5. Genres réellement vus

Règle actuelle : « pose B sous A », un Genre retourné toutes les 3 manches. Les tas A (Romance, Enquête, Plage, Rediffusion) sortent d’abord.

| Résultat (3 000 parties, 5 joueurs) | Règle actuelle | Alternance A, B, A, B |
| --- | --- | --- |
| Parties où Shonen, Tournoi, Fausse mort, Trahison apparaissent | **0 %** | 21 à 22 % chacun |
| Parties où Romance, Enquête, Plage, Rediffusion apparaissent | 47 à 54 % | 30 à 35 % |
| Parties atteignant le 1er Genre B (15 manches) | 0,2 % | n/a |

Les 4 Genres « climax », y compris le Shonen qui est la promesse parodique du jeu, **ne se jouent pas** en pratique. Correctif : D9.

### T6. Cartes Événement vues

Avec 8 étoiles : 9,2 Événements par partie (acte I : 3,0 sur 8 cartes ; acte II : 4,0 sur 8 ; acte III : 2,1 sur 9). Les « coups de théâtre » de l’acte III sont presque invisibles.

| Plateau | Événements/partie | Par acte (I / II / III) | Manches |
| --- | --- | --- | --- |
| 8 étoiles (actuel) | 9,2 | 3,0 / 4,0 / 2,1 | 8,1 |
| **12 étoiles (+6, 12, 25, 29)** | **14,0** | 4,5 / 5,7 / 3,8 | 8,0 |
| 14 étoiles (+6, 12, 16, 25, 29, 31) | 15,8 | 4,5 / 7,1 / 4,2 | 7,9 |

Correctif retenu : 12 étoiles (D2). Durée inchangée.

### T7. Rediffusion

Pendant 3 manches, chacun rejoue sa carte : le Scénariste a **100 % de réussite** (+3 trois fois de suite, trois Rebondissements pour les cibles) et tous les duels sont connus d’avance. Mesuré : précision globale des prophéties 56 % avec Rediffusion contre 47 % sans. Correctif : la limiter à une manche (D10).

### T8. Autres mesures

- Le leader après la manche 4 gagne 53 % du temps (4 joueurs : 57 % ; 6 : 49 % ; 7 : 51 %). Poursuite correcte, pas de snowball excessif.
- Le vol de Relique par un Coup gagnant se produit 1,9 fois par partie. Sans vol : 7,9 manches. **On le garde** (le pouvoir du Hurleur et le Rebondissement R04 le supposent).
- Aucune partie bloquée sur 100 000 simulées (le plafond d’arrêt était de 80 manches).

## 4. Registre des problèmes

Gravité : **P0** bloque l’impression ou la vente ; **P1** à corriger avant le test à table ; **P2** à améliorer.

| ID | Gr. | Constat (preuve) | Correction | Propriétaire |
| --- | --- | --- | --- | --- |
| P01 | P0 | Les règles imprimables sont périmées : case 30 (v0.5 : 33), Reliques sur 8/15/22 (jetons « ? »), recul de duel 2 (3), prophétie +2/−1 (+3/−2), Vedette 3 cases (2), 20 Événements (25), Flash-back (Rediffusion), dès 10 ans (12), « page 9 des cartes » (page 7). Aucune règle complète v0.5 n’existe, seulement la carte du tronc. | Nouvelle règle A4 v0.6 | **Claude : fait** |
| P02 | P0 | La fiche de test v0.2 ignore la Mémoire, le mode Aventure seule, et la question « le perdant sait-il dire pourquoi ». | Fiche v0.6 | **Claude : fait** |
| P03 | P0 | Flacon calqué sur un emballage commercial (textes « babyoil », « locks in up to 10X more moisture », « no parabens, phthalates or dyes », « aceite para bebés », « 20 FL OZ ») sur la case 33 du plateau et sur les 3 Reliques-Bouteilles. Contraire à votre règle « éléments libres de droits uniquement ». | Redessiner un flacon original, sans aucun texte réel | IA-1 (plateau), IA-2 (jetons), IA-4 (audit) |
| P04 | P0 | Genres B jamais vus (T5). Le plateau dit « pose B sous A ». | D9 : alternance A/B | IA-1, IA-2 |
| P05 | P1 | Rediffusion : prophéties à 100 % pendant 3 manches (T7). | D10 : une manche | IA-2 |
| P06 | P1 | Ambiguïtés de règle (section 6, A1 à A11) : duels une ou deux fois, moment où les cartes se retournent, portes de départ, jeton Relique déjà pris, victoire « franchir » ou « atteindre ». | Contrat v0.6 (section 5), règle v0.6, carte du tronc | Claude (règle), IA-2 (cartes) |
| P07 | P1 | Maître cassé si les cartes sont visibles tôt (T4). | D4 | IA-3 vérifie |
| P08 | P1 | Contenu Événement peu vu (T6). | D2 : 4 étoiles de plus | IA-1 dessine, IA-3 valide |
| P09 | P1 | Siège désavantagé à 7 joueurs (T2). | D12 (déjà écrit dans la règle v0.6) | IA-3 valide |
| P10 | P2 | Entre experts, 60 % de duels nuls (T3). | Tester des variantes (ex. égalité qui fait reculer de 1 les deux, Mémoire élargie à 2 manches) | IA-3 |
| P11 | P1 | Trois dossiers de cartes (`carte-page-1`, `cartes_v0_5_pages-2`, `carte-recto-verso`) contiennent les mêmes cartes. Un seul recto existe en recto-verso (p01). La carte Rediffusion n’est que dans `carte-page-1`, Aventure que dans `pages-2`. Risque d’imprimer la mauvaise version. | Une source unique, recto-verso complet, nomenclature claire | IA-2 |
| P12 | P1 | Production : polices non incorporées (Carlito, Poppins, Caladea, Arial, Brush Script MT dont la licence est commerciale), pas de fond perdu, pas de repères de coupe, couleurs RVB, cartes sans gouttière. | PDF d’impression avec texte vectorisé, 3 mm de fond perdu | IA-1 (plateau), IA-4 (spécifications), IA-2 (cartes) |
| P13 | P1 | Texte à faible contraste sur le plateau (sous-titre rouge sur fond bleu nuit), slogan « Une seule Relique » alors que le jeu a 3 Reliques. | D13 | IA-1 |
| P14 | P2 | Réserve d’Armures dessinée : 5 emplacements pour 12 Armures. Marqueur de manche : un seul jeton « I » imprimé. Dé non fourni. | Aligner sur les comptes du contrat | IA-1, IA-2 |
| P15 | P2 | Cohérence bible et cartes : tampons (couleurs), « Constat n° X », Étiquette n° 9, Bouteille « cachée », correspondances héros/gardiens non validées. | Audit et propositions | IA-5 |
| P16 | P1 | Aucun test humain. | Protocole de test (fiche v0.6) | Vous, avec la fiche |

## 5. Contrat de cohérence v0.6 (source de vérité)

**Toute IA qui modifie un fichier doit respecter ce tableau.** En cas de conflit entre un fichier et ce tableau, le tableau gagne. Les décisions marquées « à valider » sont des recommandations mesurées ; vous pouvez les changer, mais il faut alors me le dire pour que je mette à jour le contrat avant de lancer les IA.

| N° | Sujet | Valeur de référence | Statut |
| --- | --- | --- | --- |
| D1 | Plateau | 34 cases, de 0 (Coulisses, on ne recule jamais plus bas) à 33 (Épisode final). Départ des pions sur la case écrite sur la carte Héros (1, 2 ou 3 ; Rival en 3 à 7 joueurs). | acquis |
| D2 | Étoiles d’Événement | Acte I : 4, 6, 9 · Acte II : 12, 13, 17, 21 · Acte III : 24, 25, 28, 29, 32. Soit 12 étoiles (8 actuelles + 6, 12, 25, 29). Jetons « ? » inchangés : 8, 11, 15, 19, 26, 30. | **à valider** |
| D3 | Duels | Chacun affronte le joueur à sa gauche (le dernier contre le premier) : chaque joueur est donc dans **deux duels** avec la même carte. Coup bat Ruse, Ruse bat Garde, Garde bat Coup. Perdant : recul de 3. Même carte : rien. Un Coup gagnant vole la Relique du perdant si le gagnant n’en porte pas. | acquis |
| D4 | Ordre de l’information | Les cartes action restent face cachée jusqu’à l’étape Duels. À la Lecture, seule la carte de la cible est retournée (elle reste visible). Les pouvoirs « après la Lecture » (Maître) se jouent entre la Lecture et les Duels. | **à valider** |
| D5 | Prophétie | Juste : le Scénariste avance de 3, la cible pioche un Rebondissement. Faux : le Scénariste recule de 2, la cible gagne une Armure. Le Scénariste ne peut pas se viser. | acquis |
| D6 | Mémoire | Jamais la même carte action que la manche précédente. Aucune carte jouable : joue celle que tu veux. | acquis |
| D7 | Reliques et jetons | 3 Reliques + 3 Leurres (= 1 Armure) en jetons face cachée sur les cases « ? ». On retourne un jeton en le **atteignant ou dépassant**. Relique : on la prend si on n’en porte pas ; sinon elle reste visible et le prochain qui passe la prend. 1 Relique par joueur au plus. | acquis |
| D8 | Portes de départ | Avant la manche 1, chacun pose en secret une porte ROUGE (avance de 3) ou BLEUE (1 Armure). Révélation simultanée. 7 rouges, 7 bleues. | **à valider** |
| D9 | Genres | Départ : Aventure. Après les manches 3, 6, 9…, on retourne un Genre, **en alternance : A, B, A, B…** Tas A : Romance, Enquête, Plage, Rediffusion (+ Bureau avec le Dossier). Tas B : Shonen, Tournoi, Fausse mort, Trahison. Le marqueur repart sur 1. Première partie : mode « Aventure seule », aucun Genre. | **à valider** |
| D10 | Rediffusion | Dure **une seule manche**, puis retour à Aventure. Texte de carte : « Cette manche seulement, tu dois rejouer la même carte que la manche précédente. » | **à valider** |
| D11 | Victoire | On gagne en **atteignant ou dépassant la case 33** avec 1 Relique, ou 2 Armures qu’on défausse. Sans l’un ni l’autre : arrêt sur la case 32. | **à valider** |
| D12 | Ordre de la course | Le dé se lance en commençant par le dernier du parcours, puis en remontant (égalité : le plus proche de la Plume vers la gauche). Les duels se résolvent toujours du Scénariste vers la gauche. | **à valider** |
| D13 | Slogan | « Sept héros. Une seule sortie. Et un Scénariste qui jure que tout était écrit. » (remplace « Une seule Relique », qui contredit les 3 Reliques et qui se rattache mieux à l’histoire de la sortie de salle). | **à valider** |
| D14 | Vedette | Un seul joueur en tête avec au moins 2 cases d’avance et ayant dépassé la case 5 prend le Projecteur : il joue en premier, face visible. | acquis |
| D15 | Signalétique | Titre : C’ÉTAIT ÉCRIT. Plateau : La Bobine. Public : dès 12 ans · 4 à 7 joueurs · 30 à 40 min. | acquis |

**Comptes du matériel (à imprimer et à afficher à l’identique partout)** : 7 Héros · 21 cartes action (3 par héros) · 25 Événements (acte I : 8, acte II : 8, acte III : 9) · 16 Rebondissements · 8 Genres + Aventure · 3 Reliques · 3 Leurres · 12 Armures · 7 portes rouges · 7 portes bleues · 12 parchemins · 6 dos « ? » · 1 Plume · 1 Projecteur · 1 marqueur de manche · 7 pions · 1 dé (à fournir). **Dossier Gérard (facultatif)** : +4 Événements (E21 à E24), +1 Rebondissement (R17), +1 Genre (Bureau, tas A), 3 Reliques-Bouteilles qui remplacent les 3 Reliques, 6 pièces de Procès-verbal ; total avec Dossier : 29 Événements, 17 Rebondissements, 9 Genres.

**Vocabulaire fixe** : Scénariste, Plume, Prophétie, parchemin, Lecture, Armure, Relique, Leurre, Genre, Vedette, Projecteur, Rebondissement, Événement, Coulisses, Épisode final. Pas de synonyme.

**Pouvoirs de héros** : texte identique à `cartes_v0_5_page1` ; le Maître remplace « une autre carte de sa main » en respectant la Mémoire (pas celle de la manche précédente).

## 6. Ambiguïtés trouvées à la lecture (partie jouée à la main)

| N° | Ambiguïté | Résolution |
| --- | --- | --- |
| A1 | « Affronte le joueur à ta gauche » : un duel ou deux ? (v0.2 : deux, v0.5 : silence) | D3 |
| A2 | Quand les cartes sont-elles retournées ? (v0.2 : étape 2) | D4 |
| A3 | Porte rouge/bleue : quand et comment on la révèle ? (rien d’écrit) | D8 |
| A4 | Jeton Relique retourné par un joueur qui porte déjà une Relique | D7 |
| A5 | Le Coup gagnant vole-t-il encore la Relique ? (v0.2 oui, v0.5 silence, Hurleur le suppose) | D3 |
| A6 | « Franchir la case 33 » : atteindre ou dépasser ? | D11 |
| A7 | « Pose B sous A » avec un Genre toutes les 3 manches | D9 |
| A8 | Durée de Rediffusion | D10 |
| A9 | Vedette : 3 cases et plus de la case 5 (v0.2), 2 cases sans condition (plateau) | D14 |
| A10 | Maître : « une autre carte de ta main » et Mémoire | D4 + note du contrat |
| A11 | Fausse mort : le mort tient la Plume, ou est visé par une prophétie ? | Le mort ne peut pas être visé. S’il tient la Plume, il n’écrit pas de prophétie cette manche. |
| A12 | Cliffhanger (R14, joue en premier face visible) et Vedette en même temps | Vedette d’abord, puis le Cliffhanger. À tester. |

## 7. Plan de répartition : moi et 5 IA

**Principe** : une IA = un périmètre = un petit dossier de fichiers. Chaque dossier contient ce rapport, le contrat, sa mission (`MISSION.md`) et uniquement les fichiers qu’elle doit lire ou modifier. Aucune IA ne touche aux fichiers d’une autre.

| Qui | Mission | Fichiers reçus |
| --- | --- | --- |
| **Claude (moi)** | Règle A4 v0.6 et fiche de test v0.6 (**faites**), contrat, contrôleur de cohérence, intégration finale | tout |
| **IA-1 Plateau** | P03 (flacon du plateau), P04 (texte tas A/B), P08 (+4 étoiles), P12 (PDF d’impression), P13 (slogan, contraste), P14 (réserve d’Armures) | plateau SVG |
| **IA-2 Cartes et jetons** | P03 (jetons), P05, P06 (carte du tronc), P11 (source unique, recto-verso complet), P12 (cartes), P14 | tous les SVG de `CARTE/` |
| **IA-3 Équilibre** | Valider T2, T4, T6 ; P07, P09 ; P10 (variantes de Mémoire) ; simulateur fidèle aux 25 Événements et aux pouvoirs | simulateur, texte des cartes |
| **IA-4 Légal et production** | P03 (audit), P12 : provenance des 34 images et des icônes, licences des polices, spécifications d’impression, devis à Casablanca dans votre budget de 1 000 MAD | plateau, jeton page 1, textes |
| **IA-5 Univers et Codex** | P15 : cohérence bible, cartes, plateau et manga ; Dossier Gérard ; correspondances héros/gardiens | bible, règles par couches, manga tomes 3 et 4, texte des cartes |

**Ordre** (vous décidez ; voici ma proposition) :

1. Vous validez les décisions « à valider » du contrat (D2, D4, D8, D9, D10, D11, D12, D13). Rien n’est lancé avant, car IA-1 et IA-2 en dépendent.
2. En parallèle : IA-1, IA-2, IA-3, IA-4, IA-5.
3. Au retour, vous me renvoyez les fichiers. Je lance `check_coherence.py` (zéro alerte bloquante exigée), je contrôle les rendus et je valide les versions finales.
4. Impression du test (privé) puis de la série.

**Critères de réception communs** : le fichier respecte le contrat ; `python3 check_coherence.py <dossier>` ne signale aucune alerte bloquante sur les fichiers de l’IA ; aucune valeur numérique n’a changé sans que le contrat le dise ; l’IA liste ce qu’elle n’a pas pu vérifier.

## 8. Ce que vous pouvez imprimer dès aujourd’hui (test privé du 16 nov.)

- Règles et fiche de test v0.6 (PDF livré).
- Cartes : `cartes_v0_5_pages-2` (pages 1 à 8) et `carte-page-1` (héros, actions, parchemins). Pour Rediffusion, notez à la main « 1 manche seulement » en attendant la carte corrigée.
- Plateau A3 tel quel pour le test privé. Les testeurs suivent la règle v0.6 (tas A et B en alternance). Les 4 étoiles ajoutées (D2) ne sont pas nécessaires pour ce test.
- Jetons : les Reliques-Bouteilles ne servent qu’avec le Dossier. Pour un test normal, imprimez les 3 Reliques classiques.
- **Ne photographiez pas** le flacon pour vos précommandes tant que P03 n’est pas fait.

## 9. Ce que je n’ai pas pu vérifier

- Le rire, la clarté, la durée réelle par manche, le temps d’explication de la carte du tronc.
- L’équilibre de Stratège, Comique et Rival (modèles trop simples).
- Les 34 images du plateau et les icônes de héros : je ne connais pas leur origine ni leur licence.
- L’alignement recto-verso à l’impression (je n’ai pas imprimé).
- Le manga (5 tomes) : non audité au-delà de ce que la bible cite.
- Les prix d’impression à Casablanca : je n’ai pas cherché.
