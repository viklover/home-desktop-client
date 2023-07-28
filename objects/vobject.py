from objects import Label
from objects.object import Object


class VObject(Object):

    def __init__(self, window, config):
        super(VObject, self).__init__(window, config)

        self.vector = 3
        self.value = None

    def init_pyqt_object(self, config, object_type='label'):
        pyqt_obj = None

        if object_type == 'labels':
            pyqt_obj = Label(self.widget, config)

        self.set_pyqt_object(pyqt_obj)

    def set_value(self, array):
        status, value, vector, stats, date = array

        if status:
            self.value = value
            self.vector = vector

        self.update_pyqt_object()

    def process_event(self, event):

        if not event['success']:
            self.value = None
            self.vector = 3
        else:
            self.value = event['value']
            self.vector = event['vector']

        self.update_pyqt_object()

    def update_pyqt_object(self):

        vector_str = {
            0: '↓',
            1: '↑',
            2: '',
            3: ''
        }

        if isinstance(self.pyqt_object, Label):

            text = "--"

            if self.value is not None:
                text = str(self.value) + vector_str[self.vector]

            self.pyqt_object.update_text(text)

        self.widget.update()

