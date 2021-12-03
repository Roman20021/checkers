from PyQt5.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton, QLineEdit, QLayout, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtCore import QThread, pyqtSignal, QObject, pyqtSlot, Qt

import sys
import random
import numpy as np


class MechanicsHeckers:
    def __init__(self, coordinates_white_checkers, coordinates_black_checkers):
        self.coordinates_black_checkers = coordinates_black_checkers
        self.coordinates_white_checkers = coordinates_white_checkers
        self.checker_btn = None
        self.cell_btn = None

    def catch_button_checkers(self, btn, x, y, collor):
        self.checker_btn = (btn, x, y, collor)

    def catch_button_cells(self, btn, x, y):
        self.cell_btn = (btn, x, y)
        if self.checker_btn != None:
            self.change_coordinates()


    def change_coordinates(self):
        if self.cell_btn != None and self.checker_btn != None:
            x_checker = self.checker_btn[1]
            y_checker = self.checker_btn[2]
            x_cell = self.cell_btn[1]
            y_cell = self.cell_btn[2]
            if self.checker_btn[3] == 'black':
                del self.coordinates_black_checkers[(x_checker, y_checker)]
                self.coordinates_black_checkers[(x_cell, y_cell)] = self.checker_btn[0]
            if self.checker_btn[3] == 'white':
                del self.coordinates_black_checkers[(x_checker, y_checker)]
                self.coordinates_black_checkers[(x_cell, y_cell)] = self.checker_btn[0]
            self.checker_btn = None
            self.cell_btn = None


class GuiHeckers(QMainWindow):
    def __init__(self):
        super().__init__()
        self.game_size = (8, 8)
        self.coordinates_black_checkers = {}
        self.coordinates_white_checkers = {}
        self.number_black_checkers = 12
        self.number_white_checkers = 12
        self.get_first_coordinates()
        self.get_gui()
        self.mechanic = MechanicsHeckers(self.coordinates_white_checkers, self.coordinates_black_checkers)
        self.push_button()

    def get_first_coordinates(self):
        for i in range(8):
            for j in range(3):
                if i % 2 == 0 and j % 2 != 0 or i % 2 != 0 and j % 2 == 0:
                    self.coordinates_black_checkers[(i, j)] = None

        for i in range(8):
            for j in range(5, 8):
                if i % 2 == 0 and j % 2 != 0 or i % 2 != 0 and j % 2 == 0:
                    self.coordinates_white_checkers[(i, j)] = None

    def get_gui(self):
        self.white_checkers_btns = np.zeros(self.game_size, dtype=QPushButton)
        self.black_checkers_btns = np.zeros(self.game_size, dtype=QPushButton)
        self.btns = np.zeros(self.game_size, dtype=QPushButton)

        for i in range(self.game_size[0]):
            for j in range(self.game_size[1]):
                btn = QPushButton(f'', self)
                btn.setGeometry(i * 100, j * 100, 100, 100)
                btn = self._paint_over(btn, i, j)
                btn.clicked.connect(
                    lambda state, obj=btn, i=i, j=j: self.mechanic.catch_button_cells(obj, i, j))
                if (i, j) in list(self.coordinates_white_checkers.keys()):
                    btn_checker = self._paint_checkers('white', i, j)
                    self.white_checkers_btns[i, j] = btn_checker
                    btn_checker.clicked.connect(
                        lambda state, obj=btn_checker: self.mechanic.catch_button_checkers(obj, i, j, 'white'))
                if (i, j) in list(self.coordinates_black_checkers.keys()):
                    btn_checker = self._paint_checkers('black', i, j)
                    self.black_checkers_btns[i, j] = btn_checker
                    btn_checker.clicked.connect(
                        lambda state, obj=btn_checker, i=i, j=j: self.mechanic.catch_button_checkers(obj, i, j,
                                                                                                     'black'))
                self.btns[i][j] = btn
        self.showFullScreen()

    def _paint_over(self, btn, i, j):
        if i % 2 == 0 and j % 2 == 0:
            btn.setStyleSheet("background-color: white; font-size: 20px; font-weight: bold")
        if i % 2 == 0 and j % 2 != 0:
            btn.setStyleSheet("background-color: gray; font-size: 20px; font-weight: bold")
        if i % 2 != 0 and j % 2 != 0:
            btn.setStyleSheet("background-color: white; font-size: 20px; font-weight: bold")
        if i % 2 != 0 and j % 2 == 0:
            btn.setStyleSheet("background-color: gray; font-size: 20px; font-weight: bold")
        return btn

    def _paint_checkers(self, collor, i, j):
        btn = QPushButton(f'', self)
        btn.setGeometry(i * 100, j * 100, 50, 50)
        btn.setStyleSheet(
            f"background-color: {collor}; font-size: 40px; font-weight: bold")
        return btn

    def push_button(self):

        if self.mechanic.checker_btn != None and self.mechanic.cell_btn != None:
            self.coordinates_black_checkers = self.mechanic.coordinates_black_checkers
            self.coordinates_white_checkers = self.mechanic.coordinates_white_checkers
            self.get_gui()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = GuiHeckers()
    sys.exit(app.exec_())
