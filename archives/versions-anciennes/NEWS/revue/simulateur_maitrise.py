"""Simulateur de C'ÉTAIT ÉCRIT (règles v0.3 + duels v0.2 + variantes v0.5, pouvoirs des 7 héros inclus).
Simplifications assumées : pas de scènes jouées (bonus pris), Genres Enquête/Fausse mort/Trahison sans effet,
Événements et Rebondissements approchés. Sert à mesurer l'écart débutant / expert, pas le rire.
Niveaux : 0 = débutant prévisible, 1 = joueur au hasard, 2 = expert (lit les autres, bluffe un peu)."""
import random
from collections import Counter

COUP, GARDE, RUSE = 0, 1, 2
def beats(a, b): return (a == COUP and b == RUSE) or (a == RUSE and b == GARDE) or (a == GARDE and b == COUP)
START = {'Artichaut': 0, 'Maitre': 1, 'Hurleur': 2, 'Rival': 3, 'Strategue': 3, 'Traitre': 4, 'Comique': 4}
STAR = [4, 9, 13, 17, 21, 24, 28, 32]
TOK = [8, 11, 15, 19, 26, 30]
A_GENRES = ['Romance', 'Enquete', 'Plage', 'Flashback']
REDIF = False
B_GENRES = ['Shonen', 'Tournoi', 'FausseMort', 'Trahison']

DEFAULT = dict(powers=True, start=None, x_cards=True, x_armor=True, x_target=True, armor_use_p=1.0, ev_scale=1.0, recoil=3, no_repeat=False, right_bonus=2, wrong_pen=1, genre_every=3, eps=0.3, max_rounds=40,
               start_mode='classic')


