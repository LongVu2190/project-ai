from dev.evaluate import evaluate_board

class AIPlayer:
    def __init__(self, board):
        self.board = board

    def make_move(self):
        # Implement an enhanced minimax algorithm here to choose the best move
        best_move, points = self.minimax(self.board, depth=4, alpha=float('-inf'), beta=float('inf'), maximizing_player=False)
        print("Your Point: " + str(points))
        return best_move

    def minimax(self, board, depth, alpha, beta, maximizing_player):
        if depth == 0 or board.is_game_over():
            return None, evaluate_board(board)

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
  