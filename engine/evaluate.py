import chess
import chess.engine
from engine.table_values import *

# Tính điểm các quân trên bàn cờ
def evaluate_board(board):
    total = 0
    end_game = check_end_game(board)

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if not piece:
            continue

        value = piece_value[piece.piece_type] + evaluate_piece(piece, square, end_game)
        total += value if piece.color == chess.WHITE else -value

    return total

def move_value(board, move, endgame):
    if move.promotion is not None:
        return -float("inf") if board.turn == chess.BLACK else float("inf")

    piece = board.piece_at(move.from_square)
    from_value = evaluate_piece(piece, move.from_square, endgame)
    to_value = evaluate_piece(piece, move.to_square, endgame)
    position_change = to_value - from_value

    capture_value = 0.0
    if board.is_capture(move):
        capture_value = evaluate_capture(board, move)

    current_move_value = capture_value + position_change
    if board.turn == chess.BLACK:
        current_move_value = -current_move_value

    return current_move_value

def evaluate_capture(board, move):
    if board.is_en_passant(move):
        return piece_value[chess.PAWN]
    piece_to = board.piece_at(move.to_square)
    piece_from = board.piece_at(move.from_square)
    return piece_value[piece_to.piece_type] - piece_value[piece_from.piece_type]

def evaluate_piece(piece, square, end_game):
    piece_type = piece.piece_type
    mapping = []
    if piece_type == chess.PAWN:
        mapping = pawnEvalWhite if piece.color == chess.WHITE else pawnEvalBlack
    if piece_type == chess.KNIGHT:
        mapping = knightEval
    if piece_type == chess.BISHOP:
        mapping = bishopEvalWhite if piece.color == chess.WHITE else bishopEvalBlack
    if piece_type == chess.ROOK:
        mapping = rookEvalWhite if piece.color == chess.WHITE else rookEvalBlack
    if piece_type == chess.QUEEN:
        mapping = queenEval
    if piece_type == chess.KING:
        # use end game piece-square tables if neither side has a queen
        if end_game:
            mapping = (
                kingEvalEndGameWhite
                if piece.color == chess.WHITE
                else kingEvalEndGameBlack
            )
        else:
            mapping = kingEvalWhite if piece.color == chess.WHITE else kingEvalBlack

    return mapping[square]

def check_end_game(board):
    queens = 0
    minors = 0

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece and piece.piece_type == chess.QUEEN:
            queens += 1
        if piece and (
            piece.piece_type == chess.BISHOP or piece.piece_type == chess.KNIGHT
        ):
            minors += 1

    if queens == 0 or (queens == 2 and minors <= 1):
        return True

    return False