class Game:
    def __init__(s, levels, rng, cfg):
        s.rng, s.cfg, s.lv, s.n = rng, cfg, levels, len(levels)
        n = s.n
        heroes = rng.sample(list(START), n)
        st = cfg.get('start') or START
        s.hero = heroes
        s.used = [False] * n
        s.pb = [0] * n
        s.dodge = {}
        s.in_ev = False
        s.cur = None
        s.pos = [st[h] for h in heroes]
        s.armor = [0] * n
        s.relic = [False] * n
        for i in range(n):
            if rng.random() < 0.5: s.pos[i] += 3
            else: s.armor[i] += 1
        tk = ['R'] * 3 + ['L'] * 3
        rng.shuffle(tk)
        s.tokens = dict(zip(TOK, tk))
        s.hist = [Counter() for _ in range(n)]
        s.last = [None] * n
        s.fav = [rng.randrange(3) for _ in range(n)]
        s.skip = [False] * n
        s.half = [False] * n
        s.block = [None] * n
        s.open_next = [False] * n
        s.winner = None
        s.win_by = None
        a = (['Romance', 'Enquete', 'Plage', 'Rediffusion'] if cfg.get('redif') else A_GENRES[:]); b = B_GENRES[:]
        rng.shuffle(a); rng.shuffle(b)
        s.genres = ['Aventure'] + a + b
        s.rounds = 0

    # ---------- état
    def genre(s):
        return s.genres[min((s.rounds) // s.cfg['genre_every'], len(s.genres) - 1)]

    def leader(s):
        m = max(s.pos); return [i for i in range(s.n) if s.pos[i] == m]

    # ---------- mouvements
    def advance(s, i, k, event_ok=True):
        if s.winner is not None or k <= 0: return
        old = s.pos[i]; new = old + k
        for c in TOK:
            if old < c <= new and c in s.tokens:
                t = s.tokens[c]
                if t == 'L':
                    s.armor[i] += 1; del s.tokens[c]
                else:  # relique : reste posée tant que personne ne la prend
                    if not s.relic[i]:
                        s.relic[i] = True; del s.tokens[c]
        if new >= 33:
            if s.relic[i] or s.armor[i] >= 2:
                s.winner = i; s.win_by = 'relique' if s.relic[i] else 'armures'; s.pos[i] = 33; return
            new = 32
        s.pos[i] = new

    def want_armor(s, i, sev, kind=''):
        if s.armor[i] == 0: return False
        if s.lv[i] != 2 or not s.cfg['x_armor']: return kind == 'relic' or s.rng.random() < s.cfg['armor_use_p']
        if kind == 'relic': return True
        if s.armor[i] >= 2 and s.pos[i] >= 20: return False
        return sev >= 3

    def power_ok(s, i, name):
        return s.cfg['powers'] and s.hero[i] == name and not s.used[i] and s.pb[i] == 0

    def retreat(s, i, k, kind='move'):
        if k <= 0: return
        if s.in_ev and kind == 'move' and i == s.cur and s.power_ok(i, 'Comique') and s.rng.random() < 0.5:
            s.used[i] = True; return
        if s.want_armor(i, k, kind):
            s.armor[i] -= 1; return
        s.pos[i] = max(0, s.pos[i] - k)

    # ---------- choix des cartes
    def avail(s, i):
        av = [0, 1, 2]
        if s.last[i] is not None and s.genre() == 'Rediffusion':
            av = [s.last[i]]
        elif s.last[i] is not None and (s.cfg['no_repeat'] or s.genre() == 'Flashback'):
            av = [c for c in av if c != s.last[i]]
        if s.block[i] is not None:
            av = [c for c in av if c != s.block[i]] or av
        if i in s.dodge:
            av = [c for c in av if c != s.dodge[i]] or av
        return av

    def dist(s, j, pub):
        if j in pub:
            return {c: (1.0 if c == pub[j] else 0.0) for c in range(3)}
        av = [0, 1, 2]
        if s.last[j] is not None and s.genre() == 'Rediffusion':
            av = [s.last[j]]
        elif s.last[j] is not None and (s.cfg['no_repeat'] or s.genre() == 'Flashback'):
            av = [c for c in av if c != s.last[j]]
        w = {c: (s.hist[j][c] + 1.0 if c in av else 0.0) for c in range(3)}
        t = sum(w.values())
        return {c: w[c] / t for c in range(3)}

    def choose(s, i, pub):
        av = s.avail(i)
        lv = s.lv[i]
        if lv == 0:
            w = [3.0 if c == s.fav[i] else 1.0 for c in av]
            return s.rng.choices(av, w)[0]
        if lv == 1:
            return s.rng.choice(av)
        if (not s.cfg['x_cards']) or s.rng.random() < s.cfg['eps']:
            return s.rng.choice(av)
        left, right = (i + 1) % s.n, (i - 1) % s.n
        best, bs = [], -9
        for c in av:
            sc = 0
            for j in (left, right):
                d = s.dist(j, pub)
                for x in range(3):
                    sc += d[x] * (1 if beats(c, x) else -1 if beats(x, c) else 0)
            if sc > bs + 1e-9: best, bs = [c], sc
            elif abs(sc - bs) < 1e-9: best.append(c)
        return s.rng.choice(best)

    def prophecy(s, sc):
        others = [j for j in range(s.n) if j != sc]
        if s.lv[sc] != 2 or not s.cfg['x_target']:
            return s.rng.choice(others), s.rng.randrange(3)
        best, bs = None, -1
        for j in others:
            d = s.dist(j, {})
            m = max(d.values())
            score = m + (0.15 if j in s.leader() else 0)
            if score > bs: bs, best = score, j
        d = s.dist(best, {})
        card = max(range(3), key=lambda c: d[c])
        return best, card

    # ---------- événements
    def _events(s, i, act):
        r = s.rng; n = s.n
        _adv = s.advance
        sc_ = s.cfg['ev_scale']
        def adv(j, k, _a=_adv):
            k2 = k * sc_
            _a(j, int(k2) + (1 if r.random() < k2 - int(k2) else 0))
        s.advance_ev = adv
        if act == 1:
            k = r.randrange(8)
            if k == 0: s.advance_ev(i, 3)
            elif k in (1, 3, 5): s.advance_ev(i, 2)
            elif k == 2:
                if r.random() < .5: s.armor[i] += 1
                else: s.retreat(i, 2)
            elif k == 4: s.armor[i] += 1
            elif k == 6:
                nxt = [c for c in STAR if c > s.pos[i]]
                s.advance_ev(i, (nxt[0] - s.pos[i]) if nxt else 1)
            else:
                s.advance_ev(i, 2); o = r.choice([j for j in range(n) if j != i]); s.advance_ev(o, 2)
        elif act == 2:
            k = r.randrange(8)
            if k == 0: s.retreat(i, 3)
            elif k == 1: s.retreat(i, 3) if r.random() < .5 else None
            elif k == 2: s.retreat(i, 1) if r.random() < .3 else None
            elif k == 3:
                trade = s.armor[i] >= (2 if s.lv[i] == 2 else 1) and r.random() < .7
                if trade: s.armor[i] -= 1; s.advance_ev(i, 4)
            elif k == 4:
                s.advance_ev(i, 3)
                for o in range(n):
                    if o != i: s.advance_ev(o, 1)
            elif k == 5: s.advance_ev(i, 3)
            elif k == 6:
                for o in range(n):
                    if o != i: s.retreat(o, 1)
            else: s.retreat(i, 2)
        else:
            k = r.randrange(9)
            L = s.leader()
            if k == 0:
                near = [j for j in range(n) if j != i and abs(s.pos[j] - s.pos[i]) <= 6]
                if near:
                    j = max(near, key=lambda q: s.pos[q]) if s.lv[i] == 2 else r.choice(near)
                    if s.pos[j] > s.pos[i]:
                        s.pos[i], s.pos[j] = s.pos[j], s.pos[i]
                    else:
                        s.pos[i], s.pos[j] = s.pos[j], s.pos[i]
            elif k == 1:
                if r.random() < .5: s.retreat(i, 2)
            elif k == 2:
                if r.random() < 1.0 / n: s.retreat(i, 2)
            elif k == 3:
                o = r.choice([j for j in range(n) if j != i]); s.rebond(o)
            elif k == 4:
                for j in L: s.retreat(j, 3)
            elif k == 5:
                m = min(s.pos)
                for j in range(n):
                    if s.pos[j] == m: s.advance_ev(j, 4)
            elif k == 6:
                if i in L: s.advance_ev(i, 2)
                else:
                    j = L[0]; s.pos[i], s.pos[j] = s.pos[j], s.pos[i]
            elif k == 7:
                o = min((j for j in range(n) if j != i), key=lambda q: abs(s.pos[q] - s.pos[i]))
                if r.random() < .5: s.retreat(i, 3)
                else: s.retreat(o, 3)
            else:
                top = max(s.pos)
                for j in range(n):
                    if 0 < top - s.pos[j] <= 3: s.advance_ev(j, 2)

    def events(s, i, act):
        s.in_ev = True; s.cur = i
        try: s._events(i, act)
        finally: s.in_ev = False; s.cur = None

    def rebond(s, i):
        if s.power_ok(i, 'Comique') and s.rng.random() < 0.5:
            s.used[i] = True; return
        k = s.rng.randrange(16)
        sev, kind = 2, ''
        if k in (0, 2, 11, 14): sev = 2
        elif k == 1: sev = 3
        elif k == 3: sev, kind = 4, 'relic'
        elif k == 4: sev = 3
        elif k == 5: sev = 1
        elif k == 6: sev = 2
        elif k == 7: sev = 1.5
        elif k == 8: sev = 2
        elif k == 9: sev = 2.2
        elif k == 10: sev = 1.5
        elif k == 12: sev = 2.5
        elif k == 13: sev = 1.5
        elif k == 15: sev = 0
        if sev > 0 and s.want_armor(i, sev, kind) and k != 12:
            s.armor[i] -= 1; return
        if k in (0, 2, 11, 14): s.retreat_hard(i, 2)
        elif k == 1: s.retreat_hard(i, 3)
        elif k == 3:
            if s.relic[i]: s.relic[i] = False
            else: s.retreat_hard(i, 3)
        elif k == 4: s.skip[i] = True
        elif k == 5: s.pb[i] = 2
        elif k == 6:
            m = min(s.pos)
            if s.pos[i] == m: s.advance(i, 2)
            else:
                j = min((q for q in range(s.n) if s.pos[q] == m))
                s.pos[i], s.pos[j] = s.pos[j], s.pos[i]
        elif k == 7: s.block[i] = COUP
        elif k == 8: s.half[i] = True
        elif k == 9: s.retreat_hard(i, 4 if s.rng.random() < 1 / 3 else 1)
        elif k == 10: s.block[i] = s.rng.randrange(3)
        elif k == 12:
            if s.armor[i] > 0: s.armor[i] -= 1
            else: s.retreat_hard(i, 2)
        elif k == 13: s.retreat_hard(i, 1); s.open_next[i] = True
        elif k == 15:
            for o in range(s.n):
                if o != i: s.advance(o, 1)

    def retreat_hard(s, i, k):
        s.pos[i] = max(0, s.pos[i] - k)

    # ---------- une manche
    def play_round(s, sc):
        n, cfg, rng = s.n, s.cfg, s.rng
        g = s.genre()
        t, pc = s.prophecy(sc)
        s.dodge = {}
        if cfg['powers']:
            for i in range(n):
                if s.power_ok(i, 'Strategue') and t == i:
                    s.dodge[i] = pc; s.used[i] = True
        pub = {}
        L = s.leader()
        order = [(sc + k) % n for k in range(n)]
        if len(L) == 1:
            srt = sorted(s.pos, reverse=True)
            if srt[0] - srt[1] >= 2 and srt[0] > 5:
                pub[L[0]] = None
        for i in order:
            if s.open_next[i]: pub[i] = None
        cards = [None] * n
        for i in list(pub):
            c = s.choose(i, {k: v for k, v in pub.items() if v is not None}); cards[i] = c; pub[i] = c
        for i in order:
            if cards[i] is None:
                cards[i] = s.choose(i, {k: v for k, v in pub.items() if v is not None})
        for i in range(n):
            s.open_next[i] = False
            s.block[i] = None
        # lecture
        if cards[t] == pc:
            s.advance(sc, cfg['right_bonus'])
            if s.winner is not None: return
            s.rebond(t)
        else:
            s.armor[t] += 1
            s.retreat(sc, cfg['wrong_pen'])
        for i in range(n):
            s.hist[i][cards[i]] += 1
            s.last[i] = cards[i]
        if cfg['powers']:
            for i in range(n):
                if s.power_ok(i, 'Maitre'):
                    if s.lv[i] == 2:
                        if t in ((i + 1) % n, (i - 1) % n):
                            x = cards[t]
                            cur = 1 if beats(cards[i], x) else -1 if beats(x, cards[i]) else 0
                            if cur <= 0:
                                alts = [c for c in range(3) if beats(c, x)]
                                if alts: cards[i] = alts[0]; s.last[i] = cards[i]; s.used[i] = True
                    elif rng.random() < 0.15:
                        cards[i] = rng.choice([c for c in range(3) if c != cards[i]]); s.last[i] = cards[i]; s.used[i] = True
        # duels
        for k in range(n):
            a = order[k]; b = (a + 1) % n
            ca, cb = cards[a], cards[b]
            if ca == cb:
                if g == 'Romance':
                    s.advance(a, 2); s.advance(b, 2)
                    if s.winner is not None: return
                continue
            w, l, cw = (a, b, ca) if beats(ca, cb) else (b, a, cb)
            rec = cfg['recoil']
            if g == 'Plage': rec = 1
            if g == 'Tournoi' and l in s.leader(): rec = cfg['recoil'] + 1
            if g == 'Shonen' and cw == COUP: rec = cfg['recoil'] + 2
            hurl = False
            if s.power_ok(l, 'Hurleur') and (s.lv[l] != 2 or s.relic[l] or s.pos[l] >= 14):
                s.used[l] = True; hurl = True
            if not hurl:
                s.retreat(l, rec, 'duel')
                if cw == COUP and s.relic[l] and not s.relic[w]:
                    s.relic[l] = False; s.relic[w] = True
            if cfg['powers'] and s.hero[l] == 'Rival':
                s.retreat(w, 1, 'duel')
        # course
        for k in range(n):
            i = order[k]
            if cfg['powers']:
                if s.power_ok(i, 'Artichaut'):
                    cand = [j for j in range(n) if 1 <= s.pos[j] - s.pos[i] <= 3]
                    if cand and ((s.lv[i] == 2 and s.pos[i] >= 18) or (s.lv[i] != 2 and rng.random() < 0.25)):
                        j = max(cand, key=lambda q: s.pos[q]); s.pos[i], s.pos[j] = s.pos[j], s.pos[i]; s.used[i] = True
                if s.power_ok(i, 'Traitre') and not s.relic[i]:
                    hold = [j for j in range(n) if s.relic[j] and j != i]
                    if hold and ((s.lv[i] == 2 and s.pos[i] >= 18) or (s.lv[i] != 2 and rng.random() < 0.25)):
                        j = max(hold, key=lambda q: s.pos[q]); s.relic[j] = False; s.relic[i] = True; s.used[i] = True
            d = rng.randint(1, 6)
            if s.skip[i]: d = 0; s.skip[i] = False
            elif s.half[i]: d = (d + 1) // 2; s.half[i] = False
            before = s.pos[i]
            s.advance(i, d)
            if s.winner is not None: return
            p = s.pos[i]
            if p in STAR and p != before:
                s.events(i, 1 if p <= 11 else 2 if p <= 23 else 3)
                if s.winner is not None: return

    def run(s):
        sc = s.rng.randrange(s.n)
        while s.winner is None and s.rounds < s.cfg['max_rounds']:
            s.play_round(sc)
            for q in range(s.n):
                if s.pb[q] > 0: s.pb[q] -= 1
            s.rounds += 1
            sc = (sc + 1) % s.n
        return s.winner


def batch(levels, N, seed=1, **over):
    cfg = dict(DEFAULT); cfg.update(over)
    rng = random.Random(seed)
    wins = Counter(); rounds = 0; relic = 0; done = 0; ha = Counter(); hw = Counter()
    for _ in range(N):
        lv = levels[:]
        rng.shuffle(lv)
        g = Game(lv, rng, cfg)
        w = g.run()
        if w is None: continue
        for h in g.hero: ha[h] += 1
        hw[g.hero[w]] += 1
        done += 1; rounds += g.rounds; relic += g.win_by == 'relique'
        wins[lv[w]] += 1
        wins[('seat', w)] += 1
    return dict(N=done, wins=wins, rounds=rounds / max(done, 1), relic=relic / max(done, 1), levels=levels, ha=ha, hw=hw)


def share(res, lv):
    """taux de victoire du niveau lv, comparé à sa part équitable"""
    cnt = res['levels'].count(lv)
    if cnt == 0: return None
    p = res['wins'][lv] / res['N']
    fair = cnt / len(res['levels'])
    return p, fair, (p / fair)


START_V05 = {'Artichaut': 1, 'Hurleur': 1, 'Rival': 2, 'Strategue': 2, 'Maitre': 3, 'Traitre': 3, 'Comique': 3}
CAL = dict(armor_use_p=0.15, ev_scale=0.4)            # calibré sur la durée et la part de victoires par Relique de la v0.3
V05 = dict(no_repeat=True, right_bonus=3, wrong_pen=2, redif=True, start=START_V05)

if __name__ == '__main__':
    # python3 simulateur_maitrise.py   (environ 1 minute)
    cfg = dict(CAL); cfg.update(V05)
    n = 5
    a = batch([2] + [0] * (n - 1), 3000, seed=1, **cfg)
    b = batch([2] + [1] * (n - 1), 3000, seed=2, **cfg)
    d = batch([1] * n, 3000, seed=3, **cfg)
    print("v0.5, 5 joueurs : expert/prévisibles x%.2f, expert/hasard x%.2f, %.1f manches, Relique %.0f%%" % (
        a['wins'][2] / a['N'] * n, b['wins'][2] / b['N'] * n, d['rounds'], d['relic'] * 100))
    r = batch([1] * n, 6000, seed=4, **cfg)
    print("force des héros (1,00 = équilibré, joueurs au hasard) :")
    for h in START_V05:
        print("  %-10s x%.2f" % (h, r['hw'][h] / r['ha'][h] * n))
