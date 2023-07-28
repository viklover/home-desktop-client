
import json
import datetime

from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow, QAction, QWidget

from controller import Controller
from objects import ObjectManager

from path import path_to


class Window(QMainWindow):

    CONFIG = json.load(open(path_to("configs", "window.json")))

    SHUTDOWN = False

    AUDIO_MUTED = False

    def __init__(self):
        super(QMainWindow, self).__init__()

        self.content = QWidget()
        self.setCentralWidget(self.content)

        self.controller = Controller(self)
        self.controller.events_signal.connect(self.process_events, Qt.QueuedConnection)
        self.controller.init_objects_signal.connect(self.init_object_values, Qt.QueuedConnection)

        self.object_manager = ObjectManager(self)

        self.setWindowTitle("Home")
        self.setWindowIcon(QtGui.QIcon(path_to('configs', 'pictures', 'icon.ico')))
        self.setMinimumSize(*Window.CONFIG['size'])
        
        self.setStyleSheet("background-color: white; color: black;")

        self.statusBar().showMessage('Запуск...')

        self.first = True

        self.initUI()

    def initUI(self):

        audioAction = QAction(QIcon(''), 'Без звука', self)
        audioAction.setCheckable(True)
        audioAction.setChecked(False)
        audioAction.triggered.connect(self.set_audio_mute)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&Меню')
        fileMenu.addAction(audioAction)

        self.object_manager.init_pictures()
        self.object_manager.init_labels()

    def get_content_widget(self):
        return self.content

    def process_events(self, event):
        self.object_manager.process_event(event['content'])

        strf_time = datetime.datetime.fromtimestamp(event["content"]["time"]).strftime("%H:%M:%S")
        connector_name = self.controller.event_manager.current_connector.name
        self.show_message(f'Обновлено - {strf_time} ({connector_name})')

        self.update()

    def init_object_values(self, data):

        for type_obj in data:
            for class_obj in data[type_obj]:
                for obj in data[type_obj][class_obj]:
                    if int(obj) in self.object_manager.objects:
                        self.object_manager.objects[int(obj)].set_value(data[type_obj][class_obj][obj])

    @staticmethod
    def set_audio_mute(value):
        Window.AUDIO_MUTED = value

    def show_message(self, message):
        self.statusBar().showMessage(message)
        self.update()

    def show(self):
        self.controller.start()
        super().show()

    def update(self):
        self.content.update()
        super().update()

    def closeEvent(self, event):
        Window.SHUTDOWN = True
