from engine.evaluate import *
from stockfish import Stockfish
import sys, config, chess.engine
import math

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
        
        stockfish.set_elo_rating(2800)
        stockfish.set_depth(15)

        # Get the best move in UCI format
        best_move_uci = stockfish.get_best_move()

        # Convert the UCI move string to a chess.Move object
        best_move = chess.Move.from_uci(best_move_uci)

        # Get the evaluation score after making the best move
        evaluation = stockfish.get_evaluation()
      
        # Print the evaluation score
        print("White score:", evaluation['value'])

        return best_move, evaluation['value']

    def make_move(self, minimax_depth, AI_player):
        # Implement an enhanced minimax algorithm here to choose the best move
        maximizing = False
        if (AI_player == "WHITE"):
            maximizing = True
            
        best_move, score = self.minimax(depth=minimax_depth, alpha=float('-inf'), beta=float('inf'), maximizing_player=maximizing)
        print("White score: " + str(score))

        if (score == float('-inf')):
            best_move = self.get_ordered_moves()[0]
            score = -1000000

        return best_move, score

    def minimax(self, depth, alpha, beta, maximizing_player):
        if depth == 0:
            return None, evaluate_board(self.board)

        legal_moves = self.get_ordered_moves()
        best_move = None
        if maximizing_player:
            best_eval = float('-inf')

            # Không còn nước nào để đi
            # if (len(legal_moves) == 0):
            #     return None, -1000000
            for move in legal_moves:
                self.board.push(move)
                if self.board.is_checkmate():
                    self.board.pop()
                    return move, 1000000  # Return immediately if the move leads to a checkmate
                current_move, eval_score = self.minimax(depth - 1, alpha, beta, False)

                # Tránh lặp lại nước dẫn tới hoà khi điểm trên 300
                # Tránh dẫn tới hoà khi đối phương không đi được (is_stalemate)
                if ((self.board.is_fivefold_repetition() or self.board.can_claim_threefold_repetition() and eval_score > 300) or self.board.is_stalemate()):
                    self.board.pop()
                    return legal_moves[0], evaluate_board(self.board)
                
                self.board.pop()
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
                self.board.push(move)
                if self.board.is_checkmate():
                    self.board.pop()
                    return move, -1000000  # Return immediately if the move leads to a checkmate
                current_move, eval_score = self.minimax(depth - 1, alpha, beta, True)
                self.board.pop()
                if eval_score < best_eval:
                    best_eval = eval_score
                    best_move = move

                beta = min(beta, best_eval)
                if beta <= alpha:
                    break
            return best_move, best_eval
       
    def get_ordered_moves(self):
        """
        Get legal moves.
        Attempt to sort moves by best to worst.
        Use piece values (and positional gains/losses) to weight captures.
        """
        end_game = check_end_game(self.board)

        def orderer(move):
            return move_value(self.board, move, end_game)

        in_order = sorted(
            self.board.legal_moves, key=orderer, reverse=(self.board.turn == chess.WHITE)
        )
        return list(in_order)
  