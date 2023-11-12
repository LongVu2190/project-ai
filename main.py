from dev.board import *
from PyQt5.QtWidgets import QApplication, QHBoxLayout
import config

q_app = QApplication([])
board = ChessBoard()

board_controls = BoardControls(board)

layout = QHBoxLayout()
layout.addWidget(board)
layout.addWidget(board_controls)

main_widget = QWidget()
main_widget.setLayout(layout)
main_widget.setWindowTitle(config.SCREEN_TITLE)
main_widget.setFixedSize(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
main_widget.show()

q_app.exec()