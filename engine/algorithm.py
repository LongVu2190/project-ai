#%%
import chess
from engine.table import *

def evaluate_board(board):
    if board.is_checkmate():
        if board.turn:
            return -9999
        else:
            return 9999
    if board.is_stalemate():
        return 0
    if board.is_insufficient_material():
        return 0

    wp = len(board.pieces(chess.PAWN, chess.WHITE))
    bp = len(board.pieces(chess.PAWN, chess.BLACK))
    wn = len(board.pieces(chess.KNIGHT, chess.WHITE))
    bn = len(board.pieces(chess.KNIGHT, chess.BLACK))
    wb = len(board.pieces(chess.BISHOP, chess.WHITE))
    bb = len(board.pieces(chess.BISHOP, chess.BLACK))
    wr = len(board.pieces(chess.ROOK, chess.WHITE))
    br = len(board.pieces(chess.ROOK, chess.BLACK))
    wq = len(board.pieces(chess.QUEEN, chess.WHITE))
    bq = len(board.pieces(chess.QUEEN, chess.BLACK))

    material = 100*(wp-bp)+320*(wn-bn)+330*(wb-bb)+500*(wr-br)+900*(wq-bq)

    pawnsq = sum([pawntable[i] for i in board.pieces(chess.PAWN, chess.WHITE)])
    pawnsq= pawnsq + sum([-pawntable[chess.square_mirror(i)] 
                                    for i in board.pieces(chess.PAWN, chess.BLACK)])
    knightsq = sum([knightstable[i] for i in board.pieces(chess.KNIGHT, chess.WHITE)])
    knightsq = knightsq + sum([-knightstable[chess.square_mirror(i)] 
                                    for i in board.pieces(chess.KNIGHT, chess.BLACK)])
    bishopsq= sum([bishopstable[i] for i in board.pieces(chess.BISHOP, chess.WHITE)])
    bishopsq= bishopsq + sum([-bishopstable[chess.square_mirror(i)] 
                                    for i in board.pieces(chess.BISHOP, chess.BLACK)])
    rooksq = sum([rookstable[i] for i in board.pieces(chess.ROOK, chess.WHITE)]) 
    rooksq = rooksq + sum([-rookstable[chess.square_mirror(i)] 
                                    for i in board.pieces(chess.ROOK, chess.BLACK)])
    queensq = sum([queenstable[i] for i in board.pieces(chess.QUEEN, chess.WHITE)]) 
    queensq = queensq + sum([-queenstable[chess.square_mirror(i)] 
                                    for i in board.pieces(chess.QUEEN, chess.BLACK)])
    kingsq = sum([kingstable[i] for i in board.pieces(chess.KING, chess.WHITE)]) 
    kingsq = kingsq + sum([-kingstable[chess.square_mirror(i)] 
                                    for i in board.pieces(chess.KING, chess.BLACK)])

    eval = material + pawnsq + knightsq + bishopsq+ rooksq+ queensq + kingsq
    if board.turn:
        return eval
    else:
        return -eval

def minimax_root(depth, board, is_maximizing):
    possible_moves = board.legal_moves
    best_move = -9999
    best_move_final = None
    for move in possible_moves:
        board.push(move)
        value = minimax(depth - 1, board, -10000, 10000, not is_maximizing)
        board.pop()
        if value > best_move:
            best_move = value
            best_move_final = move
    return best_move_final

def minimax(depth, board, alpha, beta, is_maximizing):
    if depth == 0:
        return -evaluate_board(board)
    possible_moves = board.legal_moves
    if is_maximizing:
        best_move = -9999
        for move in possible_moves:
            board.push(move)
            best_move = max(best_move, minimax(depth - 1, board, alpha, beta, not is_maximizing))
            board.pop()
            alpha = max(alpha, best_move)
            if beta <= alpha:
                return best_move
        return best_move
    else:
        best_move = 9999
        for move in possible_moves:
            board.push(move)
            best_move = min(best_move, minimax(depth - 1, board, alpha, beta, not is_maximizing))
            board.pop()
            beta = min(beta, best_move)
            if beta <= alpha:
                return best_move
        return best_move

def main():
    board = chess.Board()
    n = 0
    while not board.is_game_over(claim_draw=True):
        if n % 2 == 0:
            move = minimax_root(3, board, True)
            board.push(move)
        else:
            move = minimax_root(3, board, False)
            board.push(move)
        print(board)
        print("...........................")
        n += 1

if __name__ == "__main__":
    main()
# %%
