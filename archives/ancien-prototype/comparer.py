# Compare les règles historiques v0.2 et la version de travail v0.3.
import random, statistics
from multiprocessing import Pool
from simulateur import *

def tache(args):
    version, n = args
    R = Regles() if version == "v0.2" else regles_v03()
    r = resume(R, n, 20000)
    # coût de la timidité : moitié timides (0,1), moitié acteurs (0,95)
    Rt = Regles(p_scene=[0.1, 0.95] * 4) if version == "v0.2" else regles_v03(p_scene=[0.1, 0.95] * 4)
    rng = random.Random(77 + n); tim = 0; nb = 8000
    for _ in range(nb):
        p = jouer(n, Rt, rng)
        if p.gagnant and p.gagnant.i % 2 == 0: tim += 1
    nt = (n + 1) // 2
    attendu = 100 * nt / n
    return version, n, r, 100 * tim / nb, attendu

if __name__ == "__main__":
    taches = [(v, n) for v in ("v0.2", "v0.3") for n in (4, 5, 6, 7)]
    with Pool() as p:
        res = p.map(tache, taches)
    for v in ("v0.2", "v0.3"):
        print("=====", v)
        for (vv, n, r, tim, att) in res:
            if vv != v: continue
            hmax = max(abs(x / r["ideal_%"] - 1) for x in r["heros_%"]) * 100
            smax = max(abs(x - r["ideal_%"]) for x in r["siege_%"])
            print("%d joueurs | manches %.1f (p10 %d p90 %d) | bloqué %.1f %% | Relique %.0f %% | remontada %.0f %% | retournements %.1f | photo-finish %.0f %% | héros écart max %.0f %% | siège écart max %.1f pt | timides %.1f %% (attendu %.1f)" % (
                n, r["manches_moy"], r["manches_p10"], r["manches_p90"], r["bloque_%"], r["relique_%"], r["remontada_%"], r["retournements"], r["photo_finish_%"], hmax, smax, tim, att))
