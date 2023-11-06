#%%
import chess
import chess.svg

def piece_value(piece):
    # Assign values to chess pieces for evaluation
    values = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 20000,
    }
    return values.get(piece, 0)

class AIPlayer:
    def __init__(self, board):
        self.board = board

    def make_move(self):
        # Implement an enhanced minimax algorithm here to choose the best move
        best_move, _ = self.minimax(self.board, depth=2, alpha=float('-inf'), beta=float('inf'), maximizing_player=False)
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
            if piece.color == chess.WHITE:
                score += piece_value(piece)
                score += self.get_capture_bonus(board, square)
            else:
                score -= piece_value(piece)
                score -= self.get_capture_bonus(board, square)
        return score

    def get_capture_bonus(self, board, square):
        capture_bonus = 0
        for move in board.legal_moves:
            if move.to_square == square and board.is_capture(move):
                # Add a bonus for capturing opponent pieces
                capture_bonus += 500  # Adjust this value as needed
        return capture_bonus
# %%
