
from . import Label, Picture
from .object import Object

from .audio import play_track


class TObject(Object):

    def __init__(self, window, config):
        super(TObject, self).__init__(window, config)

        self.tracks = [None, None]

        if 'audio' in config:
            self.tracks = config['audio']

        self.status = False

    def set_value(self, array):
        status, stats, date = array
        self.status = status
        self.update_pyqt_object()

    def init_pyqt_object(self, config, object_type='label'):
        pyqt_obj = None

        if object_type == 'labels':
            pyqt_obj = Label(self.widget, config, default_text='Off')
        elif object_type == 'pictures':
            pyqt_obj = Picture(self.widget, config)

        self.set_pyqt_object(pyqt_obj)

    def process_event(self, event):

        if event['status'] != self.status:
            self.status = event['status']
            self.update_pyqt_object()

            if not self.window.AUDIO_MUTED:
                play_track(self.tracks[int(self.status)])

    def update_pyqt_object(self):

        if isinstance(self.pyqt_object, Label):
            self.pyqt_object.update_text('On' if self.status else 'Off')

        elif isinstance(self.pyqt_object, Picture):
            self.pyqt_object.set_pixmap_from_prepared_list(int(self.status))

        self.widget.update()
