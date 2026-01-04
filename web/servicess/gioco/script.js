const X_CLASS = 'x';
const O_CLASS = 'o';
const cellElements = document.querySelectorAll('[data-cell]');
const board = document.getElementById('board');
const winningMessageElement = document.getElementById('winningMessage');
const restartButton = document.getElementById('restartButton');
const winningMessageTextElement = document.querySelector('[data-winning-message-text]');
let oTurn;

startGame();

restartButton.addEventListener('click', startGame);

function startGame() {
    oTurn = false;
    cellElements.forEach(cell => {
        cell.classList.remove(X_CLASS);
        cell.classList.remove(O_CLASS);
        cell.removeEventListener('click', handleClick);
        cell.addEventListener('click', handleClick, { once: true });
    });
    winningMessageElement.classList.remove('show');
}

function handleClick(e) {
    const cell = e.target;
    placeMark(cell, X_CLASS); // Il giocatore è sempre X
    if (checkWin(X_CLASS)) {
        endGame(false);
    } else if (isDraw()) {
        endGame(true);
    } else {
        swapTurns();
        setTimeout(computerMove, 500); // Aggiunge un piccolo ritardo per la mossa del computer
    }
}

function endGame(draw) {
    if (draw) {
        winningMessageTextElement.innerText = 'Pareggio!';
    } else {
        winningMessageTextElement.innerText = `${oTurn ? "Il Computer" : "Tu hai"} vince!`;
    }
    winningMessageElement.classList.add('show');
}

function isDraw() {
    return [...cellElements].every(cell => {
        return cell.classList.contains(X_CLASS) || cell.classList.contains(O_CLASS);
    });
}

function placeMark(cell, currentClass) {
    cell.classList.add(currentClass);
}

function swapTurns() {
    oTurn = !oTurn;
}

async function computerMove() {
    const currentBoard = [...cellElements].map(cell => {
        if (cell.classList.contains(X_CLASS)) return '1'; // Giocatore
        if (cell.classList.contains(O_CLASS)) return '0'; // Computer
        return ' ';
    });

    try {
        const response = await fetch('/gioco/move', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ board: currentBoard }),
        });
        const move = await response.json();
        
        if (move && move.row !== undefined && move.col !== undefined) {
            const cellIndex = move.row * 3 + move.col;
            const cell = cellElements[cellIndex];
            if (!cell.classList.contains(X_CLASS) && !cell.classList.contains(O_CLASS)) {
                placeMark(cell, O_CLASS);
                if (checkWin(O_CLASS)) {
                    endGame(false);
                } else if (isDraw()) {
                    endGame(true);
                } else {
                    swapTurns();
                }
            }
        }
    } catch (error) {
        console.error('Errore durante la chiamata al server:', error);
        winningMessageTextElement.innerText = 'Errore del server!';
        winningMessageElement.classList.add('show');
    }
}

function checkWin(currentClass) {
    const WINNING_COMBINATIONS = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],
        [0, 3, 6], [1, 4, 7], [2, 5, 8],
        [0, 4, 8], [2, 4, 6]
    ];
    return WINNING_COMBINATIONS.some(combination => {
        return combination.every(index => {
            return cellElements[index].classList.contains(currentClass);
        });
    });
}
