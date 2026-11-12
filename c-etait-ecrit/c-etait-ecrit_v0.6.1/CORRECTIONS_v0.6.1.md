# C'ÉTAIT ÉCRIT : corrections v0.6.1

## Appliquées
- Départ case 2 pour les 7 héros (cartes, plateau, règles). Exception du Rival à 7 joueurs supprimée.
- Maître : « puis recule de 1 ». Traître : « au début de la Course, puis recule de 2 ».
- Carte du tronc : « pose ton pion sur la case 2 ».
- E23 : « retourne le prochain Genre (A, B…) » (proposition à confirmer).
- Guillemets orphelins reflowés : héros Maître et Traître, Dernière chance, Avis de passage, Audit surprise, Le public soupire, Procès-verbal n° 5.
- check_coherence.py : exclut les docx IA-/RAPPORT, alerte sur départs 1 ou 3 et guillemets en fin de ligne.

## Limites connues
- Règles A4 : correction par recouvrement de lignes. Le texte ancien reste sous le blanc (invisible à l'écran et à l'impression, mais présent à la copie et pour check_coherence, d'où 1 alerte bloquante à ignorer). À régénérer depuis la source si tu l'as.
- Plateau PDF : zone « La troupe » superposée à l'ancien PDF.
- Cartes : 5 pages régénérées (p01, p13, p17, p21, p23), le reste est identique à v0.6.
- Non traité : règle des sièges à 7 joueurs, Rival faible à 7 joueurs, nuls entre experts, simulation non relancée, aucun test humain, vrai fond perdu des cartes.
