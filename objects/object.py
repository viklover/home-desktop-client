
class Object:

    def __init__(self, window, config):
        self.id = int(config['id'])
        self.type = config['type']

        self.pyqt_object = None

        self.window = window
        self.widget = window.content

    def set_pyqt_object(self, q_obj):
        self.pyqt_object = q_obj
