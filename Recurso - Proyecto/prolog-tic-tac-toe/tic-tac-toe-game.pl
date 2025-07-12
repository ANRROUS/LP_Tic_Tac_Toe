% ==================================================
% DEFINICIONES BÁSICAS Y CONSTANTES
% ==================================================

% --------------------------------------------------
% Símbolos válidos y jugadores alternos
% --------------------------------------------------

% isProperSymbol(+Symbol)
isProperSymbol(x).
isProperSymbol(o).
isProperSymbol(0).

% otherPlayer(+Player, -OtherPlayer)
otherPlayer(x, o).
otherPlayer(o, x).

% switchMinMax(+MinMax, -OtherMinMax)
switchMinMax(min, max).
switchMinMax(max, min).

% equal(+X1, +X2, +X3, +X4)
equal(X, X, X, X).


% ==================================================
% VALIDACIÓN DEL TABLERO Y ESTADO DEL JUEGO
% ==================================================

% --------------------------------------------------
% Validación del tablero
% --------------------------------------------------

% isBoardValid(+Board)
isBoardValid([CurrentSymbol|OtherSymbols]) :-
    isProperSymbol(CurrentSymbol),
    isBoardValid(OtherSymbols).
isBoardValid([]).

% isProperSize(+Board)
isProperSize([_, _, _, _, _, _, _, _, _]).  % tablero 3x3

% isDraw(+Board)
isDraw(Board) :-
    \+ member(0, Board).


% ==================================================
% LÓGICA DE MOVIMIENTOS
% ==================================================

% --------------------------------------------------
% Generación y simulación de jugadas
% --------------------------------------------------

% makeMove(+Player, +Board, -NextBoard)
makeMove(P, [B|Bs], [B|B2s]) :-
    makeMove(P, Bs, B2s).
makeMove(P, [0|Bs], [P|Bs]).

% allMoves(+Player, +Board, -AllMoves)
allMoves(P, Board, AllMoves) :-
    findall(NextBoard, makeMove(P, Board, NextBoard), AllMoves).


% ==================================================
% VERIFICACIÓN DE VICTORIA
% ==================================================

% --------------------------------------------------
% Verificación de ganador
% --------------------------------------------------

% isWinning(+Player, +Board)
isWinning(P, [X1, X2, X3, X4, X5, X6, X7, X8, X9]) :-
    equal(P, X1, X2, X3);
    equal(P, X4, X5, X6);
    equal(P, X7, X8, X9);
    equal(P, X1, X4, X7);
    equal(P, X2, X5, X8);
    equal(P, X3, X6, X9);
    equal(P, X1, X5, X9);
    equal(P, X3, X5, X7).


% ==================================================
% VALIDACIÓN DE PARÁMETROS DE ENTRADA
% ==================================================

% --------------------------------------------------
% Validación de parámetros del algoritmo
% --------------------------------------------------

% validateInput(+Depth, +Player, +Board)
validateInput(Depth, Player, Board) :-
    \+ isBoardValid(Board),
    throw("Board contains invalid signs!");

    \+ isProperSize(Board),
    throw("Board is inpropely sized!");

    \+ otherPlayer(Player, _),
    throw("Invalid input Player!");

    Depth < 1,
    throw("Invalid input Depth!").


% ==================================================
% EVALUACIÓN DEL TABLERO (SCORING)
% ==================================================

% --------------------------------------------------
% Puntaje del tablero según estado actual
% --------------------------------------------------

% scoreBoard(+Depth, +Player, +Board, -Score)
scoreBoard(_, _, [], Score) :-
    Score is 0.
scoreBoard(0, _, _, Score) :-
    Score is 0.

scoreBoard(_, P, Board, Score) :-
    isWinning(P, Board),
    Score is 1, !.

scoreBoard(_, P, Board, Score) :-
    otherPlayer(P, P2),
    isWinning(P2, Board),
    Score is -1, !.

scoreBoard(_, _, Board, Score) :-
    isDraw(Board),
    Score is 0, !.


