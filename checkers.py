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
        client.data = self
        self.permission_change_stranger_checker = False
        self.permission_change_main_checker = True
        self.permission_send = True
        self.color = None
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
        self.btns = np.zeros(self.game_size, dtype=QPushButton)
        for i in range(self.game_size[0]):
            for j in range(self.game_size[1]):
                btn = QPushButton(f"", self)
                btn.setGeometry(i * 100, j * 100, 100, 100)
                if (i, j) in self.coordinates_white_checkers:
                    self.coordinates_white_checkers[(i, j)] = btn
                    btn.setStyleSheet(f"background-color: white;")
                    btn.clicked.connect(
                        lambda state, obj=btn, i=i, j=j: self.catch_button_checkers(
                            obj, i, j, "white"
                        )
                    )
                elif (i, j) in self.coordinates_black_checkers:
                    self.coordinates_black_checkers[(i, j)] = btn
                    btn.setStyleSheet(f"background-color: black;")
                    btn.clicked.connect(
                        lambda state, obj=btn, i=i, j=j: self.catch_button_checkers(
                            obj, i, j, "black"
                        )
                    )
                else:
                    self._paint_over(btn, i, j)
                    btn.clicked.connect(
                        lambda state, obj=btn, i=i, j=j: self.catch_button_cells(
                            obj, i, j
                        )
                    )
                self.btns[i][j] = btn
        self.show()

    def _paint_over(self, btn, i, j):
        if i % 2 == 0 and j % 2 != 0:
            btn.setStyleSheet("background-color: red; ")
        elif i % 2 != 0 and j % 2 == 0:
            btn.setStyleSheet("background-color: red; ")
        else:
            btn.deleteLater()

    def catch_button_checkers(self, btn, x, y, collor):
        self.checker_btn = (btn, x, y, collor)

    def catch_button_cells(self, btn, x, y):
        self.cell_btn = (btn, x, y)
        if self.checker_btn != None:
            self.change_coordinates()

    def change_coordinates(self):
        print((self.cell_btn[1], self.cell_btn[-1]) in self.coordinates_black_checkers)
        print((self.cell_btn[1], self.cell_btn[-1]) in self.coordinates_white_checkers)
        print(self.permission_change_main_checker)
        if (
            (self.cell_btn[1], self.cell_btn[-1]) not in self.coordinates_black_checkers
            and (self.cell_btn[1], self.cell_btn[-1])
            not in self.coordinates_white_checkers
            and self.color != None
            and self.permission_change_main_checker
        ):
            if (
                self.color == self.checker_btn[-1]
                or self.permission_change_stranger_checker
            ):
                collor = self.checker_btn[-1]
                x_checker = self.checker_btn[1]
                y_checker = self.checker_btn[2]
                x_cell = self.cell_btn[1]
                y_cell = self.cell_btn[2]
                btn = self.checker_btn[0]
                btn.setStyleSheet("background-color: red;")
                if self.checker_btn[3] == "black":
                    self.cell_btn[0].setStyleSheet("background-color: black;")
                    del self.coordinates_black_checkers[(x_checker, y_checker)]
                    self.coordinates_black_checkers[(x_cell, y_cell)] = btn
                if self.checker_btn[3] == "white":
                    self.cell_btn[0].setStyleSheet("background-color: white;")
                    del self.coordinates_white_checkers[(x_checker, y_checker)]
                    self.coordinates_white_checkers[(x_cell, y_cell)] = btn
                if self.permission_send:
                    thread = Thread(target=self.client.send)
                    thread.start()
                    time.sleep(0.4)
                    thread.join()
                self.permission_change_stranger_checker = False
                self.permission_send = True
                self.checker_btn = None


class Client:
    def __init__(self, ip, port):
        self.connect(ip, port)
        self.data = None

    def recieve(self):
        msg = self.sock.recv(SIZE_OF_PART)
        return pickle.loads(msg)

    def send(self):
        self.data.permission_change_main_checker = False
        self.sock.send(
            pickle.dumps(
                {
                    "coordinates_black_checkers": list(
                        self.data.coordinates_black_checkers
                    ),
                    "coordinates_white_checkers": list(
                        self.data.coordinates_white_checkers
                    ),
                    "number_black_checkers": self.data.number_black_checkers,
                    "number_white_checkers": self.data.number_white_checkers,
                    "checker_btn": self.data.checker_btn[1:],
                    "cell_btn": self.data.cell_btn[1:],
                }
            )
        )

    def read_socket(self):
        while True:
            data = self.recieve()
            if data in ("white", "black"):
                time.sleep(0.09)
                self.data.color = data
            else:
                self.data.permission_change_main_checker = True
                self.data.permission_change_stranger_checker = True
                self.data.permission_send = False
                cell_btn = self.data.btns[data["cell_btn"][0]][data["cell_btn"][1]]
                if self.data.color == "white":
                    checker_btn = self.data.coordinates_black_checkers[
                        (data["checker_btn"][0], data["checker_btn"][1])
                    ]
                    self.data.catch_button_checkers(
                        checker_btn,
                        data["checker_btn"][0],
                        data["checker_btn"][1],
                        "black",
                    )
                else:
                    checker_btn = self.data.coordinates_white_checkers[
                        (data["checker_btn"][0], data["checker_btn"][1])
                    ]
                    self.data.catch_button_checkers(
                        checker_btn,
                        data["checker_btn"][0],
                        data["checker_btn"][1],
                        "white",
                    )
                thread = Thread(
                    target=self.data.catch_button_cells,
                    args=(
                        cell_btn,
                        data["cell_btn"][0],
                        data["cell_btn"][1],
                    ),
                )
                thread.start()
                thread.join()

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
    w.resize(800, 800)
    w.setWindowTitle("Checkers Online")
    sys.exit(app.exec_())
