from os import path
from typing import List, Optional
from itertools import islice
from pyswip_mt import PrologMT

# Archivo base de reglas Prolog y límite de memoria para el motor
BASE_PROLOG_FILE = "tic-tac-toe.pl" 
STACK_LIMIT = 4000000000

# Función lambda para alternar entre jugadores (X/O)
OTHER_PLAYER_SYMBOL = lambda x: "x" if x == "O" else "o"  

# Instancia del intérprete Prolog con soporte multi-hilo
prolog = PrologMT()
prolog_loaded = False  # Controla si el archivo Prolog ya fue cargado

def consult_board_size(board_size: int) -> None:
    """Configura e inicializa el motor Prolog con el archivo base"""
    global prolog_loaded
    
    if not prolog_loaded:
        # Establece límite de memoria y carga el archivo Prolog
        next(prolog.query(f"set_prolog_flag(stack_limit, {STACK_LIMIT})."))  
        prolog.consult(BASE_PROLOG_FILE)
        prolog_loaded = True

def make_move(board: List[List], difficulty_level: int, player_symbol: str) -> List[List]:
    """Calcula el mejor movimiento usando el algoritmo minimax en Prolog"""
    consult_board_size(len(board))
    
    # Convierte el tablero a formato Prolog y ejecuta la consulta
    prolog_board = board_to_prolog(board)
    prolog_query = f"miniMax({difficulty_level}, {OTHER_PLAYER_SYMBOL(player_symbol)}, {prolog_board}, BestMove)"
    
    results = list(prolog.query(prolog_query, maxresult=1))
    if not results:
        raise ValueError(f"No se encontró ningún movimiento válido.\nConsulta: {prolog_query}")
    
    # Convierte el resultado de Prolog a formato Python
    return prolog_to_board(results[0]["BestMove"], len(board))

def check_is_winner(board: List[List], player_symbol: str) -> Optional[bool]:
    """Verifica si el jugador actual o el oponente han ganado"""
    consult_board_size(len(board))
    prolog_board = board_to_prolog(board)
    
    # Consulta si el jugador actual ganó
    if list(prolog.query(f"isWinning({player_symbol.lower()}, {prolog_board}).")):
        return True
        
    # Consulta si el oponente ganó    
    if list(prolog.query(f"isWinning({OTHER_PLAYER_SYMBOL(player_symbol)}, {prolog_board}).")):
        return False
        
    return None  # No hay ganador aún

def board_to_prolog(board: List[List]) -> str:
    """Convierte matriz Python a lista plana para Prolog (ej: [x,o,0,...])"""
    board_str_list = []
    for row in board:
        for cell in row:
            board_str_list.append(cell.lower() if cell else "0")  # 0 representa casilla vacía
    return str(board_str_list).replace("'", "")  # Elimina comillas simples

def prolog_to_board(board: List, board_size: int) -> List[List]:
    """Convierte lista plana de Prolog a matriz Python"""
    # Convierte 0 a string vacío y mantiene x/o en mayúsculas
    board_str_list = ["" if cell == 0 else str(cell).upper() for cell in board]  
    
    # Reconstruye la matriz bidimensional
    iterator = iter(board_str_list)
    return [list(islice(iterator, board_size)) for _ in range(board_size)]