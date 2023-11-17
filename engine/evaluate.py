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

    # total -= (king_safety(board, chess.WHITE) - king_safety(board, chess.BLACK))
    # total += pawn_structure(board, chess.WHITE) - pawn_structure(board, chess.BLACK)
    return total

def move_value(board, move, endgame):
    if move.promotion is not None:
        return -float("inf") if board.turn == chess.BLACK else float("inf")

    _piece = board.piece_at(move.from_square)
    if _piece:
        _from_value = evaluate_piece(_piece, move.from_square, endgame)
        _to_value = evaluate_piece(_piece, move.to_square, endgame)
        position_change = _to_value - _from_value
    else:
        raise Exception(f"A piece was expected at {move.from_square}")

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
    _to = board.piece_at(move.to_square)
    _from = board.piece_at(move.from_square)
    if _to is None or _from is None:
        raise Exception(
            f"Pieces were expected at _both_ {move.to_square} and {move.from_square}"
        )
    return piece_value[_to.piece_type] - piece_value[_from.piece_type]

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

def king_safety(board: chess.Board, color: bool) -> float:
    king_square = board.king(color)
    safe = 0
    if king_square:
        # Count the number of squares attacked by the opponent around the king
        opponent_moves = list(board.legal_moves)
        opponent_attacks = [move for move in opponent_moves if move.to_square in board.attacks(king_square)]
        safe = len(opponent_attacks)
    return safe

def pawn_structure(board, color):
    score = 0
    pawns = board.pieces(chess.PAWN, color)
    for pawn in pawns:
        # Penalize isolated pawns
        if isolated_pawn(board, pawn):
            score -= 0.5
        # Penalize doubled pawns
        if doubled_pawn(board, pawn):
            score -= 0.5
        # Reward passed pawns
        if passed_pawn(board, pawn):
            score += 1
    return score

def isolated_pawn(board, square):
    file_index = chess.square_file(square)
    pawn_files = [chess.square_file(pawn_square) for pawn_square in board.pieces(chess.PAWN, board.color_at(square))]
    return pawn_files.count(file_index-1) == 0 and pawn_files.count(file_index+1) == 0

def doubled_pawn(board, square):
    file_index = chess.square_file(square)
    pawn_files = [chess.square_file(pawn_square) for pawn_square in board.pieces(chess.PAWN, board.color_at(square))]
    return pawn_files.count(file_index) > 1

def passed_pawn(board, square):
    file_index = chess.square_file(square)
    rank_index = chess.square_rank(square)
    color = board.color_at(square)
    enemy_pawns = board.pieces(chess.PAWN, not color)
    enemy_pawn_files = [chess.square_file(pawn_square) for pawn_square in enemy_pawns]
    enemy_pawn_ranks = [chess.square_rank(pawn_square) for pawn_square in enemy_pawns if chess.square_file(pawn_square) in [file_index-1, file_index, file_index+1]]
    if color == chess.WHITE:
        return all(rank > rank_index for rank in enemy_pawn_ranks)
    else:
        return all(rank < rank_index for rank in enemy_pawn_ranks)