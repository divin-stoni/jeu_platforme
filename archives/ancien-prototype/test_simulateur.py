import random
import unittest

from simulateur import (
    BAT,
    CONTRE,
    GARDE,
    COUP,
    RUSE,
    Regles,
    duel,
    jouer,
    regles_v03,
)


class SimulateurTest(unittest.TestCase):
    def test_duel_cycle(self):
        self.assertEqual(duel(COUP, RUSE), 1)
        self.assertEqual(duel(RUSE, GARDE), 1)
        self.assertEqual(duel(GARDE, COUP), 1)
        self.assertEqual(set(BAT), {COUP, GARDE, RUSE})
        self.assertEqual(set(CONTRE), {COUP, GARDE, RUSE})

    def test_partie_terminee_dans_les_deux_versions(self):
        for regles in (Regles(), regles_v03()):
            for joueurs in range(4, 8):
                partie = jouer(joueurs, regles, random.Random(joueurs))
                self.assertIsNotNone(partie.gagnant)
                self.assertEqual(partie.gagnant.pos, regles.but)
                self.assertLessEqual(partie.manche, regles.max_manches)

    def test_nombre_de_joueurs_invalide(self):
        with self.assertRaises(ValueError):
            jouer(3, Regles(), random.Random(1))

    def test_reserve_armures_explicitement_initialisee(self):
        partie = jouer(4, Regles(), random.Random(1))
        self.assertGreaterEqual(partie.reserve_vide, 0)


if __name__ == "__main__":
    unittest.main()
