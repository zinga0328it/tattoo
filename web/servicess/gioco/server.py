from flask import Flask, request, jsonify
# from flask_cors import CORS
from main import mossa_macchina

app = Flask(__name__)
# CORS(app)  # Abilita CORS per tutte le rotte

@app.route('/move', methods=['POST'])
def handle_move():
    print("Handling move")
    data = request.get_json()
    board = data.get('board')

    if not board:
        return jsonify({'error': 'Board not provided'}), 400

    try:
        # La funzione mossa_macchina si aspetta una lista di liste 3x3
        grid = [
            board[0:3],
            board[3:6],
            board[6:9]
        ]
        move = mossa_macchina(grid)
        if move:
            print("Move found")
            return jsonify({'row': move[0], 'col': move[1]})
        else:
            print("No move")
            return jsonify({'message': 'No move found or game over'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting server")
    try:
        app.run(host='127.0.0.1', port=5001, debug=False)
    except Exception as e:
        print(f"Error starting server: {e}")
