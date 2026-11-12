#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
sim.py : simulateur C'ÉTAIT ÉCRIT, contrat v0.6 (IA-3 Équilibre)

Fidèle à : plateau 34 cases (0..33), 25 Événements (E01..E20 + A3-1..A3-5),
16 Rebondissements, Genres A/B en alternance, Mémoire, portes de départ,
jetons « ? » (3 Reliques + 3 Leurres), Vedette, Armures, et les 7 pouvoirs de héros
(texte de cartes_v0_5_page1). Dossier Gérard non modélisé (facultatif).

Trois profils de joueur : DEB (carte favorite), HAS (hasard), EXP (expert).
Ce sont des mesures sur des joueurs simulés, pas sur des humains.
"""
import random

COUP, GARDE, RUSE = 0, 1, 2
OUT = [[0, -1, 1], [1, 0, -1], [-1, 1, 0]]          # OUT[a][b] = 1 si a bat b
DEB, HAS, EXP = 0, 1, 2
PROF_NAMES = ['débutant', 'hasard', 'expert']
(HURL, RIVAL, MAITRE, ARTI, TRAITRE, COMIQUE, STRAT) = range(7)
H_NAMES = ['Hurleur', 'Rival', 'Maître', 'Artichaut', 'Traître', 'Comique', 'Stratège']
H_START = [1, 2, 3, 1, 3, 3, 2]
(AVENT, ROMANCE, ENQ, PLAGE, REDIF, SHONEN, TOURNOI, FMORT, TRAHI) = range(9)
GEN_NAMES = ['Aventure', 'Romance', 'Enquête', 'Plage', 'Rediffusion', 'Shonen',
             'Tournoi', 'Fausse mort', 'Trahison']
DECK_A = [ROMANCE, ENQ, PLAGE, REDIF]
DECK_B = [SHONEN, TOURNOI, FMORT, TRAHI]
STARS_V05 = (4, 9, 13, 17, 21, 24, 28, 32)
STARS_D2 = (4, 6, 9, 12, 13, 17, 21, 24, 25, 28, 29, 32)
TOK = (8, 11, 15, 19, 26, 30)
FIN = 33
ACT_EV = [
    ['E01', 'E02', 'E04', 'E06', 'E12', 'E15', 'E17', 'E18'],
    ['E03', 'E05', 'E07', 'E08', 'E09', 'E10', 'E13', 'E19'],
    ['E11', 'E14', 'E16', 'E20', 'A3-1', 'A3-2', 'A3-3', 'A3-4', 'A3-5'],
]
ALL_EV = [e for a in ACT_EV for e in a]
REB = ['R%02d' % i for i in range(1, 17)]
# gravité approchée (en cases) pour décider d'une Armure ou du Fou rire
SEV_R = {'R01': 2, 'R02': 3, 'R03': 2, 'R04': 4, 'R05': 3.5, 'R06': 1, 'R07': 3,
         'R08': 1, 'R09': 1.75, 'R10': 2, 'R11': 1, 'R12': 2, 'R13': 2, 'R14': 1,
         'R15': 2, 'R16': 1}
SEV_E = {'E03': 3, 'E19': 2, 'A3-1': 3}


def act_of(cell):
    return 0 if cell <= 10 else (1 if cell <= 22 else 2)


class Rules:
    def __init__(self, **kw):
        self.stars = STARS_D2
        self.memory = 1          # 0 aucune, 1 manche précédente, 2 deux manches
        self.tie = 'none'        # none | both1 | leader1 | both_plus1
        self.order = 'last'      # last (D12) | scen (v0.5 : Scénariste puis gauche)
        self.reveal = 'hidden'   # hidden (D4) | visible (v0.2)
        self.powers = True
        self.doors = True
        self.genres = 'alt'      # alt (D9) | stack (v0.5 : pose B sous A) | none
        self.redif_rounds = 1    # D10
        self.vedette_lead = 2
        self.p_fun = 0.75        # cris, voix, chants réussis
        self.p_shout = 0.85      # Shonen : attaque criée sans oubli
        self.p_applause = 0.75
        self.p_laugh = 0.70      # Comique : 2 joueurs rient
        self.skill = 'smart'     # politique des pouvoirs : smart | naive
        self.bluff = 0.12
        self.max_rounds = 60
        self.swap_collects = True
        self.seat0_bonus = 0
        self.maitre_info = 'D4'   # D4 | blind
        self.maitre_cost = 0
        self.traitre_cost = 0
        self.comique_thr = None
        self.traitre_timing = 'any'   # any | start
        self.start_override = None
        self.__dict__.update(kw)


class Game:
    def __init__(self, rules, profiles, rng, heroes=None):
        n = len(profiles)
        self.n, self.R, self.rng, self.prof = n, rules, rng, profiles
        self.hero = list(heroes) if heroes is not None else rng.sample(range(7), n)
        self.pos = [H_START[h] + (1 if (h == RIVAL and n >= 7) else 0) for h in self.hero]
        self.pos[0] += rules.seat0_bonus
        if rules.start_override:
            for q in range(n):
                if self.hero[q] in rules.start_override:
                    self.pos[q] = rules.start_override[self.hero[q]]
        self.arm = [0] * n
        self.rel = [False] * n
        self.pwr = [True] * n
        self.amn = [-1] * n
        self.prev = [-1] * n
        self.prev2 = [-1] * n
        self.pref = [rng.sample([0, 1, 2], 3) for _ in range(n)]
        self.cnt = [[[0, 0, 0] for _ in range(4)] for _ in range(n)]
        self.tsun = [-1] * n
        self.clone = [(-1, -1)] * n
        self.cliff = [-1] * n
        self.skip = [False] * n
        self.half = [False] * n
        self.rerollf = [False] * n
        vals = [0, 0, 0, 1, 1, 1]
        rng.shuffle(vals)
        self.tok = {c: v for c, v in zip(TOK, vals)}   # 0 Relique cachée, 1 Leurre, 2 Relique visible, 3 vide
        self.genre = AVENT
        self.genre_round = 0
        self.rnd = 1
        self.since = 0
        self.plume = 0
        self.winner = -1
        self.win_via = None
        self.dead = [False] * n
        self.dead_prev = [False] * n
        self.edeck = [rng.sample(a, len(a)) for a in ACT_EV]
        self.edisc = [[], [], []]
        self.rdeck = rng.sample(REB, 16)
        self.rdisc = []
        self.pileA = rng.sample(DECK_A, 4)
        self.pileB = rng.sample(DECK_B, 4)
        self.nextpile = 'A'
        # stats
        self.st_pred = [0, 0]
        self.st_duel = [0, 0]          # [duels, nuls]
        self.st_duel_ee = [0, 0]       # entre deux experts
        self.st_ev = []                # (id, act, drawer, d_self, d_others_mean, d_arm)
        self.st_genres = []
        self.st_power = [0] * 7
        self.st_vedette = 0
        self.st_stolen = 0
        self.st_door = [0, 0]          # [rouges, bleues]
        self.doorchoice = [None] * n
        self.last_actions = None

    # ------------------------------------------------------------------ utilitaires
    def left(self, i):
        return (i + 1) % self.n

    def legal(self, p):
        r = self.rnd
        pv = self.prev[p]
        blocked = set()
        if self.tsun[p] == r:
            blocked.add(COUP)
        if self.clone[p][0] == r:
            blocked.add(self.clone[p][1])
        if self.genre == REDIF:
            if pv >= 0 and pv not in blocked:
                return [pv]
            return [0, 1, 2]
        L = [c for c in (0, 1, 2) if c not in blocked]
        if self.R.memory >= 1 and pv >= 0:
            L = [c for c in L if c != pv]
        if self.R.memory >= 2 and self.prev2[p] >= 0:
            L = [c for c in L if c != self.prev2[p]]
        return L if L else [0, 1, 2]

    def power_ok(self, p):
        return self.R.powers and self.pwr[p] and self.amn[p] < self.rnd

    def passive_ok(self, p):
        return self.R.powers and self.amn[p] < self.rnd

    def leaders(self):
        m = max(self.pos)
        return [i for i in range(self.n) if self.pos[i] == m]

    def lasts(self):
        m = min(self.pos)
        return [i for i in range(self.n) if self.pos[i] == m]

    def others(self, p):
        return [i for i in range(self.n) if i != p]

    # ------------------------------------------------------------------ Armures
    def want_armor(self, p, sev, relic=False):
        if self.arm[p] <= 0:
            return False
        pr = self.prof[p]
        if pr == DEB:
            return sev >= 2 or relic
        if pr == HAS:
            return self.rng.random() < 0.5
        return relic or self.arm[p] >= 3

    def recul(self, p, k, sev=None, relic=False, force_armor=None):
        if k <= 0 or self.pos[p] == 0:
            return False
        use = force_armor if force_armor is not None else self.want_armor(p, sev if sev is not None else k, relic)
        if use and self.arm[p] > 0:
            self.arm[p] -= 1
            return False
        self.pos[p] = max(0, self.pos[p] - k)
        return True

    # ------------------------------------------------------------------ déplacements
    def collect(self, p, lo, hi):
        for c in TOK:
            if lo < c <= hi:
                st = self.tok[c]
                if st == 0:
                    if not self.rel[p]:
                        self.rel[p] = True
                        self.tok[c] = 3
                    else:
                        self.tok[c] = 2
                elif st == 1:
                    self.arm[p] += 1
                    self.tok[c] = 3
                elif st == 2 and not self.rel[p]:
                    self.rel[p] = True
                    self.tok[c] = 3

    def advance(self, p, k):
        """Avance de k cases. Renvoie True si p gagne."""
        if k <= 0:
            return False
        a = self.pos[p]
        t = a + k
        self.collect(p, a, min(t, FIN - 1))
        if t >= FIN:
            if self.rel[p]:
                self.winner, self.win_via = p, 'relique'
                self.pos[p] = FIN
                return True
            if self.arm[p] >= 2:
                self.arm[p] -= 2
                self.winner, self.win_via = p, 'armures'
                self.pos[p] = FIN
                return True
            self.pos[p] = FIN - 1
            return False
        self.pos[p] = t
        return False

    def swap(self, a, b):
        pa, pb = self.pos[a], self.pos[b]
        if pa == pb:
            return
        self.pos[a], self.pos[b] = pb, pa
        if self.R.swap_collects:
            if pb > pa:
                self.collect(a, pa, pb)
            else:
                self.collect(b, pb, pa)

    # ------------------------------------------------------------------ pioches
    def draw_event(self, act):
        if not self.edeck[act]:
            self.edeck[act] = self.rng.sample(self.edisc[act], len(self.edisc[act]))
            self.edisc[act] = []
        e = self.edeck[act].pop()
        self.edisc[act].append(e)
        return e

    def draw_reb(self):
        if not self.rdeck:
            self.rdeck = self.rng.sample(self.rdisc, len(self.rdisc))
            self.rdisc = []
        r = self.rdeck.pop()
        self.rdisc.append(r)
        return r

    # ------------------------------------------------------------------ Comique
    def comique_cancel(self, p, sev):
        if self.hero[p] != COMIQUE or not self.power_ok(p):
            return False
        thr = self.R.comique_thr if self.R.comique_thr else (2 if self.R.skill == 'naive' else 3)
        if sev < thr:
            return False
        if self.rng.random() < self.R.p_laugh:
            self.pwr[p] = False
            self.st_power[COMIQUE] += 1
            return True
        return False

    # ------------------------------------------------------------------ modèle adverse
    def dist(self, o, known):
        if o in known:
            return {known[o]: 1.0}
        Lo = self.legal(o)
        idx = self.prev[o] if self.prev[o] >= 0 else 3
        w = [self.cnt[o][idx][c] + 1.0 for c in Lo]
        s = sum(w)
        return {c: x / s for c, x in zip(Lo, w)}

    def loss_cost(self, p, o, xcard):
        g = self.genre
        cost = 3
        if g == PLAGE:
            cost = 1
        elif g == SHONEN and xcard == COUP:
            cost = 5
        elif g == TOURNOI and self.pos[p] == max(self.pos):
            cost = 4
        if xcard == COUP and self.rel[p] and not self.rel[o]:
            cost += 6
        return cost

    def util(self, p, c, o, x):
        res = OUT[c][x]
        if res == -1:
            return -self.loss_cost(p, o, x)
        if res == 1:
            return 5 if (c == COUP and not self.rel[p] and self.rel[o]) else 0
        return 2 if self.genre == ROMANCE else 0

    def score(self, p, c, known):
        s = 0.0
        for o in (self.left(p), (p - 1) % self.n):
            for x, pr in self.dist(o, known).items():
                s += pr * self.util(p, c, o, x)
        return s

    def choose(self, p, known, avoid=None):
        Lg = self.legal(p)
        if avoid is not None and avoid in Lg and len(Lg) > 1:
            Lg = [c for c in Lg if c != avoid]
        if len(Lg) == 1:
            return Lg[0]
        pr = self.prof[p]
        if pr == DEB:
            for c in self.pref[p]:
                if c in Lg:
                    return c
        if pr == HAS or self.rng.random() < self.R.bluff:
            return self.rng.choice(Lg)
        best, bs = [], -1e9
        for c in Lg:
            s = self.score(p, c, known)
            if s > bs + 1e-9:
                best, bs = [c], s
            elif abs(s - bs) <= 1e-9:
                best.append(c)
        return self.rng.choice(best)

    # ------------------------------------------------------------------ Prophétie
    def prophecy(self, S):
        n = self.n
        cands = [i for i in range(n) if i != S and not self.dead[i]]
        if not cands:
            return None
        pr = self.prof[S]
        if pr != EXP:
            t = self.rng.choice(cands)
            Lt = self.legal(t)
            return (t, self.rng.choice(Lt))
        best, bp, bc = [], -1, {}
        pool = cands
        nostrat = [i for i in cands if not (self.hero[i] == STRAT and self.power_ok(i))]
        if nostrat:
            pool = nostrat
        for t in pool:
            d = self.dist(t, {})
            c = max(d, key=d.get)
            pb = d[c]
            if pb > bp + 1e-9:
                best, bp, bc = [t], pb, {t: c}
            elif abs(pb - bp) <= 1e-9:
                best.append(t)
                bc[t] = c
        t = self.rng.choice(best)
        return (t, bc[t])

    # ------------------------------------------------------------------ pouvoirs
    def maitre_power(self, p, card, known):
        if self.hero[p] != MAITRE or not self.power_ok(p):
            return
        alts = [c for c in self.legal(p) if c != card]
        if not alts:
            return
        s0 = self.score(p, card, known)
        bestc, bs = None, s0
        for c in alts:
            s = self.score(p, c, known)
            if s > bs + 1e-9:
                bestc, bs = c, s
        thr = 0.5 if self.R.skill == 'naive' else 2.0
        if bestc is not None and bs - s0 >= thr:
            self.pwr[p] = False
            self.st_power[MAITRE] += 1
            if self.R.maitre_cost:
                self.recul(p, self.R.maitre_cost, force_armor=False)
            return bestc
        return None

    # ------------------------------------------------------------------ une manche
    def round(self):
        R, n, rng = self.R, self.n, self.rng
        S = self.plume
        r = self.rnd
        # --- Fausse mort
        dead = [False] * n
        if self.genre == FMORT:
            ls = self.lasts()
            if len(ls) == 1:
                dead[ls[0]] = True
            for i in range(n):
                if self.dead_prev[i] and not dead[i] and rng.random() < R.p_applause:
                    if self.advance(i, 2):
                        return
        self.dead = dead
        self.dead_prev = dead[:]
        # --- Vedette
        vedette = -1
        srt = sorted(self.pos, reverse=True)
        if srt[0] - srt[1] >= R.vedette_lead and srt[0] > 5:
            vedette = self.pos.index(srt[0])
            self.st_vedette += 1
        # --- 1. Prophétie
        pred = None if dead[S] else self.prophecy(S)
        # --- 2. Actions
        card = [-1] * n
        known = {}
        order = []
        if vedette >= 0:
            order.append(vedette)
        for i in range(n):
            if self.cliff[i] == r and i not in order:
                order.append(i)
        hidden = [i for i in range(n) if i not in order]
        # Stratège : « Suis-je la cible ? »
        avoid = {}
        for i in range(n):
            if self.hero[i] == STRAT and self.power_ok(i) and pred and pred[0] == i:
                self.pwr[i] = False
                self.st_power[STRAT] += 1
                avoid[i] = pred[1]
        for i in order:
            card[i] = self.choose(i, known, avoid.get(i))
            known[i] = card[i]
        vis_known = dict(known)
        for i in hidden:
            card[i] = self.choose(i, vis_known, avoid.get(i))
        # Shonen : Coup oublié
        void = [False] * n
        if self.genre == SHONEN:
            for i in range(n):
                if card[i] == COUP and rng.random() > R.p_shout:
                    void[i] = True
        if R.reveal == 'visible':
            known = {i: card[i] for i in range(n)}
        # --- 3. Lecture
        if pred:
            t, pc = pred
            self.st_pred[0] += 1
            known[t] = card[t]
            if card[t] == pc:
                self.st_pred[1] += 1
                if self.advance(S, 3):
                    return
                self.apply_reb(t, S, self.draw_reb())
                if self.winner >= 0:
                    return
            else:
                self.recul(S, 2)
                self.arm[t] += 1
        # Maître : après la Lecture, avant les Duels
        for i in range(n):
            if self.hero[i] == MAITRE:
                nc = self.maitre_power(i, card[i], known if R.maitre_info == 'D4' else {})
                if nc is not None:
                    card[i] = nc
                    void[i] = False
        # --- 4. Duels
        if self.genre == TRAHI:
            point = [0] * n
            ld = self.leaders()
            for i in range(n):
                if self.prof[i] == EXP:
                    c = [x for x in ld if x != i]
                    if not c:
                        srt2 = sorted([x for x in range(n) if x != i], key=lambda z: -self.pos[z])
                        c = [srt2[0]]
                    point[rng.choice(c)] += 1
                else:
                    point[rng.choice(self.others(i))] += 1
            m = max(point)
            top = [i for i in range(n) if point[i] == m]
            if len(top) == 1:
                self.recul(top[0], 3)
        for k in range(n):
            i = (S + k) % n
            j = self.left(i)
            self.duel(i, j, card, void)
            if self.winner >= 0:
                return
        # mémoire de l'historique
        for i in range(n):
            idx = self.prev[i] if self.prev[i] >= 0 else 3
            self.cnt[i][idx][card[i]] += 1
            self.prev2[i] = self.prev[i]
            self.prev[i] = card[i]
        # --- 5. Course
        if R.order == 'last':
            seq = sorted(range(n), key=lambda i: (self.pos[i], (i - S) % n))
        else:
            seq = [(S + k) % n for k in range(n)]
        # Artichaut / Traître naïfs : agissent avant la course
        for i in seq:
            if self.hero[i] == ARTI and self.power_ok(i):
                self.arti_power(i)
        for i in seq:
            if self.hero[i] == TRAITRE and self.power_ok(i) and R.skill == 'naive':
                self.traitre_power(i, force=True)
        if R.skill == 'smart' and R.traitre_timing == 'start':
            for i in seq:
                if self.hero[i] == TRAITRE and self.power_ok(i) and not self.rel[i]:
                    hold = [q for q in range(n) if q != i and self.rel[q] and self.pos[q] >= 22]
                    if hold:
                        self.traitre_power(i, force=True, victim=max(hold, key=lambda q: self.pos[q]))
        for i in seq:
            # Traître « malin » : interrompt avant le lancer d'un porteur proche de l'arrivée
            if R.skill == 'smart' and R.traitre_timing == 'any':
                for t in range(n):
                    if t != i and self.hero[t] == TRAITRE and self.power_ok(t) and not self.rel[t] \
                            and self.rel[i] and self.pos[i] >= 27:
                        self.traitre_power(t, force=True, victim=i)
            if self.skip[i]:
                self.skip[i] = False
                continue
            d = rng.randint(1, 6)
            if self.rerollf[i]:
                self.rerollf[i] = False
                if d <= 3:
                    d = rng.randint(1, 6)
            if self.half[i]:
                self.half[i] = False
                d = (d + 1) // 2
            if self.advance(i, d):
                return
            if self.pos[i] in R.stars:
                self.event(i)
                if self.winner >= 0:
                    return
        # --- 6. Fin de manche
        self.end_round()

    def end_round(self):
        R = self.R
        if self.genre == REDIF and self.rnd >= self.genre_round + R.redif_rounds - 1 and self.genre_round > 0:
            self.genre = AVENT
        self.since += 1
        if self.since >= 3 and R.genres != 'none':
            self.since = 0
            g = None
            if R.genres == 'alt':
                if self.nextpile == 'A':
                    pile = self.pileA if self.pileA else self.pileB
                else:
                    pile = self.pileB if self.pileB else self.pileA
                self.nextpile = 'B' if self.nextpile == 'A' else 'A'
            else:
                pile = self.pileA if self.pileA else self.pileB
            if pile:
                g = pile.pop()
            if g is not None:
                self.genre = g
                self.genre_round = self.rnd + 1
                self.st_genres.append(g)
        self.plume = (self.plume + 1) % self.n
        self.rnd += 1

    # ------------------------------------------------------------------ Duels
    def duel(self, i, j, card, void):
        R = self.R
        ci, cj = card[i], card[j]
        res = OUT[ci][cj]
        if res != 0:
            if res == 1 and ci == COUP and void[i]:
                res = 0 if cj == RUSE else res
            elif res == -1 and cj == COUP and void[j]:
                res = 0 if ci == RUSE else res
        self.st_duel[0] += 1
        ee = self.prof[i] == EXP and self.prof[j] == EXP
        if ee:
            self.st_duel_ee[0] += 1
        if res == 0:
            self.st_duel[1] += 1
            if ee:
                self.st_duel_ee[1] += 1
            if ci == cj:
                if self.genre == ROMANCE:
                    for q in (i, j):
                        if self.advance(q, 2):
                            return
                elif R.tie == 'both1':
                    for q in (i, j):
                        if not self.dead[q]:
                            self.recul(q, 1)
                elif R.tie == 'both_plus1':
                    for q in (i, j):
                        if self.advance(q, 1):
                            return
                elif R.tie == 'tiebreak':
                    S0, n0 = self.plume, self.n
                    wq = i if (i - S0) % n0 < (j - S0) % n0 else j
                    lq = j if wq == i else i
                    if not self.dead[lq]:
                        self.recul(lq, 1 if self.genre == PLAGE else 3)
                elif R.tie == 'typed':
                    if ci == COUP:
                        for q in (i, j):
                            if not self.dead[q]:
                                self.recul(q, 1)
                    elif ci == RUSE:
                        for q in (i, j):
                            if self.advance(q, 1):
                                return
                elif R.tie == 'leader1':
                    if self.pos[i] != self.pos[j]:
                        q = i if self.pos[i] > self.pos[j] else j
                        if not self.dead[q]:
                            self.recul(q, 1)
            return
        w, l = (i, j) if res == 1 else (j, i)
        wc = card[w]
        wcoup = (wc == COUP and not void[w])
        # Hurleur
        hurl = False
        if self.hero[l] == HURL and self.power_ok(l):
            use = False
            if R.skill == 'naive':
                use = True
            else:
                use = (self.rel[l] and wcoup and not self.rel[w]) or self.pos[l] >= 24
            if use and self.rng.random() < R.p_fun:
                self.pwr[l] = False
                self.st_power[HURL] += 1
                hurl = True
        g = self.genre
        k = 3
        if g == PLAGE:
            k = 1
        elif g == SHONEN and wcoup:
            k = 5
        elif g == TOURNOI and self.pos[l] == max(self.pos):
            k = 4
        if not hurl and not self.dead[l]:
            self.recul(l, k)
            if self.hero[l] == RIVAL and self.passive_ok(l):
                self.recul(w, 1)
        if wcoup and not hurl and self.rel[l] and not self.rel[w]:
            self.rel[l] = False
            self.rel[w] = True
            self.st_stolen += 1

    # ------------------------------------------------------------------ pouvoirs actifs (Course)
    def arti_power(self, p):
        cands = [q for q in range(self.n) if 1 <= self.pos[q] - self.pos[p] <= 3]
        if not cands:
            return
        def gain(q):
            lo, hi = self.pos[p], self.pos[q]
            v = hi - lo
            for c in TOK:
                if lo < c <= hi and self.tok[c] in (0, 1, 2):
                    v += 2.5
            return v
        q = max(cands, key=gain)
        gv = gain(q)
        if self.R.skill == 'naive':
            ok = True
        else:
            ok = gv >= 5 or (self.rnd >= 7 and gv >= 3)
        if ok:
            self.pwr[p] = False
            self.st_power[ARTI] += 1
            self.swap(p, q)

    def traitre_power(self, p, force=False, victim=None):
        if self.rel[p]:
            return
        if victim is None:
            hold = [q for q in range(self.n) if q != p and self.rel[q]]
            if not hold:
                return
            victim = max(hold, key=lambda q: self.pos[q])
        if not self.rel[victim]:
            return
        self.rel[victim] = False
        self.rel[p] = True
        self.pwr[p] = False
        self.st_power[TRAITRE] += 1
        if self.R.traitre_cost:
            self.recul(p, self.R.traitre_cost, force_armor=False)

    # ------------------------------------------------------------------ Rebondissements
    def apply_reb(self, t, S, rid):
        sev = SEV_R[rid]
        if rid == 'R04' and self.rel[t]:
            sev = 8
        if rid == 'R07':
            sev = max(0, self.pos[t] - min(self.pos))
        if self.comique_cancel(t, sev):
            return
        if rid not in ('R13', 'R16') and self.arm[t] > 0 and self.want_armor(t, sev, relic=(rid == 'R04' and self.rel[t])):
            self.arm[t] -= 1
            return
        n = self.n
        if rid == 'R01':
            self.recul(t, 2, force_armor=False)
        elif rid == 'R02':
            self.recul(t, 3, force_armor=False)
        elif rid == 'R03':
            self.recul(t, 2, force_armor=False)
        elif rid == 'R04':
            if self.rel[t]:
                if not self.rel[S]:
                    self.rel[t] = False
                    self.rel[S] = True
            else:
                self.recul(t, 3, force_armor=False)
        elif rid == 'R05':
            self.skip[t] = True
        elif rid == 'R06':
            self.amn[t] = self.rnd + 1
        elif rid == 'R07':
            ls = self.lasts()
            if t in ls:
                if self.advance(t, 2):
                    return
            else:
                self.swap(t, self.rng.choice(ls))
        elif rid == 'R08':
            self.tsun[t] = self.rnd + 1
        elif rid == 'R09':
            self.half[t] = True
        elif rid == 'R10':
            d = self.rng.randint(1, 6)
            self.recul(t, 4 if d <= 2 else 1, force_armor=False)
        elif rid == 'R11':
            if self.prof[S] == EXP:
                d = self.dist(t, {})
                nxt = self.rnd + 1
                c = max(d, key=d.get)
            else:
                c = self.rng.randint(0, 2)
                nxt = self.rnd + 1
            self.clone[t] = (nxt, c)
        elif rid == 'R12':
            self.recul(t, 2, force_armor=False)
        elif rid == 'R13':
            if self.arm[t] > 0:
                self.arm[t] -= 1
            else:
                self.recul(t, 2, force_armor=False)
        elif rid == 'R14':
            self.recul(t, 1, force_armor=False)
            self.cliff[t] = self.rnd + 1
        elif rid == 'R15':
            self.recul(t, 2, force_armor=False)
        elif rid == 'R16':
            for q in range(n):
                if q != t:
                    if self.advance(q, 1):
                        return

    # ------------------------------------------------------------------ Événements
    def pick(self, p, mode):
        """choix d'un autre joueur selon le profil"""
        cands = self.others(p)
        if self.prof[p] != EXP:
            return self.rng.choice(cands)
        if mode == 'leader':
            m = max(self.pos[q] for q in cands)
            return self.rng.choice([q for q in cands if self.pos[q] == m])
        if mode == 'last':
            m = min(self.pos[q] for q in cands)
            return self.rng.choice([q for q in cands if self.pos[q] == m])
        return self.rng.choice(cands)

    def mini_duel(self, a, b):
        """Duel hors Mémoire (Tournoi surprise, Duel d'arène). Renvoie le perdant ou -1."""
        rng = self.rng
        def pickc(p, o):
            pr = self.prof[p]
            if pr == DEB:
                return self.pref[p][0]
            if pr == HAS:
                return rng.randint(0, 2)
            tot = [1.0, 1.0, 1.0]
            for idx in range(4):
                for c in range(3):
                    tot[c] += self.cnt[o][idx][c]
            s = sum(tot)
            best, bs = [], -1e9
            for c in (0, 1, 2):
                v = 0.0
                for x in (0, 1, 2):
                    v += tot[x] / s * OUT[c][x]
                if v > bs + 1e-9:
                    best, bs = [c], v
                elif abs(v - bs) < 1e-9:
                    best.append(c)
            return rng.choice(best)
        ca, cb = pickc(a, b), pickc(b, a)
        res = OUT[ca][cb]
        if res == 0:
            return -1
        return b if res == 1 else a

    def event(self, p):
        a = act_of(self.pos[p])
        eid = self.draw_event(a)
        pos0 = self.pos[:]
        arm0 = self.arm[p]
        self.resolve_event(p, eid)
        d_self = self.pos[p] - pos0[p]
        oth = [self.pos[q] - pos0[q] for q in range(self.n) if q != p]
        self.st_ev.append((eid, a, p, d_self, sum(oth) / len(oth), self.arm[p] - arm0))

    def resolve_event(self, p, e):
        R, n, rng = self.R, self.n, self.rng
        sev = SEV_E.get(e, 0)
        if e == 'A3-1' and p not in self.leaders():
            sev = 0
        if sev and self.comique_cancel(p, sev):
            return
        if e == 'E01':
            self.advance(p, 2 + (1 if rng.random() < R.p_fun else 0))
        elif e == 'E02':
            self.advance(p, 2)
        elif e == 'E04':
            if rng.randint(1, 6) % 2 == 0:
                self.arm[p] += 1
            else:
                self.recul(p, 2)
        elif e == 'E06':
            self.advance(p, 1 + (1 if rng.random() < R.p_fun else 0))
        elif e == 'E12':
            self.arm[p] += 1
        elif e == 'E15':
            if self.advance(p, 2):
                return
            self.rerollf[p] = True
        elif e == 'E17':
            tgt = [c for c in R.stars if self.pos[p] < c <= self.pos[p] + 4]
            if tgt:
                self.advance(p, tgt[0] - self.pos[p])
            else:
                self.advance(p, 1)
        elif e == 'E18':
            q = self.pick(p, 'last')
            self.advance(p, 2)
            if self.winner < 0:
                self.advance(q, 2)
        elif e == 'E03':
            self.recul(p, 3, sev=3, force_armor=None)
        elif e == 'E05':
            q = self.pick(p, 'leader')
            lo = self.mini_duel(p, q)
            if lo >= 0:
                self.recul(lo, 3)
        elif e == 'E07':
            if rng.random() > R.p_fun:
                self.recul(p, 1)
        elif e == 'E08':
            ok = self.arm[p] >= 1 and (self.prof[p] != EXP or self.arm[p] >= 2 or self.pos[p] <= 12)
            if ok:
                self.arm[p] -= 1
                self.advance(p, 4)
        elif e == 'E09':
            if self.advance(p, 3):
                return
            for q in self.others(p):
                if self.advance(q, 1):
                    return
        elif e == 'E10':
            self.advance(p, 2 + (1 if rng.random() < R.p_fun else 0))
        elif e == 'E13':
            for q in self.others(p):
                self.recul(q, 1)
        elif e == 'E19':
            self.recul(p, 2, force_armor=False)
        elif e == 'E11':
            cands = [q for q in self.others(p) if abs(self.pos[q] - self.pos[p]) <= 6]
            if cands:
                if self.prof[p] == EXP:
                    q = max(cands, key=lambda z: (self.pos[z] - self.pos[p]) + rng.random() * 0.01)
                else:
                    q = rng.choice(cands)
                self.swap(p, q)
        elif e == 'E14':
            q = self.pick(p, 'leader')
            x = rng.random()
            if x < 0.45:
                self.recul(q, 2)
            elif x < 0.90:
                self.recul(p, 2)
        elif e == 'E16':
            w = []
            for q in range(n):
                w.append(1 + 2 * (1 if self.rel[q] else 0) + (1 if q in self.leaders() else 0))
            q = rng.choices(range(n), weights=w)[0]
            self.recul(q, 2)
        elif e == 'E20':
            q = self.pick(p, 'leader')
            self.apply_reb(q, p, self.draw_reb())
        elif e == 'A3-1':
            for q in self.leaders():
                self.recul(q, 3)
        elif e == 'A3-2':
            for q in self.lasts():
                if self.advance(q, 4):
                    return
        elif e == 'A3-3':
            ld = self.leaders()
            if p in ld:
                self.advance(p, 2)
            else:
                self.swap(p, rng.choice(ld))
        elif e == 'A3-4':
            best = min(abs(self.pos[q] - self.pos[p]) for q in self.others(p))
            cs = [q for q in self.others(p) if abs(self.pos[q] - self.pos[p]) == best]
            q = rng.choice(cs)
            lo = self.mini_duel(p, q)
            if lo >= 0:
                self.recul(lo, 3)
        elif e == 'A3-5':
            m = max(self.pos)
            for q in range(n):
                if 1 <= m - self.pos[q] <= 3:
                    if self.advance(q, 2):
                        return

    # ------------------------------------------------------------------ partie
    def run(self):
        R, n, rng = self.R, self.n, self.rng
        if R.doors:
            for i in range(n):
                red = rng.random() < 0.5
                self.doorchoice[i] = red
                if red:
                    self.st_door[0] += 1
                    self.advance(i, 3)
                else:
                    self.st_door[1] += 1
                    self.arm[i] += 1
        while self.winner < 0 and self.rnd <= R.max_rounds:
            self.round()
        return self


def play(rules, profiles, seed, heroes=None):
    rng = random.Random(seed)
    g = Game(rules, profiles, rng, heroes)
    g.run()
    return g
