#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
simulateur.py : simulateur de « C'ÉTAIT ÉCRIT ».
Reproduit les règles v0.2 et v0.3 puis permet de tester des variantes.

Usage : python3 simulateur.py            (compare v0.2 et v0.3 en quelques secondes)
        python3 comparer.py              (comparaison complète, 4 à 7 joueurs)
"""
import random
import statistics
from dataclasses import dataclass, field

COUP, GARDE, RUSE = 0, 1, 2
NOMS_CARTE = {COUP: "Coup", GARDE: "Garde", RUSE: "Ruse"}
BAT = {COUP: RUSE, RUSE: GARDE, GARDE: COUP}      # A bat BAT[A]
CONTRE = {RUSE: COUP, GARDE: RUSE, COUP: GARDE}   # carte qui bat la clé


def duel(a, b):
    """1 si a gagne, -1 si b gagne, 0 si égalité."""
    if a == b:
        return 0
    return 1 if BAT[a] == b else -1


# ----------------------------------------------------------------------
# Réglages d'une version du jeu
# ----------------------------------------------------------------------
@dataclass
class Regles:
    nom: str = "v0.2"
    but: int = 30
    cases_relique: tuple = (8, 15, 22)
    cases_event: tuple = (3, 6, 10, 13, 17, 20, 24, 27)
    de: tuple = (1, 2, 3, 4, 5, 6)
    recul_duel: int = 2
    vedette: bool = True
    seuil_vedette: int = 3
    p_contre_vedette: float = 0.7     # voisins qui contrent la carte visible
    p_scene: object = 0.85            # float ou liste par siège
    p_rire: float = 0.5
    competence_scenariste: float = 0.0  # chance « il lit dans ta tête »
    scenes_equitables: bool = False   # refuser une scène ne coûte presque rien
    depart_heros: dict = field(default_factory=dict)   # héros -> case de départ
    depart_siege: list = field(default_factory=list)   # siège -> décalage
    actes: bool = False               # paquets d'événements par acte
    cartes_relatives: bool = False    # cartes qui dépendent du classement
    portee_artichaut: int = 6
    seuil_artichaut: int = 3
    comique_garde: bool = False       # pouvoir du Comique gardé si personne ne rit
    artichaut_avance: int = 0         # si > 0 : le pouvoir devient « avance de N »
    armures_depart_siege: list = field(default_factory=list)
    reliques_cachees: tuple = ()      # cases ◆ : 3 Reliques + 3 leurres (Armure)
    ev_par_acte: bool = False         # 3 paquets d'événements (un par acte)
    genres_empiles: bool = False      # genres légers d'abord, puis climax
    bornes_actes: tuple = (10, 20)
    portes: bool = False              # Entrée en scène : Sprint ou Blindage
    max_manches: int = 45


# ----------------------------------------------------------------------
class Joueur:
    def __init__(self, i, heros, p_scene):
        self.i = i
        self.heros = heros
        self.p_scene = p_scene
        self.pos = 0
        self.depart = 0
        self.relique = False
        self.armures = 0
        self.pouvoir_utilise = False
        self.bloque = 0          # pouvoir bloqué (Amnésie)
        self.saute_de = False
        self.demi_de = False
        self.relance = False
        self.pas_coup = 0
        self.interdite = None
        self.interdite_n = 0
        self.premier = 0         # Cliffhanger
        self.derniere = None
        self.carte = None
        self.coup_annule = False


class Partie:
    GENRES = ["SHONEN", "ROMANCE", "ENQUETE", "TOURNOI",
              "FLASHBACK", "PLAGE", "FAUSSEMORT", "TRAHISON"]

    def __init__(self, n, R, rng):
        if not 4 <= n <= 7:
            raise ValueError("Le nombre de joueurs doit être compris entre 4 et 7.")
        if isinstance(R.p_scene, list) and len(R.p_scene) < n:
            raise ValueError("p_scene doit fournir une valeur pour chaque joueur.")
        self.n, self.R, self.rng = n, R, rng
        self.reserve = 12
        self.reserve_vide = 0
        heros = rng.sample(range(1, 8), n)
        ps = R.p_scene if isinstance(R.p_scene, list) else [R.p_scene] * n
        self.J = [Joueur(i, heros[i], ps[i]) for i in range(n)]
        for j in self.J:
            d = R.depart_heros.get(j.heros, 0)
            if R.depart_siege:
                d += R.depart_siege[j.i]
            j.pos = j.depart = d
        self.reliques = set(R.cases_relique)
        if R.portes:
            for j in self.J:
                if rng.random() < 0.5:
                    j.pos += 3
                else:
                    j.armures += 1
                    self.reserve -= 1
        for j in self.J:
            if R.armures_depart_siege:
                j.armures = R.armures_depart_siege[j.i]
        self.jetons = {}
        if R.reliques_cachees:
            t = ["R", "R", "R", "L", "L", "L"]
            rng.shuffle(t)
            self.jetons = dict(zip(R.reliques_cachees, t))
            self.reliques = set()
        self.ev = list(range(1, 21)); rng.shuffle(self.ev)
        self.rb = list(range(1, 17)); rng.shuffle(self.rb)
        self.gn = list(self.GENRES); rng.shuffle(self.gn)
        if R.genres_empiles:
            lourds = ["SHONEN", "TOURNOI", "FAUSSEMORT", "TRAHISON"]
            legers = ["ROMANCE", "ENQUETE", "PLAGE", "FLASHBACK"]
            rng.shuffle(lourds); rng.shuffle(legers)
            self.gn = lourds + legers      # on pioche par la fin : légers d'abord
        self.ev_acte = {1: [], 2: [], 3: []}
        self.ev_acte_def = {1: [], 2: [], 3: []}
        if R.ev_par_acte:
            self.ev_acte = {1: [2, 6, 12, 18, 4, 1, 17, 15],
                            2: [3, 5, 7, 8, 9, 10, 13, 19],
                            3: [11, 14, 16, 20, 21, 22, 23, 24, 25]}
            for k in self.ev_acte:
                rng.shuffle(self.ev_acte[k])
        self.ev_def, self.rb_def, self.gn_def = [], [], []
        self.genre = "AVENTURE"
        self.manche = 0
        self.manche_genre = 0
        self.scen = 0
        self.gagnant = None
        self.par_relique = None
        self.historique = []     # positions du meneur par manche
        self.nb_vol = 0
        self.nb_prophetie_ok = 0
        self.nb_prophetie = 0

    # ------------------------------------------------------------ outils
    def pioche(self, paquet, defausse):
        if not paquet:
            paquet.extend(defausse); defausse.clear()
            self.rng.shuffle(paquet)
        c = paquet.pop()
        defausse.append(c)
        return c

    def acte(self, pos):
        b1, b2 = self.R.bornes_actes
        return 1 if pos <= b1 else (2 if pos <= b2 else 3)

    def classement(self):
        return sorted(self.J, key=lambda j: -j.pos)

    def dernier(self):
        m = min(j.pos for j in self.J)
        return [j for j in self.J if j.pos == m]

    def premier_joueur(self):
        m = max(j.pos for j in self.J)
        return [j for j in self.J if j.pos == m]

    def meneur_unique(self):
        pos = sorted((j.pos for j in self.J), reverse=True)
        if pos[0] > pos[1]:
            return [j for j in self.J if j.pos == pos[0]][0]
        return None

    def est_mort(self, j):
        if self.genre != "FAUSSEMORT":
            return False
        d = self.dernier()
        return len(d) == 1 and d[0] is j

    def scene(self, j):
        return self.rng.random() < j.p_scene

    def peut_finir(self, j):
        return j.relique or j.armures >= 2

    def pouvoir_ok(self, j, num):
        return j.heros == num and not j.pouvoir_utilise and j.bloque == 0

    # ---------------------------------------------------------- mouvement
    def avancer(self, j, n):
        if n <= 0 or self.gagnant:
            return
        old = j.pos
        new = old + n
        if new >= self.R.but:
            if self.peut_finir(j):
                j.pos = self.R.but
                self.gagnant = j
                self.par_relique = j.relique
                return
            new = self.R.but - 1
        for c in sorted(self.reliques):
            if old < c <= new and not j.relique:
                self.reliques.discard(c)
                j.relique = True
        for c in sorted(self.jetons):
            if old < c <= new:
                t = self.jetons[c]
                if t == "L":
                    del self.jetons[c]
                    self.gagner_armure(j)
                elif not j.relique:
                    del self.jetons[c]
                    j.relique = True
        j.pos = new

    def veut_armure(self, j, n):
        reserve = 0 if j.relique else 2
        return j.armures > reserve and n >= 2

    def reculer(self, j, n, armure=True):
        if n <= 0:
            return 0
        if armure and self.veut_armure(j, n):
            j.armures -= 1
            self.reserve += 1
            return 0
        j.pos = max(0, j.pos - n)
        return n

    def gagner_armure(self, j):
        if self.reserve > 0:
            self.reserve -= 1
            j.armures += 1
        else:
            self.reserve_vide += 1

    def echanger(self, a, b):
        a.pos, b.pos = b.pos, a.pos

    # ----------------------------------------------------------- Événements
    def evenement(self, j):
        if self.R.ev_par_acte:
            a = self.acte(j.pos)
            c = self.pioche(self.ev_acte[a], self.ev_acte_def[a])
        else:
            c = self.pioche(self.ev, self.ev_def)
        R, rng = self.R, self.rng
        mauvaises = {3, 7, 19, 16, 14, 5}
        if (self.pouvoir_ok(j, 6) and c in mauvaises
                and rng.random() < 0.9):
            if rng.random() < R.p_rire:
                j.pouvoir_utilise = True
                return
            if not R.comique_garde:
                j.pouvoir_utilise = True
        eq = R.scenes_equitables
        autres = [x for x in self.J if x is not j]
        if c == 1:   # vieux sage
            if eq:
                self.avancer(j, 2 + (1 if self.scene(j) else 0))
            else:
                self.avancer(j, 3) if self.scene(j) else self.reculer(j, 1)
        elif c == 2:
            self.avancer(j, 2)
        elif c == 3:
            self.reculer(j, 3)
        elif c == 4:
            if rng.choice(self.R.de) % 2 == 0:
                self.gagner_armure(j)
            else:
                self.reculer(j, 2)
        elif c == 5:  # tournoi surprise
            o = rng.choice(autres)
            ca, cb = rng.randrange(3), rng.randrange(3)
            r = duel(ca, cb)
            if r == 1:
                self.reculer(o, 3)
            elif r == -1:
                self.reculer(j, 3)
        elif c == 6:  # festin
            if eq:
                self.avancer(j, 1 + (1 if self.scene(j) else 0))
            else:
                self.avancer(j, 2) if self.scene(j) else self.reculer(j, 1)
        elif c == 7:  # pont
            if eq:
                self.reculer(j, 0 if self.scene(j) else 1)
            elif not self.scene(j):
                self.reculer(j, 2)
        elif c == 8:  # marchand
            if j.armures >= 1 and (j.relique or j.armures >= 3):
                j.armures -= 1; self.reserve += 1
                self.avancer(j, 4)
        elif c == 9:  # vent
            self.avancer(j, 3)
            for o in autres:
                self.avancer(o, 1)
        elif c == 10:  # musical
            if eq:
                self.avancer(j, 2 + (1 if self.scene(j) else 0))
            else:
                self.avancer(j, 3) if self.scene(j) else self.reculer(j, 1)
        elif c == 11:  # faille
            cand = [o for o in autres if abs(o.pos - j.pos) <= 6]
            if cand:
                o = max(cand, key=lambda x: x.pos)
                if o.pos > j.pos:
                    self.echanger(j, o)
        elif c == 12:  # nuit étoilée
            self.gagner_armure(j)
        elif c == 13:  # grand méchant
            for o in autres:
                self.reculer(o, 1)
        elif c == 14:  # concours de regard
            o = rng.choice(autres)
            if rng.random() < 0.7:
                self.reculer(j if rng.random() < 0.5 else o, 2)
        elif c == 15:  # montée de niveau
            self.avancer(j, 2)
            j.relance = True
        elif c == 16:  # vote du village
            if rng.random() < 0.4:
                v = self.premier_joueur()[0]
            else:
                v = rng.choice(self.J)
            self.reculer(v, 2)
        elif c == 17:  # raccourci
            ev = [e for e in sorted(R.cases_event) if e > j.pos]
            self.avancer(j, (ev[0] - j.pos) if ev else 1)
        elif c == 18:  # rencontre
            o = rng.choice(autres)
            self.avancer(j, 2); self.avancer(o, 2)
        elif c == 19:
            self.reculer(j, 2)
        elif c == 20:  # cadeau du destin
            cible = self.premier_joueur()
            cible = [x for x in cible if x is not j] or autres
            self.rebondissement(rng.choice(cible))
        elif c == 21:  # les projecteurs : le meneur recule de 3
            for m in self.premier_joueur():
                self.reculer(m, 3)
        elif c == 22:  # dernière chance : le dernier avance de 4
            for d in self.dernier():
                self.avancer(d, 4)
        elif c == 23:  # le twist : échange avec le meneur (ou +2 si meneur)
            m = self.premier_joueur()
            if j in m:
                self.avancer(j, 2)
            else:
                self.echanger(j, m[0])
        elif c == 24:  # duel final contre le plus proche
            o = min(autres, key=lambda x: abs(x.pos - j.pos))
            r = duel(rng.randrange(3), rng.randrange(3))
            if r == 1:
                self.reculer(o, 3)
            elif r == -1:
                self.reculer(j, 3)
        elif c == 25:  # le chœur : le peloton se resserre
            m = max(x.pos for x in self.J)
            for x in self.J:
                if m - x.pos <= 3 and x.pos != m:
                    self.avancer(x, 2)

    # ------------------------------------------------------ Rebondissements
    def rebondissement(self, j):
        c = self.pioche(self.rb, self.rb_def)
        R, rng = self.R, self.rng
        if self.pouvoir_ok(j, 6) and rng.random() < 0.9:
            if rng.random() < R.p_rire:
                j.pouvoir_utilise = True
                return
            if not R.comique_garde:
                j.pouvoir_utilise = True
        # une armure annule un rebondissement (si elle est de trop)
        if j.armures > (0 if j.relique else 2) and c not in (5, 6, 8, 9, 14):
            j.armures -= 1; self.reserve += 1
            return
        S = self.J[self.scen]
        if c == 1:
            self.reculer(j, 2, armure=False)
        elif c == 2:
            self.reculer(j, 3 + (0 if (self.R.scenes_equitables or self.scene(j)) else 1), armure=False)
        elif c == 3:
            self.reculer(j, 2, armure=False)
        elif c == 4:   # trahison dans le dos
            if j.relique:
                if not S.relique and S is not j:
                    j.relique = False; S.relique = True
            else:
                self.reculer(j, 3, armure=False)
        elif c == 5:
            j.saute_de = True
        elif c == 6:
            j.bloque = 2
        elif c == 7:   # le rival te dépasse
            d = self.dernier()
            if j in d:
                self.avancer(j, 2)
            else:
                o = self.rng.choice(d)
                self.echanger(j, o)
        elif c == 8:
            j.pas_coup = 2
        elif c == 9:
            j.demi_de = True
        elif c == 10:
            self.reculer(j, 4 if rng.choice(R.de) <= 2 else 1, armure=False)
        elif c == 11:
            j.interdite = rng.randrange(3); j.interdite_n = 2
        elif c == 12:
            self.reculer(j, 2, armure=False)
        elif c == 13:
            if j.armures:
                j.armures -= 1; self.reserve += 1
            else:
                self.reculer(j, 2, armure=False)
        elif c == 14:
            self.reculer(j, 1, armure=False)
            j.premier = 2
        elif c == 15:
            self.reculer(j, 2, armure=False)
        elif c == 16:
            for o in self.J:
                if o is not j:
                    self.avancer(o, 1)

    # ------------------------------------------------------------- Manche
    def choisir_carte(self, j, visibles):
        rng = self.rng
        ok = [COUP, GARDE, RUSE]
        if j.pas_coup > 0 and COUP in ok:
            ok.remove(COUP)
        if j.interdite_n > 0 and j.interdite in ok and len(ok) > 1:
            ok.remove(j.interdite)
        if self.genre == "FLASHBACK" and j.derniere in ok and len(ok) > 1:
            ok.remove(j.derniere)
        # les voisins contrent les cartes visibles
        for v in visibles:
            if v is j:
                continue
            gauche = (v.i + 1) % self.n
            droite = (v.i - 1) % self.n
            if j.i in (gauche, droite) and rng.random() < self.R.p_contre_vedette:
                c = CONTRE[v.carte]
                if c in ok:
                    return c
        return rng.choice(ok)

    def jouer_manche(self):
        R, rng, n = self.R, self.rng, self.n
        self.manche += 1
        g = self.genre
        s = self.scen
        S = self.J[s]
        # 1 Prophétie
        cibles = [j for j in self.J if j is not S and not self.est_mort(j)]
        if not cibles:
            cibles = [j for j in self.J if j is not S]
        lead = [j for j in cibles if j in self.premier_joueur()]
        cible = rng.choice(lead) if lead and rng.random() < 0.5 else rng.choice(cibles)
        prevu = rng.randrange(3)
        # Vedette et Cliffhanger : jouent d'abord, à découvert
        vedettes = []
        if R.vedette:
            m = self.meneur_unique()
            if m is not None:
                second = sorted((j.pos for j in self.J), reverse=True)[1]
                if m.pos - second >= R.seuil_vedette and m.pos > 5:
                    vedettes.append(m)
        for j in self.J:
            if j.premier > 0 and j not in vedettes:
                vedettes.append(j)
        # 2 Actions
        for j in vedettes:
            j.carte = self.choisir_carte(j, [])
        for j in self.J:
            if j in vedettes:
                continue
            if j is cible and self.pouvoir_ok(j, 7):
                # Stratège : il voit le parchemin et joue autre chose
                j.pouvoir_utilise = True
                ok = [c for c in range(3) if c != prevu]
                j.carte = rng.choice(ok)
                continue
            j.carte = self.choisir_carte(j, vedettes)
        for j in self.J:
            j.coup_annule = (g == "SHONEN" and j.carte == COUP
                             and rng.random() < 0.15)
        # le Scénariste « lit » parfois dans la tête de sa cible (Enquête : +15 %)
        lit = R.competence_scenariste + (0.15 if g == "ENQUETE" else 0)
        if lit and rng.random() < lit:
            if not (cible.heros == 7 and cible.pouvoir_utilise):
                prevu = cible.carte
        # 3 Lecture
        self.nb_prophetie += 1
        if prevu == cible.carte:
            self.nb_prophetie_ok += 1
            self.avancer(S, 2)
            self.rebondissement(cible)
        else:
            self.gagner_armure(cible)
            self.reculer(S, 1, armure=False)
        if self.gagnant:
            return
        # 4 Duels
        for j in self.J:       # Maître : change sa carte après la lecture
            if self.pouvoir_ok(j, 3):
                gch = self.J[(j.i + 1) % n]; drt = self.J[(j.i - 1) % n]
                def score(c):
                    return duel(c, gch.carte) + duel(drt.carte, c) * -1
                cur = score(j.carte)
                best = max(range(3), key=score)
                if score(best) - cur >= 2 or (j.relique and score(best) > cur):
                    j.carte = best; j.pouvoir_utilise = True
        for k in range(n):
            a = self.J[(s + k) % n]; b = self.J[(s + k + 1) % n]
            self.resoudre_duel(a, b)
            if self.gagnant:
                return
        # 5 Course
        for k in range(n):
            j = self.J[(s + k) % n]
            self.course(j)
            if self.gagnant:
                return
        # 6 Fin de manche
        for j in self.J:
            j.derniere = j.carte
            for att in ("bloque", "pas_coup", "interdite_n", "premier"):
                if getattr(j, att) > 0:
                    setattr(j, att, getattr(j, att) - 1)
        self.scen = (s + 1) % n
        self.manche_genre += 1
        if self.manche_genre >= 3:
            self.genre = self.pioche(self.gn, self.gn_def)
            self.manche_genre = 0
        self.historique.append([j.pos for j in self.J])

    def resoudre_duel(self, a, b):
        g = self.genre
        ca = a.carte; cb = b.carte
        # un Coup annulé ne bat personne
        def r_eff():
            r = duel(ca, cb)
            if r == 1 and ca == COUP and a.coup_annule:
                return 0
            if r == -1 and cb == COUP and b.coup_annule:
                return 0
            return r
        r = r_eff()
        if r == 0:
            if g == "ROMANCE" and ca == cb:
                self.avancer(a, 2); self.avancer(b, 2)
            return
        w, l = (a, b) if r == 1 else (b, a)
        cw = w.carte
        recul = self.R.recul_duel
        if g == "PLAGE":
            recul = 1
        if g == "TOURNOI" and l in self.premier_joueur():
            recul = 3
        if g == "SHONEN" and cw == COUP:
            recul = 4
        hurleur = False
        if (self.pouvoir_ok(l, 1) and (l.relique or self.manche >= 4)):
            l.pouvoir_utilise = True
            hurleur = True
        if not self.est_mort(l) and not hurleur:
            self.reculer(l, recul)
            if l.heros == 2 and l.bloque == 0:
                self.reculer(w, 1)
        if cw == COUP and l.relique and not w.relique and not hurleur:
            l.relique = False; w.relique = True; self.nb_vol += 1

    def course(self, j):
        R, rng = self.R, self.rng
        # Pouvoirs de position
        if self.pouvoir_ok(j, 5) and not j.relique:
            porteurs = [o for o in self.J if o.relique and o is not j]
            if porteurs:
                o = max(porteurs, key=lambda x: x.pos)
                o.relique = False; j.relique = True
                j.pouvoir_utilise = True
        if self.pouvoir_ok(j, 4) and self.manche >= 3 and self.R.artichaut_avance:
            j.pouvoir_utilise = True
            self.avancer(j, self.R.artichaut_avance)
            if self.gagnant:
                return
        elif self.pouvoir_ok(j, 4) and self.manche >= 3:
            cand = [o for o in self.J if o is not j and 0 < o.pos - j.pos <= self.R.portee_artichaut]
            if cand:
                o = max(cand, key=lambda x: x.pos)
                if o.pos - j.pos >= self.R.seuil_artichaut:
                    self.echanger(j, o)
                    j.pouvoir_utilise = True
        if j.saute_de:
            j.saute_de = False
            return
        d = rng.choice(R.de)
        if j.relance:
            d = max(d, rng.choice(R.de)); j.relance = False
        if j.demi_de:
            d = (d + 1) // 2; j.demi_de = False
        self.avancer(j, d)
        if self.gagnant:
            return
        if j.pos in R.cases_event:
            self.evenement(j)


def jouer(n, R, rng):
    p = Partie(n, R, rng)
    while not p.gagnant and p.manche < R.max_manches:
        p.jouer_manche()
        if p.genre == "TRAHISON":
            # tout le monde pointe : le plus pointé recule de 3
            votes = [0] * n
            for j in p.J:
                votes[rng.choice([o.i for o in p.J if o is not j])] += 1
            m = max(votes)
            if votes.count(m) == 1:
                p.reculer(p.J[votes.index(m)], 3)
    return p


# ----------------------------------------------------------------------
def mesurer(R, n, nb=4000, graine=1):
    rng = random.Random(graine)
    res = dict(manches=[], bloque=0, victoires_heros=[0] * 8,
               victoires_siege=[0] * n, relique=0, armures=0,
               remontadas=0, retournements=[], ecart2=[], proche=0)
    parties_h = [0] * 8
    for _ in range(nb):
        p = jouer(n, R, rng)
        for j in p.J:
            parties_h[j.heros] += 1
        if not p.gagnant:
            res["bloque"] += 1
            continue
        res["manches"].append(p.manche)
        res["victoires_heros"][p.gagnant.heros] += 1
        res["victoires_siege"][p.gagnant.i] += 1
        if p.par_relique:
            res["relique"] += 1
        else:
            res["armures"] += 1
        h = p.historique
        if len(h) >= 2:
            mid = h[len(h) // 2]
            if max(mid) - mid[p.gagnant.i] >= 6:
                res["remontadas"] += 1
            # retournements de tête
            tete = None; c = 0
            for pos in h:
                mx = max(pos)
                lead = [i for i, x in enumerate(pos) if x == mx]
                if len(lead) == 1:
                    if tete is not None and tete != lead[0]:
                        c += 1
                    tete = lead[0]
            res["retournements"].append(c)
        second = sorted((j.pos for j in p.J), reverse=True)[1]
        res["ecart2"].append(R.but - second)
        if R.but - second <= 4:
            res["proche"] += 1
    ok = len(res["manches"])
    res["ok"] = ok
    res["parties_h"] = parties_h
    return res


def resume(R, n, nb=4000):
    r = mesurer(R, n, nb)
    ok = max(1, r["ok"])
    ms = r["manches"] or [0]
    h = [r["victoires_heros"][k] / max(1, r["parties_h"][k]) for k in range(1, 8)]
    return {
        "n": n,
        "manches_moy": statistics.mean(ms),
        "manches_p10": sorted(ms)[len(ms) // 10],
        "manches_p90": sorted(ms)[(len(ms) * 9) // 10],
        "bloque_%": 100 * r["bloque"] / nb,
        "relique_%": 100 * r["relique"] / ok,
        "remontada_%": 100 * r["remontadas"] / ok,
        "retournements": statistics.mean(r["retournements"] or [0]),
        "photo_finish_%": 100 * r["proche"] / ok,
        "siege_%": [round(100 * x / ok, 1) for x in r["victoires_siege"]],
        "heros_%": [round(100 * x, 1) for x in h],
        "ideal_%": round(100 / n, 1),
    }


DECALAGES_V03 = {1: 2, 2: 3, 3: 2, 4: 0, 5: 3, 6: 3, 7: 3}   # calibrés par simulation


def regles_v03(offsets=None, **kw):
    """Version 0.3 : plateau de 34 cases en 3 actes, jetons cachés, entrée en scène."""
    base = dict(
        nom="v0.3", but=34, bornes_actes=(11, 23),
        cases_event=(4, 9, 13, 17, 21, 24, 28, 32),
        reliques_cachees=(7, 11, 15, 19, 26, 30),
        cases_relique=(),
        ev_par_acte=True, genres_empiles=True, scenes_equitables=True,
        portes=True, portee_artichaut=3, seuil_artichaut=2, comique_garde=True,
        depart_heros=dict(DECALAGES_V03 if offsets is None else offsets))
    base.update(kw)
    return Regles(**base)


if __name__ == "__main__":
    # Comparaison rapide v0.2 / v0.3 à 5 joueurs (quelques secondes)
    for nom, R in (("v0.2", Regles()), ("v0.3", regles_v03())):
        r = resume(R, 5, 6000)
        print("=== %s (5 joueurs, 6000 parties simulées) ===" % nom)
        print("  manches moyennes : %.1f (de %d à %d)" % (r["manches_moy"], r["manches_p10"], r["manches_p90"]))
        print("  victoires par héros (Hurleur, Rival, Maître, Artichaut, Traître, Comique, Stratège) :", r["heros_%"], "| idéal", r["ideal_%"])
        print("  victoires par siège :", r["siege_%"])
        print("  remontadas : %.0f %% | changements de tête : %.1f | photo-finish : %.0f %%" % (r["remontada_%"], r["retournements"], r["photo_finish_%"]))
