from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLineEdit, QLayout, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtCore import QThread, pyqtSignal, QObject, pyqtSlot, Qt

import sys
import random
import numpy as np


class Checkers(QMainWindow):
    def __init__(self):
        super().__init__()
        self.game_size = (8, 8)
        self.coordinates_black_checkers = {}
        self.coordinates_white_checkers = {}
        self.number_black_checkers = 12
        self.number_white_checkers = 12
        self.get_first_coordinates()
        self.get_board_gui()
        self.get_checkers_gui()

    def get_first_coordinates(self):
        for i in range(8):
            for j in range(3):
                if i % 2 == 0 and j % 2 != 0 or i % 2 != 0 and j % 2 == 0:
                    self.coordinates_black_checkers[(i, j)] = None

        for i in range(8):
            for j in range(5, 8):
                if i % 2 == 0 and j % 2 != 0 or i % 2 != 0 and j % 2 == 0:
                    self.coordinates_white_checkers[(i, j)] = None

    def get_checkers_gui(self):
        self.white_checkers_btn = np.zeros(self.game_size, dtype=QPushButton)
        self.black_checkers_btn = np.zeros(self.game_size, dtype=QPushButton)
        for i in range(self.game_size[0]):
            for j in range(self.game_size[1]):
                if (i, j) in list(self.coordinates_white_checkers.keys()):
                    btn = QPushButton(f'', self)
                    btn.setGeometry(i * 100, j * 100, 50, 50)
                    btn.setStyleSheet(
                        "background-color: white; font-size: 40px; font-weight: bold")
                    self.white_checkers_btn[i, j] = btn
                if (i, j) in list(self.coordinates_black_checkers.keys()):
                    btn = QPushButton(f'', self)
                    btn.setGeometry(i * 100, j * 100, 50, 50)
                    btn.setStyleSheet(
                        "background-color: yellow; font-size: 40px; font-weight: bold, background-image : url(unnamed.png);")
                    self.black_checkers_btn[i, j] = btn
        self.showFullScreen()

    def get_board_gui(self):
        self.btns = np.zeros(self.game_size, dtype=QPushButton)
        for i in range(self.game_size[0]):
            for j in range(self.game_size[1]):
                btn = QPushButton(f'', self)
                btn.setGeometry(i * 100, j * 100, 100, 100)
                btn = self.paint_over(btn, i, j)
                self.btns[i][j] = btn

    def paint_over(self, btn, i, j):
        if i % 2 == 0 and j % 2 == 0:
            btn.setStyleSheet("background-color: white; font-size: 20px; font-weight: bold")
        if i % 2 == 0 and j % 2 != 0:
            btn.setStyleSheet("background-color: black; font-size: 20px; font-weight: bold")
        if i % 2 != 0 and j % 2 != 0:
            btn.setStyleSheet("background-color: white; font-size: 20px; font-weight: bold")
        if i % 2 != 0 and j % 2 == 0:
            btn.setStyleSheet("background-color: black; font-size: 20px; font-weight: bold")
        return btn


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Checkers()
    sys.exit(app.exec_())
