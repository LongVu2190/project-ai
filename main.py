from dev.board import *
from PyQt5.QtWidgets import QApplication, QHBoxLayout

q_app = QApplication([])
board = ChessBoard()

board_controls = BoardControls(board)

layout = QHBoxLayout()
layout.addWidget(board)
layout.addWidget(board_controls)

main_widget = QWidget()
main_widget.setLayout(layout)
main_widget.show()

q_app.exec()