
import os
import json

from .pyqt_objects import Label, Picture

from .tobject import TObject
from .vobject import VObject


class ObjectManager:
    CONFIG = json.load(open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs", "objects.json")))

    OBJECT_TYPES = {
        'tobject': 'TObject',
        'vobject': 'VObject'
    }

    PYQT_OBJECT_TYPES = {
        'pictures': 'Picture',
        'labels': 'Label'
    }

    def __init__(self, window):
        self.window = window

        self.objects = {}

    def init_labels(self):
        self.init_pyqt_objects('labels')

    def init_pictures(self):
        self.init_pyqt_objects('pictures')

    def init_pyqt_objects(self, object_type):

        for config in ObjectManager.CONFIG[object_type]:
            if 'id' in config and 'type' in config:
                if config['type'] in ObjectManager.OBJECT_TYPES:
                    obj = eval(f'{ObjectManager.OBJECT_TYPES[config["type"]]}(self.window, config)')
                    obj.init_pyqt_object(config, object_type)
                    self.add_object(obj)
            else:
                eval(f'{ObjectManager.PYQT_OBJECT_TYPES[object_type]}(self.window.content, config)')

    def add_object(self, obj):
        self.objects[obj.id] = obj

    def process_event(self, event):
        if int(event['id']) in self.objects:
            self.objects[int(event['id'])].process_event(event)
