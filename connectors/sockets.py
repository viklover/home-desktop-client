import json
import select
import socket
import time

from connectors import BaseConnector


class SocketsConnector(BaseConnector):

    class ReceivingChannel(BaseConnector.ReceivingChannel):

        def __init__(self, connector):
            super(SocketsConnector.ReceivingChannel, self).__init__(connector)
            self.socket = connector.socket

        @staticmethod
        def recv_timeout(sock, bytes_to_read, timeout_seconds):
            sock.setblocking(0)
            ready = select.select([sock], [], [], timeout_seconds)
            if ready[0]:
                return sock.recv(bytes_to_read)

            return False

        def run(self):
            while self.status:
                try:
                    data = self.recv_timeout(self.socket, 3024, 5)

                    if not data:
                        continue

                    self.connector.last_response_time = time.time()

                    udata = data.decode('utf-8')
                    json_data = json.loads(udata)

                    if 'event' in json_data and self.connector.values_accepted:
                        print('Receive: ', json_data)
                        self.connector.events.append(json_data)

                    if 'response' in json_data and json_data['id'] in self.connector.request_ids:
                        print('Receive: ', json_data)
                        self.connector.request_ids.remove(json_data['id'])
                        self.connector.responses.append(json_data)

                except json.decoder.JSONDecodeError:
                    pass
                except (ConnectionError, ConnectionResetError, ConnectionRefusedError):
                    self.connector.connected = False

    def __init__(self, controller):
        super(SocketsConnector, self).__init__(controller)
        self.name = 'Sockets'

        self.socket = None

    def init_connection(self):
        try:
            self.socket = socket.socket()
            self.socket.settimeout(1.5)
            self.socket.connect(tuple(BaseConnector.SOCKET_CONFIG))
            self.socket.settimeout(None)

            super().init_connection()

            self.start_io_threads()

            if self.get_response(self.send_request({'request': 'set_ready', 'args': {'status': True}})):
                self.connected = True
                self.start_alive_thread()
        except:
            self.connected = False

        return self.connected

    def process_task(self, task, args, kwargs):

        if not self.socket:
            return False

        try:
            self.socket.send(json.dumps(task).encode())
        except Exception:
            self.connected = False

        return self.connected
