import chess
import chess.svg
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QDialog, QWidget, QRadioButton, QPushButton, QButtonGroup, QGroupBox, QHBoxLayout, QVBoxLayout
import sys

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
                capture_bonus += 10000
        return capture_bonus
    
class ChessBoard(QWidget, chess.Board):
    # An interactive chessboard that only allows legal moves
    ReadyForNextMove = pyqtSignal(str)
    GameOver = pyqtSignal()
   
    def __init__(self, parent = None):
        # Initialize the chessboard
        super().__init__(parent)
        self.setWindowTitle("Chess")
        
        self.svg_xy = 50 # top left x,y-pos of chessboard
        self.board_size = 600 # size of chessboard
        self.margin = 0.05 * self.board_size
        self.square_size  = (self.board_size - 2*self.margin) / 8.0
        wnd_wh = self.board_size + 2*self.svg_xy
        
        self.setMinimumSize(wnd_wh, wnd_wh)
        
        self.svg_widget = QSvgWidget(parent=self)
        self.undo_button = QPushButton("Undo", parent=self)
        
        v_layout = QVBoxLayout(self)
        v_layout.addWidget(self.svg_widget)
        v_layout.addWidget(self.undo_button)
        
        self.svg_widget.setGeometry(self.svg_xy, self.svg_xy, self.board_size, self.board_size)
        
        self.last_click = None
        self.DrawBoard()
        
        self.undo_button.released.connect(self.UndoMove)
      
    @pyqtSlot(QWidget)
    def mousePressEvent(self, event):
        # Update the board state based on user clicks If the state changes, update the svg widget
        if self.LeftClickedBoard(event):
            this_click = self.GetClicked(event)
            
            if self.last_click:
                if self.last_click != this_click:
                    uci = self.last_click + this_click
                    self.ApplyMove(uci + self.GetPromotion(uci))
                
            self.last_click = this_click
         
    def GetPromotion(self, uci):
        # Get the uci piece type the pawn will be promoted to
        if chess.Move.from_uci(uci + 'q') in self.legal_moves:
            dialog = PromotionDialog(self)
            if dialog.exec() == QDialog.Accepted:
                return dialog.SelectedPiece()
        return ''
      
    @pyqtSlot(str)
    def ApplyMove(self, uci):
        # Apply a move to the board
        move = chess.Move.from_uci(uci)
        if move in self.legal_moves:
            self.push(move)

            if not self.is_game_over():
                self.ReadyForNextMove.emit(self.fen())

                # Check if it's black's turn, then let the AI player make a move
                if self.turn == chess.BLACK:
                    ai_player = AIPlayer(self)
                    ai_move = ai_player.make_move()
                    if ai_move:
                        self.ApplyMove(ai_move.uci())

            self.DrawBoard()
            sys.stdout.flush()
         
    @pyqtSlot()
    def UndoMove(self):
        try:
            self.pop()
            self.pop()

            if not self.is_game_over():
                self.ReadyForNextMove.emit(self.fen())

            self.DrawBoard()
        except IndexError:
            pass
         
    def DrawBoard(self):
        # Redraw the chessboard based on board state
        # Highlight src and dest squares for last move
        # Highlight king if in check
        self.svg_widget.load(self._repr_svg_().encode("utf-8"))
      
    def GetClicked(self, event):
        # Get the algebraic notation for the clicked square
        top_left = self.svg_xy + self.margin
        file_i =     int((event.x() - top_left)/self.square_size)
        rank_i = 7 - int((event.y() - top_left)/self.square_size)
        return chr(file_i + 97) + str(rank_i + 1)
      
    def LeftClickedBoard(self, event):
        # Check to see if they left-clicked on the chess board
        topleft     = self.svg_xy + self.margin
        bottomright = self.board_size + self.svg_xy - self.margin
        return all([
            event.buttons() == Qt.LeftButton,
            topleft < event.x() < bottomright,
            topleft < event.y() < bottomright,
        ])
      
class PromotionDialog(QDialog):
    def __init__(self, parent = None):
        # Initialize the dialog with buttons
        super().__init__(parent, Qt.WindowSystemMenuHint | Qt.WindowTitleHint)
        self.setWindowTitle("Promotion")
        
        radio_q = QRadioButton("q")
        radio_r = QRadioButton("r")
        radio_b = QRadioButton("b")
        radio_n = QRadioButton("n")
        
        self.button_group = QButtonGroup()
        self.button_group.addButton(radio_q)
        self.button_group.addButton(radio_r)
        self.button_group.addButton(radio_b)
        self.button_group.addButton(radio_n)
        
        radio_q.setChecked(True)
        
        radio_h_layout = QHBoxLayout()
        radio_h_layout.addWidget(radio_q)
        radio_h_layout.addWidget(radio_r)
        radio_h_layout.addWidget(radio_b)
        radio_h_layout.addWidget(radio_n)
        
        group_box = QGroupBox()
        group_box.setLayout(radio_h_layout)
        
        ok_button = QPushButton("Ok")
        cancel_button = QPushButton("Cancel")
        
        ok_button.released.connect(self.accept)
        cancel_button.released.connect(self.reject)
        
        button_h_layout = QHBoxLayout()
        button_h_layout.addWidget(ok_button)
        button_h_layout.addWidget(cancel_button)
        
        v_layout = QVBoxLayout()
        v_layout.addWidget(group_box)
        v_layout.addLayout(button_h_layout)
        self.setLayout(v_layout)
      
    def SelectedPiece(self):
        # Get the uci piece type the user selected from the dialog
        return self.button_group.checkedButton().text()

if __name__ == "__main__":
    # Test the ChessBoard class
    from PyQt5.QtWidgets import QApplication
    q_app = QApplication([])
    board = ChessBoard()
    board.show()
    q_app.exec()