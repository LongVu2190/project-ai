# AI sử dụng minimax algorithm để chạy
import chess
import chess.svg
from dev.table_value import piece_value

class AIPlayer:
    def __init__(self, board):
        self.board = board

    def make_move(self):
        # Implement an enhanced minimax algorithm here to choose the best move
        best_move, _ = self.minimax(self.board, depth=2, alpha=float('-inf'), beta=float('inf'), maximizing_player=True)
        return best_move

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        if depth == 0 or board.is_game_over():
            return None, self.evaluate_board(board)

        legal_moves = list(board.legal_moves)
        best_move = None
        if maximizing_player:
            best_eval = float('-inf')
            for move in legal_moves:
                board.push(move)
                _, eval_score = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                if eval_score > best_eval:
                    best_eval = eval_score
                    best_move = move
                alpha = max(alpha, best_eval)
                if beta <= alpha:
                    break
            return best_move, best_eval
        else:
            best_eval = float('inf')
            for move in legal_moves:
                board.push(move)
                _, eval_score = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                if eval_score < best_eval:
                    best_eval = eval_score
                    best_move = move
                beta = min(beta, best_eval)
                if beta <= alpha:
                    break

            return best_move, best_eval

    def evaluate_board(self, board):
        score = 0
        for square, piece in board.piece_map().items():
            # Get the value of the piece
            value = piece_value(piece, square)
            
            # Subtract a penalty if the piece is threatened
            if self.threatened_piece(board, square):
                value -= piece_value(piece, square) / 2  # The penalty could be half the value of the piece, for example
                
            # Add a bonus for a pawn structure
            if piece.piece_type == chess.PAWN:
                # Check for doubled pawns
                if self.doubled_pawn(board, square):
                    value -= 10
                # Check for isolated pawns
                if self.isolated_pawn(board, square):
                    value -= 20
                # Check for passed pawns
                if self.passed_pawn(board, square):
                    value += 20

            # Add a bonus for piece development
            if piece.piece_type in [chess.KNIGHT, chess.BISHOP]:
                value += self.piece_development(board, piece.piece_type, piece.color) * 10

            # Add a bonus for mobility
            if piece.piece_type in [chess.ROOK, chess.QUEEN]:
                value += self.mobility(board, piece.piece_type, piece.color)

            # Add a bonus for capture moves
            for move in board.legal_moves:
                if self.capture_move(board, move):
                    value += 200

            # Add or subtract the value from the score
            if piece.color == chess.BLACK:
                score += value
            else:
                score -= value
        return score
     
    def capture_move(self, board, move):
        # Check if a move is a capture move
        return board.is_capture(move)

    def threatened_piece(self, board, square):
        # Check if a piece is threatened by an opponent's piece
        opponent_moves = [move for move in board.legal_moves if board.piece_at(move.from_square).color != board.piece_at(square).color]
        return any(move.to_square == square for move in opponent_moves)
    
    def mobility(self, board, piece_type, color):
        # Mobility is the number of legal moves a piece has
        return len([m for m in board.legal_moves if board.piece_at(m.from_square).piece_type == piece_type and board.piece_at(m.from_square).color == color])

    def piece_development(self, board, piece_type, color):
        # A piece is considered developed if it is not on its starting square
        if color == chess.WHITE:
            if piece_type == chess.KNIGHT:
                starting_squares = [chess.B1, chess.G1]
            elif piece_type == chess.BISHOP:
                starting_squares = [chess.C1, chess.F1]
        else:
            if piece_type == chess.KNIGHT:
                starting_squares = [chess.B8, chess.G8]
            elif piece_type == chess.BISHOP:
                starting_squares = [chess.C8, chess.F8]
        return len([p for p in board.pieces(piece_type, color) if p not in starting_squares])
    
    def doubled_pawn(self, board, square):
        # Check if there is a pawn of the same color on the adjacent file
        pawns = board.pieces(chess.PAWN, board.piece_at(square).color)
        return any((chess.square_file(s) == chess.square_file(square) and
                    chess.square_rank(s) < chess.square_rank(square)) for s in pawns)

    def isolated_pawn(self, board, square):
        # Check if there are no pawns of the same color on the adjacent files
        pawns = board.pieces(chess.PAWN, board.piece_at(square).color)
        return all(chess.square_file(s) != chess.square_file(square) + 1 and
                chess.square_file(s) != chess.square_file(square) - 1 for s in pawns)

    def passed_pawn(self, board, square):
        # Check if there are no opponent pawns on the same file or adjacent files that are ahead of this pawn
        pawns = board.pieces(chess.PAWN, not board.piece_at(square).color)
        return all(chess.square_rank(s) <= chess.square_rank(square) or
                (chess.square_file(s) != chess.square_file(square) + 1 and
                    chess.square_file(s) != chess.square_file(square) - 1) for s in pawns)
