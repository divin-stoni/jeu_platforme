#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""experiments.py : expériences IA-3 (T2, T4, T6, P07, P09, P10).
Usage : python3 experiments.py <nom> [N]      noms : calib t2 t4 t6 p10 p07 all
Sorties : resultats/<nom>.json
"""
import sys, os, json, time, math, random
from sim import *

SCALE = 1.0


def S(x):
    return max(300, int(x * SCALE))


OUTDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'resultats')
os.makedirs(OUTDIR, exist_ok=True)


def batch(rules, n, N, seed0=0, profs=None, expert_seat_random=False, heroes=None, base_prof=HAS, ex_prof=EXP):
    """Joue N parties. profs : liste de profils par siège, ou None (tous base_prof).
    expert_seat_random : un joueur de profil ex_prof à un siège tiré au hasard, les autres base_prof."""
    a = dict(N=N, done=0, rounds=0, relic=0, pred=[0, 0], duel=[0, 0], duel_ee=[0, 0],
             wins_seat=[0] * n, wins_rel_plume=[0] * n, wins_hero=[0] * 7, app_hero=[0] * 7,
             power=[0] * 7, win_prof=[0] * 3, cnt_prof=[0] * 3, stuck=0, vedette=0, stolen=0,
             door=[0, 0], door_win=[0, 0], genres=[0] * 9, genre_games=[0] * 9,
             ev_games=0, ev_act=[0, 0, 0], ev_distinct=0, ev_total=0,
             ev={e: [0, 0.0, 0.0, 0.0, 0, 0] for e in ALL_EV},   # tirages, Σself, Σautres, Σarmure, parties vues, victoires du tireur
             rounds_list=[], armor_win=0)
    R = rules
    for s in range(N):
        if profs is not None:
            pf = list(profs)
        elif expert_seat_random:
            pf = [base_prof] * n
            pf[s % n] = ex_prof
        else:
            pf = [base_prof] * n
        rng = random.Random(seed0 * 10_000_019 + s)
        g = Game(R, pf, rng, heroes)
        g.run()
        if g.winner < 0:
            a['stuck'] += 1
            continue
        a['done'] += 1
        w = g.winner
        a['rounds'] += g.rnd
        a['rounds_list'].append(g.rnd)
        a['relic'] += (g.win_via == 'relique')
        a['pred'][0] += g.st_pred[0]
        a['pred'][1] += g.st_pred[1]
        a['duel'][0] += g.st_duel[0]
        a['duel'][1] += g.st_duel[1]
        a['duel_ee'][0] += g.st_duel_ee[0]
        a['duel_ee'][1] += g.st_duel_ee[1]
        a['wins_seat'][w] += 1
        a['wins_rel_plume'][(w - g.plume) % n] += 1
        a['wins_hero'][g.hero[w]] += 1
        for q in range(n):
            a['app_hero'][g.hero[q]] += 1
            a['cnt_prof'][pf[q]] += 1
        a['win_prof'][pf[w]] += 1
        for h in range(7):
            a['power'][h] += g.st_power[h]
        a['vedette'] += g.st_vedette
        a['stolen'] += g.st_stolen
        a['door'][0] += g.st_door[0]
        a['door'][1] += g.st_door[1]
        if g.doorchoice[w] is not None:
            a['door_win'][0 if g.doorchoice[w] else 1] += 1
        for ge in g.st_genres:
            a['genres'][ge] += 1
        for ge in set(g.st_genres):
            a['genre_games'][ge] += 1
        a['ev_games'] += 1
        seen = set()
        for (eid, act, p, ds, do, da) in g.st_ev:
            e = a['ev'][eid]
            e[0] += 1
            e[1] += ds
            e[2] += do
            e[3] += da
            if p == w:
                e[5] += 1
            seen.add(eid)
            a['ev_act'][act] += 1
            a['ev_total'] += 1
        for eid in seen:
            a['ev'][eid][4] += 1
        a['ev_distinct'] += len(seen)
    return a


def agg_basic(a, n):
    d = a['done']
    out = dict(parties=d, bloquees=a['stuck'], manches=a['rounds'] / d,
               p10=sorted(a['rounds_list'])[int(0.1 * d)], p90=sorted(a['rounds_list'])[int(0.9 * d)],
               relique=a['relic'] / d,
               propheties=a['pred'][1] / max(1, a['pred'][0]),
               nuls=a['duel'][1] / max(1, a['duel'][0]),
               nuls_ee=(a['duel_ee'][1] / a['duel_ee'][0]) if a['duel_ee'][0] else None,
               vedette_par_partie=a['vedette'] / d,
               vols_par_partie=a['stolen'] / d)
    return out


def ci_rel(k, N, expect):
    """IC95 en relatif (part observée / part attendue) pour un compte k sur N."""
    p = k / N
    se = math.sqrt(max(p * (1 - p), 1e-12) / N)
    return p / expect, 1.96 * se / expect


def save(name, obj):
    with open(os.path.join(OUTDIR, name + '.json'), 'w', encoding='utf-8') as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


# ============================================================ CALIBRATION (T1)
def calib(N=20000):
    N = S(N)
    res = {}
    base05 = dict(stars=STARS_V05, order='scen', genres='stack')
    cfgs = {
        'v0.5 telle qu’écrite (5 j.)': (5, Rules(**base05)),
        'v0.5, 4 j.': (4, Rules(**base05)),
        'v0.5, 6 j.': (6, Rules(**base05)),
        'v0.5, 7 j.': (7, Rules(**base05)),
        'v0.5 sans Genre (première partie)': (5, Rules(**{**base05, 'genres': 'none'})),
        'v0.5 sans Mémoire': (5, Rules(**{**base05, 'memory': 0})),
        'v0.5 sans pouvoirs': (5, Rules(**{**base05, 'powers': False})),
        'v0.5 sans portes': (5, Rules(**{**base05, 'doors': False})),
        'v0.6 (contrat) 4 j.': (4, Rules()),
        'v0.6 (contrat) 5 j.': (5, Rules()),
        'v0.6 (contrat) 6 j.': (6, Rules()),
        'v0.6 (contrat) 7 j.': (7, Rules()),
        'v0.6 sans Genre': (5, Rules(genres='none')),
        'v0.5 + Genres en alternance (D9 seul)': (5, Rules(**{**base05, 'genres': 'alt'})),
        'v0.5 + 12 étoiles (D2 seul)': (5, Rules(**{**base05, 'stars': STARS_D2})),
        'v0.5 + course par le dernier (D12 seul)': (5, Rules(**{**base05, 'order': 'last'})),
    }
    for k, (n, R) in cfgs.items():
        a = batch(R, n, N, seed0=1)
        res[k] = agg_basic(a, n)
        print(k, {x: (round(y, 3) if isinstance(y, float) else y) for x, y in res[k].items()}, flush=True)
    save('calib', res)


# ============================================================ T2 / P09 : équité des sièges
def t2(N5=100000, N7=200000, N46=100000):
    N5, N7, N46 = S(N5), S(N7), S(N46)
    res = {}
    for n, N in ((4, N46), (5, N5), (6, N46), (7, N7)):
        for label, order in (('Scénariste (v0.5)', 'scen'), ('Dernier du parcours (D12)', 'last')):
            for pl, prof in (('hasard', HAS), ('experts', EXP)):
                if pl == 'experts' and n not in (5, 7):
                    continue
                Nn = N if pl == 'hasard' else N // 4
                R = Rules(order=order)
                a = batch(R, n, Nn, seed0=2, base_prof=prof)
                seats = []
                for s in range(n):
                    rel, ci = ci_rel(a['wins_seat'][s], a['done'], 1.0 / n)
                    seats.append([rel, ci])
                relp = []
                for s in range(n):
                    rel, ci = ci_rel(a['wins_rel_plume'][s], a['done'], 1.0 / n)
                    relp.append([rel, ci])
                # chi2 d'uniformité
                exp_ = a['done'] / n
                chi2 = sum((x - exp_) ** 2 / exp_ for x in a['wins_seat'])
                key = '%d joueurs | %s | %s' % (n, label, pl)
                res[key] = dict(n=n, ordre=order, profil=pl, parties=a['done'], sieges=seats,
                                sieges_vs_plume_finale=relp, chi2=chi2, ddl=n - 1,
                                min=min(x[0] for x in seats), max=max(x[0] for x in seats),
                                manches=a['rounds'] / a['done'])
                print(key, 'min %.3f max %.3f chi2 %.1f (ddl %d)' % (res[key]['min'], res[key]['max'], chi2, n - 1), flush=True)
    save('t2', res)


# ============================================================ T4 / P07 : héros
def t4(N5=150000, N7=100000):
    N5, N7 = S(N5), S(N7)
    res = {}
    cfgs = []
    for n, N in ((5, N5), (7, N7)):
        for rev in ('visible', 'hidden'):
            for skill in ('naive', 'smart'):
                cfgs.append((n, N, rev, skill, 'hasard', True))
    cfgs.append((5, N5 // 2, 'hidden', 'smart', 'hasard', False))     # sans pouvoirs
    cfgs.append((7, N7 // 2, 'hidden', 'smart', 'hasard', False))
    cfgs.append((5, N5 // 4, 'hidden', 'smart', 'experts', True))
    for n, N, rev, skill, pl, pw in cfgs:
        R = Rules(reveal=rev, skill=skill, powers=pw)
        a = batch(R, n, N, seed0=4, base_prof=(HAS if pl == 'hasard' else EXP))
        rows = []
        for h in range(7):
            expect = a['app_hero'][h] / n          # victoires attendues = apparitions / n
            k = a['wins_hero'][h]
            rel = k / expect - 1
            ci = 1.96 * math.sqrt(max(1e-12, (1.0 / n) * (1 - 1.0 / n) / a['app_hero'][h])) * n
            rows.append(dict(heros=H_NAMES[h], ecart=rel, ci=ci,
                             usage_pouvoir=a['power'][h] / max(1, a['app_hero'][h])))
        key = '%d joueurs | cartes %s | pouvoirs %s | %s | %s' % (
            n, 'visibles (v0.2)' if rev == 'visible' else 'cachées (D4)',
            skill, 'avec pouvoirs' if pw else 'SANS pouvoirs', pl)
        res[key] = dict(n=n, parties=a['done'], heros=rows, manches=a['rounds'] / a['done'])
        print(key, ' '.join('%s %+.1f%%' % (r['heros'][:4], 100 * r['ecart']) for r in rows), flush=True)
    save('t4', res)


# ============================================================ T6 : Événements vus
def t6(N=60000):
    N = S(N)
    res = {}
    stars = {'8 étoiles (actuel)': STARS_V05, '12 étoiles (D2)': STARS_D2,
             '14 étoiles': (4, 6, 9, 12, 13, 16, 17, 21, 24, 25, 28, 29, 31, 32)}
    for n in (4, 5, 6, 7):
        for lab, st in stars.items():
            if n != 5 and lab == '14 étoiles':
                continue
            R = Rules(stars=st)
            a = batch(R, n, N, seed0=6)
            d = a['done']
            ev = {}
            for e in ALL_EV:
                x = a['ev'][e]
                ev[e] = dict(tirages=x[0] / d, vue=x[4] / d,
                             self=x[1] / max(1, x[0]), autres=x[2] / max(1, x[0]),
                             armure=x[3] / max(1, x[0]), gagne=x[5] / max(1, x[0]))
            res['%d joueurs | %s' % (n, lab)] = dict(
                n=n, parties=d, manches=a['rounds'] / d, par_partie=a['ev_total'] / d,
                actes=[a['ev_act'][i] / d for i in range(3)], distincts=a['ev_distinct'] / d, ev=ev)
            print(n, lab, 'ev/partie %.1f actes %s distincts %.1f manches %.2f' % (
                a['ev_total'] / d, [round(a['ev_act'][i] / d, 1) for i in range(3)], a['ev_distinct'] / d,
                a['rounds'] / d), flush=True)
    save('t6', res)


# ============================================================ P10 : variantes de Mémoire / duels nuls
def p10(N=25000):
    N = S(N)
    res = {}
    variants = {
        'V0 contrat (Mémoire 1 manche, égalité = rien)': dict(),
        'V1 égalité : les deux reculent de 1': dict(tie='both1'),
        'V2 égalité : le plus avancé recule de 1': dict(tie='leader1'),
        'V3 Mémoire sur 2 manches': dict(memory=2),
        'V4 (contrôle) égalité : les deux avancent de 1': dict(tie='both_plus1'),
        'V6 égalité départagée : le plus proche de la Plume gagne': dict(tie='tiebreak'),
        'V7 égalités typées : Coup/Coup −1 les deux, Ruse/Ruse +1 les deux, Garde/Garde rien': dict(tie='typed'),
        'V5 sans Mémoire (rappel)': dict(memory=0),
    }
    matchs = {
        '1 expert vs 4 hasard': ('exp', HAS), '1 expert vs 4 débutants': ('exp', DEB),
        '5 experts': ('all', EXP), '1 débutant vs 4 experts': ('deb_vs_exp', EXP),
        '5 hasard': ('all', HAS),
    }
    for vn, kw in variants.items():
        R = Rules(**kw)
        row = {}
        for mn, (kind, base) in matchs.items():
            if kind == 'exp':
                a = batch(R, 5, N, seed0=10, expert_seat_random=True, base_prof=base)
                share = a['win_prof'][EXP] / a['done']
                row[mn] = dict(part=share, rel=share / 0.2, ci=1.96 * math.sqrt(share * (1 - share) / a['done']) / 0.2)
            elif kind == 'deb_vs_exp':
                a = batch(R, 5, N, seed0=10, expert_seat_random=True, base_prof=EXP, ex_prof=DEB)
                share = a['win_prof'][DEB] / a['done']
                row[mn] = dict(part=share, rel=share / 0.2, ci=1.96 * math.sqrt(share * (1 - share) / a['done']) / 0.2)
            else:
                a = batch(R, 5, N, seed0=10, base_prof=base)
                row[mn] = {}
            row[mn].update(agg_basic(a, 5))
        res[vn] = row
        r5 = row['5 experts']
        print(vn, 'nuls E-E %.3f | 1E vs 4H x%.2f | 1E vs 4D x%.2f | 1D vs 4E x%.2f | manches 5E %.1f | proph 5E %.2f' % (
            r5['nuls'], row['1 expert vs 4 hasard']['rel'], row['1 expert vs 4 débutants']['rel'],
            row['1 débutant vs 4 experts']['rel'], r5['manches'], r5['propheties']), flush=True)
    save('p10', res)


if __name__ == '__main__':
    name = sys.argv[1]
    SCALE = float(sys.argv[2]) if len(sys.argv) > 2 else 1.0
    t0 = time.time()
    f = dict(calib=calib, t2=t2, t4=t4, t6=t6, p10=p10)[name]
    f()
    print('durée %.0f s' % (time.time() - t0))
