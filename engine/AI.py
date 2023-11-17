from engine.evaluate import evaluate_board
from stockfish import Stockfish
import sys, config, chess.engine

class AIPlayer:
    def __init__(self, board):
        self.board = board
    
    def stockfish_make_move(self):
        application_path = ""
        if getattr(sys, 'frozen', False):
            # Nếu chương trình đang chạy từ một tệp thực thi được đóng gói (exe)
            application_path = "stockfish-windows-x86-64-avx2.exe"
        else:
            # Nếu đang chạy trong môi trường mã nguồn Python
            if __file__:
                application_path = ".\stockfish\stockfish-windows-x86-64-avx2.exe"

        # Initialize the Stockfish chess engine
        stockfish = Stockfish(application_path)

        # Set the position to the current board state
        stockfish.set_fen_position(self.board.fen())

        # Get the best move in UCI format
        best_move_uci = stockfish.get_best_move()

        # Convert the UCI move string to a chess.Move object
        best_move = chess.Move.from_uci(best_move_uci)

        # Get the evaluation score after making the best move
        evaluation = stockfish.get_evaluation()

        stockfish.set_elo_rating(2800)
        stockfish.set_depth(15)
        
        # Print the evaluation score
        print("White score:", evaluation['value'])

        return best_move

    def make_move(self, minimax_depth, AI_player):        
        # Implement an enhanced minimax algorithm here to choose the best move
        maximizing = False
        if (AI_player == "WHITE"):
            maximizing = True
            
        best_move, points = self.minimax(self.board, depth=minimax_depth, alpha=float('-inf'), beta=float('inf'), maximizing_player=maximizing)
        print("White score: " + str(points))

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
  