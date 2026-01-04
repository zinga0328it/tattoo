from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from tetris import TetrisGame
import json

app = Flask(__name__)
CORS(app)

game = TetrisGame()

@app.route('/')
def index():
    return send_from_directory('.', 'index_tetris.html')

@app.route('/style_tetris.css')
def style():
    return send_from_directory('.', 'style_tetris.css')

@app.route('/script_tetris.js')
def script():
    return send_from_directory('.', 'script_tetris.js')

@app.route('/new_game', methods=['POST'])
def new_game():
    global game
    game = TetrisGame()
    game.new_piece()
    return jsonify(game.get_state())

@app.route('/get_state', methods=['GET'])
def get_state():
    return jsonify(game.get_state())

@app.route('/ai_move', methods=['POST'])
def ai_move():
    if not game.game_over and game.current_piece:
        game.ai_move()
    return jsonify(game.get_state())

@app.route('/manual_move', methods=['POST'])
def manual_move():
    data = request.get_json()
    action = data.get('action')

    if game.game_over:
        return jsonify({'error': 'Game over'}), 400

    if action == 'left':
        game.move_piece(-1, 0)
    elif action == 'right':
        game.move_piece(1, 0)
    elif action == 'down':
        if not game.move_piece(0, 1):
            game.drop_piece()
    elif action == 'rotate':
        game.rotate_current_piece()
    elif action == 'drop':
        game.drop_piece()

    return jsonify(game.get_state())

if __name__ == '__main__':
    print("Starting Tetris server")
    try:
        app.run(host='127.0.0.1', port=5002, debug=False)
    except Exception as e:
        print(f"Error starting server: {e}")
