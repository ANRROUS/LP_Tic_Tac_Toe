/*=======================================
 * REGLAS BÁSICAS DEL JUEGO
 * Define los símbolos válidos y relaciones entre jugadores
 *=======================================*/

% Símbolos válidos en el tablero (x, o o 0 para vacío)
isProperSymbol(x).
isProperSymbol(o).
isProperSymbol(0).

% Relación entre jugadores (x <-> o)
otherPlayer(x, o).
otherPlayer(o, x).

% Alternancia entre modos minimax (min <-> max)
switchMinMax(min, max).
switchMinMax(max, min).

% Predicado para verificar 4 elementos iguales (para tableros 4x4)
equal(X, X, X, X).


/*=======================================
 * VALIDACIÓN DEL TABLERO
 * Verifica que el tablero cumpla con las reglas del juego
 *=======================================*/

% Verifica que todos los símbolos del tablero sean válidos
isBoardValid([CurrentSymbol|OtherSymbols]) :-
    isProperSymbol(CurrentSymbol),
    isBoardValid(OtherSymbols).
isBoardValid([]).  % Caso base: lista vacía

% Verifica que el tablero tenga el tamaño correcto (9 posiciones para 3x3)
isProperSize([_, _, _, _, _, _, _, _, _]).


/*=======================================
 * LÓGICA DEL JUEGO
 * Reglas para movimientos y condiciones de finalización
 *=======================================*/

% Determina si hay empate (no quedan espacios vacíos)
isDraw(Board) :-
    \+ member(0, Board).

% Genera movimientos posibles (reemplaza un 0 por el símbolo del jugador)
makeMove(P, [B|Bs], [B|B2s]) :-
    makeMove(P, Bs, B2s).
makeMove(P, [0|Bs], [P|Bs]).

% Encuentra todos los movimientos posibles para un jugador
allMoves(P, Board, AllMoves) :-
    findall(NextBoard, makeMove(P, Board, NextBoard), AllMoves).


/*=======================================
 * CONDICIONES DE VICTORIA
 * Todas las posibles combinaciones ganadoras
 *=======================================*/

% Combinaciones ganadoras para tablero 3x3
isWinning(P, [X1, X2, X3, X4, X5, X6, X7, X8, X9]) :-
    equal(P, X1, X2, X3);  % Horizontal superior
    equal(P, X4, X5, X6);  % Horizontal medio
    equal(P, X7, X8, X9);  % Horizontal inferior
    equal(P, X1, X4, X7);  % Vertical izquierda
    equal(P, X2, X5, X8);  % Vertical centro
    equal(P, X3, X6, X9);  % Vertical derecha
    equal(P, X1, X5, X9);  % Diagonal \
    equal(P, X3, X5, X7).  % Diagonal /


/*=======================================
 * VALIDACIÓN DE ENTRADAS
 * Verifica que los parámetros sean correctos
 *=======================================*/

validateInput(Depth, Player, Board) :-
    \+ isBoardValid(Board),
    throw("Board contains invalid signs!");
    \+ isProperSize(Board),
    throw("Board is inpropely sized!");
    \+ otherPlayer(Player, _),
    throw("Invalid input Player!");
    Depth < 1,
    throw("Invalid input Depth!").


/*=======================================
 * EVALUACIÓN DEL TABLERO
 * Asigna puntuaciones a los estados del juego
 *=======================================*/

scoreBoard(_, _, [], Score) :-
    Score is 0.
scoreBoard(0, _, _, Score) :-
    Score is 0.
scoreBoard(_, P, Board, Score) :-
    isWinning(P, Board),
    Score is 1, !.          % Corta si el jugador gana
scoreBoard(_, P, Board, Score) :-
    otherPlayer(P, P2),
    isWinning(P2, Board),
    Score is -1, !.         % Corta si el oponente gana
scoreBoard(_, _, Board, Score) :-
    isDraw(Board),
    Score is 0, !.          % Corta si es empate


/*=======================================
 * ALGORITMO MINIMAX
 * Implementación de la IA para el juego
 *=======================================*/

% Compara movimientos según el modo (maximizar o minimizar)
compareMoves(max, MoveA, ScoreA, _, ScoreB, MoveA, ScoreA) :-
    ScoreA >= ScoreB, !.
compareMoves(max, _, ScoreA, MoveB, ScoreB, MoveB, ScoreB) :-
    ScoreA < ScoreB, !.
compareMoves(min, MoveA, ScoreA, _, ScoreB, MoveA, ScoreA) :-
    ScoreA =< ScoreB, !.
compareMoves(min, _, ScoreA, MoveB, ScoreB, MoveB, ScoreB) :-
    ScoreA > ScoreB, !.

% Encuentra el mejor movimiento según la estrategia minimax
bestMove(Depth, OriginalPlayer, Player, MinMax, [Move | OtherMoves], BestMove, BestScore) :-
    scoreBoard(Depth, OriginalPlayer, Move, Score),
    bestMove(Depth, OriginalPlayer, Player, MinMax, OtherMoves, CurrentBestMove, CurrentBestScore),
    compareMoves(MinMax, Move, Score, CurrentBestMove, CurrentBestScore, BestMove, BestScore).
bestMove(Depth, OriginalPlayer, Player, MinMax, [Move | OtherMoves], BestMove, BestScore) :-
    bestMove(Depth, OriginalPlayer, Player, MinMax, OtherMoves, CurrentBestMove, CurrentBestScore),
    otherPlayer(Player, OtherPlayer),
    switchMinMax(MinMax, OtherMinMax),
    miniMaxStep(Depth, OriginalPlayer, OtherPlayer, OtherMinMax, Move, _, LeafBestScore),
    compareMoves(MinMax, Move, LeafBestScore, CurrentBestMove, CurrentBestScore, BestMove, BestScore).
bestMove(_, _, _, max, [], [], -2).  % Valor mínimo inicial para maximizar
bestMove(_, _, _, min, [], [], 2).   % Valor máximo inicial para minimizar

% Paso recursivo del algoritmo minimax
miniMaxStep(Depth, OriginalPlayer, Player, MinMax, Board, BestMove, BestScore) :-
    Depth > 0,
    NewDepth is Depth - 1,
    allMoves(Player, Board, AllMoves),
    bestMove(NewDepth, OriginalPlayer, Player, MinMax, AllMoves, BestMove, BestScore).
miniMaxStep(_, OriginalPlayer, _, _, Board, _, Score) :-
    scoreBoard(0, OriginalPlayer, Board, Score).


/*=======================================
 * INTERFAZ PRINCIPAL
 * Punto de entrada para el algoritmo minimax
 *=======================================*/

% Casos base: juego terminado (victoria/empate)
miniMax(_, Player, Board, Board) :-
    isWinning(Player, Board);
    otherPlayer(Player, OtherPlayer),
    isWinning(OtherPlayer, Board);
    isDraw(Board).
    
% Implementación principal del algoritmo minimax
miniMax(Depth, Player, Board, BestMove) :-
    \+ validateInput(Depth, Player, Board),  % Validación silenciosa
    miniMaxStep(Depth, Player, Player, max, Board, BestMove, _).