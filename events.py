from connectors.sockets import SocketsConnector
from connectors.vkbot import VkConnector


class EventsManager:

    def __init__(self, controller):
        self.controller = controller

        self.connectors = [
            SocketsConnector(controller),
            VkConnector(controller)
        ]

        self.current_connector = None
        self.status = True

    def shutdown(self):
        for connector in self.connectors:
            connector.shutdown()

    def next_controller(self):

        if self.current_connector is None or self.connectors.index(self.current_connector) == len(self.connectors) - 1:
            self.current_connector = self.connectors[0]
        else:
            for connector in self.connectors[self.connectors.index(self.current_connector) + 1:]:
                self.current_connector = connector
                break

        return self.current_connector

    def connection_exists(self):
        return any(connector.has_connection() for connector in self.connectors)

    def get_updates(self):
        while self.current_connector.has_connection() and self.status:
            for event in self.current_connector.get_updates():
                yield event

    def send_request(self, data):
        if self.current_connector is None:
            raise ConnectionError("Отсутствует соединение с каким-либо коннектором")
        request_id = self.current_connector.send_request(data)
        return self.current_connector.get_response(request_id)
