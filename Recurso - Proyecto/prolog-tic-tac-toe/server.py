# Importación de librerías
from flask import Flask, jsonify, request, Response
from flask import send_from_directory
from prolog_bridge import make_move, check_is_winner

# Inicialización de la aplicación Flask
app = Flask(__name__)

# --------------------------------------------------
# Rutas principales
# --------------------------------------------------

# Ruta para servir la página principal
@app.route("/")
def index():
    """Sirve el archivo index.html como página principal"""
    with open("index.html", "r", encoding='utf-8') as f_obj:
        html_content = f_obj.read()
    
    return Response(html_content, mimetype='text/html; charset=utf-8')

# Ruta para servir archivos estáticos (CSS, JS, imágenes)
@app.route('/assets/<path:path>')
def serve_assets(path):
    """Entrega archivos estáticos desde el directorio assets"""
    return send_from_directory('assets', path)

# --------------------------------------------------
# API Endpoints
# --------------------------------------------------

# Endpoint para verificar si hay un ganador
@app.route("/api/is_winner", methods=["POST"])
def is_winner():
    """
    Verifica si el jugador actual ha ganado
    Recibe: {board: [], symbol: 'X/O'}
    Devuelve: {result: True/False/None}
    """
    data = request.get_json()
    winner_result = check_is_winner(data.get("board"), data.get("symbol"))
    return jsonify({"result": winner_result})

# Endpoint para realizar un movimiento de la IA
@app.route("/api/make_move", methods=["POST"])
def make_move_api():
    """
    Realiza un movimiento automático de la IA
    Recibe: {board: [], difficultyLevel: int, symbol: 'X/O'}
    Devuelve: {board: []} con el nuevo estado del tablero
    """
    data = request.get_json()
    new_board = make_move(data.get("board"), data.get("difficultyLevel"), data.get("symbol"))
    return jsonify({"board": new_board})

# --------------------------------------------------
# Punto de entrada principal
# --------------------------------------------------
if __name__ == "__main__":
    # Inicia el servidor en modo debug, accesible desde cualquier IP
    app.run(debug=True, host="0.0.0.0")