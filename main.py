import sys, config
from PyQt5.QtWidgets import QApplication, QHBoxLayout
from dev.board import *
from PyQt5 import QtGui
import io

# for export .exe with pyinstaller
# stream = io.StringIO()
# sys.stdout = stream
# sys.stderr = stream

q_app = QApplication([])
board = ChessBoard()

board_controls = BoardControls(board)

layout = QHBoxLayout()
layout.addWidget(board)
layout.addWidget(board_controls)

main_widget = QWidget()
main_widget.setLayout(layout)
main_widget.setWindowTitle(config.SCREEN_TITLE)
main_widget.setWindowIcon(QtGui.QIcon('favicon.ico'))
main_widget.setFixedSize(config.SCREEN_WIDTH, config.SCREEN_HEIGHT)
main_widget.show()

q_app.exec()