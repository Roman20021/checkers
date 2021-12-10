import threading

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QMainWindow,
    QPushButton,
    QLineEdit,
    QLayout,
    QMessageBox,
)
from PyQt5.QtGui import QIcon
from PyQt5 import uic, QtWidgets, QtCore
from PyQt5.QtCore import QThread, pyqtSignal, QObject, pyqtSlot, Qt
import pickle
import socket
import time
from threading import Thread

import sys
import random
import numpy as np

SIZE_OF_PART = 1024


class GuiCheckers(QWidget):
    def __init__(self, client):
        super().__init__()
        self.client = client
        self.game_size = (8, 8)
        self.coordinates_black_checkers = {}
        self.coordinates_white_checkers = {}
        self.checker_btn = None
        self.cell_btn = None
        self.number_black_checkers = 12
        self.number_white_checkers = 12
        self.get_first_coordinates()
        self.get_gui()

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
                btn = QPushButton(f"", self)
                btn.setGeometry(i * 100, j * 100, 100, 100)
                btn = self._paint_over(btn, i, j)
                btn.clicked.connect(
                    lambda state, obj=btn, i=i, j=j: self.catch_button_cells(obj, i, j)
                )
                if (i, j) in list(self.coordinates_white_checkers.keys()):
                    btn_checker = self._paint_checkers("white", i, j)
                    self.white_checkers_btns[i, j] = btn_checker
                    self.coordinates_white_checkers[(i, j)] = btn_checker
                    btn_checker.clicked.connect(
                        lambda state, obj=btn_checker, i=i, j=j: self.catch_button_checkers(
                            obj, i, j, "white"
                        )
                    )
                    btn_checker.show()
                if (i, j) in list(self.coordinates_black_checkers.keys()):
                    btn_checker = self._paint_checkers("black", i, j)
                    self.black_checkers_btns[i, j] = btn_checker
                    self.coordinates_black_checkers[(i, j)] = btn_checker
                    btn_checker.clicked.connect(
                        lambda state, obj=btn_checker, i=i, j=j: self.catch_button_checkers(
                            obj, i, j, "black"
                        )
                    )
                    btn_checker.show()
                self.btns[i][j] = btn
        self.show()

    def _paint_over(self, btn, i, j):
        if i % 2 == 0 and j % 2 == 0:
            btn.setStyleSheet(
                "background-color: white; font-size: 20px; font-weight: bold"
            )
        if i % 2 == 0 and j % 2 != 0:
            btn.setStyleSheet(
                "background-color: gray; font-size: 20px; font-weight: bold"
            )
        if i % 2 != 0 and j % 2 != 0:
            btn.setStyleSheet(
                "background-color: white; font-size: 20px; font-weight: bold"
            )
        if i % 2 != 0 and j % 2 == 0:
            btn.setStyleSheet(
                "background-color: gray; font-size: 20px; font-weight: bold"
            )
        return btn

    def _paint_checkers(self, collor, i, j):
        btn = QPushButton(f"", self)
        btn.setGeometry(i * 100, j * 100, 50, 50)
        btn.setStyleSheet(
            f"background-color: {collor}; font-size: 40px; font-weight: bold"
        )
        return btn

    def catch_button_checkers(self, btn, x, y, collor):
        self.checker_btn = (btn, x, y, collor)

    def catch_button_cells(self, btn, x, y):
        self.cell_btn = (btn, x, y)
        if self.checker_btn != None:
            self.change_coordinates()

    def change_coordinates(self):
        if (self.cell_btn[1], self.cell_btn[-1]) not in list(
            self.coordinates_black_checkers.keys()
        ) and (self.cell_btn[1], self.cell_btn[-1]) not in list(
            self.coordinates_white_checkers.keys()
        ):
            collor = self.checker_btn[-1]
            x_checker = self.checker_btn[1]
            y_checker = self.checker_btn[2]
            x_cell = self.cell_btn[1]
            y_cell = self.cell_btn[2]
            self.checker_btn[0].deleteLater()
            btn = self._paint_checkers(self.checker_btn[-1], x_cell, y_cell)
            btn.show()
            del_btn = self.checker_btn[0]
            del_btn.deleteLater()
            if self.checker_btn[3] == "black":
                del self.coordinates_black_checkers[(x_checker, y_checker)]
                self.coordinates_black_checkers[(x_cell, y_cell)] = btn
            if self.checker_btn[3] == "white":
                del self.coordinates_white_checkers[(x_checker, y_checker)]
                self.coordinates_white_checkers[(x_cell, y_cell)] = btn
            self.checker_btn = None
            btn.clicked.connect(
                lambda state, obj=btn, i=x_cell, j=y_cell: self.catch_button_checkers(
                    obj, i, j, collor
                )
            )
            thread = Thread(target=self.client.send)
            thread.start()
            time.sleep(0.2)
            thread.join()


class Client:
    def __init__(self, ip, port):
        self.connect(ip, port)
        self.data = None

    def recieve(self):
        msg = self.sock.recv(SIZE_OF_PART)
        return pickle.loads(msg)

    def send(self):
        self.sock.send(pickle.dumps(self.data))

    def read_socket(self):
        while True:
            data = self.recieve()

    def loop(self):
        self.thread = Thread(target=self.read_socket)
        self.thread.start()

    def connect(self, ip, port):
        self.sock = socket.socket()
        self.sock.connect((ip, port))

        self.loop()

    def disconnect(self):
        self.thread.join()
        self.sock.close()


if __name__ == "__main__":
    client = Client("localhost", 8090)
    app = QApplication(sys.argv)
    w = GuiCheckers(client)
    client.data = w
    w.resize(800, 800)
    w.setWindowTitle("Checkers Online")
    sys.exit(app.exec_())
