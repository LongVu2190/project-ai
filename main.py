from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont
from PyQt5 import QtGui
from dev.board import *
import config

# for export .exe with pyinstaller
# import io, sys
# stream = io.StringIO()
# sys.stdout = stream
# sys.stderr = stream

class DepthDialog(QDialog):
    def __init__(self, parent=None):
        super(DepthDialog, self).__init__(parent)

        self.setWindowTitle('Chess AI')

        self.depth_input = QSpinBox()
        self.depth_input.setRange(1, 5)
        self.depth_input.setValue(3)
        self.depth_input.setFont(QFont("Arial", 16))
        self.depth_input.setFixedSize(380, 40)

        # Tạo một checkbox mới với nhãn là "Impossible"
        self.checkbox = QCheckBox("Can not be defeated mode")
        self.checkbox.setFont(QFont("Arial", 12))

        self.label = QLabel("AI_Player:")
        self.label.setFont(QFont("Arial", 14))

        self.label1 = QLabel("Depth of AI:")
        self.label1.setFont(QFont("Arial", 14))

        # Tạo một dropdown box mới với hai giá trị là "black" và "white"
        self.dropdown = QComboBox()
        self.dropdown.addItems(["BLACK", "WHITE"])
        self.dropdown.setFont(QFont("Arial", 14))

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.label1)
        layout.addWidget(self.depth_input)
        layout.addWidget(self.checkbox)
        layout.addWidget(self.label)
        layout.addWidget(self.dropdown)
        layout.addWidget(self.button_box)
        self.setLayout(layout)

        # Đặt kích thước cố định cho cửa sổ
        self.setFixedSize(400, 250)

    def getDepth(self):
        return self.depth_input.value()

    def getCheckboxState(self):
        return self.checkbox.isChecked()
    
    def getDropdownValue(self):
        return self.dropdown.currentText()

q_app = QApplication([])
dialog = DepthDialog()
dialog.setWindowIcon(QtGui.QIcon('favicon.ico'))

if dialog.exec() == QDialog.Accepted:
    depth = dialog.getDepth()
    stockfish = dialog.getCheckboxState()
    AI_Player = dialog.getDropdownValue()

    board = ChessBoard(depth, stockfish, AI_Player)

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

