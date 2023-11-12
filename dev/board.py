# Bao gồm bàn cờ, AI đi ở hàm ApplyMove() (AI chỉ thao tác ở hàm ApplyMove() ở file py này)
import chess
import chess.svg
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QDialog, QWidget, QRadioButton, QPushButton, QButtonGroup, QGroupBox, QHBoxLayout, QVBoxLayout
import sys
from dev.AI import AIPlayer

class ChessBoard(QWidget, chess.Board):
    # An interactive chessboard that only allows legal moves
    ReadyForNextMove = pyqtSignal(str)
    GameOver = pyqtSignal()
   
    def __init__(self, parent = None):
        # Initialize the chessboard
        super().__init__(parent)
        
        self.svg_xy = 50 # top left x,y-pos of chessboard
        self.board_size = 650 # size of chessboard
        self.margin = 0.05 * self.board_size
        self.square_size  = (self.board_size - 2*self.margin) / 8.0
        wnd_wh = self.board_size + 2*self.svg_xy
        
        self.setMinimumSize(wnd_wh, wnd_wh)
        self.svg_widget = QSvgWidget(parent=self)
        self.svg_widget.setGeometry(self.svg_xy, self.svg_xy, self.board_size, self.board_size)
      
        self.last_click = None
        self.DrawBoard()
 
    @pyqtSlot(QWidget)
    def mousePressEvent(self, event):
        # Update the board state based on user clicks If the state changes, update the svg widget
        if self.LeftClickedBoard(event):
            this_click = self.GetClicked(event)
            self.HighlightLegalMoves(this_click)
            
            if self.last_click:
                if self.last_click != this_click:
                    uci = self.last_click + this_click
                    self.ApplyMove(uci + self.GetPromotion(uci))
                
            self.last_click = this_click
    
    def GetLegalMoves(self, piece_position):
        # Get the piece at the given position
        piece = self.piece_at(chess.parse_square(piece_position))

        # If there is a piece at the given position
        if piece:
            # Get all legal moves
            legal_moves = list(self.legal_moves)

            # Filter the legal moves for the selected piece
            legal_moves_for_piece = [move for move in legal_moves if move.from_square == chess.parse_square(piece_position)]
            # Return the legal moves for the selected piece
            return [(chess.square_name(move.from_square), chess.square_name(move.to_square)) for move in legal_moves_for_piece]

        # If there is no piece at the given position, return an empty list
        return []

    def HighlightLegalMoves(self, this_click):
        # Get the legal moves for the clicked piece
        legal_moves = self.GetLegalMoves(this_click)
        highlight_positions = [move[1] for move in legal_moves]

        # Sử dụng biến highlight_positions để tạo ra hướng dẫn đi cho quân cờ
        # print(highlight_positions)
      
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
            self.DrawBoard()
            self.repaint()

            if not self.is_game_over():
                self.ReadyForNextMove.emit(self.fen())

                # Check if it's black's turn, then let the AI player make a move
                if self.turn == chess.BLACK:
                    ai_player = AIPlayer(self)
                    ai_move = ai_player.make_move()
                    if ai_move:
                        self.ApplyMove(ai_move.uci())
                
            else:
                print("Game over!")
                self.GameOver.emit()

            self.DrawBoard()
            sys.stdout.flush()
         
    @pyqtSlot()
    def UndoMove(self):
        try:
            self.pop()
            self.pop()
            self.DrawBoard()
            self.ReadyForNextMove.emit(self.fen())
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
      
class BoardControls(QWidget):
    # A UI used to modify the board  
    def __init__(self, board, parent = None):
        # Initialize the controls
        super().__init__(parent)
        
        undo_button = QPushButton("Undo", self)
        
        v_layout = QVBoxLayout()
        v_layout.addWidget(undo_button)
        
        self.setLayout(v_layout)
        
        # connect signals/slots
        undo_button.released.connect(board.UndoMove)