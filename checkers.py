import threading
from copy import deepcopy

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
from PyQt5 import uic, QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal, QObject, pyqtSlot, Qt, QSize
import pickle
import socket
import time
from threading import Thread

import sys
import random
import numpy as np

SIZE_OF_PART = 1024


class Button:
    def __init__(self):
        self.__btn = None
        self.__x = None
        self.__y = None

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @property
    def btn(self):
        return self.__btn

    @x.setter
    def x(self, x):
        self.__x = x

    @y.setter
    def y(self, y):
        self.__y = y

    @btn.setter
    def btn(self, btn):
        self.__btn = btn


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
        self.sell_btns = {}
        self.checker_btn = None
        self.cell_btn = None
        self.number_black_checkers = 12
        self.number_white_checkers = 12
        self.get_first_coordinates()
        self.get_gui()
        self.btn = None
        self.resize(800, 800)
        self.setWindowTitle("Checkers Online")
        self.setWindowIcon(QtGui.QIcon("images.png"))
        self.show()

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
        for i in range(self.game_size[0]):
            for j in range(self.game_size[1]):
                if i % 2 == 0 and j % 2 != 0 or i % 2 != 0 and j % 2 == 0:
                    btn = Button()
                    btn.btn = QPushButton(f"", self)
                    btn.btn.setGeometry(i * 100, j * 100, 100, 100)
                    if (i, j) in list(self.coordinates_white_checkers.keys()):
                        self.coordinates_white_checkers[(i, j)] = btn
                        btn.btn.setStyleSheet("background-color: red; ")
                        btn.btn.setIcon(QIcon("белая_шашка.png"))
                        btn.btn.setIconSize(QSize(100, 100))
                        btn.btn.clicked.connect(
                            lambda state, obj=btn: self.catch_button_checkers(
                                obj, "white"
                            )
                        )
                    elif (i, j) in list(self.coordinates_black_checkers.keys()):
                        self.coordinates_black_checkers[(i, j)] = btn
                        btn.btn.setStyleSheet("background-color: red; ")
                        btn.btn.setIcon(QIcon("черная_шашка.png"))
                        btn.btn.setIconSize(QSize(100, 100))
                        btn.btn.clicked.connect(
                            lambda state, obj=btn: self.catch_button_checkers(
                                obj, "black"
                            )
                        )
                    else:
                        self._paint_over(btn.btn)
                        btn.btn.clicked.connect(
                            lambda state, obj=btn: self.catch_button_cells(obj)
                        )
                        self.sell_btns[(i, j)] = btn
                    btn.x = i
                    btn.y = j
                else:
                    btn = QPushButton(f"", self)
                    btn.setGeometry(i * 100, j * 100, 100, 100)
                    btn.setStyleSheet("background-color: #F0F8FF")

    def _paint_over(self, btn):
        btn.setStyleSheet("background-color: red; ")
        btn.setIcon(QIcon("K.png"))
        btn.setIconSize(QSize(200, 200))

    def catch_button_checkers(self, btn, collor):
        self.checker_btn = (btn, btn.x, btn.y, collor)

    def catch_button_cells(self, btn):
        self.cell_btn = (btn, btn.x, btn.y)
        if self.checker_btn != None:
            self.change_coordinates()

    def permission_kill_checkers(self):
        print(self.checker_btn, self.cell_btn)
        if (
                self.checker_btn[-1] == "white"
                and (self.checker_btn[1] + 1, self.checker_btn[2] - 1)
                in self.coordinates_black_checkers.keys()
                and (self.checker_btn[1] + 2, self.checker_btn[2] - 2) in self.sell_btns
                and self.cell_btn[0]
                == self.sell_btns[(self.checker_btn[1] + 2, self.checker_btn[2] - 2)]
            ):
    def black_move(self, checker_btn, cell_btn):
        if checker_btn[-1] == "black":
            return cell_btn[2] == checker_btn[2] + 1 and (
                    cell_btn[1] == checker_btn[1] + 1 or cell_btn[1] == checker_btn[1] - 1
            )
        return True

    def white_move(self, checker_btn, cell_btn):
        if checker_btn[-1] == "white":
            return cell_btn[2] == checker_btn[2] - 1 and (
                    cell_btn[1] == checker_btn[1] + 1 or cell_btn[1] == checker_btn[1] - 1
            )
        return True

    def change_coordinates(self):
        if self.color != None and self.permission_change_main_checker:
            if (
                    self.black_move(self.checker_btn, self.cell_btn)
                    and self.white_move(self.checker_btn, self.cell_btn)
            ) or self.permission_kill_checkers():
                if (
                        self.color == self.checker_btn[-1]
                        or self.permission_change_stranger_checker
                ):
                    collor = self.checker_btn[-1]
                    x_checker = self.checker_btn[1]
                    y_checker = self.checker_btn[2]
                    x_cell = self.cell_btn[1]
                    y_cell = self.cell_btn[2]
                    btn = self.checker_btn[0].btn
                    btn.setGeometry(x_cell * 100, y_cell * 100, 100, 100)
                    self.cell_btn[0].btn.setGeometry(
                        x_checker * 100, y_checker * 100, 100, 100
                    )
                    self.checker_btn[0].x = x_cell
                    self.checker_btn[0].y = y_cell
                    self.cell_btn[0].x = x_checker
                    self.cell_btn[0].y = y_checker
                    del self.sell_btns[(x_cell, y_cell)]
                    self.sell_btns[(x_checker, y_checker)] = self.cell_btn[0]
                    if self.checker_btn[3] == "black":
                        del self.coordinates_black_checkers[(x_checker, y_checker)]
                        self.coordinates_black_checkers[
                            (x_cell, y_cell)
                        ] = self.checker_btn[0]
                    if self.checker_btn[3] == "white":
                        del self.coordinates_white_checkers[(x_checker, y_checker)]
                        self.coordinates_white_checkers[
                            (x_cell, y_cell)
                        ] = self.checker_btn[0]
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
                cell_btn = self.data.sell_btns[
                    (data["cell_btn"][0], data["cell_btn"][1])
                ]
                if self.data.color == "white":
                    checker_btn = self.data.coordinates_black_checkers[
                        (data["checker_btn"][0], data["checker_btn"][1])
                    ]
                    self.data.catch_button_checkers(
                        checker_btn,
                        "black",
                    )
                else:
                    checker_btn = self.data.coordinates_white_checkers[
                        (data["checker_btn"][0], data["checker_btn"][1])
                    ]
                    self.data.catch_button_checkers(
                        checker_btn,
                        "white",
                    )
                thread = Thread(
                    target=self.data.catch_button_cells,
                    args=(cell_btn,),
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
    sys.exit(app.exec_())