% ==================================================
% ALGORITMO MINIMAX
% ==================================================

% --------------------------------------------------
% Comparación entre movimientos
% --------------------------------------------------

% compareMoves(+MinMax, +MoveA, +ScoreA, +MoveB, +ScoreB, -BetterMove, -BetterScore)
compareMoves(max, MoveA, ScoreA, _, ScoreB, MoveA, ScoreA) :-
    ScoreA >= ScoreB, !.
compareMoves(max, _, ScoreA, MoveB, ScoreB, MoveB, ScoreB) :-
    ScoreA < ScoreB, !.
compareMoves(min, MoveA, ScoreA, _, ScoreB, MoveA, ScoreA) :-
    ScoreA =< ScoreB, !.
compareMoves(min, _, ScoreA, MoveB, ScoreB, MoveB, ScoreB) :-
    ScoreA > ScoreB, !.


% --------------------------------------------------
% Exploración de opciones y búsqueda óptima
% --------------------------------------------------

% bestMove(+Depth, +OriginalPlayer, +Player, +MinMax, +AllMoves, -BestMove, -BestScore)

% Caso 1: hay score inmediato
bestMove(Depth, OriginalPlayer, Player, MinMax, [Move | OtherMoves], BestMove, BestScore) :-
    scoreBoard(Depth, OriginalPlayer, Move, Score),
    bestMove(Depth, OriginalPlayer, Player, MinMax, OtherMoves, CurrentBestMove, CurrentBestScore),
    compareMoves(MinMax, Move, Score, CurrentBestMove, CurrentBestScore, BestMove, BestScore).

% Caso 2: hay que seguir explorando
bestMove(Depth, OriginalPlayer, Player, MinMax, [Move | OtherMoves], BestMove, BestScore) :-
    bestMove(Depth, OriginalPlayer, Player, MinMax, OtherMoves, CurrentBestMove, CurrentBestScore),
    otherPlayer(Player, OtherPlayer),
    switchMinMax(MinMax, OtherMinMax),
    miniMaxStep(Depth, OriginalPlayer, OtherPlayer, OtherMinMax, Move, _, LeafBestScore),
    compareMoves(MinMax, Move, LeafBestScore, CurrentBestMove, CurrentBestScore, BestMove, BestScore).

% Caso 3: sin movimientos posibles
bestMove(_, _, _, max, [], [], -2).
bestMove(_, _, _, min, [], [], 2).


% --------------------------------------------------
% Paso recursivo dentro del algoritmo
% --------------------------------------------------

% miniMaxStep(+Depth, +OriginalPlayer, +Player, +MinMax, +Board, -BestMove, -BestScore)
miniMaxStep(Depth, OriginalPlayer, Player, MinMax, Board, BestMove, BestScore) :-
    Depth > 0,
    NewDepth is Depth - 1,
    allMoves(Player, Board, AllMoves),
    bestMove(NewDepth, OriginalPlayer, Player, MinMax, AllMoves, BestMove, BestScore).

% Cuando ya no queda profundidad para explorar
miniMaxStep(_, OriginalPlayer, _, _, Board, _, Score) :-
    scoreBoard(0, OriginalPlayer, Board, Score).


% --------------------------------------------------
% Entrada principal del algoritmo
% --------------------------------------------------

% miniMax(+Depth, +Player, +Board, -BestMove)
miniMax(_, Player, Board, Board) :-
    isWinning(Player, Board);
    otherPlayer(Player, OtherPlayer),
    isWinning(OtherPlayer, Board);
    isDraw(Board).

miniMax(Depth, Player, Board, BestMove) :-
    \+ validateInput(Depth, Player, Board),
    miniMaxStep(Depth, Player, Player, max, Board, BestMove, _).

% Psdt: Intente que ejecute con esto pero da error con 0x81 invalid. Pero esto sirve para entender como funciona si necesitan mas preguntenle a chatGPT parte por parte :3