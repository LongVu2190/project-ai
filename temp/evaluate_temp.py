import chess
from dev.table_value import values, piece_value

def evaluate_board(board):
    score = 0
    for square, piece in board.piece_map().items():
        # Get the value of the piece
        value = piece_value(piece, square)
        
        # Subtract a penalty if the piece is threatened
        if threatened_piece(board, square):
            # The penalty could be half the value of the piece, for example
            value -= piece_value(piece, square) / 1.5 
            
        # Add a bonus for a pawn structure
        if piece.piece_type == chess.PAWN:
            # Check for doubled pawns
            if doubled_pawn(board, square):
                value -= 20
            # Check for isolated pawns
            if isolated_pawn(board, square):
                value -= 40
            # Check for passed pawns
            if passed_pawn(board, square):
                value += 40

        # Add a bonus for piece development
        if piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
            value += piece_development(board, piece.piece_type, piece.color) * 10

        # Add a bonus for mobility
        if piece.piece_type in [chess.ROOK, chess.QUEEN]:
            value += mobility(board, piece.piece_type, piece.color)

        # Add a bonus for capture moves
        for move in board.legal_moves:
            if capture_move(board, move):
                value += 200

        # Add or subtract the value from the score
        if piece.color == chess.BLACK:
            score += value
        else:
            score -= value

    return score
    
def capture_move(board, move):
    # Kiểm tra nếu một nước đi là nước ăn
    if board.is_capture(move):
        # Lấy quân cờ sẽ bị ăn
        captured_piece = board.piece_at(move.to_square)
        # Trả về giá trị của quân cờ sẽ bị ăn
        return values[captured_piece.piece_type]
    return 0

def threatened_piece(board, square):
    # Check if a piece is threatened by an opponent's piece
    opponent_moves = [move for move in board.legal_moves if board.piece_at(move.from_square).color != board.piece_at(square).color]
    return any(move.to_square == square for move in opponent_moves)

def mobility(board, piece_type, color):
    # Mobility is the number of legal moves a piece has
    return len([m for m in board.legal_moves if board.piece_at(m.from_square).piece_type == piece_type and board.piece_at(m.from_square).color == color])

def piece_development(board, piece_type, color):
    # A piece is considered developed if it is not on its starting square
    if color == chess.WHITE:
        if piece_type == chess.KNIGHT:
            starting_squares = [chess.B1, chess.G1]
        elif piece_type == chess.BISHOP:
            starting_squares = [chess.C1, chess.F1]
        elif piece_type == chess.ROOK:
            starting_squares = [chess.A1, chess.H1]
        elif piece_type == chess.QUEEN:
            starting_squares = [chess.D1]
    else:
        if piece_type == chess.KNIGHT:
            starting_squares = [chess.B8, chess.G8]
        elif piece_type == chess.BISHOP:
            starting_squares = [chess.C8, chess.F8]
        elif piece_type == chess.ROOK:
            starting_squares = [chess.A8, chess.H8]
        elif piece_type == chess.QUEEN:
            starting_squares = [chess.D8]
    return len([p for p in board.pieces(piece_type, color) if p not in starting_squares])

def doubled_pawn(board, square):
    # Check if there is a pawn of the same color on the adjacent file
    pawns = board.pieces(chess.PAWN, board.piece_at(square).color)
    return any((chess.square_file(s) == chess.square_file(square) and
                chess.square_rank(s) < chess.square_rank(square)) for s in pawns)

def isolated_pawn(board, square):
    # Check if there are no pawns of the same color on the adjacent files
    pawns = board.pieces(chess.PAWN, board.piece_at(square).color)
    return all(chess.square_file(s) != chess.square_file(square) + 1 and
            chess.square_file(s) != chess.square_file(square) - 1 for s in pawns)

def passed_pawn(board, square):
    # Check if there are no opponent pawns on the same file or adjacent files that are ahead of this pawn
    pawns = board.pieces(chess.PAWN, not board.piece_at(square).color)
    return all(chess.square_rank(s) <= chess.square_rank(square) or
            (chess.square_file(s) != chess.square_file(square) + 1 and
                chess.square_file(s) != chess.square_file(square) - 1) for s in pawns)
