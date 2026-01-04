# Programma "tipo scuola" per trovare la colonna con più numeri pari
# Spiegazione passo-passo, come in classe!

matrice = [
    [2, 3, 8],
    [7, 4, 5],
    [4, 6, 1]
]

best_count = -1
best_col = -1

for col in range(len(matrice[0])):
    print(f"\nControllo la colonna {col}:")
    count = 0
    for riga in range(len(matrice)):
        val = matrice[riga][col]
        if val % 2 == 0:
            print(f"  {val} è pari ✅")
            count += 1
        else:
            print(f"  {val} è dispari ❌")
    print(f"Totale numeri pari nella colonna {col} = {count}")
    if count > best_count:
        best_count = count
        best_col = col
        print(f"👉 Nuova colonna migliore trovata: {col} (con {count} pari)")

print(f"\nRisultato finale: la colonna con più numeri pari è {best_col}")
