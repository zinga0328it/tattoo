import random
import copy

# Definizione dei tetromini
SHAPES = {
    'I': [[1, 1, 1, 1]],
    'O': [[1, 1], [1, 1]],
    'T': [[0, 1, 0], [1, 1, 1]],
    'S': [[0, 1, 1], [1, 1, 0]],
    'Z': [[1, 1, 0], [0, 1, 1]],
    'J': [[1, 0, 0], [1, 1, 1]],
    'L': [[0, 0, 1], [1, 1, 1]]
}

class TetrisGame:
    def __init__(self, width=10, height=20):
        self.width = width
        self.height = height
        self.grid = [[0] * width for _ in range(height)]
        self.current_piece = None
        self.current_pos = [0, width // 2 - 1]
        self.next_pieces = [random.choice(list(SHAPES.keys())) for _ in range(5)]
        self.score = 0
        self.lines = 0
        self.game_over = False

    def new_piece(self):
        if not self.next_pieces:
            self.next_pieces = [random.choice(list(SHAPES.keys())) for _ in range(5)]
        self.current_piece = self.next_pieces.pop(0)
        self.current_pos = [0, self.width // 2 - 1]
        if self.check_collision(self.current_piece, self.current_pos):
            self.game_over = True

    def rotate_piece(self, piece):
        return [list(reversed(col)) for col in zip(*piece)]

    def check_collision(self, piece, pos):
        for y, row in enumerate(piece):
            for x, cell in enumerate(row):
                if cell:
                    grid_x = pos[1] + x
                    grid_y = pos[0] + y
                    if (grid_x < 0 or grid_x >= self.width or
                        grid_y >= self.height or
                        (grid_y >= 0 and self.grid[grid_y][grid_x])):
                        return True
        return False

    def place_piece(self, piece, pos):
        for y, row in enumerate(piece):
            for x, cell in enumerate(row):
                if cell:
                    grid_y = pos[0] + y
                    grid_x = pos[1] + x
                    if 0 <= grid_y < self.height and 0 <= grid_x < self.width:
                        self.grid[grid_y][grid_x] = 1

    def clear_lines(self):
        lines_cleared = 0
        new_grid = []
        for row in self.grid:
            if all(cell for cell in row):
                lines_cleared += 1
            else:
                new_grid.append(row)
        # Aggiungi righe vuote in cima
        while len(new_grid) < self.height:
            new_grid.insert(0, [0] * self.width)
        self.grid = new_grid
        self.lines += lines_cleared
        self.score += lines_cleared * 100 * (lines_cleared if lines_cleared > 1 else 1)

    def move_piece(self, dx, dy):
        new_pos = [self.current_pos[0] + dy, self.current_pos[1] + dx]
        if not self.check_collision(self.current_piece, new_pos):
            self.current_pos = new_pos
            return True
        return False

    def rotate_current_piece(self):
        rotated = self.rotate_piece(self.current_piece)
        if not self.check_collision(rotated, self.current_pos):
            self.current_piece = rotated
            return True
        return False

    def drop_piece(self):
        while self.move_piece(0, 1):
            pass
        self.place_piece(self.current_piece, self.current_pos)
        self.clear_lines()
        self.new_piece()

    def get_possible_moves(self, piece):
        moves = []
        for rotation in range(4):
            rotated_piece = piece
            for _ in range(rotation):
                rotated_piece = self.rotate_piece(rotated_piece)

            for x in range(-3, self.width + 3):
                pos = [0, x]
                if not self.check_collision(rotated_piece, pos):
                    # Trova la posizione più bassa
                    while not self.check_collision(rotated_piece, [pos[0] + 1, pos[1]]):
                        pos[0] += 1
                    moves.append((pos, rotated_piece))
        return moves

    def evaluate_position(self, grid):
        # Calcola altezze colonne
        heights = []
        for x in range(self.width):
            height = 0
            for y in range(self.height):
                if grid[y][x]:
                    height = self.height - y
                    break
            heights.append(height)

        # Calcola buchi
        holes = 0
        for x in range(self.width):
            found_block = False
            for y in range(self.height):
                if grid[y][x]:
                    found_block = True
                elif found_block:
                    holes += 1

        # Altezza massima
        max_height = max(heights) if heights else 0

        # Deviazione altezze
        avg_height = sum(heights) / len(heights)
        height_diff = sum(abs(h - avg_height) for h in heights)

        # Linee complete
        complete_lines = sum(1 for row in grid if all(cell for cell in row))

        # Punteggio
        score = (-0.5 * max_height) + (-0.3 * holes) + (10 * complete_lines) + (-0.2 * height_diff)
        return score

    def ai_move(self):
        if not self.current_piece:
            return

        best_score = float('-inf')
        best_move = None

        for pos, piece in self.get_possible_moves(SHAPES[self.current_piece]):
            # Simula il posizionamento
            temp_grid = copy.deepcopy(self.grid)
            for y, row in enumerate(piece):
                for x, cell in enumerate(row):
                    if cell:
                        grid_y = pos[0] + y
                        grid_x = pos[1] + x
                        if 0 <= grid_y < self.height and 0 <= grid_x < self.width:
                            temp_grid[grid_y][grid_x] = 1

            # Simula cancellazione linee
            lines_cleared = 0
            temp_grid_clean = []
            for row in temp_grid:
                if all(cell for cell in row):
                    lines_cleared += 1
                else:
                    temp_grid_clean.append(row)
            while len(temp_grid_clean) < self.height:
                temp_grid_clean.insert(0, [0] * self.width)

            score = self.evaluate_position(temp_grid_clean) + (lines_cleared * 50)

            if score > best_score:
                best_score = score
                best_move = pos

        if best_move:
            self.current_pos = best_move
            self.drop_piece()

    def get_state(self):
        return {
            'grid': self.grid,
            'current_piece': self.current_piece,
            'current_pos': self.current_pos,
            'next_pieces': self.next_pieces,
            'score': self.score,
            'lines': self.lines,
            'game_over': self.game_over
        }
