import sys, chess, config, chess.svg
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QDialog, QWidget, QRadioButton, QPushButton, QButtonGroup, QGroupBox, QHBoxLayout, QVBoxLayout, QLabel

from engine.AI import AIPlayer

class ChessBoard(QWidget, chess.Board):
    # An interactive chessboard that only allows legal moves
    ReadyForNextMove = pyqtSignal(str)
    GameOver = pyqtSignal()
   
    def __init__(self, minimax_depth, useStockfish, AI_player, parent = None):
        # Initialize the chessboard
        super().__init__(parent)

        self.minimax_depth = minimax_depth
        self.useStockfish = useStockfish
        self.AI_player = AI_player
        
        self.svg_xy = 50 # top left x,y-pos of chessboard
        self.board_size = config.BOARD_SIZE # size of chessboard
        self.margin = 0.05 * self.board_size
        self.square_size  = (self.board_size - 2*self.margin) / 8.0
        wnd_wh = self.board_size + 2*self.svg_xy
        
        self.highlight_positions = []
        self.setMinimumSize(wnd_wh, wnd_wh)
        self.svg_widget = QSvgWidget(parent=self)
        self.svg_widget.setGeometry(self.svg_xy, self.svg_xy, self.board_size, self.board_size)
         # AI Thinking
        # sub_layout = QVBoxLayout()
        self.label_AI_thinking = QLabel(self)
        self.label_AI_thinking.setStyleSheet("color: rgb(255,105,180); font-weight: bold; font-size: 26px")
        self.label_AI_thinking.setText("AI is thinking...")

        self.label_AI_thinking.move(300, 0) 
        self.label_AI_thinking.hide()
        self.last_click = None
        self.DrawBoard()

        # if AI is white
        self.AI_move()
 
    @pyqtSlot(QWidget)
            
    def mousePressEvent(self, event):
        # Update the board state based on user clicks If the state changes, update the svg widget
        if self.LeftClickedBoard(event):
            this_click = self.GetClicked(event)
            self.HighlightLegalMoves(this_click)
            self.DrawBoard()
            
            if self.last_click:
                if self.last_click != this_click:
                    uci = self.last_click + this_click
                    self.ApplyMove(uci + self.GetPromotion(uci))
                
            self.last_click = this_click

    def HighlightLegalMoves(self, this_click):
        # Get the piece at the given position
        piece = self.piece_at(chess.parse_square(this_click))

        # If there is a piece at the given position
        if piece:
            # Get all legal moves
            legal_moves = list(self.legal_moves)

            # Filter the legal moves for the selected piece
            legal_moves_for_piece = [move for move in legal_moves if move.from_square == chess.parse_square(this_click)]
            # Return the legal moves for the selected piece
            legal_moves = [(chess.square_name(move.from_square), chess.square_name(move.to_square)) for move in legal_moves_for_piece]
            self.highlight_positions = [move[1] for move in legal_moves]

        # If there is no piece at the given position, return an empty list
        else:
            self.highlight_positions = []
      
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
                self.AI_move()                                  
            else:
                print("Game over!")
                self.GameOver.emit()

            self.DrawBoard()
            sys.stdout.flush()


    def AI_move(self):
        # Check if it's black's turn, then let the AI player make a move
        if (self.AI_player == "BLACK" and self.turn == chess.BLACK) or (self.AI_player == "WHITE" and self.turn == chess.WHITE):
            self.label_AI_thinking.show()
            self.DrawBoard()
            self.repaint()         

            ai_player = AIPlayer(self)

            if (self.useStockfish):
                ai_move = ai_player.stockfish_make_move()
            else:
                ai_move = ai_player.make_move(self.minimax_depth, self.AI_player)

            if ai_move:
                self.ApplyMove(ai_move.uci())

        else:
            self.label_AI_thinking.hide() 
            self.DrawBoard()
            self.repaint()

    @pyqtSlot()
    def UndoMove(self):
        if not self.is_game_over():
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
        # Highlight legal moves for selected piece
        svg = self._repr_svg_().encode("utf-8")
        for pos in self.highlight_positions:
            svg = self.highlight_square(svg, pos)
        self.svg_widget.load(svg)

    def highlight_square(self, svg, pos):
        # Convert the SVG from bytes to string
        svg = svg.decode('utf-8')

        # Convert the position to a square number
        square_number = chess.parse_square(pos)

        # Calculate the x and y coordinates of the square
        x = (0.435 + square_number % 8) * (config.BOARD_SIZE / 14.3) + config.BOARD_SIZE / 40
        y = (7.43 - square_number // 8) * (config.BOARD_SIZE / 14.3) + config.BOARD_SIZE / 40
        circle = None
        if self.piece_at(chess.parse_square(pos)):
            circle = f'<circle cx="{x}" cy="{y}" r="{config.BOARD_SIZE / 60}" fill="red" fill-opacity="0.9" />'
        else:
            circle = f'<circle cx="{x}" cy="{y}" r="{config.BOARD_SIZE / 60}" fill="green" fill-opacity="0.9" />'

        # Add the circle element to the svg
        svg = svg.replace('</svg>', circle + '</svg>')

        # Convert the SVG back to bytes
        svg = svg.encode('utf-8')

        return svg
      
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
        
        radio_q = QRadioButton("q_Queen")
        radio_r = QRadioButton("r_Rook")
        radio_b = QRadioButton("b_Bishop")
        radio_n = QRadioButton("n_Knight")
        
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
        return self.button_group.checkedButton().text()[0]
      
class BoardControls(QWidget):
    # A UI used to modify the board  
    def __init__(self, board, parent = None):
        # Initialize the controls
        super().__init__(parent)
        
        undo_button = QPushButton("Undo", self)
        
        self.setButtonStyle(undo_button, background_color="rgb(176,196,222)", text_color="#000", font_size=14, button_size=(100, 50), scale_factor=1.5)

        v_layout = QVBoxLayout()
        # label_AI_thinking.hide()
        v_layout.addWidget(undo_button)
        # label_AI_thinking.hide()
        self.setLayout(v_layout)
        
        # connect signals/slots
        undo_button.released.connect(board.UndoMove)

    def setButtonStyle(self, button, background_color, text_color, font_size, button_size, scale_factor):
        # Scale the font size and button size
        scaled_font_size = int(font_size * scale_factor)
        scaled_button_size = (int(button_size[0] * scale_factor), int(button_size[1] * scale_factor))

        # Set the style of the button
        button.setStyleSheet(
            f"QPushButton {{ background-color: {background_color}; color: {text_color}; font-size: {scaled_font_size}px; }}"
            f"QPushButton:hover {{ border: 3px solid rgb(105,105,105); }}"  # Add hover effect if desired
        )
        button.setFixedSize(scaled_button_size[0], scaled_button_size[1])

    