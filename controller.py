import time

from PyQt5 import QtCore
from PyQt5.QtCore import QThread

from threading import Thread

from events import EventsManager


class Controller(QThread):

    events_signal = QtCore.pyqtSignal(dict)
    init_objects_signal = QtCore.pyqtSignal(dict)

    def __init__(self, window):
        super(Controller, self).__init__(window)
        self.daemon = True
        self.name = "Controller Thread"

        self.window = window
        self.event_manager = EventsManager(self)

    def run(self):

        while not self.window.SHUTDOWN:
            controller = self.event_manager.next_controller()

            self.window.show_message(f'Попытка соединения через {controller.name}..')

            if controller.init_connection():
                self.window.show_message('Получаю информацию об объектах..')
                controller.init_objects()
                self.window.show_message('Соединение установлено')

                for event in self.event_manager.get_updates():
                    self.events_signal.emit(event)

            controller.shutdown()

            time.sleep(2)

        self.event_manager.shutdown()
