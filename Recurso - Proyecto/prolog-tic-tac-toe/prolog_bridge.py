from os import path
from typing import List, Optional
from itertools import islice

from pyswip_mt import PrologMT
from jinja2 import Template

BASE_PROLOG_FILE = "tic-tac-toe.pl"
STACK_LIMIT = 4000000000    # Límite de uso de stack para Prolog (~30 segundos de procesamiento)

# Función para obtener el símbolo del otro jugador (X ↔ O)
OTHER_PLAYER_SYMBOL = lambda x: "x" if x == "O" else "o"

prolog = PrologMT()
currently_consulted = ""


def consult_board_size(board_size: int) -> None:
    # Aumentar el límite de stack para evitar errores por tiempo de ejecución
    next(prolog.query(f"set_prolog_flag(stack_limit, {STACK_LIMIT})."))

    # Verificar si el archivo consultado ya corresponde con el tamaño del tablero actual
    global currently_consulted
    sized_file_name = f"{board_size}-{BASE_PROLOG_FILE}"
    if sized_file_name == currently_consulted:
        return

    # Si el archivo aún no existe, lo generamos desde plantilla
    if not path.exists(sized_file_name):
        with open(BASE_PROLOG_FILE, "r") as f_obj:
            template = Template(f_obj.read())

        # Creamos las sentencias dinámicas para ese tamaño de tablero
        board_str = generate_prolog_statements(board_size)
        rendered_template = template.render(board_statements=board_str)
        # Guardamos el nuevo archivo generado
        with open(sized_file_name, "w") as f_obj:
            f_obj.write(rendered_template)

    # Descargamos el archivo anterior y cargamos el nuevo
    next(prolog.query(f'unload_file("{currently_consulted}").'))
    prolog.consult(sized_file_name)
    currently_consulted = sized_file_name

def make_move(board: List[List], difficulty_level: int, player_symbol: str) -> List[List]:
    """
    Recibe el tablero, nivel de dificultad y símbolo del jugador.
    Llama al motor Prolog para calcular la mejor jugada posible.
    """
    prolog_board = board_to_prolog(board)

    consult_board_size(len(board))
    prolog_query = f"miniMax({difficulty_level}, {OTHER_PLAYER_SYMBOL(player_symbol)}, {prolog_board}, BestMove)"
    results = list(prolog.query(prolog_query, maxresult=1))
    if not results:
        raise ValueError(f"No se encontró ningún movimiento válido desde Prolog.\nConsulta: {prolog_query}")
    query_result = results[0].get("BestMove")

    # Convertimos el resultado devuelto por Prolog al formato Python
    result = prolog_to_board(query_result, len(board))
    return result

def check_is_winner(board: List[List], player_symbol: str) -> Optional[bool]:
    """
    Verifica si hay un ganador en el tablero.
    Retorna True si gana el jugador, False si gana la computadora, None si aún no hay ganador.
    """
    prolog_board = board_to_prolog(board)

    # Verificar si el jugador actual ha ganado
    consult_board_size(len(board))
    prolog_query = f"isWinning({player_symbol.lower()}, {prolog_board})."
    query_result = list(prolog.query(prolog_query))
    if len(query_result) > 0:
        return True

    # Verificar si el jugador contrario ha ganado
    prolog_query = f"isWinning({OTHER_PLAYER_SYMBOL(player_symbol)}, {prolog_board})."
    query_result = list(prolog.query(prolog_query))
    if len(query_result) > 0:
        return False

    return None

def board_to_prolog(board: List[List]) -> str:
    """
    Convierte el tablero de Python a formato de lista plano para Prolog.
    """
    board_str_list = []
    for row in board:
        for cell in row:
            board_str_list.append(cell.lower() if cell else "0")

    result = str(board_str_list).replace("'", "")
    return result

def prolog_to_board(board: List, board_size: int) -> List[List]:
    """
    Convierte el tablero devuelto por Prolog al formato de lista de listas en Python.
    """
    board_str_list = ["" if cell == 0 else str(cell).upper() for cell in board]

    iterator = iter(board_str_list)
    result = [list(islice(iterator, board_size)) for _ in range(board_size)]
    return result

def generate_prolog_statements(board_size: int):
    """
    Genera las cláusulas de Prolog: isWinning, equal y isProperSize
    según el tamaño dinámico del tablero.
    Esto permite que el juego se adapte a distintos tamaños sin romper.
    """
    board_array = [f"X{i}" for i in range(1, board_size * board_size + 1)]
    statements_lists = []

    # Generar combinaciones ganadoras verticales
    for i in range(1, board_size + 1):
        statements_lists.append([f"X{i + (board_size * j)}" for j in range(board_size)])

    # Generar combinaciones ganadoras horizontales
    for i in range(board_size):
        statements_lists.append([f"X{(i * board_size) + j}" for j in range(1, board_size + 1)])

    # Generar combinaciones diagonales
    statements_lists.append([f"X{(i * board_size) + i + 1}" for i in range(board_size)])
    statements_lists.append([f"X{(i * board_size) + (board_size - i)}" for i in range(board_size)])

    statements_string = []

    # Definir cláusula equal dinámica
    statements_string.append(f"equal({', '.join(['X' for i in range(board_size + 1)])}).")
    # Clausula de tamaño del tablero
    statements_string.append(f"isProperSize([{', '.join(['_' for i in range(board_size * board_size)])}]).")

    # Clausula principal de victoria
    statements_string.append(f"isWinning(P, [{', '.join(board_array)}]) :-")
    for statement in statements_lists[:-1]:
        statements_string.append(f"\tequal(P, {', '.join(statement)});")

    statements_string.append(f"\tequal(P, {', '.join(statements_lists[-1])}).")

    full_prolog_statements = "\n" + "\n".join(statements_string) + "\n"
    return full_prolog_statements
