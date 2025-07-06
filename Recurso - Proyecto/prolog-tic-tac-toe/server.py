from flask import Flask, jsonify, request, Response
from flask import send_from_directory
from prolog_bridge import make_move, check_is_winner

app = Flask(__name__)

@app.route("/")
def index():
    """
    Index page of server, returns index.html with proper encoding.
    """
    with open("index.html", "r", encoding='utf-8') as f_obj:
        html_content = f_obj.read()
    
    # Crear una respuesta con el charset correcto
    return Response(html_content, mimetype='text/html; charset=utf-8')

# ... el resto de tus rutas ...
@app.route('/assets/<path:path>')
def serve_assets(path):
    return send_from_directory('assets', path)

@app.route("/api/is_winner", methods=["POST"])
def is_winner():
    """
    API function to expose checking for a winner in XO board.
    Call receives JSON with board + player's symbol and returns result.
    """
    data = request.get_json()
    winner_result = check_is_winner(data.get("board"), data.get("symbol"))
    return jsonify({"result": winner_result})


@app.route("/api/make_move", methods=["POST"])
def make_move_api():
    """
    API function to expose making a XO move.
    Call receives json with board and returns new board with move.
    """
    data = request.get_json()
    new_board = make_move(data.get("board"), data.get("difficultyLevel"), data.get("symbol"))
    return jsonify({"board": new_board})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
