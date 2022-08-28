import os

from PIL import Image
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QLabel


class Label:

    def __init__(self, widget, config, default_text='--'):
        self.body = QLabel(widget)
        self.body.setFont(QFont(*config['font']))
        self.body.setGeometry(*config['position'], 1400, int(config['font'][1]*2))

        if 'text' in config:
            self.body.setText(config['text'])
        else:
            self.body.setText(default_text)

    def update_text(self, text):
        self.body.setText(text)


class Picture:

    def __init__(self, widget, config):
        self.body = QLabel(widget)

        self.prepared_pixmaps = []
        self.prepared_paths = []

        self.scale = 1.0

        if "paths" in config:
            self.prepared_paths.extend(config['paths'])

        if "path" in config:
            self.prepared_paths.append(config['path'])

        if "scale" in config:
            self.scale = config['scale']

        if 'size' in config:
            self.size = config['size']
        elif os.path.isfile(os.path.join("configs", "pictures", self.prepared_paths[0])):
            self.size = [w, h] = Image.open(os.path.join("configs", "pictures", self.prepared_paths[0])).size
        else:
            self.size = [0, 0]

        self.size = list(map(lambda x: int(x * self.scale), self.size))

        self.position = config['position']

        for path in self.prepared_paths:
            self.prepared_pixmaps.append(
                Picture.create_pixmap(os.path.join("configs", "pictures", path), self.size)
            )

        self.set_pixmap(self.prepared_pixmaps[0])

    def set_pixmap(self, pixmap):
        self.body.setPixmap(pixmap)
        self.body.setGeometry(*self.position, *self.size)

    def set_pixmap_from_prepared_list(self, num):
        if len(self.prepared_pixmaps) - 1 >= num:
            self.set_pixmap(self.prepared_pixmaps[num])

    @staticmethod
    def create_pixmap(path, size=None):
        if size is None:
            size = [0, 0]
        pixmap = QPixmap(path)
        return pixmap.scaled(*size, Qt.KeepAspectRatio)

