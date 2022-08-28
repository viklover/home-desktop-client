import os
import json
import time
import random

from threading import Thread, Lock


class BaseConnector:
    SOCKET_CONFIG = None
    VK_CONFIG = None

    class ReceivingChannel(Thread):

        def __init__(self, connector):
            super(BaseConnector.ReceivingChannel, self).__init__()
            self.name = 'ReceivingChannel'
            self.daemon = True
            self.status = True

            self.connector = connector

    class IsAliveThread(Thread):

        def __init__(self, connector):
            super(BaseConnector.IsAliveThread, self).__init__()
            self.daemon = True
            self.name = 'IsAliveThread'

            self.connector = connector
            self.status = True

            self.sleep = 60
            self.timeout = 10

        def run(self):

            while self.status:

                while time.time() - self.connector.last_response_time < 20:
                    time.sleep(1)

                if not self.connector.get_response(self.connector.send_request({"request": "is_alive"}),
                                                   timeout=self.timeout):
                    self.connector.connected = False

    def __init__(self, controller):
        config = json.load(open(os.path.join(os.path.dirname(os.path.dirname(__file__)), "configs", "connectors.json")))
        BaseConnector.SOCKET_CONFIG = config['socket']
        BaseConnector.VK_CONFIG = config['vk']

        self.controller = controller

        self.tasks_lock = Lock()

        self.tasks_buffer = []
        self.timeout = 10

        self.last_response_time = None

        self.request_ids = []
        self.responses = []
        self.events = []

        self.status = True
        self.connected = False
        self.values_accepted = False

        self.alive_thread = None
        self.receiving_sock = None

        self.thread = None

    def has_connection(self):
        return self.connected

    def shutdown(self):

        if not self.receiving_sock is None and self.receiving_sock.is_alive():
            self.receiving_sock.status = False
            self.receiving_sock.join()

        if not self.alive_thread is None and self.alive_thread.is_alive():
            self.alive_thread.status = False
            self.alive_thread.join()

        self.status = False
        if not self.thread is None and self.thread.is_alive():
            self.thread.join()

    def init_connection(self):
        self.status = True
        self.values_accepted = False

    def start_io_threads(self):

        self.thread = Thread(target=self.process_tasks, daemon=True)
        self.thread.start()

        self.receiving_sock = self.ReceivingChannel(self)
        self.receiving_sock.start()

    def start_alive_thread(self):

        self.alive_thread = self.IsAliveThread(self)
        self.alive_thread.start()

    def send_request(self, request):
        request['id'] = random.randint(11111, 99999)
        request['api'] = 1.0
        self.add_task(request)
        return request['id']

    def get_response(self, request_id, timeout=10):

        attempts = 0

        while not any('id' in task and request_id == task['id'] for task in self.responses) and \
                attempts < timeout:
            attempts += 1
            time.sleep(1)

        task = list(filter(lambda x: 'id' in x and request_id == x['id'], self.responses))

        if len(task):
            self.responses.remove(task[0])
            return task[0]

        return None

    def add_task(self, task, args=None, kwargs=None, timeout=20):

        if args is None:
            args = []

        if kwargs is None:
            kwargs = {}

        marked = None

        self.tasks_lock.acquire()
        self.tasks_buffer.append([task, args, kwargs, timeout, marked])
        self.request_ids.append(task['id'])
        self.tasks_lock.release()

        return len(self.tasks_buffer)

    def process_tasks(self):

        while self.status:
            self.execute_tasks()
            time.sleep(0.5)

    def execute_tasks(self):
        self.tasks_lock.acquire()

        for index, task in enumerate(self.tasks_buffer):

            task_body, args, kwargs, timeout, marked = task

            if marked is not None and time.time() - marked > timeout:
                del self.tasks_buffer[index]
                self.request_ids.remove(task_body['id'])
                continue

            print('Request:', task_body)
            if self.process_task(task_body, args, kwargs):
                del self.tasks_buffer[index]
            elif marked is None:
                task[-1] = time.time()

        self.tasks_lock.release()

    def init_objects(self):
        values = self.get_response(self.send_request({'request': 'get_values'}), 30)

        if not values:
            self.connected = False
            return

        self.controller.init_objects_signal.emit(values['objects'])
        self.controller.window.update()

        self.values_accepted = True

    def get_updates(self):
        while self.has_connection():
            for event in self.events:
                self.events.remove(event)
                yield event
            time.sleep(0.5)
