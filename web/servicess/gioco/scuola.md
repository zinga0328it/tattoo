# Progetto Tetris - Spiegazione Scolastica

## Che cos'è Tetris?

Tetris è un videogioco puzzle classico inventato da Alexey Pajitnov nel 1984. Il nome "Tetris" viene dalla parola greca "tetra" (che significa quattro) e "tennis" (il gioco preferito del creatore).

Il gioco consiste nel posizionare pezzi geometrici chiamati "tetromini" che cadono dall'alto in una griglia rettangolare. L'obiettivo è completare linee orizzontali per farle scomparire e guadagnare punti, prima che la griglia si riempia.

## Come Funziona il Gioco

### I Tetromini
I pezzi sono formati da 4 quadrati uniti in diverse forme:
- **I**: Una linea retta (4 quadrati)
- **O**: Un quadrato (2x2)
- **T**: Una T
- **S** e **Z**: Forme a zigzag
- **J** e **L**: Forme ad L

Ogni pezzo può essere ruotato di 90 gradi e spostato lateralmente.

### La Griglia
- Dimensioni tipiche: 10 colonne x 20 righe
- I pezzi cadono dall'alto verso il basso
- Quando una linea orizzontale è completa, scompare e le linee sopra scendono

### Punteggio
- Più linee si completano contemporaneamente, più punti si guadagnano
- Il gioco accelera man mano che si progrediscono livelli
- Game over quando i pezzi raggiungono la cima della griglia

## L'Intelligenza Artificiale nel Tetris

Nel nostro progetto, implementiamo un'AI che gioca automaticamente a Tetris. L'AI deve prendere decisioni intelligenti per:

1. **Posizionare i pezzi**: Scegliere la posizione e rotazione migliore
2. **Ottimizzare lo spazio**: Creare buchi il più possibile piccoli
3. **Completare linee**: Massimizzare il numero di linee cancellate
4. **Pianificare**: Considerare l'impatto dei pezzi futuri

### Algoritmi Utilizzati

#### 1. Valutazione della Griglia
L'AI calcola un "punteggio" per ogni possibile posizionamento del pezzo:

- **Altezze delle colonne**: Mantenere colonne di altezza simile
- **Buchi**: Evitare spazi vuoti sotto i pezzi
- **Linee complete**: Premiare posizionamenti che creano linee piene
- **Altezza massima**: Evitare colonne troppo alte

#### 2. Ricerca ad Albero
L'AI simula diverse possibilità:
- Prova tutte le rotazioni possibili del pezzo
- Prova tutte le posizioni orizzontali
- Valuta il risultato per ogni combinazione
- Sceglie la mossa con il punteggio più alto

#### 3. Algoritmo Genetico (Opzionale)
Per AI più avanzate, si possono usare algoritmi genetici:
- Genera molte "strategie" diverse
- Le fa competere tra loro
- Le migliori si "riproducono" creando versioni ibride
- Dopo molte generazioni, emerge la strategia ottimale

## Implementazione Tecnica

### Linguaggi e Tecnologie
- **Python**: Per la logica di gioco e AI
- **Pygame**: Libreria per grafica e input
- **NumPy**: Per calcoli matriciali efficienti

### Struttura del Codice

```python
class TetrisAI:
    def __init__(self):
        self.grid = [[0] * 10 for _ in range(20)]  # Griglia 10x20

    def evaluate_position(self, piece, x, y, rotation):
        # Simula il posizionamento
        # Calcola punteggio basato su:
        # - Altezze colonne
        # - Numero buchi
        # - Linee complete
        # - Altezza massima
        return score

    def find_best_move(self, current_piece, next_pieces):
        best_score = -inf
        best_move = None

        for rotation in range(4):
            for x in range(10):
                if self.can_place(piece, x, rotation):
                    score = self.evaluate_position(piece, x, 0, rotation)
                    if score > best_score:
                        best_score = score
                        best_move = (x, rotation)

        return best_move
```

### Formule Matematiche

#### Calcolo dell'Altezza delle Colonne
```
altezza_colonna[j] = max(i) dove grid[i][j] != 0
```

#### Conteggio dei Buchi
```
buchi = sum(1 for cella vuota sotto una piena nella stessa colonna)
```

#### Punteggio Totale
```
punteggio = w1 * (-altezza_max) + w2 * (-buchi) + w3 * linee_complete + w4 * (-deviazione_altezze)
```

Dove w1, w2, w3, w4 sono pesi da ottimizzare.

## Concetti di Programmazione Imparati

### Algoritmi e Strutture Dati
- **Matrici**: Rappresentazione della griglia di gioco
- **Ricerca**: Trovare la migliore mossa tra molte possibilità
- **Ottimizzazione**: Bilanciare velocità e qualità delle decisioni

### Intelligenza Artificiale
- **Heuristica**: Regole pratiche per prendere decisioni
- **Valutazione**: Assegnare punteggi agli stati del gioco
- **Simulazione**: Prevedere il futuro del gioco

### Matematica Applicata
- **Statistica**: Analisi delle altezze e distribuzioni
- **Combinatoria**: Numero di possibili posizionamenti dei pezzi
- **Ottimizzazione**: Trovare i migliori parametri per l'AI

## Sfide e Soluzioni

### Problema: Troppi Possibili Posizionamenti
**Soluzione**: Limitare la ricerca alle rotazioni e posizioni valide, usare pruning per scartare mosse chiaramente cattive.

### Problema: Valutare la "Qualità" di una Posizionamento
**Soluzione**: Usare una combinazione di fattori con pesi calcolati empiricamente o tramite machine learning.

### Problema: Prestazioni in Tempo Reale
**Soluzione**: Ottimizzare il codice, precalcolare dove possibile, usare algoritmi efficienti.

## Conclusioni

Il progetto Tetris con AI dimostra come:
- I computer possono giocare a giochi complessi meglio degli umani
- Gli algoritmi possono simulare il ragionamento strategico
- La programmazione combina matematica, logica e creatività
- L'AI può essere applicata a problemi del mondo reale (ottimizzazione, pianificazione)

Questo progetto è un ottimo esempio di come l'informatica moderna può rendere "intelligenti" macchine per compiti che richiedono strategia e pianificazione.

---

*Preparato per la presentazione scolastica - Progetto Tetris con AI*
