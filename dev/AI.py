from dev.evaluate import evaluate_board
from stockfish import Stockfish
import config, chess.engine

class AIPlayer:
    def __init__(self, board):
        self.board = board

    # def make_move(self):
    #     # Initialize the Stockfish chess engine
    #     stockfish = Stockfish("./engine/engine.exe")

    #     # Set the position to the current board state
    #     stockfish.set_fen_position(self.board.fen())

    #     # Get the best move in UCI format
    #     best_move_uci = stockfish.get_best_move()

    #     # Convert the UCI move string to a chess.Move object
    #     best_move = chess.Move.from_uci(best_move_uci)

    #     return best_move
    
    def make_move(self):
        # Implement an enhanced minimax algorithm here to choose the best move
        maximizing = False
        if (config.AI_PLAYER == "WHITE"):
            maximizing = True
            
        best_move, points = self.minimax(self.board, depth=config.MINIMAX_DEPTH, alpha=float('-inf'), beta=float('inf'), maximizing_player=maximizing)
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
  