import os, sys

from PyQt5.QtWidgets import QApplication

from window import Window


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    import sys

    sys.excepthook = except_hook
    sys.path.append(os.path.abspath('path.py'))

    app = QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
