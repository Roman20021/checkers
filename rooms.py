from checkers import *


class Room(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(800, 800)
        self.setWindowTitle("Checkers Online")
        self.setWindowIcon(QtGui.QIcon("images.png"))
        self.resize(800, 800)
        self.room_btn()
        self.show()

    def room_btn(self):
        for i in range(1, 10):
            btn = QPushButton(f"{i} room", self)
            btn.setGeometry(800, 200 + 50 * i, 300, 50)
            btn.clicked.connect(
                lambda state, obj=i: self.connect_room(
                    obj
                )
            )

    def connect_room(self, port):
        client = Client("localhost", port)
        w = GuiCheckers(client)
        self.close()
