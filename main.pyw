import sys

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QApplication

from window import Window


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    import sys

    sys.excepthook = except_hook

    app = QApplication(sys.argv)
    window = Window()
    # window.controller.start()
    # window.controller.join()
    window.show()
    sys.exit(app.exec_())

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
