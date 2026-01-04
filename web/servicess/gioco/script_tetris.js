const API_BASE = 'http://127.0.0.1:5002';

let gameState = null;
let gameInterval = null;

document.addEventListener('DOMContentLoaded', function() {
    initializeGame();
    setupEventListeners();
});

function initializeGame() {
    fetch(`${API_BASE}/new_game`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            gameState = data;
            updateDisplay();
        })
        .catch(error => console.error('Error initializing game:', error));
}

function setupEventListeners() {
    // Pulsanti principali
    document.getElementById('new-game-btn').addEventListener('click', newGame);
    document.getElementById('ai-play-btn').addEventListener('click', startAIPlay);
    document.getElementById('ai-step-btn').addEventListener('click', aiStep);

    // Controlli manuali
    document.getElementById('left-btn').addEventListener('click', () => manualMove('left'));
    document.getElementById('right-btn').addEventListener('click', () => manualMove('right'));
    document.getElementById('down-btn').addEventListener('click', () => manualMove('down'));
    document.getElementById('rotate-btn').addEventListener('click', () => manualMove('rotate'));
    document.getElementById('drop-btn').addEventListener('click', () => manualMove('drop'));

    // Controlli tastiera
    document.addEventListener('keydown', handleKeyPress);
}

function handleKeyPress(event) {
    switch(event.key.toLowerCase()) {
        case 'a':
        case 'arrowleft':
            event.preventDefault();
            manualMove('left');
            break;
        case 'd':
        case 'arrowright':
            event.preventDefault();
            manualMove('right');
            break;
        case 's':
        case 'arrowdown':
            event.preventDefault();
            manualMove('down');
            break;
        case 'r':
            event.preventDefault();
            manualMove('rotate');
            break;
        case 'f':
            event.preventDefault();
            manualMove('drop');
            break;
    }
}

function newGame() {
    stopAIPlay();
    initializeGame();
}

function startAIPlay() {
    if (gameInterval) return; // Già in esecuzione

    gameInterval = setInterval(() => {
        if (gameState && !gameState.game_over) {
            aiStep();
        } else {
            stopAIPlay();
        }
    }, 500); // Ogni 500ms
}

function stopAIPlay() {
    if (gameInterval) {
        clearInterval(gameInterval);
        gameInterval = null;
    }
}

function aiStep() {
    fetch(`${API_BASE}/ai_move`, { method: 'POST' })
        .then(response => response.json())
        .then(data => {
            gameState = data;
            updateDisplay();
        })
        .catch(error => console.error('Error AI move:', error));
}

function manualMove(action) {
    fetch(`${API_BASE}/manual_move`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: action })
    })
    .then(response => response.json())
    .then(data => {
        gameState = data;
        updateDisplay();
    })
    .catch(error => console.error('Error manual move:', error));
}

function updateDisplay() {
    if (!gameState) return;

    updateGrid();
    updateScore();
    updateNextPiece();
    updateGameOver();
}

function updateGrid() {
    const gridElement = document.getElementById('grid');
    gridElement.innerHTML = '';

    for (let y = 0; y < 20; y++) {
        for (let x = 0; x < 10; x++) {
            const cell = document.createElement('div');
            cell.className = 'cell';

            // Controlla se c'è un blocco fisso
            if (gameState.grid[y][x]) {
                cell.classList.add('filled');
            }

            // Controlla se è parte del pezzo corrente
            if (gameState.current_piece && gameState.current_pos) {
                const piece = getShape(gameState.current_piece);
                const pieceY = y - gameState.current_pos[0];
                const pieceX = x - gameState.current_pos[1];

                if (pieceY >= 0 && pieceY < piece.length &&
                    pieceX >= 0 && pieceX < piece[0].length &&
                    piece[pieceY][pieceX]) {
                    cell.classList.add('current');
                }
            }

            gridElement.appendChild(cell);
        }
    }
}

function updateScore() {
    document.getElementById('score').textContent = gameState.score;
    document.getElementById('lines').textContent = gameState.lines;
}

function updateNextPiece() {
    const nextPieceElement = document.getElementById('next-piece-display');
    nextPieceElement.innerHTML = '';

    if (gameState.next_pieces && gameState.next_pieces.length > 0) {
        const nextPiece = getShape(gameState.next_pieces[0]);

        for (let y = 0; y < 4; y++) {
            for (let x = 0; x < 4; x++) {
                const cell = document.createElement('div');
                cell.className = 'next-cell';

                if (y < nextPiece.length && x < nextPiece[0].length && nextPiece[y][x]) {
                    cell.classList.add('filled');
                }

                nextPieceElement.appendChild(cell);
            }
        }
    }
}

function updateGameOver() {
    const gameOverElement = document.getElementById('game-over');
    if (gameState.game_over) {
        gameOverElement.classList.remove('hidden');
        stopAIPlay();
    } else {
        gameOverElement.classList.add('hidden');
    }
}

function getShape(pieceType) {
    const shapes = {
        'I': [[1, 1, 1, 1]],
        'O': [[1, 1], [1, 1]],
        'T': [[0, 1, 0], [1, 1, 1]],
        'S': [[0, 1, 1], [1, 1, 0]],
        'Z': [[1, 1, 0], [0, 1, 1]],
        'J': [[1, 0, 0], [1, 1, 1]],
        'L': [[0, 0, 1], [1, 1, 1]]
    };
    return shapes[pieceType] || [];
}
