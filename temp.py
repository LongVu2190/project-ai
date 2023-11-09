# Bàn cờ gốc, tự đi quân cho 2 bên
import chess
import chess.svg
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QDialog, QWidget, QRadioButton, QPushButton, QButtonGroup, QGroupBox, QHBoxLayout, QVBoxLayout, QMessageBox
import sys

class ChessBoard(QWidget, chess.Board):
    ReadyForNextMove = pyqtSignal(str)
    GameOver = pyqtSignal(bool)
   
    def __init__(self, parent = None):
        # Initialize the chessboard
        super().__init__(parent)
        self.setWindowTitle("Chess")
        self.SQUARES = {
            chess.A1: "a1",
            chess.B1: "b1",
            chess.C1: "c1",
            chess.D1: "d1",
            chess.E1: "e1",
            chess.F1: "f1",
            chess.G1: "g1",
            chess.H1: "h1",
            chess.A2: "a2",
            chess.B2: "b2",
            chess.C2: "c2",
            chess.D2: "d2",
            chess.E2: "e2",
            chess.F2: "f2",
            chess.G2: "g2",
            chess.H2: "h2",
            chess.A3: "a3",
            chess.B3: "b3",
            chess.C3: "c3",
            chess.D3: "d3",
            chess.E3: "e3",
            chess.F3: "f3",
            chess.G3: "g3",
            chess.H3: "h3",
            chess.A4: "a4",
            chess.B4: "b4",
            chess.C4: "c4",
            chess.D4: "d4",
            chess.E4: "e4",
            chess.F4: "f4",
            chess.G4: "g4",
            chess.H4: "h4",
            chess.A5: "a5",
            chess.B5: "b5",
            chess.C5: "c5",
            chess.D5: "d5",
            chess.E5: "e5",
            chess.F5: "f5",
            chess.G5: "g5",
            chess.H5: "h5",
            chess.A6: "a6",
            chess.B6: "b6",
            chess.C6: "c6",
            chess.D6: "d6",
            chess.E6: "e6",
            chess.F6: "f6",
            chess.G6: "g6",
            chess.H6: "h6",
            chess.A7: "a7",
            chess.B7: "b7",
            chess.C7: "c7",
            chess.D7: "d7",
            chess.E7: "e7",
            chess.F7: "f7",
            chess.G7: "g7",
            chess.H7: "h7",
            chess.A8: "a8",
            chess.B8: "b8",
            chess.C8: "c8",
            chess.D8: "d8",
            chess.E8: "e8",
            chess.F8: "f8",
            chess.G8: "g8",
            chess.H8: "h8",
        }
        self.svg_xy = 50 # top left x,y-pos of chessboard
        self.board_size = 600 # size of chessboard
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

            # Highlight the legal moves
            self.HighlightLegalMoves(this_click)

            if self.last_click:
                if self.last_click != this_click:
                    uci = self.last_click + this_click
                    self.highlight_positions = None
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

        # Highlight the positions
        svg_data = self._repr_svg_().encode("utf-8")
        svg_data_str = svg_data.decode("utf-8")

        print(highlight_positions)
        # Add <rect> SVG elements for each highlighted position
        # for position in highlight_positions:

        #     # Calculate the coordinates of the square in the SVG
        #     file = ord(position[0]) - ord('a')
        #     rank = int(position[1]) - 1
        #     x = file * self.square_size
        #     y = (7 - rank) * self.square_size  # Subtract from 7 because SVG y-coordinates start from the top

        #     # Create the <rect> element
        #     rect = f'<rect x="{x}" y="{y}" width="{self.square_size}" height="{self.square_size}" fill="#FFFF00"/>'

        #     # Add the <rect> element to the SVG
        #     svg_data_str = svg_data_str.replace('</svg>', f'{rect}\n</svg>')

        # self.svg_widget.load(bytes(svg_data_str, 'utf-8'))
        
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
            
            if not self.is_game_over():
                self.ReadyForNextMove.emit(self.fen())
            else:
                print("Game over!")
                self.GameOver.emit(self.result())
            sys.stdout.flush()
         
    @pyqtSlot()
    def UndoMove(self):
        try:
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
        
        radio_q = QRadioButton("Queen")
        radio_r = QRadioButton("Rook")
        radio_b = QRadioButton("Bishop")
        radio_n = QRadioButton("Knight")
        
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
  
class ChessGame(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chess")
        self.setGeometry(100, 100, 1000, 700)
        
        self.board = ChessBoard(self)
        self.board_controls = BoardControls(self.board, self)
        
        layout = QHBoxLayout()
        layout.addWidget(self.board)
        layout.addWidget(self.board_controls)
        
        self.setLayout(layout)
        
        self.board.ReadyForNextMove.connect(self.DoComputerMove)
        self.board.GameOver.connect(self.ShowGameOverDialog)
    
    @pyqtSlot()
    def DoComputerMove(self):
        # Do something
        pass
        
    @pyqtSlot(bool)
    def ShowGameOverDialog(self, result):
        if result == '1-0':
            message_box = QMessageBox.information(self, "Game over!", "White wins!")
        elif result == '0-1':
            message_box = QMessageBox.information(self, "Game over!", "Black wins!")
        elif result == '1/2-1/2':
            message_box = QMessageBox.information(self, "Game over!", "It's a draw!")
        else:
            message_box = QMessageBox.information(self, "Game over!", "Game ended.")
        
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication

    q_app = QApplication([])
    game = ChessGame()
    game.show()
    q_app.exec()