from PyQt5.QtWidgets import *
from PyQt5.QtGui import QFont, QColor

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
        self.depth_input.setRange(1, 6)
        self.depth_input.setValue(3)
        self.depth_input.setFont(QFont("Consolas", 16))
        self.depth_input.setFixedSize(200, 40)
        
        # Apply the QGraphicsOpacityEffect to the depth_input widget
        self.checkbox = QCheckBox("Stockfish Mode")
        self.checkbox.setFont(QFont("Consolas", 20))
        self.checkbox.setStyleSheet("color: rgb(255,250,250); font-weight: bold; font-size: 20px")
        
        self.label = QLabel("AI Player:")
        self.label.setFont(QFont("Consolas", 14))
        self.label.setStyleSheet("color: rgb(255,250,250); font-weight: bold; font-size: 26px")
        self.label_depth = QLabel("AI Depth:")
        self.label_depth.setStyleSheet("color: rgb(255,250,250); font-weight: bold; font-size: 26px")
        self.label_depth.setFont(QFont("Consolas", 14))

        # Tạo một dropdown box mới với hai giá trị là "black" và "white"
        self.dropdown = QComboBox()
        self.dropdown.addItems(["BLACK", "WHITE"])
        self.dropdown.setFont(QFont("Consolas", 14))
        self.dropdown.setFixedSize(200, 40)

        # Tạo hiệu ứng shadow
        shadow1 = QGraphicsDropShadowEffect()
        shadow1.setBlurRadius(20)
        shadow1.setXOffset(1)
        shadow1.setYOffset(1)
        shadow1.setColor(QColor('black'))

        shadow2 = QGraphicsDropShadowEffect()
        shadow2.setBlurRadius(20)
        shadow2.setXOffset(1)
        shadow2.setYOffset(1)
        shadow2.setColor(QColor('black'))

        shadow3 = QGraphicsDropShadowEffect()
        shadow3.setBlurRadius(20)
        shadow3.setXOffset(1)
        shadow3.setYOffset(1)
        shadow3.setColor(QColor('black'))

        # Thêm hiệu ứng shadow vào label
        self.label.setGraphicsEffect(shadow1)
        self.label_depth.setGraphicsEffect(shadow2)
        self.checkbox.setGraphicsEffect(shadow3)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.setStyleSheet(
            f"QPushButton {{ background-color:rgb(176,196,222) ; color:#000 ; font-size: 14px; }}"
            f"QPushButton:hover {{ border: 3px solid rgb(105,105,105); }}"  # Add hover effect if desired
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        spacer = QSpacerItem(0, 0, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)

        bg_layout = QVBoxLayout()
        self.label_image = QLabel(self)
        self.label_image.move(-28, 0) 
        self.label_image.setStyleSheet("background-image : url(chess.png);")
        self.label_image.resize(490, 480)
        opacity_effect = QGraphicsOpacityEffect()
        opacity_effect.setOpacity(0.9) 
        self.label_image.setGraphicsEffect(opacity_effect)
        bg_layout.addWidget(self.label_image)
        layout.addChildLayout(bg_layout)
        layout.addWidget(self.checkbox)

        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()

        # Thêm các widget vào hbox
        hbox1.addWidget(self.label_depth)
        hbox1.addWidget(self.depth_input)

        # Thêm các widget vào hbox
        hbox2.addWidget(self.label)
        hbox2.addWidget(self.dropdown)
        
        # Thêm hbox vào layout chính
        layout.addLayout(hbox1)
        layout.addLayout(hbox2)

        layout.addWidget(self.button_box)
        
        self.setLayout(layout)
        # Đặt kích thước cố định cho cửa sổ
        self.setFixedSize(450, 450)

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

