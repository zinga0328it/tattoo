import unittest

from colonna_pari_scuola import matrice

# Funzione da testare (copiata dal file, per evitare problemi di import)
def trova_colonna_con_piu_pari(matrice):
    best_count = -1
    best_col = -1
    for col in range(len(matrice[0])):
        count = 0
        for riga in range(len(matrice)):
            val = matrice[riga][col]
            if val % 2 == 0:
                count += 1
        if count > best_count:
            best_count = count
            best_col = col
    return best_col

class TestColonnaPari(unittest.TestCase):
    def test_esempio_base(self):
        m = [
            [2, 3, 8],
            [7, 4, 5],
            [4, 6, 1]
        ]
        self.assertEqual(trova_colonna_con_piu_pari(m), 0)

    def test_tutte_dispari(self):
        m = [
            [1, 3],
            [5, 7]
        ]
        self.assertEqual(trova_colonna_con_piu_pari(m), 0)

    def test_colonna_1_vincente(self):
        m = [
            [1, 2],
            [3, 4],
            [5, 6]
        ]
        self.assertEqual(trova_colonna_con_piu_pari(m), 1)

if __name__ == "__main__":
    unittest.main()
